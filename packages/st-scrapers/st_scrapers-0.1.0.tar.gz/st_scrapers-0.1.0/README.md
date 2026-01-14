# st-scrapers

Collection of scrapers that power automated data collection for Subsidy Tracker.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The editable install exposes the CLI entry points (`scraper-manager`, `st-transformer`) and installs all required dependencies (Socrata scraper, storage backends, Beam transformer tooling).

## Running the Socrata scraper locally

```bash
scraper-manager \
  --scraper socrata \
  update \
  --identifier <4x4-id> \
  --domain <data.ny.gov> \
  --local-path data/cache/<dataset-folder> \
  --download-formats csv
```

Optional flags:

- `--last-update <ISO timestamp>` (for `check` command) tells the manager when you last synced locally.
- `--download-formats csv,json` lets you pull multiple formats at once.
- `--app-token` can be set via environment variable `SOCRATA_APP_TOKEN` if needed.

Outputs:

- Scraped files under `--local-path`.
- Metadata logs (`*.metadata.json`, `metadata_log.csv`, `dataset_status.csv`).

To write directly into GCS, configure the DAG or manager to use `GcsStorageBackend` (see `storage/backends.py`) or set environment variables when running in Composer.

## Running the Beam transformer

You can run transformations via the CLI:

```bash
python -m transformer.beam_pipeline \
  --config tmp/toy_transform.yaml \
  --transform transformer.transforms.sample:clean_csv
```

Override config values with flags:

```
python -m transformer.beam_pipeline \
  --config configs/job.yaml \
  --runner DataflowRunner \
  --project my-project \
  --region us-central1 \
  --temp-location gs://my-bucket/temp
```

This launches on Dataflow if `runner=DataflowRunner` and GCP options are set; otherwise it runs locally using DirectRunner.

## Airflow / Composer DAGs

DAGs live under `dags/`:

- `sample_transform_dag.py` — monitors a local file and runs the Beam toy transform (via Beam/Dataflow operator).
- `socrata_scrape_dag.py` — runs the Socrata scraper via `ScraperManager`; configure dataset, bucket, and schedule via environment variables (e.g., `SOCRATA_DATASET_ID`, `SCRAPER_BUCKET`, `SOCRATA_SCHEDULE`).
- `hello_world_dag.py` — minimal DAG to validate Composer deployment.

To deploy to Composer:

1. Build/install this package in the Composer environment or include the source in the DAGs bucket so imports resolve.
2. Upload DAG files to the Composer DAG bucket: `gsutil cp dags/*.py gs://<composer-dag-bucket>/dags/`
3. Configure required environment variables (Airflow Variables or environment settings) for dataset IDs, bucket names, etc.
4. Enable the DAGs in the Composer Airflow UI.
