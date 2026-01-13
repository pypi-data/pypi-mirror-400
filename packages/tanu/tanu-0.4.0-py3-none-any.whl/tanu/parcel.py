from __future__ import annotations

import hashlib
import mimetypes
import os
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .exceptions import TanukiParcelError


@dataclass(frozen=True, slots=True)
class S3Config:
    bucket: str | None
    endpoint_url: str | None = None
    region_name: str | None = None
    prefix: str = "tanu"
    addressing_style: str | None = None  # "path" or "virtual"
    access_key_id: str | None = None
    secret_access_key: str | None = None
    session_token: str | None = None

    @classmethod
    def from_env(cls) -> "S3Config":
        region = os.getenv("TANU_S3_REGION") or os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
        prefix = os.getenv("TANU_S3_PREFIX", "tanu")
        addressing_style = os.getenv("TANU_S3_ADDRESSING_STYLE") or None
        return cls(
            bucket=os.getenv("TANU_S3_BUCKET") or None,
            endpoint_url=os.getenv("TANU_S3_ENDPOINT_URL") or None,
            region_name=region or None,
            prefix=prefix,
            addressing_style=addressing_style,
            access_key_id=os.getenv("TANU_S3_ACCESS_KEY_ID") or None,
            secret_access_key=os.getenv("TANU_S3_SECRET_ACCESS_KEY") or None,
            session_token=os.getenv("TANU_S3_SESSION_TOKEN") or None,
        )


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_guess_content_type(filename: str) -> str:
    guess, _ = mimetypes.guess_type(filename)
    return guess or "application/octet-stream"


def _normalize_prefix(prefix: str) -> str:
    return prefix.strip().strip("/")


def _gen_key(prefix: str, filename: str) -> str:
    ext = Path(filename).suffix
    uid = uuid.uuid4().hex
    p = _normalize_prefix(prefix)
    if p:
        return f"{p}/{uid}{ext}"
    return f"{uid}{ext}"


class S3ParcelStore:
    def __init__(self, *, config: S3Config) -> None:
        self._config = config
        self._client = None

    @property
    def config(self) -> S3Config:
        return self._config

    def _get_client(self):  # type: ignore[no-untyped-def]
        if self._client is not None:
            return self._client

        try:
            import boto3
            from botocore.config import Config as BotocoreConfig
        except ModuleNotFoundError as e:
            raise TanukiParcelError("boto3 is required for S3 Parcel support (install: pip install tanu[s3])") from e

        botocore_cfg: BotocoreConfig | None = None
        if self._config.addressing_style:
            botocore_cfg = BotocoreConfig(s3={"addressing_style": self._config.addressing_style})
        else:
            botocore_cfg = BotocoreConfig()

        kwargs: dict[str, Any] = {}
        if self._config.endpoint_url:
            kwargs["endpoint_url"] = self._config.endpoint_url
        if self._config.region_name:
            kwargs["region_name"] = self._config.region_name
        if self._config.access_key_id:
            kwargs["aws_access_key_id"] = self._config.access_key_id
        if self._config.secret_access_key:
            kwargs["aws_secret_access_key"] = self._config.secret_access_key
        if self._config.session_token:
            kwargs["aws_session_token"] = self._config.session_token
        kwargs["config"] = botocore_cfg

        self._client = boto3.client("s3", **kwargs)
        return self._client

    def put_file(
        self,
        path: Path,
        *,
        bucket: str | None = None,
        key: str | None = None,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        target_bucket = bucket or self._config.bucket
        if not target_bucket:
            raise TanukiParcelError("S3 bucket is not configured (set TANU_S3_BUCKET)")

        filename = filename or path.name
        content_type = content_type or _safe_guess_content_type(filename)
        target_key = key or _gen_key(self._config.prefix, filename)

        size = int(path.stat().st_size)
        sha256 = _sha256_file(path)

        extra_args: dict[str, Any] = {"ContentType": content_type}
        try:
            self._get_client().upload_file(str(path), target_bucket, target_key, ExtraArgs=extra_args)
        except Exception as e:
            raise TanukiParcelError(f"failed to upload to S3: {e}") from e

        uri = f"s3://{target_bucket}/{target_key}"
        return {
            "uri": uri,
            "bucket": target_bucket,
            "key": target_key,
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "sha256": sha256,
        }

    def download_file(self, *, bucket: str, key: str, dst: Path) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._get_client().download_file(bucket, key, str(dst))
        except Exception as e:
            raise TanukiParcelError(f"failed to download from S3: {e}") from e


_DEFAULT_S3_CONFIG: S3Config | None = None
_DEFAULT_S3_STORE: S3ParcelStore | None = None


def get_default_s3_store() -> S3ParcelStore:
    global _DEFAULT_S3_CONFIG, _DEFAULT_S3_STORE
    cfg = S3Config.from_env()
    if _DEFAULT_S3_STORE is not None and _DEFAULT_S3_CONFIG == cfg:
        return _DEFAULT_S3_STORE
    _DEFAULT_S3_CONFIG = cfg
    _DEFAULT_S3_STORE = S3ParcelStore(config=cfg)
    return _DEFAULT_S3_STORE


class Parcel:
    """
    File reference transferred via S3-compatible object storage.

    - Send: Parcel("/path/to/file")  # uploads during RPC serialization
    - Receive: Parcel(...)           # created from metadata in response/request
    - Download: parcel.save("path")  # downloads from object storage
    """

    def __init__(
        self,
        path: str | os.PathLike[str] | None = None,
        *,
        uri: str | None = None,
        bucket: str | None = None,
        key: str | None = None,
        filename: str | None = None,
        content_type: str | None = None,
        size: int | None = None,
        sha256: str | None = None,
    ) -> None:
        self._local_path: Path | None = Path(path) if path is not None else None
        self.uri = uri
        self.bucket = bucket
        self.key = key
        self.filename = filename or (self._local_path.name if self._local_path else None)
        self.content_type = content_type
        self.size = size
        self.sha256 = sha256

    def _ensure_remote(self) -> dict[str, Any]:
        if self.bucket and self.key:
            uri = self.uri or f"s3://{self.bucket}/{self.key}"
            return {
                "uri": uri,
                "bucket": self.bucket,
                "key": self.key,
                "filename": self.filename,
                "content_type": self.content_type,
                "size": self.size,
                "sha256": self.sha256,
            }

        if self._local_path is None:
            raise TanukiParcelError("Parcel has no local path and no remote reference")
        if not self._local_path.exists():
            raise TanukiParcelError(f"Parcel file not found: {self._local_path}")

        meta = get_default_s3_store().put_file(
            self._local_path,
            filename=self.filename or self._local_path.name,
            content_type=self.content_type or _safe_guess_content_type(self._local_path.name),
        )
        self.uri = str(meta.get("uri") or self.uri)
        self.bucket = str(meta.get("bucket") or "")
        self.key = str(meta.get("key") or "")
        self.filename = str(meta.get("filename") or self.filename or self._local_path.name)
        self.content_type = str(meta.get("content_type") or self.content_type or _safe_guess_content_type(self.filename))
        self.size = int(meta.get("size") or self.size or self._local_path.stat().st_size)
        self.sha256 = str(meta.get("sha256") or self.sha256 or "")
        return meta

    def save(self, filename: str | os.PathLike[str] | None = None) -> str:
        if not self.bucket or not self.key:
            if self._local_path is None:
                raise TanukiParcelError("Parcel has no remote reference (bucket/key) and no local file")
            dst = Path(filename) if filename is not None else Path(self.filename or self._local_path.name)
            if dst.is_dir():
                dst = dst / (self.filename or self._local_path.name)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.resolve() != self._local_path.resolve():
                shutil.copy2(self._local_path, dst)
            return str(dst)

        dst = Path(filename) if filename is not None else Path(self.filename or Path(self.key).name)
        if dst.is_dir():
            dst = dst / (self.filename or Path(self.key).name)
        get_default_s3_store().download_file(bucket=self.bucket, key=self.key, dst=dst)
        return str(dst)
