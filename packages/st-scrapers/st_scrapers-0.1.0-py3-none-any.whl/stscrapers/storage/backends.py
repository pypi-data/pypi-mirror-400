from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Protocol

from stscrapers.scrapers.models import DatasetConfig


class StorageBackend(Protocol):
    def write_dataset_file(
        self, dataset: DatasetConfig, file_format: str, payload: bytes
    ) -> Path:
        ...

    def write_metadata(self, dataset: DatasetConfig, metadata: Dict[str, object]) -> Path:
        ...


class LocalFileStorageBackend:
    """Local filesystem storage backend (default)."""

    def __init__(self, base_directory: Optional[Path] = None) -> None:
        self.base_directory = Path(base_directory) if base_directory else None

    def _resolve(self, target: Path) -> Path:
        return (self.base_directory / target) if self.base_directory else target

    def _ensure_dir(self, target: Path) -> None:
        target.mkdir(parents=True, exist_ok=True)

    def write_dataset_file(
        self, dataset: DatasetConfig, file_format: str, payload: bytes
    ) -> Path:
        directory = self._resolve(dataset.local_path)
        self._ensure_dir(directory)
        file_path = directory / f"{dataset.identifier}.{file_format}"
        file_path.write_bytes(payload)
        return file_path

    def write_metadata(self, dataset: DatasetConfig, metadata: Dict[str, object]) -> Path:
        directory = self._resolve(dataset.local_path)
        self._ensure_dir(directory)
        filename = dataset.metadata_filename or f"{dataset.identifier}.metadata.json"
        path = directory / filename
        path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return path


class GcsStorageBackend:
    """Google Cloud Storage backend for storing dataset files."""

    def __init__(
        self,
        bucket_name: str,
        client: Optional[object] = None,
        prefix: Optional[str] = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.prefix = (prefix or "").strip("/")
        if client is None:
            try:
                from google.cloud import storage
            except ImportError as exc:  # pragma: no cover - import guard
                raise ImportError(
                    "google-cloud-storage is required for GcsStorageBackend. "
                    "Install with `pip install google-cloud-storage`."
                ) from exc
            client = storage.Client()
        self._client = client
        self._bucket = self._client.bucket(bucket_name)

    def write_dataset_file(
        self, dataset: DatasetConfig, file_format: str, payload: bytes
    ) -> Path:
        filename = f"{dataset.identifier}.{file_format}"
        blob_path = self._blob_path(dataset, filename)
        self._upload(blob_path, payload, content_type=self._guess_content_type(file_format))
        return Path(f"gs://{self.bucket_name}/{blob_path}")

    def write_metadata(self, dataset: DatasetConfig, metadata: Dict[str, object]) -> Path:
        filename = dataset.metadata_filename or f"{dataset.identifier}.metadata.json"
        blob_path = self._blob_path(dataset, filename)
        payload = json.dumps(metadata, indent=2).encode("utf-8")
        self._upload(blob_path, payload, content_type="application/json")
        return Path(f"gs://{self.bucket_name}/{blob_path}")

    def _upload(self, blob_name: str, payload: bytes, content_type: Optional[str]) -> None:
        blob = self._bucket.blob(blob_name)
        blob.upload_from_string(payload, content_type=content_type)

    def _blob_path(self, dataset: DatasetConfig, filename: str) -> str:
        parts = [
            self.prefix,
            str(dataset.local_path).strip("/"),
            filename,
        ]
        return "/".join(part for part in parts if part)

    @staticmethod
    def _guess_content_type(file_format: str) -> Optional[str]:
        mapping = {
            "csv": "text/csv",
            "tsv": "text/tab-separated-values",
            "json": "application/json",
            "geojson": "application/geo+json",
        }
        return mapping.get(file_format.lower())
