"""Google Cloud Storage module."""

import json
import re
import typing as t
from datetime import timedelta

import google.api_core.exceptions as gs_errors
from fw_utils import AnyFile, Filters
from google.cloud.storage import Blob, Client
from google.cloud.storage import transfer_manager as tx_manager
from google.cloud.storage.client import Connection
from google.cloud.storage.retry import DEFAULT_RETRY

from .. import errors
from ..config import SIGNED_URL_EXPIRY, GSConfig
from ..fileinfo import FileInfo
from ..filters import StorageFilter
from ..storage import AnyPath, CloudStorage, UploadPart

__all__ = ["GSStorage"]

DEFAULT_CONTENT_TYPE = "application/octet-stream"

ERRMAP = {
    gs_errors.NotFound: errors.FileNotFound,
    gs_errors.Forbidden: errors.PermError,
    gs_errors.GoogleAPIError: errors.StorageError,
}
errmap = errors.ErrorMapper(ERRMAP)


class GSStorage(CloudStorage):
    """Google Cloud Storage class."""

    # NOTE Cloud Storage only supports up to 100 requests in a single batch
    delete_batch_size: t.ClassVar[int] = 100

    def __init__(  # noqa: D417
        self,
        config: GSConfig,
        **kwargs,
    ):
        """Google Cloud Storage class for working with blobs in GCS buckets.

        Args:
            config: config: GSConfig
        """
        self.config = config

        secret = None
        if self.config.application_credentials:
            secret = self.config.application_credentials.get_secret_value()
        if secret and secret.strip().startswith("{"):
            creds_obj = json.loads(secret)
            self.client = Client.from_service_account_info(info=creds_obj)
        else:
            # fallback to default credentials
            self.client = Client()  # pragma: no cover

        super().__init__(**kwargs)

    def abspath(self, path: AnyPath) -> str:
        """Return path string relative to the storage URL, including the perfix."""
        return f"{self.config.prefix}/{self.relpath(path)}".lstrip("/")

    def fullpath(self, path: AnyPath) -> str:
        """Return path string including the storage URL and prefix."""
        return f"gs://{self.config.bucket}/{self.abspath(path)}".rstrip("/")

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
        # https://cloud.google.com/storage/docs/folders#gsutil
        # https://cloud.google.com/storage/docs/hashes-etags
        filt = StorageFilter(include=include, exclude=exclude)
        prefix = f"{self.config.prefix}/{path}".strip("/")
        if prefix:
            prefix += "/"
        safe_config_prefix = re.escape(self.config.prefix)
        for blob in self.client.list_blobs(self.config.bucket, prefix=prefix):
            relpath = re.sub(rf"^{safe_config_prefix}", "", blob.name).lstrip("/")
            info = FileInfo(
                type="gs",
                path=relpath,
                size=blob.size,
                hash=blob.etag,
                created=blob.time_created.timestamp(),
                modified=blob.updated.timestamp(),
            )
            # skip gs "folders" - path is empty if the prefix itself is a "folder"
            if not relpath or relpath.endswith("/") and info.size == 0:
                continue  # pragma: no cover
            if filt.match(info):
                yield info

    @errmap
    def stat(self, path: AnyPath) -> FileInfo:
        """Return FileInfo for a single file."""
        blob = self.client.bucket(self.config.bucket).blob(self.abspath(path))
        blob.reload()
        return FileInfo(
            type="gs",
            path=str(path),
            size=blob.size,
            hash=blob.etag,
            created=blob.time_created.timestamp(),
            modified=blob.updated.timestamp(),
        )

    @errmap
    def download_file(self, path: AnyPath, dst: t.IO[bytes]) -> None:
        """Download file and it opened for reading in binary mode."""
        path = self.abspath(path)
        self.client.bucket(self.config.bucket).blob(path).download_to_file(dst)

    @errmap
    def upload_file(self, path: AnyPath, file: AnyFile) -> None:
        """Upload file to the given path."""
        path = self.abspath(path)
        blob = self.client.bucket(self.config.bucket).blob(path)
        if isinstance(file, bytes):
            upload_func = blob.upload_from_string
        elif isinstance(file, str):
            upload_func = blob.upload_from_filename
        else:
            upload_func = blob.upload_from_file
        # by default, only uploads with if_generation_match set
        # will be retried, override this and retry always for now
        # TODO consider fetching the current generation and use that
        # but it would require one additional request per upload
        # see: https://cloud.google.com/storage/docs/generations-preconditions
        upload_func(file, content_type=DEFAULT_CONTENT_TYPE, retry=DEFAULT_RETRY)

    @errmap
    def flush_delete(self):
        """Flush pending remove operations."""
        keys = sorted(self.delete_keys)
        with self.client.batch(raise_exception=False) as batch:
            for key in keys:
                self.client.bucket(self.config.bucket).blob(key).delete()
        self.delete_keys.clear()
        keys_responses = zip(keys, batch._responses)
        errs = [(k, r) for k, r in keys_responses if not 200 <= r.status_code < 300]
        if errs:  # pragma: no cover
            msg = f"Bulk delete operation failed for {len(errs)} files"
            exc = errors.StorageError(msg)
            exc.errors = [f"{k}: {r.json()['error']['message']}" for k, r in errs]
            raise exc

    def initiate_multipart_upload(self, path: AnyPath) -> str:
        """Initiate a multipart upload session."""
        # https://cloud.google.com/storage/docs/multipart-uploads
        path = self.abspath(path)
        blob = self.client.bucket(self.config.bucket).blob(path)
        return get_xml_mpu_container(blob).upload_id

    def generate_download_url(
        self,
        path: AnyPath,
    ) -> str:
        """Generate signed download url."""
        path = self.abspath(path)
        blob = self.client.bucket(self.config.bucket).blob(path)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=SIGNED_URL_EXPIRY),
            method="GET",
            api_access_endpoint=Connection.DEFAULT_API_ENDPOINT,
        )
        return url

    def generate_upload_url(
        self,
        path: AnyPath,
        multipart_upload_id: t.Optional[str] = None,
        part: t.Optional[int] = None,
    ) -> str:
        """Generate signed upload url."""
        path = self.abspath(path)
        blob = self.client.bucket(self.config.bucket).blob(path)
        params = {}
        if multipart_upload_id:
            params = {
                "uploadId": multipart_upload_id,
                "partNumber": part,
            }

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=SIGNED_URL_EXPIRY),
            method="PUT",
            query_parameters=params,
            api_access_endpoint=Connection.DEFAULT_API_ENDPOINT,
        )
        return url

    def complete_multipart_upload(
        self,
        path: AnyPath,
        multipart_upload_id: str,
        parts: t.List[UploadPart],
    ) -> None:
        """Complete a multipart upload."""
        path = self.abspath(path)
        blob = self.client.bucket(self.config.bucket).blob(path)
        container = get_xml_mpu_container(blob, multipart_upload_id)
        for part in parts:
            container.register_part(part["part"], part["etag"])
        container.finalize(blob._get_transport(self.client))


def get_xml_mpu_container(
    blob: Blob, multipart_upload_id: t.Optional[str] = None
) -> tx_manager.XMLMPUContainer:
    """Return low-level XML mpu container from blob and upload id."""
    # https://github.com/googleapis/python-storage/blob/ae9a53/google/cloud/storage/transfer_manager.py#L956
    bucket = blob.bucket
    client = blob.client
    transport = blob._get_transport(blob.client)
    hostname = client._connection.get_api_base_url_for_mtls()
    url = f"{hostname}/{bucket.name}/{blob.name}"

    base_headers, object_metadata, content_type = blob._get_upload_arguments(
        client,
        "application/octet-stream",
        filename=blob.name,
        command="tm.upload_sharded",
    )
    headers = {**base_headers, **tx_manager._headers_from_metadata(object_metadata)}

    if blob.user_project:  # pragma: no cover
        headers["x-goog-user-project"] = blob.user_project

    if blob.kms_key_name and "cryptoKeyVersions" not in blob.kms_key_name:
        kms_header = "x-goog-encryption-kms-key-name"  # pragma: no cover
        headers[kms_header] = blob.kms_key_name  # pragma: no cover

    container = tx_manager.XMLMPUContainer(
        url, blob.name, headers=headers, upload_id=multipart_upload_id
    )

    if not multipart_upload_id:
        container.initiate(transport=transport, content_type=content_type)

    return container
