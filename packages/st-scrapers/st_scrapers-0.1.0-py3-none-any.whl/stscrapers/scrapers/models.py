from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Sequence


@dataclass
class DatasetConfig:
    identifier: str
    domain: str
    local_path: Path
    last_local_update: Optional[datetime] = None
    download_formats: Optional[Sequence[str]] = None
    metadata_filename: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetCheckResult:
    dataset_id: str
    has_updates: bool
    remote_updated_at: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class DownloadedResource:
    format: str
    content: bytes
    source_url: str


@dataclass
class DatasetFetchResult:
    dataset_id: str
    files: Sequence[DownloadedResource]
    metadata: Dict[str, Any]


@dataclass
class DatasetUpdateResult:
    dataset_id: str
    files: Sequence[Dict[str, Any]]
    metadata_path: Path
