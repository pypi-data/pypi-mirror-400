"""Azure blob storage module."""

import functools
import os
import re
import typing as t
from base64 import b64encode
from datetime import timedelta

import azure.core.exceptions as az_errors
from azure.identity import DefaultAzureCredential
from azure.storage import blob as az_blob
from azure.storage.blob import ContainerClient
from azure.storage.blob._shared.policies import StorageRetryPolicy
from azure.storage.blob._shared.response_handlers import PartialBatchErrorException
from fw_utils import AnyFile, Filters, get_datetime, open_any
from pydantic import BaseModel, Field

from .. import errors
from ..config import SIGNED_URL_EXPIRY, AZConfig
from ..fileinfo import FileInfo
from ..filters import StorageFilter
from ..storage import AnyPath, CloudStorage, UploadPart

__all__ = ["AZStorage"]
LIST_PAGE_SIZE = 1000


def create_default_client(
    account: str,
    container: str,
    access_key: str = None,
) -> ContainerClient:
    """Azure Blob Container Client factory.

    Uses AZURE_ACCESS_KEY passed in directly or provided via the envvar.

    See the Azure docs for the full list of supported credential sources:
    https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential
    """
    creds = str(access_key) if access_key else DefaultAzureCredential()
    Client = functools.partial(ContainerClient, account, container, credential=creds)
    no_retry = AzureRetryPolicy(RetryConfig(total=1, backoff_factor=0.1))
    next(Client(retry_policy=no_retry).list_blobs(results_per_page=1), None)
    return Client(retry_policy=AzureRetryPolicy(RetryConfig()))


class RetryConfig(BaseModel):
    """Retry config."""

    total: int = Field(default_factory=lambda: int(os.getenv("AZURE_RETRY_TOTAL", "3")))
    backoff_factor: float = Field(
        default_factory=lambda: float(os.getenv("AZURE_RETRY_BACKOFF_FACTOR", "0.5"))
    )


class AzureRetryPolicy(StorageRetryPolicy):
    """Custom Azure retry policy."""

    def __init__(self, config: RetryConfig):
        """Init retry policy."""
        self.backoff_factor = config.backoff_factor
        super().__init__(retry_total=config.total, retry_to_secondary=False)

    def get_backoff_time(self, settings):  # pragma: no cover
        """Calculates how long to sleep before retrying."""
        # TODO re-add cover
        return self.backoff_factor * (2 ** settings["count"] - 1)


ERRMAP = {
    az_errors.ClientAuthenticationError: errors.PermError,
    az_errors.ResourceNotFoundError: errors.FileNotFound,
    az_errors.ResourceExistsError: errors.FileExists,
    az_errors.AzureError: errors.StorageError,
}
errmap = errors.ErrorMapper(ERRMAP)


class AZStorage(CloudStorage):
    """Azure Blob Storage class."""

    # NOTE Azure only supports up to 256 requests in a single batch
    delete_batch_size: t.ClassVar[int] = 256

    def __init__(
        self,
        config: AZConfig,
        **kwargs,
    ) -> None:
        """Construct Azure storage."""
        self.config = config

        secret = None
        if self.config.access_key:
            secret = self.config.access_key.get_secret_value()

        self.client = create_default_client(
            self.config.account,
            self.config.container,
            secret,
        )

        super().__init__(**kwargs)

    def abspath(self, path: AnyPath) -> str:
        """Return path string relative to the storage URL, including the perfix."""
        return f"{self.config.prefix}/{self.relpath(path)}".lstrip("/")

    def fullpath(self, path: AnyPath) -> str:
        """Return path string including the storage URL and prefix."""
        return f"az://{self.config.account}/{self.config.container}/{self.abspath(path)}".rstrip(
            "/"
        )

    @errmap
    def ls(
        self,
        path: AnyPath = "",
        *,
        include: Filters = None,
        exclude: Filters = None,
        **_,
    ) -> t.Iterator[FileInfo]:
        """Yield each item under prefix matching the include/exclude filters."""
        path = self.abspath(path)
        filt = StorageFilter(include=include, exclude=exclude)
        safe_config_prefix = re.escape(self.config.prefix)
        list_kwargs = {"name_starts_with": path, "results_per_page": LIST_PAGE_SIZE}
        for blob in self.client.list_blobs(**list_kwargs):
            relpath = re.sub(rf"^{safe_config_prefix}", "", blob.name).lstrip("/")
            info = FileInfo(
                type="az",
                path=relpath,
                size=blob.size,
                hash=blob.etag,
                created=blob.creation_time.timestamp(),
                modified=blob.last_modified.timestamp(),
            )
            # skip az "folders" - path is empty if the prefix itself is a "folder"
            if not relpath or relpath.endswith("/") and info.size == 0:
                continue  # pragma: no cover
            if filt.match(info):
                yield info

    @errmap
    def stat(self, path: AnyPath) -> FileInfo:
        """Return FileInfo for a single file."""
        blob_client = self.client.get_blob_client(self.abspath(path))
        blob = blob_client.get_blob_properties()
        return FileInfo(
            type="az",
            path=str(path),
            size=blob.size,
            hash=blob.etag,
            created=blob.creation_time.timestamp(),
            modified=blob.last_modified.timestamp(),
        )

    @errmap
    def download_file(self, path: AnyPath, dst: t.IO[bytes]) -> None:
        """Download file and it is opened for reading in binary mode."""
        blob_stream = self.client.download_blob(self.abspath(path))
        blob_stream.readinto(dst)

    @errmap
    def upload_file(self, path: AnyPath, file: AnyFile) -> None:
        """Write source file to the given path."""
        path = self.abspath(path)
        # upload_blob uses automatic chunking stated by Azure documentation
        with open_any(file, mode="rb") as r_file:
            self.client.upload_blob(name=path, data=r_file, overwrite=True)

    @errmap
    def flush_delete(self) -> None:
        """Remove a file at the given path."""
        keys = sorted(self.delete_keys)
        try:
            self.client.delete_blobs(*keys, delete_snapshots="include")
        except PartialBatchErrorException as exc:  # pragma: no cover
            keys_responses = zip(keys, exc.parts)
            errs = [(k, r) for k, r in keys_responses if not 200 <= r.status_code < 300]
            msg = f"Bulk delete operation failed for {len(errs)} files"
            exc = errors.StorageError(msg)
            exc.errors = [f"{k}: {r.reason}" for k, r in errs]
            raise exc
        finally:
            self.delete_keys.clear()

    def initiate_multipart_upload(self, path: AnyPath) -> str:
        """Initiate a multipart upload session."""
        return self.abspath(path)

    @errmap
    def generate_download_url(
        self,
        path: AnyPath,
    ) -> str:
        """Generate signed download url."""
        path = self.abspath(path)
        now = get_datetime()
        expiry = now + timedelta(seconds=SIGNED_URL_EXPIRY)

        creds: dict = {}
        if self.config.access_key:
            creds["account_key"] = self.config.access_key.get_secret_value()
        else:  # pragma: no cover
            blob_svc = self.client._get_blob_service_client()
            creds["user_delegation_key"] = blob_svc.get_user_delegation_key(now, expiry)

        sas_token = az_blob.generate_blob_sas(
            self.config.account_name,
            self.config.container,
            path,
            permission=az_blob.BlobSasPermissions(read=True),
            expiry=expiry,
            **creds,
        )
        url = f"{self.client.get_blob_client(path).url}?{sas_token}"
        return url

    @errmap
    def generate_upload_url(
        self,
        path: AnyPath,
        multipart_upload_id: t.Optional[str] = None,
        part: t.Optional[int] = None,
    ) -> str:
        """Generate signed upload url."""
        # https://learn.microsoft.com/en-us/rest/api/storageservices/put-blob
        path = self.abspath(path)
        now = get_datetime()
        expiry = now + timedelta(seconds=SIGNED_URL_EXPIRY)

        # https://learn.microsoft.com/en-us/azure/storage/blobs/sas-service-create-python
        creds: dict = {}
        if self.config.access_key:
            creds["account_key"] = self.config.access_key.get_secret_value()
        else:  # pragma: no cover
            # NOTE a user delegation SAS must be assigned an Azure RBAC role that
            # includes the generateUserDelegationKey action
            blob_svc = self.client._get_blob_service_client()
            creds["user_delegation_key"] = blob_svc.get_user_delegation_key(now, expiry)

        sas_token = az_blob.generate_blob_sas(
            self.config.account_name,
            self.config.container,
            path,
            permission=az_blob.BlobSasPermissions(write=True),
            expiry=expiry,
            **creds,
        )
        url = f"{self.client.get_blob_client(path).url}?{sas_token}"
        # https://learn.microsoft.com/en-us/rest/api/storageservices/put-block
        if part is not None:
            url += f"&comp=block&blockid={get_block_id(part, True)}"
        return url

    @errmap
    def complete_multipart_upload(
        self,
        path: AnyPath,
        multipart_upload_id: str,
        parts: t.List[UploadPart],
    ) -> None:
        """Complete a multipart upload."""
        # https://learn.microsoft.com/en-us/rest/api/storageservices/put-block-list
        path = self.abspath(path)
        # NOTE BlobBlock expects decoded block id
        block_list = [az_blob.BlobBlock(get_block_id(p["part"])) for p in parts]
        self.client.get_blob_client(path).commit_block_list(block_list)


def get_block_id(part: int, b64: bool = False) -> str:
    """Return padded blob block id."""
    block_id = f"{part:04}"
    return b64encode(block_id.encode()).decode() if b64 else block_id
