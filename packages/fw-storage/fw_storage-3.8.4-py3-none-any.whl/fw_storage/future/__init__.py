"""Flywheel storage package with config and client factories."""

from importlib import import_module

from .base import Config, Storage
from .utils import URL

STORAGE_CONFIGS = {
    "fs": ".types.fs.FSConfig",
    "gs": ".types.gs.GSConfig",
    "s3": ".types.s3.S3Config",
    "az": ".types.az.AZConfig",
}


def create_storage_client(url: str) -> Storage:
    """Return storage client from a URL."""
    return create_storage_config(url).create_client()


def create_storage_config(url: str) -> Config:
    """Return storage config from a URL."""
    scheme = URL.from_string(url).scheme
    if scheme not in STORAGE_CONFIGS:
        raise ValueError(f"invalid storage url scheme in {url!r}")
    config_cls_qname = STORAGE_CONFIGS[scheme]
    module_name, cls_name = config_cls_qname.rsplit(".", maxsplit=1)
    config_cls = getattr(import_module(module_name, __name__), cls_name)
    return config_cls.from_url(url)
