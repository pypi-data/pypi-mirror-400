from dataclasses import dataclass
from enum import StrEnum
import semver

from funfedi_results.latest import to_semver


class KnownPackages(StrEnum):
    """Predefined packages"""

    parsing = "results_funfedi_parsing"
    connect = "results_funfedi_connect"


@dataclass
class PackageDescription:
    """Describes a package"""

    name: str | KnownPackages
    version: str

    @property
    def path(self):
        return f"{self.name}/{self.version}"

    def __post_init__(self):
        if to_semver(self.version) == semver.Version(0):
            raise Exception("version should be a valid version")
