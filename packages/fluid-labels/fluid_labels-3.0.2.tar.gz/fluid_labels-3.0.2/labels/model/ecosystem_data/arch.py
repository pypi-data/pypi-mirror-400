from labels.model.ecosystem_data.base import EcosystemDataModel


class AlpmDBEntry(EcosystemDataModel):
    base_package: str = ""
    package: str = ""
    version: str = ""
    architecture: str = ""
    packager: str = ""
