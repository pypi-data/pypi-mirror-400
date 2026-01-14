import csv
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from stscrapers.scrapers.manager import ScraperManager
from stscrapers.scrapers.models import DatasetConfig
from stscrapers.scrapers.socrata import SocrataDatasetScraper


class FakeHttpClient:
    def __init__(self) -> None:
        self.json_payloads = {}
        self.byte_payloads = {}

    def add_json(self, url: str, payload) -> None:
        self.json_payloads[url] = payload

    def add_bytes(self, url: str, payload: bytes) -> None:
        self.byte_payloads[url] = payload

    def get_json(self, url, headers=None):
        return self.json_payloads[url]

    def get_bytes(self, url, headers=None):
        return self.byte_payloads[url]


class ScraperManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = ScraperManager()
        self.fake_client = FakeHttpClient()

    def test_check_dataset_records_logs(self) -> None:
        monitor_url = (
            "https://api.us.socrata.com/api/catalog/v1?"
            "ids=data.example.com%2Fabcd-1234&only=datasets"
        )
        self.fake_client.add_json(
            monitor_url,
            {
                "results": [
                    {
                        "permalink": "https://data.example.com/d/abcd-1234",
                        "link": "https://data.example.com/d/abcd-1234",
                        "classification": {"domain_category": "test"},
                        "resource": {
                            "id": "abcd-1234",
                            "name": "Example Dataset",
                            "dataUpdatedAt": "2022-01-01T00:00:00Z",
                        },
                    }
                ]
            },
        )
        scraper = SocrataDatasetScraper(http_client=self.fake_client)
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = DatasetConfig(
                identifier="abcd-1234",
                domain="data.example.com",
                local_path=Path(tmpdir),
                last_local_update=datetime(2020, 1, 1, tzinfo=timezone.utc),
            )
            result = self.manager.check_dataset(scraper, dataset)

            self.assertTrue(result.has_updates)
            metadata_log = dataset.local_path / "metadata_log.csv"
            self.assertTrue(metadata_log.exists())
            with metadata_log.open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[-1]["action"], "check")
            status_log = dataset.local_path / "dataset_status.csv"
            with status_log.open() as handle:
                status_rows = list(csv.DictReader(handle))
            self.assertEqual(status_rows[-1]["dataset_id"], "abcd-1234")
            self.assertTrue(status_rows[-1]["last_checked_at"])

    def test_update_dataset_persists_files_and_updates_logs(self) -> None:
        download_url = (
            "https://data.example.com/api/views/abcd-1234/rows.csv?accessType=DOWNLOAD"
        )
        payload = b"col1,col2\n1,2\n"
        self.fake_client.add_bytes(download_url, payload)
        scraper = SocrataDatasetScraper(http_client=self.fake_client)
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = DatasetConfig(
                identifier="abcd-1234",
                domain="data.example.com",
                local_path=Path(tmpdir),
                download_formats=["csv"],
            )
            result = self.manager.update_dataset(scraper, dataset)

            self.assertEqual(len(result.files), 1)
            stored_file = Path(result.files[0]["path"])
            self.assertTrue(stored_file.exists())
            self.assertEqual(stored_file.read_bytes(), payload)
            metadata_path = dataset.local_path / "abcd-1234.metadata.json"
            self.assertTrue(metadata_path.exists())
            metadata = json.loads(metadata_path.read_text())
            self.assertEqual(metadata["files"][0]["bytes"], len(payload))
            metadata_log = dataset.local_path / "metadata_log.csv"
            with metadata_log.open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(any(row["action"] == "update" for row in rows))
            status_log = dataset.local_path / "dataset_status.csv"
            with status_log.open() as handle:
                status_rows = list(csv.DictReader(handle))
            self.assertTrue(status_rows[-1]["last_updated_at"])


if __name__ == "__main__":
    unittest.main()
