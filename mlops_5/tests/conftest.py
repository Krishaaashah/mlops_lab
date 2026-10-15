from pathlib import Path

import pytest

MODEL = Path("models/model.joblib")


@pytest.fixture(scope="session", autouse=True)
def require_model():
    """The tests exercise the real model produced by the DVC pipeline."""
    if not MODEL.exists():
        pytest.fail(
            "models/model.joblib not found - run `dvc repro` before `pytest`.",
            pytrace=False,
        )
