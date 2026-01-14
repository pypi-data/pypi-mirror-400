from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Sequence
from urllib import error as urllib_error, parse as urllib_parse, request as urllib_request

from stscrapers.scrapers.base import DatasetScraper
from stscrapers.scrapers.models import (
    DatasetCheckResult,
    DatasetConfig,
    DatasetFetchResult,
    DownloadedResource,
)


logger = logging.getLogger(__name__)


class HttpClient:
    """Minimal HTTP helper to allow dependency injection in tests."""

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        payload = self._execute(url, headers)
        return json.loads(payload.decode("utf-8"))

    def get_bytes(self, url: str, headers: Optional[Dict[str, str]] = None) -> bytes:
        return self._execute(url, headers)

    def _execute(self, url: str, headers: Optional[Dict[str, str]]) -> bytes:
        req = urllib_request.Request(url, headers=headers or {})
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read()
        except urllib_error.HTTPError as exc:  # pragma: no cover - network dependent
            raise RuntimeError(f"HTTP error {exc.code} for {url}") from exc
        except urllib_error.URLError as exc:  # pragma: no cover - network dependent
            raise RuntimeError(f"Failed to reach {url}: {exc.reason}") from exc


class SocrataDatasetScraper(DatasetScraper):
    """
    Socrata implementation of the DatasetScraper base interface.
    Documentation for Socrata API: 
    - https://dev.socrata.com/docs/other/discovery#?route=get-/catalog/v1-ids-4x4-
    - https://dev.socrata.com/docs/endpoints.html
    """

    name = "socrata"
    SUPPORTED_FORMATS = {"csv", "json", "tsv", "geojson"}

    def __init__(
        self,
        discovery_base_url: str = "https://api.us.socrata.com/api/catalog/v1",
        http_client: Optional[HttpClient] = None,
        app_token: Optional[str] = None,
    ) -> None:
        self.discovery_base_url = discovery_base_url.rstrip("/")
        self.http_client = http_client or HttpClient()
        self.app_token = app_token

    def check_updates(self, dataset: DatasetConfig) -> DatasetCheckResult:
        dataset_domain = _normalize_domain(dataset.domain)
        params = urllib_parse.urlencode(
            {"ids": f"{dataset_domain}/{dataset.identifier}", "only": "datasets"}
        )
        url = f"{self.discovery_base_url}?{params}"
        payload = self.http_client.get_json(url, headers=self._build_headers())
        results = payload.get("results") or []
        if not results:
            raise ValueError(f"Dataset {dataset.identifier} not found via discovery API")

        resource = results[0].get("resource", {})
        remote_ts = (
            resource.get("dataUpdatedAt")
            or resource.get("updatedAt")
            or resource.get("metadataUpdatedAt")
        )
        remote_dt = _parse_datetime(remote_ts)
        has_updates = False
        if remote_dt and dataset.last_local_update:
            has_updates = remote_dt > dataset.last_local_update
        elif remote_dt and not dataset.last_local_update:
            has_updates = True

        metadata = {
            "name": resource.get("name"),
            "permalink": results[0].get("permalink"),
            "link": results[0].get("link"),
            "classification": results[0].get("classification"),
            "resource": resource,
        }
        return DatasetCheckResult(
            dataset_id=dataset.identifier,
            has_updates=has_updates,
            remote_updated_at=remote_dt,
            metadata=metadata,
        )

    def fetch_dataset(self, dataset: DatasetConfig) -> DatasetFetchResult:
        formats = list(dataset.download_formats or ["csv"])
        files = []
        for fmt in formats:
            normalized = fmt.lower()
            if normalized not in self.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Format '{fmt}' is not supported. "
                    f"Supported: {sorted(self.SUPPORTED_FORMATS)}"
                )
            url = self._build_export_url(dataset.domain, dataset.identifier, normalized)
            content = self.http_client.get_bytes(url, headers=self._build_headers())
            files.append(
                DownloadedResource(
                    format=normalized,
                    content=content,
                    source_url=url,
                )
            )

        metadata = {
            "dataset_id": dataset.identifier,
            "domain": dataset.domain,
            "download_formats": formats,
        }
        return DatasetFetchResult(
            dataset_id=dataset.identifier,
            files=files,
            metadata=metadata,
        )

    def _build_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.app_token:
            headers["X-App-Token"] = self.app_token
        return headers

    @staticmethod
    def _build_export_url(domain: str, dataset_id: str, fmt: str) -> str:
        normalized_domain = _normalize_domain(domain)
        return (
            f"https://{normalized_domain}/api/views/{dataset_id}/rows."
            f"{fmt}?accessType=DOWNLOAD"
        )


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        sanitized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(sanitized)
    except ValueError:
        logger.debug("Unable to parse datetime value from %s", value)
        return None


def _normalize_domain(domain: str) -> str:
    stripped = domain.strip()
    if not stripped:
        raise ValueError("Domain cannot be empty")
    parsed = urllib_parse.urlparse(stripped if "://" in stripped else f"//{stripped}")
    host = parsed.netloc or parsed.path
    return host.rstrip("/")
