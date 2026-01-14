from __future__ import annotations

from typing import Protocol

from stscrapers.scrapers.models import (
    DatasetCheckResult,
    DatasetConfig,
    DatasetFetchResult,
)


class DatasetScraper(Protocol):
    """Base interface every scraper must implement."""

    name: str

    def check_updates(self, dataset: DatasetConfig) -> DatasetCheckResult:
        """Return metadata describing whether the dataset has changed."""

    def fetch_dataset(self, dataset: DatasetConfig) -> DatasetFetchResult:
        """Download dataset payloads but do not persist them."""
