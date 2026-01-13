"""File-info module."""

import dataclasses
import typing as t
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class FileInfo:
    """FileInfo dataclass yielded from storage.ls() calls.

    Path is unique and relative to the storage prefix. Slots minimize memory
    usage to allow storing large number of FileInfo instances at once.
    """

    __slots__ = ("type", "path", "size", "hash", "created", "modified")

    type: t.Literal["fs", "s3", "gs", "az"]
    path: str
    size: int
    hash: t.Optional[str]
    created: t.Optional[t.Union[int, float]]
    modified: t.Optional[t.Union[int, float]]

    def __str__(self) -> str:  # pragma: no cover
        """Return the path string."""
        return self.path

    def asdict(self) -> t.Dict:
        """Return as a dictionary."""
        # TODO performance-test this and improve as needed
        return dataclasses.asdict(self)  # pragma: no cover

    # FUTURE COMPAT

    def dict(self) -> t.Dict:  # pragma: no cover
        """Future compatibility."""
        return self.asdict()

    def model_dump(self) -> t.Dict:  # pragma: no cover
        """Future compatibility."""
        return self.asdict()

    @property
    def name(self) -> str:  # pragma: no cover
        """Return the base filename of this path."""
        return Path(self.path).name

    @property
    def stem(self) -> str:  # pragma: no cover
        """Return the filename stem without any extension suffix."""
        return Path(self.path).stem

    @property
    def ext(self) -> str:  # pragma: no cover
        """Return the extension of this path."""
        return Path(self.path).suffix.lstrip(".")

    @property
    def dir(self) -> str:  # pragma: no cover
        """Return the directory name of this path."""
        dirname = str(Path(self.path).parent)
        return "" if dirname == "." else dirname

    @property
    def depth(self) -> int:  # pragma: no cover
        """Return the path's depth - starting at 1 for top-level files."""
        return 1 + self.path.count("/")

    @property
    def ctime(self) -> t.Optional[t.Union[int, float]]:  # pragma: no cover
        """Return file's ctime."""
        return self.created

    @property
    def mtime(self) -> t.Optional[t.Union[int, float]]:  # pragma: no cover
        """Return file's mtime."""
        return self.modified
