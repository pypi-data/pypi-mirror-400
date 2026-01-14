import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from stscrapers.transformer import (
    BeamDataTransformer,
    BeamPipelineExecutor,
    FileSinkConfig,
    FileSourceConfig,
    TransformerConfig,
)
from stscrapers.transformer.beam_pipeline import (
    build_config_from_args,
    load_transform_callable,
    parse_param_overrides,
)


class DummyExecutor:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, config, transform_fn):
        self.calls += 1
        self.config = config
        self.transform_fn = transform_fn


class TransformerTests(unittest.TestCase):
    def _config(self) -> TransformerConfig:
        return TransformerConfig(
            source=FileSourceConfig(path="input.csv"),
            output_file=FileSinkConfig(path="output.csv"),
        )

    def test_transformer_delegates_to_executor(self) -> None:
        executor = DummyExecutor()
        config = self._config()

        transformer = BeamDataTransformer(
            config=config, transform_fn=lambda pcoll: pcoll, executor=executor
        )
        transformer.process()

        self.assertEqual(executor.calls, 1)
        self.assertIs(executor.config, config)

    def test_dataflow_runner_requires_project_and_locations(self) -> None:
        config = TransformerConfig(
            source=FileSourceConfig(path="input.csv"),
            output_file=FileSinkConfig(path="output.csv"),
            runner="DataflowRunner",
        )

        with self.assertRaises(ValueError):
            config.validate()

    def test_executor_raises_when_beam_missing(self) -> None:
        config = self._config()
        executor = BeamPipelineExecutor()

        with mock.patch(
            "stscrapers.transformer.beam_pipeline.import_module",
            side_effect=ModuleNotFoundError("apache_beam"),
        ):
            transformer = BeamDataTransformer(
                config=config,
                transform_fn=lambda pcoll: pcoll,
                executor=executor,
            )
            with self.assertRaises(ImportError):
                transformer.process()


def sample_transform(values, suffix=""):
    return f"{values}{suffix}"


class TransformerCliTests(unittest.TestCase):
    def _args(self, **overrides) -> SimpleNamespace:
        defaults = {
            "config": None,
            "source_path": "input.csv",
            "source_format": "csv",
            "source_skip_header_lines": None,
            "source_compression": None,
            "source_remote": None,
            "output_file_path": "output.csv",
            "output_file_format": "csv",
            "output_file_shard_template": "",
            "output_file_suffix": None,
            "output_file_compression": None,
            "output_file_remote": None,
            "output_bigquery_dataset": None,
            "output_bigquery_table": None,
            "output_bigquery_schema": None,
            "output_bigquery_project": None,
            "runner": None,
            "project": None,
            "region": None,
            "temp_location": None,
            "staging_location": None,
            "streaming": None,
            "transform": "tests.test_transformer:sample_transform",
            "param": [],
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_build_config_from_args_without_config(self) -> None:
        args = self._args()
        config, config_data = build_config_from_args(args)
        self.assertEqual(config.source.path, "input.csv")
        self.assertEqual(config.output_file.path, "output.csv")
        self.assertEqual(config.runner, "DirectRunner")
        self.assertIsNone(config_data)

    def test_build_config_from_file_with_override(self) -> None:
        config_payload = {
            "source": {"path": "cfg_input.csv"},
            "output_file": {"path": "cfg_output.csv"},
            "runner": "DataflowRunner",
            "project": "cfg-project",
            "region": "us-central1",
            "temp_location": "gs://cfg-temp",
        }
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            json.dump(config_payload, handle)
            config_path = handle.name
        self.addCleanup(lambda: os.unlink(config_path))
        args = self._args(
            config=config_path,
            source_path=None,
            output_file_path=None,
            project="override-project",
        )
        config, config_data = build_config_from_args(args)
        self.assertEqual(config.source.path, "cfg_input.csv")
        self.assertEqual(config.output_file.path, "cfg_output.csv")
        self.assertEqual(config.runner, "DataflowRunner")
        self.assertEqual(config.project, "override-project")
        self.assertEqual(config_data["source"]["path"], "cfg_input.csv")

    def test_parse_param_overrides_casts_values(self) -> None:
        params = parse_param_overrides(["threshold=0.5", "enabled=true", "label=beta"])
        self.assertEqual(params["threshold"], 0.5)
        self.assertTrue(params["enabled"])
        self.assertEqual(params["label"], "beta")

    def test_load_transform_callable_with_params(self) -> None:
        fn = load_transform_callable(
            "tests.test_transformer:sample_transform", {"suffix": "-ok"}
        )
        self.assertEqual(fn("data"), "data-ok")


if __name__ == "__main__":
    unittest.main()
