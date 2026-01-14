import pytest
import os
from . import feature_status


@pytest.mark.skipif(not os.path.exists("data"), reason="No test data")
def test_feature_status():
    result = feature_status("mitra")

    assert result == {
        "post": "passed",
        "public_timeline": "passed",
        "webfinger": "passed",
    }
