from labels.model.file import Coordinates, Location
from labels.model.package import Language
from labels.model.syft_sbom import SyftLocation


def get_language(language_str: str) -> Language:
    try:
        return Language(language_str.lower())
    except ValueError:
        return Language.UNKNOWN_LANGUAGE


def get_locations(locations: list[SyftLocation]) -> list[Location]:
    return [
        Location(
            access_path=location.access_path,
            coordinates=Coordinates(
                real_path=location.access_path,
                file_system_id=location.layer_id,
            ),
        )
        for location in locations
        if (annotation := location.annotations)
        and (evidence := annotation.evidence)
        and evidence == "primary"
    ]
