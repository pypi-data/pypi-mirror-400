import os

import pytest
from . import CodebergPackageDownloader, KnownPackages, PackageDescription


def run_tests_against_codeberg():
    if os.environ.get("HTTP_TESTS"):
        return False
    return True


@pytest.mark.skipif(run_tests_against_codeberg(), reason="Makes requests to codeberg")
def test_has_a_version():
    pd = PackageDescription(KnownPackages.connect, "0.1.3")
    downloader = CodebergPackageDownloader(pd)

    assert downloader.has_a_version("hollo", "0.6.19")
    assert not downloader.has_a_version("hollo", "0.6.20")


@pytest.mark.skipif(run_tests_against_codeberg(), reason="Makes requests to codeberg")
def test_no_results():
    pd = PackageDescription(KnownPackages.connect, "4520.0.0")
    downloader = CodebergPackageDownloader(pd)

    assert not downloader.has_a_version("hollo", "0.6.20")
