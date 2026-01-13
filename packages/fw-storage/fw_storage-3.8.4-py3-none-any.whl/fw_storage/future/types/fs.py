"""FS / local file-system storage."""

import hashlib
import os
import re
import shutil
import sys
import typing as t
from functools import cached_property
from pathlib import Path, PureWindowsPath
from stat import S_IMODE

from pydantic import BaseModel, Field, field_validator, model_validator

from .. import base, errors, utils
from ..base import AnyPath, Config, File, Mode, Storage

ERRMAP: dict = {
    FileExistsError: errors.FileExists,
    FileNotFoundError: errors.FileNotFound,
    IsADirectoryError: errors.IsADirectory,
    NotADirectoryError: errors.NotADirectory,
    PermissionError: errors.PermError,
    OSError: errors.StorageError,
}

errmap = errors.ErrorMapper(ERRMAP)
chmod_re = r"^[0-7]{3}|([r-][w-][x-]){3}$"


class Compat(BaseModel):
    """Compatibility mixin for FSConfig and FSConfigOverride."""

    @model_validator(mode="before")
    @classmethod
    def backwards_compat(cls, values: dict) -> dict:
        """Map modified config field names/values for backwards-compatibility."""
        if not values.get("chown"):
            user = values.pop("user", None)
            uid, gid = values.pop("uid", None), values.pop("gid", None)
            if user or uid:
                # TODO deprecation warning (when most of future is implemented)
                pass
            if user:
                values["chown"] = user
            elif uid:
                values["chown"] = f"{uid}:{gid}" if gid else str(uid)
        values.pop("follow_links", None)
        return values

    @model_validator(mode="before")
    @classmethod
    def load_values(cls, values: dict) -> dict:
        """Coerce types and canonize raw user input values for chown/chmod."""
        if "chown" in values:
            values["chown"] = coerce_opt_str(values["chown"])
        if "chmod" in values:
            values["chmod"] = canonize_chmod(coerce_opt_str(values["chmod"]))
        return values

    @property
    def user(self) -> t.Optional[str]:
        """Alias for accessing 'chown' field for backwards-compatibility."""
        return getattr(self, "chown", None)


def coerce_opt_str(value: t.Optional[t.Union[int, str]]) -> t.Optional[str]:
    """Coerce optional string values provided as an int to str."""
    return str(value) if value is not None else None


def canonize_chmod(chmod: t.Optional[str]) -> t.Optional[str]:
    """Return file permissions in canonized, octal form if given."""
    if chmod and re.match(chmod_re, chmod):
        if not chmod.isdigit():
            chmod = "".join(["0" if c == "-" else "1" for c in chmod])
            chmod = "".join([str(int(chmod[i : i + 3], base=2)) for i in (0, 3, 6)])
        modes = [int(c) for c in chmod]
        modes[0] = 6  # always use read-write owner perms
        modes[1] -= modes[1] % 2  # disable group +x
        modes[2] -= modes[2] % 2  # disable other +x
        chmod = "".join([str(c) for c in modes])
    return chmod


class FSConfig(Config, Compat):
    """FS / local file-system storage config."""

    type: t.Literal["fs"] = Field("fs", title="FS storage type")
    path: str = Field(title="FS directory path", examples=["/mnt/data"])
    cleanup_dirs: utils.Bool = Field(
        default=False,
        title="Remove empty directories on cleanup",
    )
    content_hash: utils.Bool = Field(
        default=False,
        title="Calculate content-hash for files (md5)",
    )
    groups: t.Optional[t.List[int]] = Field(
        default=None,
        title="Supplementary unix group IDs to use when accessing files",
        examples=[[2000]],
    )
    chown: t.Optional[str] = Field(
        default=None,
        title="Unix user[:group] ID to use when accessing files",
        examples=["1000", "1000:1000"],
        pattern=r"^[0-9]+(:[0-9]+)?$",
    )
    chmod: t.Optional[str] = Field(
        default=None,
        title="Unix file permissions to set when writing files",
        examples=["664", "rw-rw-r--"],
        pattern=chmod_re,
    )

    @classmethod
    def from_url(cls, url: str) -> "FSConfig":
        """Return FS storage config parsed from the given storage URL."""
        parsed = utils.URL.from_string(url).model_dump()
        groups = parsed.pop("groups", None)
        config = {
            "type": parsed.pop("scheme"),
            "path": f"{parsed.pop('host', '')}{parsed.pop('path', '')}",
            "cleanup_dirs": parsed.pop("cleanup_dirs", None),
            "content_hash": parsed.pop("content_hash", None),
            "groups": groups.split(",") if groups else None if groups is None else [],
            "chown": parsed.pop("chown", None),
            "chmod": parsed.pop("chmod", None),
        }
        config.update(parsed)
        return cls(**utils.filter_none(config))

    def to_url(self, params: bool = False) -> str:
        """Return FS storage URL, optionally including all parameters."""
        parsed: dict = {"scheme": self.type, "path": self.path}
        if params:
            config = self.model_dump()
            extras = ["cleanup_dirs", "content_hash", "chown", "chmod"]
            parsed["query"] = {key: config.get(key) for key in extras}
            if self.groups is not None:
                parsed["query"]["groups"] = ",".join(str(g) for g in self.groups)

        return str(utils.URL(**parsed))

    def create_client(self) -> "FSStorage":
        """Return FS storage client from this config."""
        return FSStorage(self)

    @cached_property
    def file_owner(self) -> t.Tuple[t.Optional[int], t.Optional[int]]:
        """Return unix user & group as a tuple of ints for os.seteud/setegid."""
        user_and_group = self.chown or ""
        user, _, group = user_and_group.partition(":")
        uid = int(user) if user else None
        gid = int(group) if group else None
        return uid, gid

    @cached_property
    def file_perms(self) -> t.Optional[int]:
        """Return unix file permissions as needed for pathlib.Path.chmod."""
        return int(self.chmod, base=8) if self.chmod else None

    @cached_property
    def dir_perms(self) -> t.Optional[int]:
        """Return unix dir permissions as needed for pathlib.Path.chmod."""
        # add +x (required for ls) for user/group/all if +r(4->5) or +rw(6->7)
        table = str.maketrans({"4": "5", "6": "7"})
        return int(self.chmod.translate(table), base=8) if self.chmod else None

    @field_validator("path")
    @classmethod
    def canonize_path(cls, path: str) -> str:
        """Return absolute path, resolving any ~ refs and symlinks."""
        if not (Path(path).is_absolute() or PureWindowsPath(path).is_absolute()):
            raise ValueError(f"Path must be absolute: {path}")
        return path


CopyField = utils.copy_field_func(FSConfig)


class FSConfigOverride(Compat):
    """FS / local file-system storage config runtime overrides."""

    type: t.Literal["fs"] = CopyField("type")
    cleanup_dirs: utils.Bool = CopyField("cleanup_dirs")
    content_hash: utils.Bool = CopyField("content_hash")
    groups: t.Optional[t.List[int]] = CopyField("groups")
    chown: t.Optional[str] = CopyField("chown")
    chmod: t.Optional[str] = CopyField("chmod")


class FSFile(File):
    """FS / local file-system file model."""

    type: t.Literal["fs"] = "fs"
    owner: str
    perms: str


class FSStorage(Storage):
    """FS / local file-system storage client."""

    def __init__(self, config: FSConfig) -> None:
        """Init FS / local file-system storage from a config."""
        self.config = config
        path = Path(config.path)
        if sys.platform != "win32":
            self.fs_groups = config.groups
            self.os_groups = os.getgroups()
            self.fs_uid, self.fs_gid = config.file_owner
            self.os_uid, self.os_gid = os.geteuid(), os.getegid()
        with self:
            if not path.exists():
                raise errors.StorageError(f"path doesn't exist: {path}")
            if not path.is_dir():
                raise errors.NotADirectory(f"path is not a dir: {path}")

    def __enter__(self: "FSStorage") -> "FSStorage":
        """Set effective UID/GID for the storage context if configured."""
        # NOTE uid changes are process-global and thus not thread-safe!
        # and not supported on Windows
        if sys.platform != "win32":
            if self.fs_groups and set(self.fs_groups) != set(os.getgroups()):
                os.setgroups(self.fs_groups)
            if self.fs_gid is not None and self.fs_gid != os.getegid():
                os.setegid(self.fs_gid)
            if self.fs_uid is not None and self.fs_uid != os.geteuid():
                os.seteuid(self.fs_uid)
        return super().__enter__()

    def __exit__(self, exc_type, exc, tb) -> None:
        """Restore effective UID/GID when exiting the storage context."""
        super().__exit__(exc_type, exc, tb)
        if sys.platform != "win32":
            if self.os_uid != os.geteuid():
                os.seteuid(self.os_uid)
            if self.os_gid != os.getegid():
                os.setegid(self.os_gid)
            if set(self.os_groups) != set(os.getgroups()):
                os.setgroups(self.os_groups)

    def relpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return relative file path, excluding the storage path."""
        root = Path(self.config.path).as_posix()
        path = Path(str(path or "")).as_posix()
        relpath = Path(re.sub(rf"^{root}/?", "", str(path))).as_posix()
        return "" if str(relpath) == "." else str(relpath)

    def abspath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return absolute file path, including the storage path."""
        return str(Path(self.config.path) / self.relpath(path))

    @errmap
    def ls(  # noqa: D417, PLR0913
        self,
        path: t.Optional[AnyPath] = None,
        filt: t.Optional[t.Callable[[FSFile], bool]] = None,
        filt_dir: t.Optional[t.Callable[[str], bool]] = None,
        filt_file: t.Optional[t.Callable[[str], bool]] = None,
        **kw,
    ) -> t.Iterator[FSFile]:
        """Yield sorted files, optionally filtered.

        Args:
            path: Path prefix / subdir to yield files from.
            filt: File filter callback for including/exluding by path, size, etc.
            filt_dir: Dirname filter callback for pruning the walk tree.
            filt_file: Filename filter callback for skipping stat() calls.
        """
        top = self.abspath(path)
        filt = filt or self.ls_filt_compat(kw) or utils.true
        # TODO before 1st usage in prod, consider adding to super() interface
        filt_dir = filt_dir or utils.true
        filt_file = filt_file or utils.true
        rel_dirs: t.List[str] = []
        rel_files: t.List[str] = []
        for root, dirs, files in os.walk(top, onerror=onerr):

            def rel(name):
                return self.relpath(f"{root}/{name}")

            # pop first dir from the buffer (should be the root)
            assert not rel_dirs or rel_dirs.pop(0) == rel("")
            # filter out symbolic links - os.walk returns them in dirs but won't visit them
            dirs[:] = [d for d in dirs if not os.path.islink(f"{root}/{d}")]
            # apply the dir filters to prune the walk tree for efficiency
            # also sort dirs to enforce deterministic walk order
            dirs[:] = [d for d in sorted(dirs) if filt_dir(d)]
            rel_dirs.extend([rel(d) for d in dirs])
            rel_dirs.sort()
            # apply the path-based filters before using os.stat for efficiency
            files = [f for f in sorted(files) if filt_file(f)]
            rel_files.extend([rel(f) for f in files])
            rel_files.sort()
            # use sorted dir and file buffers to yield in total order
            # ie. stop yielding if a sibling dir should be walked first
            while rel_files and not (rel_dirs and rel_dirs[0] < rel_files[0]):
                item = self.stat(rel_files.pop(0))
                if filt(item):
                    yield item

    @errmap
    def stat(self, path: AnyPath) -> FSFile:
        """Return file stat from an str or Path."""
        path = Path(self.abspath(path))
        stat = path.stat()
        return FSFile(
            path=self.relpath(path),
            size=stat.st_size,
            ctime=stat.st_ctime,
            mtime=stat.st_mtime,
            hash=md5sum(path, stat, self.config.content_hash),
            owner=f"{stat.st_uid}:{stat.st_gid}",
            perms=oct(S_IMODE(path.stat().st_mode))[-3:],
        )

    @errmap
    def open(self, path: AnyPath, mode: Mode = "r") -> t.BinaryIO:
        """Return a file opened for reading or writing."""
        path = Path(self.abspath(path))
        mode_str = "reading" if mode == "r" else "writing"
        # ! raise if the file path is a directory
        if path.is_dir():
            raise errors.IsADirectory(
                f"Can't open '{self.relpath(path)}' for {mode_str} "
                f"because it is a directory (file expected)"
            )
        # ! raise if any parent path exists and is not a directory
        parent = None
        while parent := (parent or path).parent:
            if parent.is_dir():
                break
            if parent.exists():
                raise errors.NotADirectory(
                    f"Can't open file '{self.relpath(path)}' for {mode_str}: "
                    f"path prefix '{self.relpath(parent)}' is not a directory"
                )
        if mode == "w":
            # detect missing parents
            parent = path.parent
            missing: t.List[Path] = []
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            # autocreate missing parents
            for parent in reversed(missing):
                parent.mkdir(exist_ok=True)
                if self.config.chmod:
                    parent.chmod(self.config.dir_perms)
            # ensure the file exists (touch) & set perms
            path.touch()
            if self.config.chmod:
                path.chmod(self.config.file_perms)
        file = path.open(mode=f"{mode}b")
        return t.cast(t.BinaryIO, file)

    @errmap
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove a file at the given path."""
        path = Path(self.abspath(path))
        if not path.is_dir():
            path.unlink()
        elif recurse:
            shutil.rmtree(path)
        else:
            raise errors.IsADirectory(f"cannot remove dir w/o recurse=True: {path!r}")

    @errmap
    def rm_empty_dirs(self):
        """Remove empty directories recursivey, bottom-up."""
        top = self.config.path
        deleted = set()
        for root, dirs, files in os.walk(top, topdown=False, onerror=onerr):
            if root == top:
                break
            dirs.sort()
            if not files and all(f"{root}/{d}" in deleted for d in dirs):
                os.rmdir(root)
                deleted.add(root)

    @errmap
    def download_file(self, path: AnyPath, dst: t.IO[bytes]) -> None:
        """Download file into the given binary handle."""
        with self.open(path) as src:
            shutil.copyfileobj(src, dst)

    def initiate_multipart_upload(self, path: AnyPath) -> str:
        """Initiate a multipart upload session."""
        raise NotImplementedError  # pragma: no cover

    def generate_upload_url(
        self,
        path: AnyPath,
        multipart_upload_id: t.Optional[str] = None,
        part: t.Optional[int] = None,
    ) -> str:
        """Generate signed upload url."""
        raise NotImplementedError  # pragma: no cover

    def complete_multipart_upload(
        self,
        path: AnyPath,
        multipart_upload_id: str,
        parts: t.List[base.UploadPart],
    ) -> None:
        """Complete a multipart upload."""
        raise NotImplementedError  # pragma: no cover

    def cleanup(self) -> None:
        """Remove empty directories if enabled on the config."""
        if self.config.cleanup_dirs:
            self.rm_empty_dirs()

    # STORAGE INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)

    @property
    def prefix(self) -> Path:
        """Backwards compatibility only."""
        return Path(self.config.path)


def onerr(exc: OSError):
    """Walk error callback to raise exceptions instead of swallowing them."""
    raise exc  # pragma: no cover


def md5sum(
    path: AnyPath,
    stat: os.stat_result,
    content_hash: bool = False,
    block_size: int = 2**20,
) -> str:
    """Return the first 32 chars of the file's MD5 content-hash."""
    md5 = hashlib.md5()  # noqa: S324
    if content_hash:
        with open(str(path), mode="rb") as file:
            while data := file.read(block_size):
                md5.update(data)
    else:
        md5.update(f"{path}{stat.st_size}{stat.st_mtime}".encode("utf8"))
    return md5.hexdigest()[:32]
