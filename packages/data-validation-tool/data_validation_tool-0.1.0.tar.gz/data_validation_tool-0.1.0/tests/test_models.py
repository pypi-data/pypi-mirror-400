"""Tests for model discovery utilities."""

from pathlib import Path

from data_validation_tool.core.models import ModelInfo, discover_models


class TestModelInfo:
    """Tests for the ModelInfo class."""

    def test_model_info_creation(self) -> None:
        """Test ModelInfo can be created with expected attributes."""
        path = Path("/test/models/sample.sql")
        model = ModelInfo(name="sample", directory="models", path=path)

        assert model.name == "sample"
        assert model.directory == "models"
        assert model.path == path

    def test_model_info_repr(self) -> None:
        """Test ModelInfo has readable string representation."""
        model = ModelInfo(name="test", directory="mart", path=Path("/x/y.sql"))
        repr_str = repr(model)

        assert "test" in repr_str
        assert "mart" in repr_str


class TestDiscoverModels:
    """Tests for the discover_models function."""

    def test_discover_models_empty_dir(self, tmp_path: Path) -> None:
        """Test discover_models returns empty list for empty directory."""
        models = discover_models(tmp_path)
        assert models == []

    def test_discover_models_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test discover_models handles nonexistent directory."""
        models = discover_models(tmp_path / "nonexistent")
        assert models == []

    def test_discover_models_finds_sql_files(self, tmp_path: Path) -> None:
        """Test discover_models finds .sql files."""
        (tmp_path / "model_a.sql").write_text("SELECT 1")
        (tmp_path / "model_b.sql").write_text("SELECT 2")
        (tmp_path / "not_a_model.txt").write_text("ignored")

        models = discover_models(tmp_path)

        assert len(models) == 2
        names = [m.name for m in models]
        assert "model_a" in names
        assert "model_b" in names

    def test_discover_models_sorted_by_name(self, tmp_path: Path) -> None:
        """Test discover_models returns models sorted by name."""
        (tmp_path / "zebra.sql").write_text("SELECT 1")
        (tmp_path / "apple.sql").write_text("SELECT 2")
        (tmp_path / "mango.sql").write_text("SELECT 3")

        models = discover_models(tmp_path)

        names = [m.name for m in models]
        assert names == ["apple", "mango", "zebra"]

    def test_discover_models_with_filter(self, tmp_path: Path) -> None:
        """Test discover_models filters by model name."""
        (tmp_path / "target.sql").write_text("SELECT 1")
        (tmp_path / "other.sql").write_text("SELECT 2")

        models = discover_models(tmp_path, model_name="target")

        assert len(models) == 1
        assert models[0].name == "target"

    def test_discover_models_nested_directories(self, tmp_path: Path) -> None:
        """Test discover_models finds models in subdirectories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested_model.sql").write_text("SELECT 1")

        models = discover_models(tmp_path)

        assert len(models) == 1
        assert models[0].name == "nested_model"
        assert models[0].directory == "subdir"
