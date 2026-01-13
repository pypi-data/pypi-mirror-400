from __future__ import annotations

import base64
import dataclasses
import datetime as dt
import gzip
import importlib
import io
import json
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any

from ..exceptions import TanukiParcelError
from ..parcel import Parcel, get_default_s3_store

_TYPE_KEY = "__tanu_type__"

_AUTO_PARCEL_THRESHOLD = int(os.getenv("TANU_AUTO_PARCEL_THRESHOLD", "10000"))
_NUMPY: Any | None = None
_PANDAS: Any | None = None


def _maybe_numpy() -> Any | None:
    global _NUMPY
    if _NUMPY is False:  # type: ignore[comparison-overlap]
        return None
    if _NUMPY is None:
        try:
            _NUMPY = importlib.import_module("numpy")
        except Exception:
            _NUMPY = False  # type: ignore[assignment]
            return None
    return _NUMPY


def _maybe_pandas() -> Any | None:
    global _PANDAS
    if _PANDAS is False:  # type: ignore[comparison-overlap]
        return None
    if _PANDAS is None:
        try:
            _PANDAS = importlib.import_module("pandas")
        except Exception:
            _PANDAS = False  # type: ignore[assignment]
            return None
    return _PANDAS


def _default(obj: Any) -> Any:
    if isinstance(obj, Parcel):
        meta = obj._ensure_remote()
        return {_TYPE_KEY: "parcel", "kind": "file", **meta}

    np = _maybe_numpy()
    if np is not None:
        if isinstance(obj, np.ndarray):
            if int(obj.size) > _AUTO_PARCEL_THRESHOLD:
                tmp_path: Path | None = None
                try:
                    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
                        tmp_path = Path(f.name)
                    np.save(tmp_path, obj, allow_pickle=False)
                    meta = get_default_s3_store().put_file(
                        tmp_path,
                        filename="ndarray.npy",
                        content_type="application/x-npy",
                    )
                finally:
                    if tmp_path is not None:
                        try:
                            tmp_path.unlink()
                        except Exception:
                            pass
                return {_TYPE_KEY: "parcel", "kind": "numpy.ndarray", "format": "npy", **meta}

            buf = io.BytesIO()
            np.save(buf, obj, allow_pickle=False)
            return {_TYPE_KEY: "ndarray", "format": "npy", "npy": buf.getvalue()}

        if isinstance(obj, np.generic):
            return obj.item()

    pd = _maybe_pandas()
    if pd is not None:
        if isinstance(obj, pd.DataFrame):
            if int(obj.size) > _AUTO_PARCEL_THRESHOLD:
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(suffix=".pkl.gz", delete=False) as f:
                        tmp_path = Path(f.name)
                    obj.to_pickle(tmp_path, compression="gzip")  # type: ignore[call-arg]
                    meta = get_default_s3_store().put_file(
                        tmp_path,
                        filename="dataframe.pkl.gz",
                        content_type="application/x-python-serialize",
                    )
                finally:
                    if tmp_path is not None:
                        try:
                            tmp_path.unlink()
                        except Exception:
                            pass
                return {_TYPE_KEY: "parcel", "kind": "pandas.DataFrame", "format": "pickle+gzip", **meta}

            raw = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
            return {_TYPE_KEY: "dataframe", "format": "pickle+gzip", "pickle_gzip": gzip.compress(raw)}

    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if isinstance(obj, dt.datetime):
        return {_TYPE_KEY: "datetime", "value": obj.isoformat()}
    if isinstance(obj, dt.date):
        return {_TYPE_KEY: "date", "value": obj.isoformat()}
    if isinstance(obj, Path):
        return {_TYPE_KEY: "path", "value": str(obj)}
    if isinstance(obj, bytes):
        return {_TYPE_KEY: "bytes", "base64": base64.b64encode(obj).decode("ascii")}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _object_hook(obj: dict[str, Any]) -> Any:
    t = obj.get(_TYPE_KEY)
    if not t:
        return obj
    if t == "datetime":
        return dt.datetime.fromisoformat(str(obj["value"]))
    if t == "date":
        return dt.date.fromisoformat(str(obj["value"]))
    if t == "path":
        return Path(str(obj["value"]))
    if t == "bytes":
        return base64.b64decode(str(obj["base64"]))
    if t == "parcel":
        kind = str(obj.get("kind") or "file")
        bucket = str(obj.get("bucket") or "")
        key = str(obj.get("key") or "")
        uri = obj.get("uri")
        filename = obj.get("filename")
        content_type = obj.get("content_type")
        size = obj.get("size")
        sha256 = obj.get("sha256")
        fmt = str(obj.get("format") or "")

        if not bucket or not key:
            raise TanukiParcelError("invalid parcel reference (missing bucket/key)")

        if kind == "file":
            return Parcel(
                None,
                uri=str(uri) if uri is not None else None,
                bucket=bucket,
                key=key,
                filename=str(filename) if filename is not None else None,
                content_type=str(content_type) if content_type is not None else None,
                size=int(size) if size is not None else None,
                sha256=str(sha256) if sha256 is not None else None,
            )

        np = _maybe_numpy()
        pd = _maybe_pandas()
        store = get_default_s3_store()

        if kind == "numpy.ndarray":
            if np is None:
                raise TanukiParcelError("numpy is required to decode numpy.ndarray Parcel")
            suffix = ".npy" if not fmt or fmt == "npy" else ""
            tmp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                    tmp_path = Path(f.name)
                store.download_file(bucket=bucket, key=key, dst=tmp_path)
                return np.load(tmp_path, allow_pickle=False)
            finally:
                if tmp_path is not None:
                    try:
                        tmp_path.unlink()
                    except Exception:
                        pass

        if kind == "pandas.DataFrame":
            if pd is None:
                raise TanukiParcelError("pandas is required to decode pandas.DataFrame Parcel")
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".pkl.gz", delete=False) as f:
                    tmp_path = Path(f.name)
                store.download_file(bucket=bucket, key=key, dst=tmp_path)
                return pd.read_pickle(tmp_path, compression="gzip")  # type: ignore[call-arg]
            finally:
                if tmp_path is not None:
                    try:
                        tmp_path.unlink()
                    except Exception:
                        pass

        raise TanukiParcelError(f"unknown parcel kind: {kind}")

    if t == "ndarray":
        np = _maybe_numpy()
        if np is None:
            raise TanukiParcelError("numpy is required to decode numpy.ndarray")
        data = obj.get("npy")
        if not isinstance(data, (bytes, bytearray)):
            raise TanukiParcelError("invalid ndarray payload")
        return np.load(io.BytesIO(bytes(data)), allow_pickle=False)

    if t == "dataframe":
        pd = _maybe_pandas()
        if pd is None:
            raise TanukiParcelError("pandas is required to decode pandas.DataFrame")
        data = obj.get("pickle_gzip")
        if not isinstance(data, (bytes, bytearray)):
            raise TanukiParcelError("invalid dataframe payload")
        return pickle.loads(gzip.decompress(bytes(data)))
    return obj


def encode_json(payload: Any) -> bytes:
    return json.dumps(payload, default=_default, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def decode_json(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"), object_hook=_object_hook)
