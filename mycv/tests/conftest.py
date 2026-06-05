import pytest
from pathlib import Path


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent.parent / "data" / "professional.yaml"


@pytest.fixture
def config_path() -> Path:
    return Path(__file__).parent.parent / "cv_config.yaml"


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    return tmp_path / "cv_output"
