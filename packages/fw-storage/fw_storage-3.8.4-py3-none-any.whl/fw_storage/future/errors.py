"""Storage errors."""

import functools
import inspect
import re
import sys
import types
import typing as t


class StorageError(Exception):
    """Base exception class for all storage errors."""

    def __init__(self, message: str) -> None:
        """Init StorageError."""
        super().__init__(message)
        self.message = message
        self.exc = None  # if present and not one of the builtins based on
        self.path = None  # if present and not in message (~cloud)
        self.errors: list = []  # if present, sample and count at the end

    def __str__(self) -> str:
        """Return string representation."""
        msg = self.message
        cls_name = type(self).__name__
        if self.exc and not format_exc_cls(self.exc).startswith(cls_name):
            msg = f"{format_exc_cls(self.exc)}: {msg}"  # pragma: no cover
        if self.path and re.sub(r"^.*://", "", self.path) not in msg:
            msg += f"\n  path: {self.path}"
        if self.errors:  # pragma: no cover
            err_cnt, limit = len(self.errors), 3
            msg += f"\n  errors (showing first {limit} of {err_cnt}):"
            msg += "\n    - ".join([""] + [str(e) for e in self.errors[:limit]])
            if err_cnt > limit:
                msg += f"\n    - and {err_cnt - limit} more...')"
        return msg


class PermissionError(StorageError):
    """Permission error. Raised when roles/permissions are insufficient."""


# TODO deprecation warning (when most of future is implemented)
PermError = PermissionError


class FileNotFound(StorageError):
    """File not found. Raised when trying to access a file that doesn't exist."""


class FileExists(StorageError):
    """File already exists. Raised when trying to create a file that's present."""


class IsADirectory(StorageError):
    """Path is a directory. Raised when a file operation is used on a dir."""


class NotADirectory(StorageError):
    """Path is not a directory. Raised when a dir operation is used on a file."""


ErrorHandler = t.Callable[
    [t.Union[Exception, t.Type[Exception]]],
    t.Union[StorageError, t.Type[StorageError]],
]


class ErrorMapper:
    """Parameterized decorator for raising StorageErrors from 3rd-party exceptions."""

    def __init__(
        self,
        errors: t.Dict[t.Type[Exception], t.Type[StorageError]],
        mapper: t.Optional[ErrorHandler] = None,
    ):
        """Init the decorator with the errors to catch and the conversion func."""
        self.errors = errors
        self.mapper = mapper

    def __call__(self, func: t.Callable) -> t.Callable:
        """Return decorated function that maps errors to StorageErrors."""
        # TODO use decorator.decorator to retain signature
        if inspect.isgeneratorfunction(func):

            def wrapper(*args, **kwargs):
                try:
                    yield from func(*args, **kwargs)
                except tuple(self.errors) as exc:
                    raise self.map(exc, args, kwargs) from exc

        else:

            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except tuple(self.errors) as exc:
                    raise self.map(exc, args, kwargs) from exc

        return functools.wraps(func)(wrapper)

    def map(self, exc, args, kwargs) -> StorageError:
        """Return StorageError with context mapped from a raw exception."""
        mapped = StorageError
        if self.mapper:
            mapped = self.mapper(exc)
        else:
            for err_cls in self.errors:
                if isinstance(exc, err_cls):
                    mapped = self.errors[err_cls]
                    break
        if inspect.isclass(mapped):
            mapped = mapped(str(exc))
        assert isinstance(mapped, StorageError)
        storage = args[0]
        relpath = args[1] if len(args) > 1 else kwargs.get("path", "")
        mapped.path = storage.fullpath(relpath)
        mapped.exc = exc
        tb_frame = sys.exc_info()[2].tb_frame.f_back  # type: ignore
        assert tb_frame
        tb = types.TracebackType(
            tb_next=None,
            tb_frame=tb_frame,
            tb_lasti=tb_frame.f_lasti,
            tb_lineno=tb_frame.f_lineno,
        )
        return mapped.with_traceback(tb)


def get_exc_cls(exc: t.Union[Exception, t.Type[Exception]]) -> t.Type[Exception]:
    """Return exception class from an exception instance or type."""
    return exc if inspect.isclass(exc) else type(exc)  # type: ignore


def format_exc_cls(exc: t.Union[Exception, t.Type[Exception]]) -> str:
    """Return fully-qualified exception type formatted as in tracebacks."""
    exc_cls = get_exc_cls(exc)
    exc_fqn = f"{exc_cls.__module__}.{exc_cls.__name__}"
    return exc_fqn.replace("builtins.", "")
