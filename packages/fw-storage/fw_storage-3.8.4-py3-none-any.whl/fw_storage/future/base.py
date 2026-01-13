"""Storage base module defining the abstract config and client interfaces."""

import shutil
import typing as t
import warnings
from abc import ABC, abstractmethod
from pathlib import Path

import fw_utils  # TODO minimize/phase out usage
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from .. import filters  # TODO phase out usage
from . import errors

Mode = t.Literal["r", "w"]
AnyPath = t.Union[str, Path, "File"]
ConfigT = t.TypeVar("ConfigT", bound="Config")
CloudConfigT = t.TypeVar("CloudConfigT", bound="CloudConfig")
FileT = t.TypeVar("FileT", bound="File")
StorageT = t.TypeVar("StorageT", bound="Storage")


class File(BaseModel):
    """File model with common attrs of files or blobs."""

    type: t.Literal["fs", "s3", "gs", "az"]
    path: str
    size: int
    hash: str
    ctime: t.Union[int, float, None] = None
    mtime: t.Union[int, float, None] = None

    def __str__(self) -> str:
        """Return string representation."""
        return self.path

    @property
    def name(self) -> str:
        """Return the base filename of this path."""
        return Path(self.path).name

    @property
    def stem(self) -> str:
        """Return the filename stem without any extension suffix."""
        return Path(self.path).stem

    @property
    def ext(self) -> str:
        """Return the extension of this path."""
        return Path(self.path).suffix.lstrip(".")

    @property
    def dir(self) -> str:
        """Return the directory name of this path."""
        dirname = str(Path(self.path).parent)
        return "" if dirname == "." else dirname

    @property
    def depth(self) -> int:
        """Return the path's depth - starting at 1 for top-level files."""
        return 1 + self.path.count("/")  # pragma: no cover

    # STORAGE FILEINFO INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)

    @property
    def created(self):
        """Backwards compatibility only."""
        return self.ctime

    @property
    def modified(self):
        """Backwards compatibility only."""
        return self.mtime

    def asdict(self) -> dict:
        """Backwards compatibility only."""
        return self.model_dump()  # pragma: no cover

    @model_validator(mode="before")
    @classmethod
    def backward_compat(cls, values: dict) -> dict:
        """Backwards compatibility for created/modified fields."""
        values.setdefault("ctime", values.pop("created", None))
        values.setdefault("mtime", values.pop("modified", None))
        return values


class Config(ABC, BaseModel):
    """Storage config interface."""

    model_config = ConfigDict(extra="forbid", coerce_numbers_to_str=True)

    def model_dump(self, reveal: t.Optional[bool] = None, **kw) -> dict:
        """Return model as a dict, w/o defaults and optionally revealed secrets.

        Args:
            reveal: Set to True to reveal secret values, or False to mask them.
            **kw: Keyword arguments passed to pydantic.BaseModel.dict().
        """
        kw.setdefault("exclude_none", True)
        kw.setdefault("exclude_unset", True)
        kw.setdefault("exclude_defaults", True)
        if reveal is None:
            secret = kw.pop("secret", None)
            reveal = secret == "val" if secret else None  # noqa: S105
        data = super().model_dump(**kw)
        for key, val in data.items():
            if reveal is not None and isinstance(val, SecretStr):  # pragma: no cover
                data[key] = val.get_secret_value() if reveal else str(val)
        return data

    def dict(self, reveal: t.Optional[bool] = None, **kw) -> dict:
        """Return model as a dict, w/o defaults and optionally revealed secrets.

        Args:
            reveal: Set to True to reveal secret values, or False to mask them.
            **kw: Keyword arguments passed to pydantic.BaseModel.dict().
        """
        warnings.warn(
            f'{self.__class__.__name__}.dict() is deprecated and replaced by "model_dump()"',
            DeprecationWarning,
        )
        return self.model_dump(reveal=reveal, **kw)  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_url(cls: t.Type[ConfigT], url: str) -> ConfigT:
        """Return storage config from a URL."""

    @abstractmethod
    def to_url(self, params: bool = False) -> str:
        """Return storage URL string.

        Args:
            params: Set to True to include auth/query params in the URL, if any.
        """

    @abstractmethod
    def create_client(self) -> "Storage":
        """Return storage client from this config."""

    def __str__(self) -> str:
        """Return string representation."""
        return f"{type(self).__name__}({self.to_url()!r})"

    # STORAGE CONFIG INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)

    @property
    def safe_url(self) -> str:
        """Backwards compatibility only."""
        return self.to_url()

    @property
    def full_url(self) -> str:
        """Backwards compatibility only."""
        return self.to_url(params=True)

    def apply_override(self, override) -> None:
        """Backwards compatibility only."""
        properties = self.model_json_schema()["properties"]
        for key, value in override.model_dump(exclude_unset=True).items():
            assert key in properties
            setattr(self, key, value)


class UploadPart(t.TypedDict):
    """Single part in a multipart upload model."""

    part: int
    etag: t.Optional[str]


class Storage(ABC, t.Generic[ConfigT, FileT]):
    """File storage client interface."""

    @abstractmethod
    def __init__(self, config: ConfigT) -> None:
        """Init storage client with config."""
        self.config = config  # pragma: no cover

    @abstractmethod
    def relpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return relative item path, stripping any path prefix."""

    @abstractmethod
    def abspath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return absolute item path, including any path prefix."""

    def urlpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return fully qualified item path, including the storage URL."""
        urlpath = self.config.to_url()
        relpath = self.relpath(path)
        if relpath and not urlpath.endswith("/"):
            urlpath += "/"
        return f"{urlpath}{relpath}"

    @abstractmethod
    def ls(  # noqa: D417
        self,
        path: t.Optional[AnyPath] = None,
        filt: t.Optional[t.Callable[[FileT], bool]] = None,
        **kw,
    ) -> t.Iterator[FileT]:
        """Yield sorted storage items, optionally filtered.

        Args:
            path: Path prefix to yield items from.
            filt: Callback to filter items with.
        """

    @abstractmethod
    def stat(self, path: AnyPath) -> FileT:
        """Return a storage item from an str or Path."""

    @abstractmethod
    def open(self, path: AnyPath, mode: Mode = "r") -> t.BinaryIO:
        """Return an item opened for reading or writing."""

    @abstractmethod
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove an item from the storage.

        Args:
            path: Storage item path to remove / delete.
            recurse: Set to True remove all items with the given prefix.
                Required when deleting fs:// directories, for example.
        """

    @abstractmethod
    def initiate_multipart_upload(self, path: AnyPath) -> str:
        """Initiate a multipart upload session."""

    @t.overload
    def generate_upload_url(self, path: AnyPath) -> str: ...  # pragma: no cover

    @t.overload
    def generate_upload_url(
        self, path: AnyPath, multipart_upload_id: str, part: int
    ) -> str: ...  # pragma: no cover

    @abstractmethod
    def generate_upload_url(
        self,
        path: AnyPath,
        multipart_upload_id: t.Optional[str] = None,
        part: t.Optional[int] = None,
    ) -> str:
        """Generate a signed upload url to upload a file.

        Args:
            path: Storage item path create signed upload url for.
            multipart_upload_id: Previously initialized upload id this part belongs to.
            part: If set indicates the file part in a multipart upload session.
                  If not set single url will be used and no need to invoke complete.
        """

    @abstractmethod
    def complete_multipart_upload(
        self,
        path: AnyPath,
        multipart_upload_id: str,
        parts: t.List[UploadPart],
    ) -> None:
        """Complete a multipart upload."""

    def test(self, mode: Mode = "r") -> None:
        """Test whether the storage can be read/written and raise if not.

        Args:
            mode: Set to "w" to check write/rm perms in addition to ls/read.
        """
        # test open("w") and write() if mode=w
        fw_test = "fw-test"
        if mode == "w":
            with self.open(fw_test, mode="w") as file:
                file.write(fw_test.encode("ascii"))
        # test ls() then stat() the first item
        item: t.Any = None
        for item in self.ls():
            item = self.stat(item)
            break
        else:
            # for/else: no items found - if "w", we expect the test file
            if mode == "w":  # pragma: no cover
                raise errors.StorageError(f"ls() did not yield {fw_test!r}")
        # test open("r") and read() a single byte (whole file could be BIG)
        # use the test file if "w", or the 1st ls() yield if available
        item = fw_test if mode == "w" else item
        if item:
            with self.open(item) as file:
                file.read(1)
        # test rm() on the test file if mode=w
        if mode == "w":
            self.rm(fw_test)
            self.cleanup()

    def cleanup(self) -> None:
        """Run any cleanup steps."""

    def __enter__(self: StorageT) -> StorageT:
        """Enter context to enable auto-cleanup on exit."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Run any cleanup steps upon exiting the context."""
        self.cleanup()

    def __del__(self) -> None:
        """Run any cleanup steps when garbage-collected."""
        self.cleanup()

    def __str__(self) -> str:
        """Return string representation."""
        return f"{type(self).__name__}({self.config.to_url()!r})"

    # STORAGE INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)
    # TODO consider ditching fw_utils / BinFile / metapath

    def fullpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Backwards compatibility only."""
        return self.urlpath(path)

    def test_read(self):
        """Backwards compatibility only."""
        self.test()

    def test_write(self):
        """Backwards compatibility only."""
        self.test(mode="w")

    @staticmethod
    def ls_filt_compat(kw: dict) -> t.Optional[t.Callable]:
        """Backwards compatibility only."""
        include = kw.get("include", None)
        exclude = kw.get("exclude", None)
        if not include and not exclude:
            return None
        # TODO deprecation warning (when most of future is implemented)
        return filters.StorageFilter(include=include, exclude=exclude).match

    def get(self, path: AnyPath):
        """Backwards compatibility only."""
        file = fw_utils.BinFile(self.open(path), metapath=self.relpath(path))
        # let BinFile close the handle when exiting the context
        file.file_open = True
        return file

    def set(self, path: AnyPath, file):
        """Backwards compatibility only."""
        with fw_utils.open_any(file) as rf, self.open(path, mode="w") as wf:
            shutil.copyfileobj(rf, wf)


class CloudConfig(Config):
    """Cloud storage config interface w/ rm_batch_max."""

    rm_batch_max: t.Optional[int] = Field(
        100,
        title="Max no. of blobs to delete in a single bulk operation.",
        ge=1,
        le=1000,
    )


class CloudStorage(Storage, t.Generic[CloudConfigT]):  # pragma: no cover
    """Cloud storage client interface defining rm_bulk() / implementing rm()."""

    @abstractmethod
    def __init__(self, config: CloudConfigT) -> None:
        """Init cloud storage client with config and an empty rm_keys."""
        self.config = config
        self.rm_keys: t.List[str] = []

    @abstractmethod
    def rm_bulk(self) -> None:
        """Remove all blobs in rm_keys with a bulk operation."""

    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Mark blob path to be removed in a bulk operation later."""
        if recurse:
            for item in self.ls(path):
                self.rm(item)
        else:
            self.rm_keys.append(self.abspath(path))
            if len(self.rm_keys) >= self.config.rm_batch_max:
                self.rm_bulk()
                self.rm_keys.clear()

    def cleanup(self) -> None:
        """Run bulk delete operation if any blobs are marked for removal."""
        if self.rm_keys:
            self.rm_bulk()
            self.rm_keys.clear()
