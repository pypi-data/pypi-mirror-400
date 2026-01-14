from dataclasses import dataclass


@dataclass
class ResultDescription:
    """
    ```
    >>> t = ResultDescription("0.1.2", "mitra", "v4.15.0")
    >>> t.filename
    'data/results_funfedi_connect/0.1.2/mitra_v4.15.0.zip'

    ```
    """

    test_case_version: str
    application: str
    application_version: str

    @property
    def filename(self):
        return f"data/results_funfedi_connect/{self.test_case_version}/{self.application}_{self.application_version}.zip"


@dataclass
class LoadedResult:
    containers: list[dict]
    results: list[dict]
    attachments: dict[str, dict]


@dataclass
class FeatureResult:
    name: str
    status: str
    tags: list[str]
    start: int
    attachments: dict[str, str]

    @staticmethod
    def from_data(data: dict):
        name = data.get("fullName", "-- missing --")
        status = data.get("status", "-- missing --")
        tags = [
            x.get("value", "") for x in data.get("labels", []) if x.get("name") == "tag"
        ]
        attachments = {}
        for step in data.get("steps", []):
            for attachment in step.get("attachments", []):
                a = attachment.get("source")
                a_name = attachment.get("name")
                if a and a_name:
                    attachments[a_name] = a.removesuffix("-attachment.json")

        return FeatureResult(
            name, status, tags, start=data.get("start", 0), attachments=attachments
        )
