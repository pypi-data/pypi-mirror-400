from dataclasses import dataclass
import os
import requests

from .package_description import PackageDescription, KnownPackages  # noqa: F401


@dataclass
class CodebergUploader:
    """
    Helps uploading files to codeberg

    ```
    >>> uploader = CodebergUploader("user", "token")
    >>> uploader.upload_url(PackageDescription(KnownPackages.connect, "0.1.2"), "app_v1.2.3.zip")
    'https://token:user@codeberg.org/api/packages/funfedidev/generic/results_funfedi_connect/0.1.2/app_v1.2.3.zip'

    ```
    """

    token: str
    user: str

    @property
    def api_prefix(self) -> str:
        return f"https://{self.user}:{self.token}@codeberg.org/api/packages/funfedidev/generic/"

    def upload_url(self, package: PackageDescription, filename):
        return self.api_prefix + f"{package.path}/{filename}"

    def upload_file(self, package: PackageDescription, filename, file):
        """Uploads a file with url as in upload_url"""

        files = {"file": open(file, "rb")}
        url = self.upload_url(package, filename)
        result = requests.put(url, files=files)
        if result.status_code != 201:
            print(f"Upload to codeberg failed with status {result.status_code}")
            print(result.text)
        else:
            print("Uploaded to codeberg")

    @staticmethod
    def from_env():
        user = os.environ.get("CODEBERG_USER")
        token = os.environ.get("CODEBERG_TOKEN")

        if user is None or token is None:
            raise Exception("Expected CODEBERG_USER and CODEBERG_TOKEN to be set")

        return CodebergUploader(user, token)
