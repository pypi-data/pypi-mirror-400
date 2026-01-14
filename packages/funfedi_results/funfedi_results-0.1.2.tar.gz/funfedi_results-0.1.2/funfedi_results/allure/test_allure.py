import os
import zipfile

import pytest
from . import AllureResults


@pytest.fixture
def sample_dir(tmp_path):
    sample_dir = tmp_path / "a"
    sample_dir.mkdir()
    return sample_dir


@pytest.fixture
def sample_file(sample_dir):
    filename = sample_dir / "file.json"
    with open(filename, "w") as f:
        f.write('{"key":"value"}')

    return filename


def test_clean(sample_file, sample_dir):
    ar = AllureResults(path=sample_dir)
    ar.clean()

    assert not os.path.exists(sample_file)


def test_create_zip_file(sample_file, sample_dir, tmp_path):
    ar = AllureResults(path=sample_dir)

    results_dir = tmp_path / "r"
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / "results_0.1.0.zip"

    ar.create_zip(results_file)

    assert os.path.exists(results_file)

    with zipfile.ZipFile(results_file) as f:
        assert "file.json" in f.namelist()


def test_create_zip_file_fails_for_incorrect_name(sample_dir, tmp_path):
    ar = AllureResults(path=sample_dir)

    results_dir = tmp_path / "r"
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / "results.zip"

    with pytest.raises(Exception):
        ar.create_zip(results_file)


def test_extract(sample_file, sample_dir, tmp_path):
    ar = AllureResults(path=sample_dir)

    results_dir = tmp_path / "r"
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / "results_0.1.0.zip"
    ar.create_zip(results_file)
    ar.clean()

    ar.extract(results_dir)

    assert os.path.exists(sample_file)
