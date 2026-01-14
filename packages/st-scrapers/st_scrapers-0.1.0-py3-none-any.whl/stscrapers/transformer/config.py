from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FileSourceConfig:
    """Represents an input file stored either locally or in cloud storage."""

    path: str
    file_format: str = "csv"
    skip_header_lines: int = 0
    compression: Optional[str] = None
    is_remote: bool = False

    def resolved_path(self) -> str:
        if self.is_remote:
            return self.path
        return str(Path(self.path).expanduser().resolve())

#TODO: Create SourceConfig class for retrieving file from Google Cloud Bucket

@dataclass
class FileSinkConfig:
    """Writes the transformed output to a file (local or remote)."""

    path: str
    file_format: str = "csv"
    shard_name_template: str = ""
    file_name_suffix: Optional[str] = None
    compression: Optional[str] = None
    is_remote: bool = False

    def resolved_path(self) -> str:
        if self.is_remote:
            return self.path
        return str(Path(self.path).expanduser().resolve())


@dataclass
class BigQuerySinkConfig:
    """Writes the transformed output to BigQuery."""

    dataset: str
    table: str
    schema: str
    project: Optional[str] = None
    create_disposition: str = "CREATE_IF_NEEDED"
    write_disposition: str = "WRITE_TRUNCATE"

    def table_spec(self) -> str:
        if self.project:
            return f"{self.project}:{self.dataset}.{self.table}"
        return f"{self.dataset}.{self.table}"


@dataclass
class TransformerConfig:
    """Holds runner and IO settings for a Beam-based transformation."""

    source: FileSourceConfig
    runner: str = "DirectRunner"
    output_file: Optional[FileSinkConfig] = None
    output_bigquery: Optional[BigQuerySinkConfig] = None
    project: Optional[str] = None
    region: Optional[str] = None
    temp_location: Optional[str] = None
    staging_location: Optional[str] = None
    streaming: bool = False

    def validate(self) -> None:
        if not (self.output_file or self.output_bigquery):
            raise ValueError("At least one output (file or BigQuery) must be configured.")
        if self.runner == "DataflowRunner":
            missing = [
                field_name
                for field_name, value in {
                    "project": self.project,
                    "temp_location": self.temp_location,
                    "region": self.region,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(
                    "DataflowRunner requires the following config fields: "
                    + ", ".join(missing)
                )
