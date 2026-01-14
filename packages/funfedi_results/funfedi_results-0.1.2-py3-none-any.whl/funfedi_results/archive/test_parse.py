import pytest
import os

from .parse import features_from_result, load_archive
from .types import ResultDescription


@pytest.mark.skipif(not os.path.exists("data"), reason="No test data")
def test_load():
    desc = ResultDescription("0.1.3", "mitra", "v4.15.0")

    result = load_archive(desc)

    assert result


@pytest.mark.skipif(not os.path.exists("data"), reason="No test data")
def test_features():
    desc = ResultDescription("0.1.3", "mitra", "v4.15.0")
    result = load_archive(desc)
    assert len(features_from_result(result)) > 0
