"""Storage configuration models."""

# TODO fw-storage
# - utilize configs for parsing/loading/validation in factory and storage classes
# - update readme with clarified, explicit creds handling
# TODO xfer
# - drop .env support and rename fs.uid->user / gs.sv_acct->app_creds
# - utilize configs for parsing/validation
import abc
import binascii
import json
import os
import re
import typing as t
import warnings
from base64 import urlsafe_b64decode
from pathlib import Path

from fw_utils import format_query_string as qs
from fw_utils import format_url, parse_url
from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator

from .future.types.fs import FSConfig, FSConfigOverride

LOAD_ENV = True  # load creds from envvars (and read file for gs)
REQUIRE_CREDS = True  # raise on missing creds (s3/gs/az)
SIGNED_URL_EXPIRY = 3600  # in seconds


class StorageConfig(BaseModel, abc.ABC):
    """Storage config model with URL <-> CFG conversion interface."""

    @classmethod
    @abc.abstractmethod
    def from_url(cls, url: str) -> "StorageConfig":
        """Return storage config parsed from a URL."""

    @property
    @abc.abstractmethod
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""

    @property
    @abc.abstractmethod
    def full_url(self) -> str:
        """Return full storage URL including credentials and options."""

    def model_dump(
        self, secret: t.Literal[None, "str", "val"] = None, **kwargs
    ) -> dict:
        """Return model as dictionary with optional secret serialization."""
        data = super().model_dump(**kwargs)
        for key, value in data.items():
            if isinstance(value, SecretStr):
                if secret == "str":  # noqa, serialize as **
                    data[key] = str(value)  # pragma: no cover
                if secret == "val":  # noqa, serialize as val, noqa
                    data[key] = value.get_secret_value()
        return data

    def dict(self, secret: t.Literal[None, "str", "val"] = None, **kwargs) -> dict:
        """Return model as dictionary with optional secret serialization."""
        warnings.warn(
            f'{self.__class__.__name__}.dict() is deprecated and replaced by "model_dump()"',
            DeprecationWarning,
        )
        return self.model_dump(secret=secret, **kwargs)  # pragma: no cover

    def apply_override(self, override: "StorageConfigOverride"):
        """Apply property overrides."""
        expected_class = f"{type(self).__name__}Override"
        actual_class = type(override).__name__
        assert expected_class == actual_class, (
            f"expected override of class {expected_class} but got {actual_class}"
        )

        for key in override.model_json_schema().get("properties", {}).keys():
            value = getattr(override, key)
            if value is not None:
                setattr(self, key, value)


class StorageConfigOverride(BaseModel):
    """Storage config override model."""


class S3Config(StorageConfig):
    """Amazon S3 storage config."""

    type: t.Literal["s3"] = Field("s3", title="S3 storage type")
    bucket: str = Field(
        title="AWS S3 bucket name",
        examples=["s3-bucket"],
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9-.]+$",
    )
    prefix: str = Field("", title="Common object key prefix", examples=["prefix"])
    connector_creds: bool = Field(
        default=False,
        title="Use connector's pre-configured credentials",
    )
    access_key_id: t.Optional[str] = Field(
        default=None,
        title="AWS Access Key ID",
        examples=["AKIAIOSFODNN7EXAMPLE"],  # gitleaks:allow
        # NTOE drop min length to support minio
        # min_length=16,
        max_length=128,
    )
    secret_access_key: t.Optional[SecretStr] = Field(
        default=None,
        title="AWS Secret Access Key",
        examples=["wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"],  # gitleaks:allow
        # NTOE drop min length to support minio
        # min_length=40,
    )

    @classmethod
    def from_url(cls, url: str) -> "S3Config":
        """Return Amazon S3 storage config parsed from a URL."""
        parsed = parse_url(url)
        params = {
            "type": parsed.pop("scheme"),
            "bucket": parsed.pop("host"),
            "prefix": parsed.pop("path", "").strip("/"),
            "access_key_id": parsed.pop("access_key_id", None),
            "secret_access_key": parsed.pop("secret_access_key", None),
            "connector_creds": parsed.pop("connector_creds", False),
        }
        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        return format_url(scheme=self.type, host=self.bucket, path=self.prefix)

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        data = self.model_dump(secret="val")  # noqa: S106
        qparams = {
            "access_key_id": data["access_key_id"],
            "secret_access_key": data["secret_access_key"],
        }
        if self.connector_creds:
            qparams["connector_creds"] = True
        return self.safe_url + qs(**qparams)

    @model_validator(mode="before")
    @classmethod
    def load_creds(cls, values: dict) -> dict:
        """Load creds from the env if enabled."""
        if values.get("connector_creds"):
            # drop creds if passed
            values.pop("access_key_id", None)
            values.pop("secret_access_key", None)
            return values
        if LOAD_ENV:
            if not values.get("access_key_id"):
                values["access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            if not values.get("secret_access_key"):
                values["secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        if REQUIRE_CREDS:
            assert values.get("access_key_id"), "access_key_id required"
            assert values.get("secret_access_key"), "secret_access_key required"
        return values

    strip_prefix = field_validator("prefix")(lambda cls, prefix: prefix.strip("/"))


class S3ConfigOverride(StorageConfigOverride):
    """Amazon S3 storage config override."""

    type: t.Literal["s3"] = Field("s3", title="S3 storage type")
    prefix: t.Optional[str] = Field(
        default=None,
        title="Common object key prefix",
        examples=["prefix"],
    )


KEY = "-----BEGIN PRIVATE KEY-----\\nK\\n-----END PRIVATE KEY-----\\n"  # gitleaks:allow
GOOGLE_SERVICE_ACCOUNT_EXAMPLE = {
    "type": "service_account",
    "project_id": "project-id",
    "private_key_id": "key-id",
    "private_key": KEY,
    "client_id": "client-id",
    "client_email": "service-account-email",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account-email",
}


class GSConfig(StorageConfig):
    """Google Cloud Storage config."""

    type: t.Literal["gs"] = Field("gs", title="Google Cloud Storage type")
    bucket: str = Field(
        title="Google Cloud Storage bucket name",
        examples=["gs-bucket"],
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9-_.]+$",
    )
    prefix: str = Field("", title="Common object key prefix", examples=["prefix"])

    application_credentials: t.Optional[SecretStr] = Field(
        default=None,
        title="Google Service Account Key path or contents",
        examples=[
            "~/google_service_account.json",
            json.dumps(GOOGLE_SERVICE_ACCOUNT_EXAMPLE),
        ],
        validate_default=True,
    )

    @classmethod
    def from_url(cls, url: str) -> "GSConfig":
        """Return Google Cloud Storage config parsed from a URL."""
        parsed = parse_url(url)
        creds = parsed.pop("application_credentials", None)
        service_account_key = parsed.pop("service_account_key", None)
        if not creds:
            creds = service_account_key
        # TODO consider not splitting qparams on commas when parsing
        # TODO consider urlsafe_b64en/decode
        creds = ",".join(creds) if isinstance(creds, list) else creds
        params = {
            "type": parsed.pop("scheme"),
            "bucket": parsed.pop("host"),
            "prefix": parsed.pop("path", "").strip("/"),
            "application_credentials": creds,
        }
        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        return format_url(scheme=self.type, host=self.bucket, path=self.prefix)

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        creds = self.model_dump(secret="val")["application_credentials"]  # noqa: S106
        return self.safe_url + qs(application_credentials=creds)

    @field_validator("application_credentials")
    @classmethod
    def load_creds(
        cls, application_credentials: t.Optional[SecretStr]
    ) -> t.Optional[SecretStr]:
        """Return creds read from disk if provided as a file path."""
        creds = ""
        if isinstance(application_credentials, SecretStr):
            creds = application_credentials.get_secret_value()
        if LOAD_ENV and not creds:
            creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or ""
        if REQUIRE_CREDS:
            assert creds, "application_credentials required"
        # try base64 decode in case of creds encoded
        if creds:
            try:
                creds = urlsafe_b64decode(f"{creds}==".encode()).decode()
            except (binascii.Error, UnicodeDecodeError):
                pass
        # TODO consider using a try/except flow instead
        if LOAD_ENV and creds and not creds.strip().startswith("{"):  # json test
            creds = Path(creds).expanduser().read_text(encoding="utf8")
        # creds are now the portable json contents - run some checks
        if creds:
            creds_obj = json.loads(creds)
            assert isinstance(creds_obj, dict), "invalid gs credentials (not a dict)"
            assert "type" in creds_obj, "invalid gs credentials (missing type)"
        return SecretStr(creds) if creds else None

    strip_prefix = field_validator("prefix")(lambda cls, prefix: prefix.strip("/"))


class GSConfigOverride(StorageConfigOverride):
    """Google Cloud Storage config override."""

    type: t.Literal["gs"] = Field("gs", title="Google Cloud Storage type")
    prefix: t.Optional[str] = Field(
        default=None,
        title="Common object key prefix",
        examples=["prefix"],
    )


AZ_BLOB_DOMAIN = "blob.core.windows.net"


class AZConfig(StorageConfig):
    """Azure Blob Storage config."""

    type: t.Literal["az"] = Field("az", title="Azure Blob Storage type")
    account: str = Field(
        title="Azure Storage Account name",
        examples=["azaccount"],
        min_length=3,
        max_length=24 + (1 + len(AZ_BLOB_DOMAIN)),
        pattern=r"^[a-z0-9]+" + re.escape(f".{AZ_BLOB_DOMAIN}") + r"$",
    )
    container: str = Field(
        title="Azure Blob Container name",
        examples=["container"],
        min_length=3,
        max_length=63,
        pattern=r"[a-z0-9-]+",
    )
    prefix: str = Field("", title="Common blob key prefix", examples=["prefix"])

    access_key: t.Optional[SecretStr] = Field(
        default=None,
        title="Azure Storage Account shared Access Key",
        examples=[
            "J94I0uS13Cc79AvAq33Hrkt3+C40yq16IF058yQUyiM7"
            "U2qBwGJXQ2VIrLhy0gwGRWMQ2OLTpJ6C9PsEXAMPLE=="
        ],
    )

    tenant_id: t.Optional[str] = Field(
        default=None,
        title="Azure tenant ID",
        examples=["c88032d3-19d1-4040-b9bf-b84c29a49480"],
    )
    client_id: t.Optional[str] = Field(
        default=None,
        title="Registered application Client ID",
        examples=["94ade9ae-5cd7-44ad-8e18-8331e5e3328e"],
    )
    client_secret: t.Optional[SecretStr] = Field(
        default=None,
        title="Registered application Client secret",
        examples=["o0O8Q~Rou2PCGn.NHGdLLneBQ4xG.fNEXAMPLE~9"],  # gitleaks:allow
    )
    connector_creds: bool = Field(
        default=False,
        title="Use connector's pre-configured credentials",
    )

    @classmethod
    def from_url(cls, url: str) -> "AZConfig":
        """Return Azure Blob Storage config parsed from a URL."""
        parsed = parse_url(url)
        path = parsed.pop("path", "").strip("/")
        if "/" in path:
            container, prefix = path.split("/", maxsplit=1)
        else:
            container, prefix = path, ""

        account = parsed.pop("host")
        params = {
            "type": parsed.pop("scheme"),
            "account": account,
            "container": container,
            "prefix": prefix,
            "access_key": parsed.pop("access_key", None),
            "tenant_id": parsed.pop("tenant_id", None),
            "client_id": parsed.pop("client_id", None),
            "client_secret": parsed.pop("client_secret", None),
            "connector_creds": parsed.pop("connector_creds", False),
        }
        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        path = f"{self.container}/{self.prefix}" if self.prefix else self.container
        return format_url(scheme=self.type, host=self.account, path=path)

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        data = self.model_dump(secret="val")  # noqa: S106
        qparams = {
            "access_key": data["access_key"],
            "tenant_id": data["tenant_id"],
            "client_id": data["client_id"],
            "client_secret": data["client_secret"],
        }
        if self.connector_creds:
            qparams["connector_creds"] = True
        return self.safe_url + qs(**qparams)

    @property
    def account_name(self) -> str:
        """Return pure account name without domain."""
        return self.account.split(".", maxsplit=1)[0]

    @field_validator("account", mode="before")
    @classmethod
    def account_url(cls, account: str) -> str:
        """Return account name with default blob domain unless given a URL."""
        return account if "." in account else f"{account}.{AZ_BLOB_DOMAIN}"

    @model_validator(mode="before")
    @classmethod
    def load_creds(cls, values: dict) -> dict:
        """Load creds from the env if enabled."""
        if values.get("connector_creds"):
            # drop creds if passed
            values.pop("access_key", None)
            return values
        if LOAD_ENV:
            if not values.get("access_key"):
                values["access_key"] = os.getenv("AZURE_ACCESS_KEY")
            if not values.get("tenant_id"):
                values["tenant_id"] = os.getenv("AZURE_TENANT_ID")
            if not values.get("client_id"):
                values["client_id"] = os.getenv("AZURE_CLIENT_ID")
            if not values.get("client_secret"):
                values["client_secret"] = os.getenv("AZURE_CLIENT_SECRET")
        if REQUIRE_CREDS:
            key_groups = [["access_key"], ["tenant_id", "client_id", "client_secret"]]
            msg = "access_key required"  # TODO mention the alternatives
            assert any(all(values.get(key) for key in keys) for keys in key_groups), msg
        return values

    strip_prefix = field_validator("prefix")(lambda cls, prefix: prefix.strip("/"))


class AZConfigOverride(StorageConfigOverride):
    """Azure Blob Storage config override."""

    type: t.Literal["az"] = Field("az", title="Azure Blob Storage type")
    prefix: t.Optional[str] = Field(
        default=None,
        title="Common object key prefix",
        examples=["prefix"],
    )


Config = t.Union[FSConfig, S3Config, GSConfig, AZConfig]
ConfigOverride = t.Union[
    FSConfigOverride, S3ConfigOverride, GSConfigOverride, AZConfigOverride
]
