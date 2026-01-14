from dataclasses import dataclass
from glob import glob
from pathlib import Path
import zipfile

from funfedi_results.latest import name_and_version, names_to_latest_dict


@dataclass
class AllureResults:
    """Class to manage allure results"""

    path: Path = Path("allure-results")

    def clean(self):
        """Removes all files from the allure-results directory"""
        if self.path.exists():
            for child in self.path.iterdir():
                child.unlink()

        self.path.mkdir(exist_ok=True)

    @property
    def files_in_allure_dir(self):
        return glob(f"{self.path}/*.json")

    def create_zip(self, zipfilename: Path):
        """Zips all files in the allure-results directory into a file. Files
        are checked to have the naming convention `{app_name}_{app_version}.zip`"""
        name, version = name_and_version(zipfilename.name)
        if not (name and version):
            raise Exception(f"Invalid filename {zipfilename}")

        with zipfile.ZipFile(zipfilename, "w") as f:
            for name in self.files_in_allure_dir:
                new_name = name.split("/")[-1]
                f.write(name, new_name)

    def extract(self, file_directory: Path):
        """Takes all zip files from directory and extracts the latest
        version for each app into the allure-results directory"""
        self.clean()

        files = [x.name for x in file_directory.glob("*.zip")]
        latest = names_to_latest_dict(files)

        for name, version in latest.items():
            with zipfile.ZipFile(file_directory / f"{name}_{version}.zip") as f:
                f.extractall(self.path)
