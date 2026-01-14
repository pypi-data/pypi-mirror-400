"""Toy Beam transforms for demonstration and testing."""

from __future__ import annotations

try:  # pragma: no cover - optional dependency import
    import apache_beam as beam
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "apache_beam is required to use the sample transforms. "
        "Install it with `pip install apache-beam`."
    ) from exc


def clean_csv(pcoll, suffix: str = ""):
    """Normalize string rows and emit dictionaries with the text/length metadata."""

    return (
        pcoll
        | "StripWhitespace" >> beam.Map(lambda line: line.strip())
        | "FilterEmpty" >> beam.Filter(bool)
        | "Uppercase" >> beam.Map(str.upper)
        | "AppendSuffix" >> beam.Map(lambda line, suf: f"{line}{suf}", suffix)
        | "ToDict" >> beam.Map(lambda line: {"text": line, "length": len(line)})
    )


__all__ = ["clean_csv"]
