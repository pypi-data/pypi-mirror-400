import dataclasses

from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .fiducial_description import FiducialDescription_V1_0_1
from .locations import Locations_V1_0_1
from .survey_attribute import SurveyAttribute_V1_0_1


@dataclasses.dataclass(kw_only=True)
class SurveyCollection_V1_0_1_Locations(Locations_V1_0_1, FiducialDescription_V1_0_1):
    """Survey collection locations.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        start (float): Starting fiducial number.
        increment (float): Fiducial increment amount.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        FiducialDescription_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class SurveyCollection_V1_0_1(Serialiser):
    """A survey collection containing a collection number, type, and attributes.

    Attributes:
        identifier (str): The collection identifier. In line-based surveys, this will typically be the line number.
        date (str, optional): The date the survey collection was conducted.
        version (int, optional): The version of the survey collection.
        group (int, optional): The group of the survey collection.
        type (str): Survey collection type.
        locations (SurveyCollection_V1_0_1_Locations, optional): Survey collection locations.
        survey_attributes (list[SurveyAttribute_V1_0_1]): List of survey attributes.
    """

    SCHEMA_ID = "/components/survey-collection/1.0.1/survey-collection.schema.json"

    identifier: str
    """The collection identifier. In line-based surveys, this will typically be the line number."""
    type: str = "Line"
    """Survey collection type."""
    survey_attributes: list[SurveyAttribute_V1_0_1]
    """List of survey attributes."""
    date: str | None = None
    """The date the survey collection was conducted."""
    version: int = 0
    """The version of the survey collection."""
    group: int = 0
    """The group of the survey collection."""
    locations: SurveyCollection_V1_0_1_Locations | None = None
    """Survey collection locations."""

    def __post_init__(self):
        if not isinstance(self.identifier, str):
            raise ValidationFailed("self.identifier is not str")
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("Line", "Base", "Tie", "Trend", "Special", "Random", "Test"):
            raise ValidationFailed('self.type in ("Line", "Base", "Tie", "Trend", "Special", "Random", "Test") failed')
        if not isinstance(self.survey_attributes, list):
            raise ValidationFailed("self.survey_attributes is not a list")
        for v in self.survey_attributes:
            if not isinstance(v, SurveyAttribute_V1_0_1):
                raise ValidationFailed("v is not SurveyAttribute_V1_0_1")
        if self.date is not None:
            if not isinstance(self.date, str):
                raise ValidationFailed("self.date is not str")
            if not Serialiser.is_date_time(self.date):
                raise ValidationFailed("Serialiser.is_date_time(self.date) failed")
        if not isinstance(self.version, int):
            raise ValidationFailed("self.version is not int")
        if not 0 <= self.version:
            raise ValidationFailed("0 <= self.version failed")
        if not isinstance(self.group, int):
            raise ValidationFailed("self.group is not int")
        if not 0 <= self.group:
            raise ValidationFailed("0 <= self.group failed")
        if self.locations is not None:
            if not isinstance(self.locations, SurveyCollection_V1_0_1_Locations):
                raise ValidationFailed("self.locations is not SurveyCollection_V1_0_1_Locations")
