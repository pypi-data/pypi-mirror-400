"""Model discovery and parsing utilities."""

from pathlib import Path

from data_validation_tool.core.logger import get_logger

logger = get_logger()


class ModelInfo:
    """Information about a dbt model."""

    def __init__(self, name: str, directory: str, path: Path) -> None:
        """Initialize model info.

        Args:
            name: Model name (without .sql extension).
            directory: Parent directory name.
            path: Full path to the model file.
        """
        self.name = name
        self.directory = directory
        self.path = path

    def __repr__(self) -> str:
        return f"ModelInfo(name={self.name!r}, directory={self.directory!r})"


def discover_models(
    directory: Path,
    model_name: str | None = None,
) -> list[ModelInfo]:
    """Discover dbt models in a directory.

    Args:
        directory: Directory to scan for SQL model files.
        model_name: Optional specific model name to filter by.

    Returns:
        Sorted list of ModelInfo objects.
    """
    models: list[ModelInfo] = []

    if not directory.exists():
        logger.warning("Directory does not exist: %s", directory)
        return models

    for sql_file in directory.rglob("*.sql"):
        name = sql_file.stem
        if model_name and name != model_name:
            continue
        parent_dir = sql_file.parent.name
        models.append(ModelInfo(name=name, directory=parent_dir, path=sql_file))

    return sorted(models, key=lambda m: m.name)
