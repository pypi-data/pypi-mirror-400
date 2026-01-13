"""Utility functions."""

import re
import typing as t
import warnings
from functools import partial

import pydantic
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated

URL_RE = re.compile(
    r"^"
    r"(?P<scheme>[^+:@/?#]+)(\+(?P<driver>[^:@/?#]+))?://"
    r"((?P<username>[^:@]+)(:(?P<password>[^@]+))?@)?"
    r"(?P<host>[a-zA-Z]:|[^:@/?#]*)"
    r"(:(?P<port>\d+))?"
    r"((?P<path>/[^?#]*))?"
    r"(\?(?P<query>[^#]+))?"
    r"(#(?P<fragment>.*))?"
    r"$"
)


class URL(BaseModel, extra="forbid"):
    """URL model with driver & parsed query string."""

    scheme: str
    driver: t.Optional[str] = None
    username: t.Optional[str] = None
    password: t.Optional[str] = None
    host: t.Optional[str] = None
    port: t.Optional[int] = None
    path: t.Optional[str] = None
    query: t.Dict[str, str] = {}
    fragment: t.Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def flex_load(cls, values: dict) -> dict:
        """Return dict without null values and unknown keys as query params."""
        props = cls.model_json_schema()["properties"]
        query = values.pop("query", {})
        extra = [key for key in values if key not in props]
        for key in extra:
            query[key] = values.pop(key)
        values["query"] = {k: str(v) for k, v in filter_none(query).items()}
        values = filter_none(values)
        return values

    def model_dump(self, merge: bool = True, **kw) -> dict:  # noqa: D417
        """Return model as a dict, w/ the query merged into it by default.

        Args:
            merge: Set to False to retain query as a top-level dict key.
        """
        kw.setdefault("exclude_none", True)
        data = super().model_dump(**kw)
        if merge:
            data.update(data.pop("query", {}))
        return data

    def dict(self, merge: bool = True, **kw) -> dict:  # noqa: D417
        """Return model as a dict, w/ the query merged into it by default.

        Args:
            merge: Set to False to retain query as a top-level dict key.
        """
        warnings.warn(
            f'{self.__class__.__name__}.dict() is deprecated and replaced by "model_dump()"',
            DeprecationWarning,
        )
        return self.model_dump(merge=merge, **kw)  # pragma: no cover

    @classmethod
    def from_string(cls, url: str) -> "URL":
        """Return URL parsed from a string."""
        match = URL_RE.match(url)
        if not match:
            raise ValueError(f"cannot parse url {url!r}")
        parsed = filter_none(match.groupdict())
        params = [p for p in parsed.pop("query", "").split("&") if p]
        query = parsed["query"] = {}
        for param in params:
            param += "=" if "=" not in param else ""
            key, value = param.split("=", maxsplit=1)
            query.setdefault(key, value)
        return cls(**parsed)

    def __str__(self) -> str:
        """Return URL string."""
        url = self.scheme
        if self.driver:
            url += f"+{self.driver}"
        url += "://"
        if self.username:
            url += self.username
            if self.password:
                url += f":{self.password}"
            url += "@"
        if self.host:
            url += self.host
        if self.port:
            url += f":{self.port}"
        if self.path:
            url += self.path
        if self.query:
            query = ""
            for key, value in self.query.items():
                value = value.lower() if value in {"True", "False"} else value
                query += "?" if not query else "&"
                query += f"{key}={value}"
            url += query
        if self.fragment:
            url += f"#{self.fragment}"
        return url


def filter_none(data: dict) -> dict:
    """Return filtered dict without any None values."""
    return {k: v for k, v in data.items() if v is not None}


def true(_) -> bool:
    """Return True, regardless of the value passed. Default ls() filter."""
    return True


def copy_field_func(model: t.Type[BaseModel]) -> t.Callable:
    """Return pydantic Field copier for a given model."""
    return partial(copy_field, model)


def copy_field(model: t.Type[BaseModel], field: str, **kw) -> t.Callable:
    """Return pydantic Field with params copied from another model field."""
    props: dict = dict(model.model_fields[field].__repr_args__())  # type: ignore
    props.pop("annotation", None)
    props.pop("required", None)
    props.pop("metadata", None)
    props.update(default=model.model_fields[field].default)
    props.update(**kw)
    return Field(**props)  # type: ignore


def validate_bool(val: t.Union[bool, int, str]) -> bool:
    """Validate that input value is a valid bool str."""
    if str(val).lower() in {"true", "yes", "1"}:
        return True
    if str(val).lower() in {"false", "no", "0"}:
        return False
    raise ValueError(f"{val!r} is not a valid boolean")  # pragma: no cover


Bool = Annotated[
    bool,
    pydantic.BeforeValidator(validate_bool),
    pydantic.WithJsonSchema(
        {
            "pattern": r"^true|yes|1|false|no|0$",
            "examples": ["true", "yes", "1"],
        }
    ),
]
