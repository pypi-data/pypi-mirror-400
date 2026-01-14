from collections import defaultdict
from glob import glob
import re
import semver

pattern = re.compile(r"data/results_funfedi_connect/(.*)?/(.*)?_(.*).zip")


def to_semver(version, skip_prerelease=True):
    try:
        if version.count(".") == 1:
            version = "0." + version
        if "a" in version:
            version = version.split("a")[0]
        result = semver.Version.parse(version.removeprefix("v"))

        if result.prerelease and skip_prerelease:
            return semver.Version(0)
        return result
    except Exception:
        return semver.Version(0)


def later_version(a, b):
    """
    ```
    >>> later_version("v4.5.2", "v4.6.2")
    'v4.6.2'

    ```
    """
    if to_semver(a) > to_semver(b):
        return a
    return b


def latest_for_app_name(name: str):
    case_version = None
    app_version = None
    for x in glob(f"data/results_funfedi_connect/*/{name}_*"):
        m = re.match(pattern, x)
        if not m:
            raise Exception("Does not match regex")
        case_version = later_version(case_version, m.group(1))
        app_version = later_version(app_version, m.group(3))

    return case_version, app_version


def name_and_version(filename: str) -> tuple[str, str]:
    """
    ```
    >>> name_and_version("cattle_grid_0.5.20.zip")
    ('cattle_grid', '0.5.20')

    ```
    """
    split = filename.split("_")
    return "_".join(split[:-1]), split[-1].removesuffix(".zip")


def names_to_latest_dict(names: list[str]) -> dict[str, str]:
    names_and_versions = [name_and_version(x) for x in names]

    name_to_version = defaultdict(list)

    for name, version in names_and_versions:
        name_to_version[name].append(version)

    return {
        name: sorted(versions, key=to_semver)[0]
        for name, versions in name_to_version.items()
    }
