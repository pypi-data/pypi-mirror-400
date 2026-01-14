from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from functools import partial
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Protocol, Sequence

from stscrapers.transformer.config import (
    BigQuerySinkConfig,
    FileSinkConfig,
    FileSourceConfig,
    TransformerConfig,
)


TransformFn = Callable[[Any], Any]


class PipelineExecutor(Protocol):
    def run(self, config: TransformerConfig, transform_fn: TransformFn) -> None:
        ...


@dataclass
class BeamPipelineExecutor:
    """Default pipeline executor that uses apache_beam under the hood."""

    pipeline_module: str = "apache_beam"

    def run(self, config: TransformerConfig, transform_fn: TransformFn) -> None:
        config.validate()
        beam = self._import_beam()
        options = self._build_pipeline_options(beam, config)
        with beam.Pipeline(options=options) as pipeline:
            input_pcoll = self._apply_read(beam, pipeline, config.source)
            transformed = transform_fn(input_pcoll)
            self._apply_writes(beam, transformed, config)

    def _import_beam(self):
        try:
            return import_module(self.pipeline_module)
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on env
            raise ImportError(
                "apache_beam is not installed. Install it with "
                "`pip install apache-beam` to run transformations."
            ) from exc

    def _build_pipeline_options(self, beam, config: TransformerConfig):
        options = beam.options.pipeline_options.PipelineOptions()
        standard_options = options.view_as(
            beam.options.pipeline_options.StandardOptions
        )
        standard_options.runner = config.runner
        standard_options.streaming = config.streaming

        if config.runner == "DataflowRunner":
            gcloud_options = options.view_as(
                beam.options.pipeline_options.GoogleCloudOptions
            )
            gcloud_options.project = config.project
            gcloud_options.region = config.region
            gcloud_options.temp_location = config.temp_location
            if config.staging_location:
                gcloud_options.staging_location = config.staging_location

        setup_options = options.view_as(
            beam.options.pipeline_options.SetupOptions
        )
        setup_options.save_main_session = True
        return options

    def _apply_read(self, beam, pipeline, source: FileSourceConfig):
        #TODO: Add implementation for reading from Google Cloud Bucket
        compression = _resolve_compression_type(beam, source.compression)
        read_transform = beam.io.ReadFromText(
            source.resolved_path(),
            skip_header_lines=source.skip_header_lines,
            compression_type=compression,
        )
        return pipeline | "ReadInputFile" >> read_transform

    def _apply_writes(self, beam, pcoll, config: TransformerConfig) -> None:
        if config.output_file:
            self._write_file(beam, pcoll, config.output_file)
        if config.output_bigquery:
            self._write_bigquery(beam, pcoll, config)

    def _write_file(self, beam, pcoll, sink: FileSinkConfig) -> None:
        suffix = sink.file_name_suffix
        if suffix is None:
            suffix = f".{sink.file_format}"
        compression = _resolve_compression_type(beam, sink.compression)
        write_transform = beam.io.WriteToText(
            sink.resolved_path(),
            shard_name_template=sink.shard_name_template,
            file_name_suffix=suffix,
            compression_type=compression,
        )
        pcoll | "WriteOutputFile" >> write_transform

    def _write_bigquery(self, beam, pcoll, config: TransformerConfig) -> None:
        sink = config.output_bigquery
        assert sink is not None
        table_spec = sink.table_spec()
        write_transform = beam.io.WriteToBigQuery(
            table=table_spec,
            schema=sink.schema,
            create_disposition=sink.create_disposition,
            write_disposition=sink.write_disposition,
        )
        pcoll | "WriteBigQuery" >> write_transform


class BeamDataTransformer:
    """High-level façade that wires configs, transforms, and executors."""

    def __init__(
        self,
        config: TransformerConfig,
        transform_fn: TransformFn,
        executor: Optional[PipelineExecutor] = None,
    ) -> None:
        self.config = config
        self.transform_fn = transform_fn
        self.executor = executor or BeamPipelineExecutor()

    def process(self) -> None:
        """Execute the configured Beam pipeline."""
        self.executor.run(self.config, self.transform_fn)


def _resolve_compression_type(beam, value: Optional[str]):
    compression_types = beam.io.filesystem.CompressionTypes
    if not value:
        return compression_types.AUTO
    if isinstance(value, str):
        normalized = value.upper()
        if hasattr(compression_types, normalized):
            return getattr(compression_types, normalized)
        raise ValueError(f"Unsupported compression type: {value}")
    return value


def parse_param_overrides(entries: Sequence[str] | None) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if not entries:
        return params
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Invalid parameter '{entry}'. Use key=value format.")
        key, value = entry.split("=", 1)
        params[key] = _coerce_cli_value(value)
    return params


def load_transform_callable(path: str, params: Dict[str, Any]) -> TransformFn:
    if ":" not in path:
        raise ValueError(
            "Transform path must use module:function format "
            f"(got '{path}')"
        )
    module_name, func_name = path.split(":", 1)
    module = import_module(module_name)
    transform_fn = getattr(module, func_name)
    if params:
        transform_fn = partial(transform_fn, **params)
    return transform_fn


def build_config_from_dict(raw: Dict[str, Any]) -> TransformerConfig:
    source_dict = raw.get("source") or {}
    if "path" not in source_dict:
        raise ValueError("Configuration file must include source.path")
    source = FileSourceConfig(**_filter_kwargs(source_dict, FileSourceConfig))

    output_file_dict = raw.get("output_file")
    output_file = (
        FileSinkConfig(**_filter_kwargs(output_file_dict, FileSinkConfig))
        if output_file_dict
        else None
    )

    output_bq_dict = raw.get("output_bigquery")
    output_bigquery = (
        BigQuerySinkConfig(**_filter_kwargs(output_bq_dict, BigQuerySinkConfig))
        if output_bq_dict
        else None
    )

    return TransformerConfig(
        source=source,
        runner=raw.get("runner", "DirectRunner"),
        output_file=output_file,
        output_bigquery=output_bigquery,
        project=raw.get("project"),
        region=raw.get("region"),
        temp_location=raw.get("temp_location"),
        staging_location=raw.get("staging_location"),
        streaming=raw.get("streaming", False),
    )


def build_config_from_args(
    args: argparse.Namespace,
) -> tuple[TransformerConfig, Optional[Dict[str, Any]]]:
    config: Optional[TransformerConfig] = None
    config_data: Optional[Dict[str, Any]] = None
    if args.config:
        config_data = _load_config_file(args.config)
        config = build_config_from_dict(config_data)
    if config is None:
        config = _build_config_from_cli(args)
    _apply_cli_overrides(config, args)
    return config, config_data


def _build_config_from_cli(args: argparse.Namespace) -> TransformerConfig:
    if not args.source_path:
        raise ValueError(
            "A source path is required when no configuration file is provided."
        )
    source = FileSourceConfig(
        path=args.source_path,
        file_format=args.source_format or "csv",
        skip_header_lines=args.source_skip_header_lines or 0,
        compression=args.source_compression,
        is_remote=args.source_remote or False,
    )

    output_file = None
    if args.output_file_path:
        output_file = FileSinkConfig(
            path=args.output_file_path,
            file_format=args.output_file_format or "csv",
            shard_name_template=args.output_file_shard_template or "",
            file_name_suffix=args.output_file_suffix,
            compression=args.output_file_compression,
            is_remote=args.output_file_remote or False,
        )

    output_bigquery = None
    if args.output_bigquery_table:
        dataset = args.output_bigquery_dataset
        schema = args.output_bigquery_schema
        if not (dataset and schema):
            raise ValueError(
                "BigQuery output requires --output-bigquery-dataset and "
                "--output-bigquery-schema."
            )
        output_bigquery = BigQuerySinkConfig(
            dataset=dataset,
            table=args.output_bigquery_table,
            schema=schema,
            project=args.output_bigquery_project or args.project,
        )

    if not (output_file or output_bigquery):
        raise ValueError(
            "Specify at least one output via --output-file-path or "
            "--output-bigquery-table."
        )

    streaming = args.streaming if args.streaming is not None else False
    return TransformerConfig(
        source=source,
        runner=args.runner or "DirectRunner",
        output_file=output_file,
        output_bigquery=output_bigquery,
        project=args.project,
        region=args.region,
        temp_location=args.temp_location,
        staging_location=args.staging_location,
        streaming=streaming,
    )


def _apply_cli_overrides(config: TransformerConfig, args: argparse.Namespace) -> None:
    if args.source_path:
        config.source.path = args.source_path
    if args.source_format:
        config.source.file_format = args.source_format
    if args.source_skip_header_lines is not None:
        config.source.skip_header_lines = args.source_skip_header_lines
    if args.source_compression:
        config.source.compression = args.source_compression
    if args.source_remote is not None:
        config.source.is_remote = args.source_remote

    if args.runner:
        config.runner = args.runner
    if args.project:
        config.project = args.project
    if args.region:
        config.region = args.region
    if args.temp_location:
        config.temp_location = args.temp_location
    if args.staging_location:
        config.staging_location = args.staging_location
    if args.streaming is not None:
        config.streaming = args.streaming

    _override_output_file(config, args)
    _override_bigquery(config, args)


def _override_output_file(config: TransformerConfig, args: argparse.Namespace) -> None:
    overrides_present = any(
        [
            args.output_file_path,
            args.output_file_format,
            args.output_file_shard_template,
            args.output_file_suffix,
            args.output_file_compression,
            args.output_file_remote is not None,
        ]
    )
    if not overrides_present:
        return

    if config.output_file is None:
        if not args.output_file_path:
            raise ValueError(
                "Creating a file output via CLI overrides requires "
                "--output-file-path."
            )
        config.output_file = FileSinkConfig(path=args.output_file_path)

    if args.output_file_path:
        config.output_file.path = args.output_file_path
    if args.output_file_format:
        config.output_file.file_format = args.output_file_format
    if args.output_file_shard_template is not None:
        config.output_file.shard_name_template = args.output_file_shard_template
    if args.output_file_suffix is not None:
        config.output_file.file_name_suffix = args.output_file_suffix
    if args.output_file_compression is not None:
        config.output_file.compression = args.output_file_compression
    if args.output_file_remote is not None:
        config.output_file.is_remote = args.output_file_remote


def _override_bigquery(config: TransformerConfig, args: argparse.Namespace) -> None:
    overrides_present = any(
        [
            args.output_bigquery_dataset,
            args.output_bigquery_table,
            args.output_bigquery_schema,
            args.output_bigquery_project,
        ]
    )
    if not overrides_present:
        return

    if config.output_bigquery is None:
        required = {
            "dataset": args.output_bigquery_dataset,
            "table": args.output_bigquery_table,
            "schema": args.output_bigquery_schema,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(
                "Creating a BigQuery sink via overrides requires: "
                + ", ".join(missing)
            )
        config.output_bigquery = BigQuerySinkConfig(
            dataset=required["dataset"],
            table=required["table"],
            schema=required["schema"],
            project=args.output_bigquery_project or args.project or config.project,
        )
    else:
        if args.output_bigquery_dataset:
            config.output_bigquery.dataset = args.output_bigquery_dataset
        if args.output_bigquery_table:
            config.output_bigquery.table = args.output_bigquery_table
        if args.output_bigquery_schema:
            config.output_bigquery.schema = args.output_bigquery_schema
        if args.output_bigquery_project:
            config.output_bigquery.project = args.output_bigquery_project


def _filter_kwargs(data: Dict[str, Any], cls: type) -> Dict[str, Any]:
    allowed = set(cls.__dataclass_fields__.keys())  # type: ignore[attr-defined]
    return {key: value for key, value in (data or {}).items() if key in allowed}


def _coerce_cli_value(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def _load_config_file(path: str) -> Dict[str, Any]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    suffix = file_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "PyYAML is required to load YAML configs. Install with `pip install pyyaml`."
            ) from exc
        data = yaml.safe_load(text)
        return data or {}
    return json.loads(text)


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an Apache Beam transformation using the configured transformer."
    )
    parser.add_argument(
        "--config",
        help="Path to a JSON or YAML config file describing the transformer.",
    )
    parser.add_argument(
        "--transform",
        help="Python path to the transform callable (e.g. module.sub:build_transform).",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Parameter passed to the transform callable (key=value; repeatable).",
    )
    parser.add_argument("--runner", help="Beam runner (DirectRunner, DataflowRunner, etc.)")
    parser.add_argument("--project", help="GCP project (required for Dataflow).")
    parser.add_argument("--region", help="GCP region (Dataflow).")
    parser.add_argument("--temp-location", help="Temp location for Dataflow staging.")
    parser.add_argument("--staging-location", help="Optional Dataflow staging location.")

    parser.add_argument("--source-path", help="Input file path or URI.")
    parser.add_argument("--source-format", help="Input file format (default csv).")
    parser.add_argument(
        "--source-skip-header-lines",
        type=int,
        help="Number of header lines to skip when reading text files.",
    )
    parser.add_argument("--source-compression", help="Compression codec for the input file.")
    parser.add_argument(
        "--source-remote",
        dest="source_remote",
        action="store_true",
        help="Treat the source path as remote (e.g., gs://).",
    )
    parser.add_argument(
        "--source-local",
        dest="source_remote",
        action="store_false",
        help="Treat the source path as local.",
    )

    parser.add_argument("--output-file-path", help="Destination file path or prefix.")
    parser.add_argument("--output-file-format", help="Output file format (default csv).")
    parser.add_argument(
        "--output-file-shard-template",
        help="Custom shard template for Beam WriteToText.",
    )
    parser.add_argument("--output-file-suffix", help="File suffix (default uses format).")
    parser.add_argument("--output-file-compression", help="Compression codec for output file.")
    parser.add_argument(
        "--output-file-remote",
        dest="output_file_remote",
        action="store_true",
        help="Treat the output file path as remote.",
    )
    parser.add_argument(
        "--output-file-local",
        dest="output_file_remote",
        action="store_false",
        help="Treat the output file path as local.",
    )

    parser.add_argument("--output-bigquery-dataset", help="BigQuery dataset name.")
    parser.add_argument("--output-bigquery-table", help="BigQuery table name.")
    parser.add_argument("--output-bigquery-schema", help="BigQuery schema definition.")
    parser.add_argument("--output-bigquery-project", help="Overrides the BigQuery project.")

    parser.add_argument(
        "--streaming",
        dest="streaming",
        action="store_true",
        help="Run the pipeline in streaming mode.",
    )
    parser.add_argument(
        "--batch",
        dest="streaming",
        action="store_false",
        help="Force batch mode when overriding a config file.",
    )

    parser.set_defaults(
        source_remote=None,
        output_file_remote=None,
        streaming=None,
    )

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_cli_parser()
    args = parser.parse_args(argv)
    config, config_data = build_config_from_args(args)
    params = parse_param_overrides(args.param)
    transform_path = args.transform or (config_data or {}).get("transform")
    if not transform_path:
        parser.error("A transform callable must be provided via --transform or config file.")
    transform_fn = load_transform_callable(transform_path, params)
    transformer = BeamDataTransformer(config=config, transform_fn=transform_fn)
    transformer.process()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
