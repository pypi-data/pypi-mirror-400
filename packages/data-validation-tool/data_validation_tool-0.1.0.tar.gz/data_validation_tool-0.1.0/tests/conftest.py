"""Pytest configuration and fixtures."""

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def tmp_models_dir(tmp_path):
    """Create a temporary models directory with sample SQL files."""
    models_dir = tmp_path / "models" / "03_mart"
    models_dir.mkdir(parents=True)

    # Create sample model files
    (models_dir / "sample_model.sql").write_text(
        """
        {{
            config(
                materialized='table',
                audit_helper__source_database='SOURCE_DB',
                audit_helper__source_schema='SOURCE_SCHEMA',
                audit_helper__old_identifier='old_table',
                audit_helper__unique_key='id'
            )
        }}
        SELECT id, name FROM {{ ref('upstream') }}
        """
    )

    return models_dir
