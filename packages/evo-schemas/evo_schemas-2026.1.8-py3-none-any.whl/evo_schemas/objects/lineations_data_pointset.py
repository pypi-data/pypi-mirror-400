import dataclasses
import typing

from ..components.attribute_list_property import (
    AttributeListProperty_V1_0_1,
    AttributeListProperty_V1_1_0,
    AttributeListProperty_V1_2_0,
)
from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.lineage import Lineage_V1_0_0
from ..components.lineation_data import LineationData_V1_0_1
from ..components.locations import Locations_V1_0_1
from ..components.one_of_attribute import OneOfAttribute_V1_0_1, OneOfAttribute_V1_1_0, OneOfAttribute_V1_2_0
from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_3_0_Locations(Locations_V1_0_1, LineationData_V1_0_1, AttributeListProperty_V1_2_0):
    """The structural lineations data and attributes.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        lineations (FloatArray2_V1_0_1): Lineation data. Columns: trend, plunge.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        LineationData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """A set of structural lineations points and their associated attributes.

    Attributes:
        schema (str)
        locations (LineationsDataPointset_V1_3_0_Locations): The structural lineations data and attributes.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/lineations-data-pointset/1.3.0/lineations-data-pointset.schema.json"

    locations: LineationsDataPointset_V1_3_0_Locations
    """The structural lineations data and attributes."""
    schema: str = "/objects/lineations-data-pointset/1.3.0/lineations-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.locations, LineationsDataPointset_V1_3_0_Locations):
            raise ValidationFailed("self.locations is not LineationsDataPointset_V1_3_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/lineations-data-pointset/1.3.0/lineations-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/lineations-data-pointset/1.3.0/lineations-data-pointset.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_1_0_Locations(Locations_V1_0_1, LineationData_V1_0_1, AttributeListProperty_V1_1_0):
    """The structural lineations data and attributes.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        lineations (FloatArray2_V1_0_1): Lineation data. Columns: trend, plunge.
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        LineationData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A set of structural lineations points and their associated attributes.

    Attributes:
        schema (str)
        locations (LineationsDataPointset_V1_1_0_Locations): The structural lineations data and attributes.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/lineations-data-pointset/1.1.0/lineations-data-pointset.schema.json"

    locations: LineationsDataPointset_V1_1_0_Locations
    """The structural lineations data and attributes."""
    schema: str = "/objects/lineations-data-pointset/1.1.0/lineations-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, LineationsDataPointset_V1_1_0_Locations):
            raise ValidationFailed("self.locations is not LineationsDataPointset_V1_1_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/lineations-data-pointset/1.1.0/lineations-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/lineations-data-pointset/1.1.0/lineations-data-pointset.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_0_1_Locations(Locations_V1_0_1, LineationData_V1_0_1, AttributeListProperty_V1_0_1):
    """The structural lineations data and attributes.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        lineations (FloatArray2_V1_0_1): Lineation data. Columns: trend, plunge.
        attributes (OneOfAttribute_V1_0_1, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        LineationData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A set of structural lineations points and their associated attributes.

    Attributes:
        schema (str)
        locations (LineationsDataPointset_V1_0_1_Locations): The structural lineations data and attributes.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/lineations-data-pointset/1.0.1/lineations-data-pointset.schema.json"

    locations: LineationsDataPointset_V1_0_1_Locations
    """The structural lineations data and attributes."""
    schema: str = "/objects/lineations-data-pointset/1.0.1/lineations-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, LineationsDataPointset_V1_0_1_Locations):
            raise ValidationFailed("self.locations is not LineationsDataPointset_V1_0_1_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/lineations-data-pointset/1.0.1/lineations-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/lineations-data-pointset/1.0.1/lineations-data-pointset.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_2_0_Locations(Locations_V1_0_1, LineationData_V1_0_1, AttributeListProperty_V1_2_0):
    """The structural lineations data and attributes.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        lineations (FloatArray2_V1_0_1): Lineation data. Columns: trend, plunge.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        LineationData_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LineationsDataPointset_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """A set of structural lineations points and their associated attributes.

    Attributes:
        schema (str)
        locations (LineationsDataPointset_V1_2_0_Locations): The structural lineations data and attributes.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/lineations-data-pointset/1.2.0/lineations-data-pointset.schema.json"

    locations: LineationsDataPointset_V1_2_0_Locations
    """The structural lineations data and attributes."""
    schema: str = "/objects/lineations-data-pointset/1.2.0/lineations-data-pointset.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.locations, LineationsDataPointset_V1_2_0_Locations):
            raise ValidationFailed("self.locations is not LineationsDataPointset_V1_2_0_Locations")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/lineations-data-pointset/1.2.0/lineations-data-pointset.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/lineations-data-pointset/1.2.0/lineations-data-pointset.schema.json" failed'
            )
