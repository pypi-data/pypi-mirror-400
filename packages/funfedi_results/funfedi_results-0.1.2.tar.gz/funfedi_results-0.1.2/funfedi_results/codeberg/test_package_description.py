import pytest
from .package_description import KnownPackages, PackageDescription


def test_package_description():
    PackageDescription("name", "0.1.2")


def test_package_description_failure():
    with pytest.raises(Exception):
        PackageDescription("name", "xxx")


def test_package_description_path():
    p = PackageDescription(KnownPackages.parsing, "0.1.4")

    assert p.path == "results_funfedi_parsing/0.1.4"
