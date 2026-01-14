from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Optional, Protocol

from stscrapers.scrapers.models import DatasetCheckResult, DatasetConfig, DatasetUpdateResult


class MetadataLogger(Protocol):
    def record_check(
        self, dataset: DatasetConfig, result: DatasetCheckResult
    ) -> None:
        ...

    def record_update(
        self, dataset: DatasetConfig, result: DatasetUpdateResult
    ) -> None:
        ...


class LocalCsvMetadataLogger:
    """CSV-backed metadata log with rows per check/update event."""

    HEADERS = [
        "timestamp",
        "dataset_id",
        "action",
        "has_updates",
        "remote_updated_at",
        "file_format",
        "file_path",
        "file_bytes",
        "source_url",
    ]

    def __init__(self, log_filename: str = "metadata_log.csv") -> None:
        self.log_filename = log_filename

    def record_check(
        self, dataset: DatasetConfig, result: DatasetCheckResult
    ) -> None:
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataset_id": dataset.identifier,
            "action": "check",
            "has_updates": str(result.has_updates),
            "remote_updated_at": (
                result.remote_updated_at.isoformat()
                if result.remote_updated_at
                else ""
            ),
            "file_format": "",
            "file_path": "",
            "file_bytes": "",
            "source_url": "",
        }
        self._write_rows(dataset, [row])

    def record_update(
        self, dataset: DatasetConfig, result: DatasetUpdateResult
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        rows = []
        for file_info in result.files:
            rows.append(
                {
                    "timestamp": timestamp,
                    "dataset_id": dataset.identifier,
                    "action": "update",
                    "has_updates": "",
                    "remote_updated_at": "",
                    "file_format": file_info.get("format", ""),
                    "file_path": file_info.get("path", ""),
                    "file_bytes": str(file_info.get("bytes", "")),
                    "source_url": file_info.get("source_url", ""),
                }
            )
        self._write_rows(dataset, rows)

    def _write_rows(
        self, dataset: DatasetConfig, rows: Iterable[Dict[str, str]]
    ) -> None:
        dataset.local_path.mkdir(parents=True, exist_ok=True)
        log_path = dataset.local_path / self.log_filename
        exists = log_path.exists()
        with log_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.HEADERS)
            if not exists:
                writer.writeheader()
            for row in rows:
                writer.writerow(row)


class CloudMetadataLogger(MetadataLogger):
    """Placeholder for future cloud metadata logging implementation."""

    def record_check(
        self, dataset: DatasetConfig, result: DatasetCheckResult
    ) -> None:  # pragma: no cover - placeholder
        raise NotImplementedError("Cloud metadata logging is not implemented yet.")

    def record_update(
        self, dataset: DatasetConfig, result: DatasetUpdateResult
    ) -> None:  # pragma: no cover - placeholder
        raise NotImplementedError("Cloud metadata logging is not implemented yet.")


class DatasetStatusLogger(Protocol):
    def record_check(
        self, dataset: DatasetConfig, result: DatasetCheckResult
    ) -> None:
        ...

    def record_update(
        self, dataset: DatasetConfig, result: DatasetUpdateResult
    ) -> None:
        ...


class LocalDatasetStatusLogger(DatasetStatusLogger):
    """Tracks per-dataset status in a CSV for quick sync monitoring."""

    HEADERS = [
        "dataset_id",
        "domain",
        "dataset_name",
        "dataset_link",
        "local_path",
        "last_checked_at",
        "last_updated_at",
        "remote_updated_at",
    ]

    def __init__(
        self,
        log_directory: Optional[Path] = None,
        log_filename: str = "dataset_status.csv",
    ) -> None:
        self.log_directory = Path(log_directory) if log_directory else None
        self.log_filename = log_filename

    def record_check(
        self, dataset: DatasetConfig, result: DatasetCheckResult
    ) -> None:
        log_path = self._resolve_path(dataset)
        rows = self._load_rows(log_path)
        row = self._get_or_create_row(rows, dataset)
        now = datetime.now(timezone.utc).isoformat()
        row["domain"] = _normalize_domain(dataset.domain)
        row["dataset_name"] = result.metadata.get("name") or result.metadata.get(
            "resource", {}
        ).get("name", "")
        row["dataset_link"] = (
            result.metadata.get("link")
            or row["dataset_link"]
            or self._default_link(dataset)
        )
        row["local_path"] = str(dataset.local_path)
        row["last_checked_at"] = now
        row["remote_updated_at"] = (
            result.remote_updated_at.isoformat()
            if result.remote_updated_at
            else row.get("remote_updated_at", "")
        )
        self._write_rows(log_path, rows)

    def record_update(
        self, dataset: DatasetConfig, result: DatasetUpdateResult
    ) -> None:
        log_path = self._resolve_path(dataset)
        rows = self._load_rows(log_path)
        row = self._get_or_create_row(rows, dataset)
        now = datetime.now(timezone.utc).isoformat()
        row["domain"] = _normalize_domain(dataset.domain)
        row["dataset_link"] = row.get("dataset_link") or self._default_link(dataset)
        row["local_path"] = str(dataset.local_path)
        row["last_updated_at"] = now
        self._write_rows(log_path, rows)

    def _resolve_path(self, dataset: DatasetConfig) -> Path:
        base_dir = self.log_directory or dataset.local_path
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / self.log_filename

    def _load_rows(self, path: Path) -> list[Dict[str, str]]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]

    def _write_rows(self, path: Path, rows: Iterable[Dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.HEADERS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def _get_or_create_row(
        self, rows: list[Dict[str, str]], dataset: DatasetConfig
    ) -> Dict[str, str]:
        for row in rows:
            if row.get("dataset_id") == dataset.identifier:
                return row
        row = {header: "" for header in self.HEADERS}
        row["dataset_id"] = dataset.identifier
        rows.append(row)
        return row

    @staticmethod
    def _default_link(dataset: DatasetConfig) -> str:
        domain = _normalize_domain(dataset.domain)
        return f"https://{domain}/d/{dataset.identifier}"


class CloudDatasetStatusLogger(DatasetStatusLogger):
    """Placeholder for a future cloud dataset status logger."""

    def record_check(
        self, dataset: DatasetConfig, result: DatasetCheckResult
    ) -> None:  # pragma: no cover - placeholder
        raise NotImplementedError(
            "Cloud dataset status logging is not implemented yet."
        )

    def record_update(
        self, dataset: DatasetConfig, result: DatasetUpdateResult
    ) -> None:  # pragma: no cover - placeholder
        raise NotImplementedError(
            "Cloud dataset status logging is not implemented yet."
        )


def _normalize_domain(domain: str) -> str:
    stripped = domain.strip()
    if not stripped:
        raise ValueError("Domain cannot be empty")
    if "://" not in stripped:
        stripped = f"//{stripped}"
    from urllib import parse

    parsed = parse.urlparse(stripped)
    host = parsed.netloc or parsed.path
    return host.rstrip("/")
