from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Sequence, Type

from stscrapers.scrapers.logs.metadata import (
    DatasetStatusLogger,
    LocalCsvMetadataLogger,
    LocalDatasetStatusLogger,
    MetadataLogger,
)
from stscrapers.scrapers.base import DatasetScraper
from stscrapers.scrapers.models import (
    DatasetCheckResult,
    DatasetConfig,
    DatasetFetchResult,
    DatasetUpdateResult,
)
from stscrapers.scrapers.socrata import SocrataDatasetScraper
from stscrapers.storage.backends import LocalFileStorageBackend, StorageBackend


SCRAPER_REGISTRY: Dict[str, Type[DatasetScraper]] = {
    "socrata": SocrataDatasetScraper,
}


class ScraperManager:
    def __init__(
        self,
        storage_backend: Optional[StorageBackend] = None,
        metadata_logger: Optional[MetadataLogger] = None,
        status_logger: Optional[DatasetStatusLogger] = None,
    ) -> None:
        self.storage = storage_backend or LocalFileStorageBackend()
        self.metadata_logger = metadata_logger or LocalCsvMetadataLogger()
        self.status_logger = status_logger or LocalDatasetStatusLogger()

    def check_dataset(
        self, scraper: DatasetScraper, dataset: DatasetConfig
    ) -> DatasetCheckResult:
        result = scraper.check_updates(dataset)
        self.metadata_logger.record_check(dataset, result)
        self.status_logger.record_check(dataset, result)
        return result

    def update_dataset(
        self, scraper: DatasetScraper, dataset: DatasetConfig
    ) -> DatasetUpdateResult:
        fetch_result = scraper.fetch_dataset(dataset)
        stored_files = self._persist_files(dataset, fetch_result)
        metadata_payload = {
            "dataset_id": dataset.identifier,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "files": stored_files,
            "domain": dataset.domain,
            "extra": dataset.extra,
            "scraper_metadata": fetch_result.metadata,
        }
        metadata_path = self.storage.write_metadata(dataset, metadata_payload)
        update_result = DatasetUpdateResult(
            dataset_id=dataset.identifier,
            files=stored_files,
            metadata_path=metadata_path,
        )
        self.metadata_logger.record_update(dataset, update_result)
        self.status_logger.record_update(dataset, update_result)
        return update_result

    def _persist_files(
        self, dataset: DatasetConfig, fetch_result: DatasetFetchResult
    ) -> Sequence[Dict[str, object]]:
        stored = []
        for resource in fetch_result.files:
            file_path = self.storage.write_dataset_file(
                dataset, resource.format, resource.content
            )
            stored.append(
                {
                    "format": resource.format,
                    "path": str(file_path),
                    "bytes": len(resource.content),
                    "source_url": resource.source_url,
                }
            )
        return stored


def build_arg_parser(require_subcommand: bool = True) -> argparse.ArgumentParser:
    def __add_common_dataset_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--identifier", required=True, help="Dataset identifier (4x4)")
        subparser.add_argument("--domain", required=True, help="Dataset domain/host")
        subparser.add_argument(
            "--local-path",
            required=True,
            help="Local directory for storing downloaded assets",
        )

    parser = argparse.ArgumentParser(description="Scraper manager CLI")
    parser.add_argument(
        "--scraper",
        required=True,
        choices=SCRAPER_REGISTRY.keys(),
        help="Which scraper to run (e.g. socrata)",
    )
    parser.add_argument("--app-token", help="Optional scraper-specific token")
    subparsers = parser.add_subparsers(dest="command", required=require_subcommand)

    check_parser = subparsers.add_parser("check", help="Check dataset for updates")
    __add_common_dataset_args(check_parser)
    check_parser.add_argument(
        "--last-update",
        help="ISO timestamp for last successful update (e.g. 2024-01-01T00:00:00Z)",
    )

    update_parser = subparsers.add_parser("update", help="Download/export dataset files")
    __add_common_dataset_args(update_parser)
    update_parser.add_argument(
        "--download-formats",
        help="Comma separated list of download formats (default depends on scraper)",
    )

    return parser





def _build_dataset_from_args(args: argparse.Namespace) -> DatasetConfig:
    last_update_value = getattr(args, "last_update", None)
    last_update = (
        datetime.fromisoformat(last_update_value.replace("Z", "+00:00"))
        if last_update_value
        else None
    )
    download_formats_value = getattr(args, "download_formats", None)
    download_formats = (
        tuple(fmt.strip() for fmt in download_formats_value.split(","))
        if download_formats_value
        else None
    )
    return DatasetConfig(
        identifier=args.identifier,
        domain=args.domain,
        local_path=Path(args.local_path),
        last_local_update=last_update,
        download_formats=download_formats,
    )


def _create_scraper(args: argparse.Namespace) -> DatasetScraper:
    scraper_cls = SCRAPER_REGISTRY[args.scraper]
    if scraper_cls is SocrataDatasetScraper:
        return scraper_cls(app_token=args.app_token)
    return scraper_cls()  # type: ignore[return-value]


def main(argv: Optional[Sequence[str]] = None) -> int:

    def __serialize_check_result(result: DatasetCheckResult) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "dataset_id": result.dataset_id,
            "has_updates": result.has_updates,
            "metadata": result.metadata,
        }
        payload["remote_updated_at"] = (
            result.remote_updated_at.isoformat() if result.remote_updated_at else None
        )
        return payload


    def __serialize_update_result(result: DatasetUpdateResult) -> Dict[str, object]:
        return {
            "dataset_id": result.dataset_id,
            "files": list(result.files),
            "metadata_path": str(result.metadata_path),
        }

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    dataset = _build_dataset_from_args(args)
    scraper = _create_scraper(args)
    manager = ScraperManager()

    if args.command == "check":
        result = manager.check_dataset(scraper, dataset)
        print(json.dumps(__serialize_check_result(result), indent=2))
        return 0
    if args.command == "update":
        result = manager.update_dataset(scraper, dataset)
        print(json.dumps(__serialize_update_result(result), indent=2))
        return 0
    parser.error("Unknown command")
    return 1





if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
