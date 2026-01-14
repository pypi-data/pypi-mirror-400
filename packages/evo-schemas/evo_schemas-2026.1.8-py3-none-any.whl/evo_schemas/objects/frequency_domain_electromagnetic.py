import dataclasses
import typing

from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.frequency_domain_electromagnetic_channel import FrequencyDomainElectromagneticChannel_V1_0_0
from ..components.lineage import Lineage_V1_0_0
from ..components.survey_line import SurveyLine_V1_1_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class FrequencyDomainElectromagnetic_V1_0_0_Survey(Serialiser):
    """Survey information.

    Attributes:
        type (str): Survey type.
    """

    type: str
    """Survey type."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR"):
            raise ValidationFailed('self.type in ("GROUND", "AIR") failed')


@dataclasses.dataclass(kw_only=True)
class FrequencyDomainElectromagnetic_V1_0_0(BaseSpatialDataProperties_V1_0_1):
    """Frequency Domain Electromagnetic data.

    Attributes:
        schema (str)
        survey (FrequencyDomainElectromagnetic_V1_0_0_Survey): Survey information.
        data_type (str, optional): Data type.
        channels (list[FrequencyDomainElectromagneticChannel_V1_0_0]): Channel information.
        line_list (list[SurveyLine_V1_1_0]): Line list.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/frequency-domain-electromagnetic/1.0.0/frequency-domain-electromagnetic.schema.json"

    survey: FrequencyDomainElectromagnetic_V1_0_0_Survey
    """Survey information."""
    channels: list[FrequencyDomainElectromagneticChannel_V1_0_0]
    """Channel information."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/frequency-domain-electromagnetic/1.0.0/frequency-domain-electromagnetic.schema.json"
    data_type: str | None = None
    """Data type."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.survey, FrequencyDomainElectromagnetic_V1_0_0_Survey):
            raise ValidationFailed("self.survey is not FrequencyDomainElectromagnetic_V1_0_0_Survey")
        if not isinstance(self.channels, list):
            raise ValidationFailed("self.channels is not a list")
        for v in self.channels:
            if not isinstance(v, FrequencyDomainElectromagneticChannel_V1_0_0):
                raise ValidationFailed("v is not FrequencyDomainElectromagneticChannel_V1_0_0")
        if not 1 <= len(self.channels):
            raise ValidationFailed("1 <= len(self.channels) failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if (
            not self.schema
            == "/objects/frequency-domain-electromagnetic/1.0.0/frequency-domain-electromagnetic.schema.json"
        ):
            raise ValidationFailed(
                'self.schema == "/objects/frequency-domain-electromagnetic/1.0.0/frequency-domain-electromagnetic.schema.json" failed'
            )
        if self.data_type is not None:
            if not isinstance(self.data_type, str):
                raise ValidationFailed("self.data_type is not str")


@dataclasses.dataclass(kw_only=True)
class FrequencyDomainElectromagnetic_V1_1_0_Survey(Serialiser):
    """Survey information.

    Attributes:
        type (str): Survey type.
    """

    type: str
    """Survey type."""

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if self.type not in ("GROUND", "AIR"):
            raise ValidationFailed('self.type in ("GROUND", "AIR") failed')


@dataclasses.dataclass(kw_only=True)
class FrequencyDomainElectromagnetic_V1_1_0(BaseSpatialDataProperties_V1_1_0):
    """Frequency Domain Electromagnetic data.

    Attributes:
        schema (str)
        survey (FrequencyDomainElectromagnetic_V1_1_0_Survey): Survey information.
        data_type (str, optional): Data type.
        channels (list[FrequencyDomainElectromagneticChannel_V1_0_0]): Channel information.
        line_list (list[SurveyLine_V1_1_0]): Line list.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/frequency-domain-electromagnetic/1.1.0/frequency-domain-electromagnetic.schema.json"

    survey: FrequencyDomainElectromagnetic_V1_1_0_Survey
    """Survey information."""
    channels: list[FrequencyDomainElectromagneticChannel_V1_0_0]
    """Channel information."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/frequency-domain-electromagnetic/1.1.0/frequency-domain-electromagnetic.schema.json"
    data_type: str | None = None
    """Data type."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.survey, FrequencyDomainElectromagnetic_V1_1_0_Survey):
            raise ValidationFailed("self.survey is not FrequencyDomainElectromagnetic_V1_1_0_Survey")
        if not isinstance(self.channels, list):
            raise ValidationFailed("self.channels is not a list")
        for v in self.channels:
            if not isinstance(v, FrequencyDomainElectromagneticChannel_V1_0_0):
                raise ValidationFailed("v is not FrequencyDomainElectromagneticChannel_V1_0_0")
        if not 1 <= len(self.channels):
            raise ValidationFailed("1 <= len(self.channels) failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if (
            not self.schema
            == "/objects/frequency-domain-electromagnetic/1.1.0/frequency-domain-electromagnetic.schema.json"
        ):
            raise ValidationFailed(
                'self.schema == "/objects/frequency-domain-electromagnetic/1.1.0/frequency-domain-electromagnetic.schema.json" failed'
            )
        if self.data_type is not None:
            if not isinstance(self.data_type, str):
                raise ValidationFailed("self.data_type is not str")
