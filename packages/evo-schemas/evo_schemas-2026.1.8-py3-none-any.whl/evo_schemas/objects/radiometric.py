import dataclasses
import typing

from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.lineage import Lineage_V1_0_0
from ..components.survey_attribute_definition import SurveyAttributeDefinition_V1_0_1
from ..components.survey_collection import SurveyCollection_V1_0_1
from ..components.survey_line import SurveyLine_V1_0_1, SurveyLine_V1_1_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_1_0_Survey(Serialiser):
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
class Radiometric_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """Radiometric survey data.

    Attributes:
        schema (str)
        survey (Radiometric_V1_1_0_Survey): Survey information.
        dead_time (float): Dead time (msec).
        live_time (float): Live time (msec).
        idle_time (float): Idle time (msec).
        array_dimension (int): Array dimension.
        energy_level (float, optional): Energy level (meV) of array elements.
        line_list (list[SurveyLine_V1_1_0]): Line list.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/radiometric/1.1.0/radiometric.schema.json"

    survey: Radiometric_V1_1_0_Survey
    """Survey information."""
    dead_time: float
    """Dead time (msec)."""
    live_time: float
    """Live time (msec)."""
    idle_time: float
    """Idle time (msec)."""
    array_dimension: int = 1024
    """Array dimension."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/radiometric/1.1.0/radiometric.schema.json"
    energy_level: float | None = None
    """Energy level (meV) of array elements."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.survey, Radiometric_V1_1_0_Survey):
            raise ValidationFailed("self.survey is not Radiometric_V1_1_0_Survey")
        if not isinstance(self.dead_time, float):
            raise ValidationFailed("self.dead_time is not float")
        if not 0.0 <= self.dead_time:
            raise ValidationFailed("0.0 <= self.dead_time failed")
        if not isinstance(self.live_time, float):
            raise ValidationFailed("self.live_time is not float")
        if not 0.0 <= self.live_time:
            raise ValidationFailed("0.0 <= self.live_time failed")
        if not isinstance(self.idle_time, float):
            raise ValidationFailed("self.idle_time is not float")
        if not 0.0 <= self.idle_time:
            raise ValidationFailed("0.0 <= self.idle_time failed")
        if not isinstance(self.array_dimension, int):
            raise ValidationFailed("self.array_dimension is not int")
        if not 1 <= self.array_dimension:
            raise ValidationFailed("1 <= self.array_dimension failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/radiometric/1.1.0/radiometric.schema.json":
            raise ValidationFailed('self.schema == "/objects/radiometric/1.1.0/radiometric.schema.json" failed')
        if self.energy_level is not None:
            if not isinstance(self.energy_level, float):
                raise ValidationFailed("self.energy_level is not float")
            if not 0.0 <= self.energy_level:
                raise ValidationFailed("0.0 <= self.energy_level failed")


@dataclasses.dataclass(kw_only=True)
class Radiometric_V2_0_0_Survey(Serialiser):
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
class Radiometric_V2_0_0(BaseSpatialDataProperties_V1_1_0):
    """Radiometric survey data.

    Attributes:
        schema (str)
        survey (Radiometric_V2_0_0_Survey): Survey information.
        sample_time (float, optional): Total time that elapses between each record (msec). Required for idle/live time corrections.
        array_dimension (int): Array dimension.
        energy_level (float, optional): Energy level (meV) of array elements.
        attribute_definition_list (list[SurveyAttributeDefinition_V1_0_1]): List of attribute definitions. These will be referenced in survey collections.
        collections (list[SurveyCollection_V1_0_1]): Survey collections.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/radiometric/2.0.0/radiometric.schema.json"

    survey: Radiometric_V2_0_0_Survey
    """Survey information."""
    array_dimension: int = 1024
    """Array dimension."""
    attribute_definition_list: list[SurveyAttributeDefinition_V1_0_1]
    """List of attribute definitions. These will be referenced in survey collections."""
    collections: list[SurveyCollection_V1_0_1]
    """Survey collections."""
    schema: str = "/objects/radiometric/2.0.0/radiometric.schema.json"
    sample_time: float | None = None
    """Total time that elapses between each record (msec). Required for idle/live time corrections."""
    energy_level: float | None = None
    """Energy level (meV) of array elements."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.survey, Radiometric_V2_0_0_Survey):
            raise ValidationFailed("self.survey is not Radiometric_V2_0_0_Survey")
        if not isinstance(self.array_dimension, int):
            raise ValidationFailed("self.array_dimension is not int")
        if not 1 <= self.array_dimension:
            raise ValidationFailed("1 <= self.array_dimension failed")
        if not isinstance(self.attribute_definition_list, list):
            raise ValidationFailed("self.attribute_definition_list is not a list")
        for v in self.attribute_definition_list:
            if not isinstance(v, SurveyAttributeDefinition_V1_0_1):
                raise ValidationFailed("v is not SurveyAttributeDefinition_V1_0_1")
        if not 1 <= len(self.attribute_definition_list):
            raise ValidationFailed("1 <= len(self.attribute_definition_list) failed")
        if not isinstance(self.collections, list):
            raise ValidationFailed("self.collections is not a list")
        for v in self.collections:
            if not isinstance(v, SurveyCollection_V1_0_1):
                raise ValidationFailed("v is not SurveyCollection_V1_0_1")
        if not 1 <= len(self.collections):
            raise ValidationFailed("1 <= len(self.collections) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/radiometric/2.0.0/radiometric.schema.json":
            raise ValidationFailed('self.schema == "/objects/radiometric/2.0.0/radiometric.schema.json" failed')
        if self.sample_time is not None:
            if not isinstance(self.sample_time, float):
                raise ValidationFailed("self.sample_time is not float")
            if not 0.0 <= self.sample_time:
                raise ValidationFailed("0.0 <= self.sample_time failed")
        if self.energy_level is not None:
            if not isinstance(self.energy_level, float):
                raise ValidationFailed("self.energy_level is not float")
            if not 0.0 <= self.energy_level:
                raise ValidationFailed("0.0 <= self.energy_level failed")


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_0_1_Survey(Serialiser):
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
class Radiometric_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """Radiometric survey data.

    Attributes:
        schema (str)
        survey (Radiometric_V1_0_1_Survey): Survey information.
        dead_time (float): Dead time (msec).
        live_time (float): Live time (msec).
        idle_time (float): Idle time (msec).
        array_dimension (int): Array dimension.
        energy_level (float, optional): Energy level (meV) of array elements.
        line_list (list[SurveyLine_V1_0_1]): Line list.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/radiometric/1.0.1/radiometric.schema.json"

    survey: Radiometric_V1_0_1_Survey
    """Survey information."""
    dead_time: float
    """Dead time (msec)."""
    live_time: float
    """Live time (msec)."""
    idle_time: float
    """Idle time (msec)."""
    array_dimension: int = 1024
    """Array dimension."""
    line_list: list[SurveyLine_V1_0_1]
    """Line list."""
    schema: str = "/objects/radiometric/1.0.1/radiometric.schema.json"
    energy_level: float | None = None
    """Energy level (meV) of array elements."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.survey, Radiometric_V1_0_1_Survey):
            raise ValidationFailed("self.survey is not Radiometric_V1_0_1_Survey")
        if not isinstance(self.dead_time, float):
            raise ValidationFailed("self.dead_time is not float")
        if not 0.0 <= self.dead_time:
            raise ValidationFailed("0.0 <= self.dead_time failed")
        if not isinstance(self.live_time, float):
            raise ValidationFailed("self.live_time is not float")
        if not 0.0 <= self.live_time:
            raise ValidationFailed("0.0 <= self.live_time failed")
        if not isinstance(self.idle_time, float):
            raise ValidationFailed("self.idle_time is not float")
        if not 0.0 <= self.idle_time:
            raise ValidationFailed("0.0 <= self.idle_time failed")
        if not isinstance(self.array_dimension, int):
            raise ValidationFailed("self.array_dimension is not int")
        if not 1 <= self.array_dimension:
            raise ValidationFailed("1 <= self.array_dimension failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_0_1):
                raise ValidationFailed("v is not SurveyLine_V1_0_1")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/radiometric/1.0.1/radiometric.schema.json":
            raise ValidationFailed('self.schema == "/objects/radiometric/1.0.1/radiometric.schema.json" failed')
        if self.energy_level is not None:
            if not isinstance(self.energy_level, float):
                raise ValidationFailed("self.energy_level is not float")
            if not 0.0 <= self.energy_level:
                raise ValidationFailed("0.0 <= self.energy_level failed")


@dataclasses.dataclass(kw_only=True)
class Radiometric_V1_2_0_Survey(Serialiser):
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
class Radiometric_V1_2_0(BaseSpatialDataProperties_V1_1_0):
    """Radiometric survey data.

    Attributes:
        schema (str)
        survey (Radiometric_V1_2_0_Survey): Survey information.
        dead_time (float): Dead time (msec).
        live_time (float): Live time (msec).
        idle_time (float): Idle time (msec).
        array_dimension (int): Array dimension.
        energy_level (float, optional): Energy level (meV) of array elements.
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

    SCHEMA_ID = "/objects/radiometric/1.2.0/radiometric.schema.json"

    survey: Radiometric_V1_2_0_Survey
    """Survey information."""
    dead_time: float
    """Dead time (msec)."""
    live_time: float
    """Live time (msec)."""
    idle_time: float
    """Idle time (msec)."""
    array_dimension: int = 1024
    """Array dimension."""
    line_list: list[SurveyLine_V1_1_0]
    """Line list."""
    schema: str = "/objects/radiometric/1.2.0/radiometric.schema.json"
    energy_level: float | None = None
    """Energy level (meV) of array elements."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.survey, Radiometric_V1_2_0_Survey):
            raise ValidationFailed("self.survey is not Radiometric_V1_2_0_Survey")
        if not isinstance(self.dead_time, float):
            raise ValidationFailed("self.dead_time is not float")
        if not 0.0 <= self.dead_time:
            raise ValidationFailed("0.0 <= self.dead_time failed")
        if not isinstance(self.live_time, float):
            raise ValidationFailed("self.live_time is not float")
        if not 0.0 <= self.live_time:
            raise ValidationFailed("0.0 <= self.live_time failed")
        if not isinstance(self.idle_time, float):
            raise ValidationFailed("self.idle_time is not float")
        if not 0.0 <= self.idle_time:
            raise ValidationFailed("0.0 <= self.idle_time failed")
        if not isinstance(self.array_dimension, int):
            raise ValidationFailed("self.array_dimension is not int")
        if not 1 <= self.array_dimension:
            raise ValidationFailed("1 <= self.array_dimension failed")
        if not isinstance(self.line_list, list):
            raise ValidationFailed("self.line_list is not a list")
        for v in self.line_list:
            if not isinstance(v, SurveyLine_V1_1_0):
                raise ValidationFailed("v is not SurveyLine_V1_1_0")
        if not 1 <= len(self.line_list):
            raise ValidationFailed("1 <= len(self.line_list) failed")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/radiometric/1.2.0/radiometric.schema.json":
            raise ValidationFailed('self.schema == "/objects/radiometric/1.2.0/radiometric.schema.json" failed')
        if self.energy_level is not None:
            if not isinstance(self.energy_level, float):
                raise ValidationFailed("self.energy_level is not float")
            if not 0.0 <= self.energy_level:
                raise ValidationFailed("0.0 <= self.energy_level failed")
