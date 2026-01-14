"""Common scraper interfaces and implementations."""

from .base import DatasetScraper
from .models import (
    DatasetCheckResult,
    DatasetConfig,
    DatasetFetchResult,
    DatasetUpdateResult,
    DownloadedResource,
)
from .socrata import SocrataDatasetScraper

__all__ = [
    "DatasetScraper",
    "DatasetCheckResult",
    "DatasetConfig",
    "DatasetFetchResult",
    "DatasetUpdateResult",
    "DownloadedResource",
    "SocrataDatasetScraper",
]
