"""Sample module for logic-based analysis."""

CONFIG = {"mode": "fast"}


def load_config() -> dict:
    """Load configuration for the application."""
    return CONFIG


def transform_values(values: list[int]) -> list[int]:
    """Normalize values and return a new list."""
    return [value * 2 for value in values]


def write_report(values: list[int]) -> None:
    """Emit a report to stdout."""
    print("Report:", values)


def run_pipeline(values: list[int]) -> None:
    """Run the full pipeline."""
    config = load_config()
    scaled = transform_values(values)
    if config.get("mode") == "fast":
        write_report(scaled)
