from dataclasses import dataclass
from pathlib import Path

import requests
from ..latest import names_to_latest_dict

from .package_description import PackageDescription, KnownPackages
from .uploader import CodebergUploader

__all__ = [
    "CodebergPackageDownloader",
    "CodebergUploader",
    "PackageDescription",
    "KnownPackages",
]


@dataclass
class CodebergPackageDownloader:
    """Enables downloading the latest version of a package"""

    package: PackageDescription
    owner: str = "funfedidev"

    api_prefix: str = "https://codeberg.org/api"

    @property
    def filelist_url(self):
        """
        ```
        >>> downloader = CodebergPackageDownloader(PackageDescription("results_funfedi_connect", "0.1.3"))
        >>> downloader.filelist_url
        'https://codeberg.org/api/v1/packages/funfedidev/generic/results_funfedi_connect/0.1.3/files'

        ```
        """
        return f"{self.api_prefix}/v1/packages/{self.owner}/generic/{self.package.path}/files"

    def download_link(self, app_name, app_version):
        """
        ```
        >>> downloader = CodebergPackageDownloader(PackageDescription("results_funfedi_connect", "0.1.3"))
        >>> downloader.download_link("cattle_grid", "0.5.20")
        'https://codeberg.org/api/packages/funfedidev/generic/results_funfedi_connect/0.1.3/cattle_grid_0.5.20.zip'

        ```
        """
        filename = f"{app_name}_{app_version}.zip"
        return f"{self.api_prefix}/packages/{self.owner}/generic/{self.package.path}/{filename}"

    def has_a_version(self, app_name, app_version):
        filename = f"{app_name}_{app_version}.zip"
        return filename in self.fetch_filelist()

    def fetch_filelist(self) -> list[str]:
        result = requests.get(self.filelist_url)

        if result.status_code == 404:
            return []

        result.raise_for_status()
        data = result.json()
        return [x.get("name") for x in data]

    def latest_version_per_app(self):
        """Returns the latest versions"""
        names = self.fetch_filelist()
        return names_to_latest_dict(names)

    def target_directory(self, directory: Path):
        return directory / self.package.path

    def download_latest(self, directory: Path):
        names_and_versions = self.latest_version_per_app()
        target_directory = self.target_directory(directory)
        target_directory.mkdir(exist_ok=True, parents=True)

        for name, version in names_and_versions.items():
            download_link = self.download_link(name, version)
            filename = target_directory / download_link.split("/")[-1]

            if filename.exists():
                continue

            print(f"downloading {download_link}")

            response = requests.get(download_link)
            assert response.status_code == 200, (
                f"Got response code {response.status_code} for downloading {download_link}"
            )
            with open(filename, "wb") as f:
                f.write(response.content)
