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
from ..components.category_data import CategoryData_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.lengths import Lengths_V1_0_1
from ..components.lineage import Lineage_V1_0_0
from ..components.locations import Locations_V1_0_1
from ..components.one_of_attribute import OneOfAttribute_V1_0_1, OneOfAttribute_V1_1_0, OneOfAttribute_V1_2_0
from ..elements.float_array_1 import FloatArray1_V1_0_1
from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_3_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of locations.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_3_0_Depths(Lengths_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of depths.

    Attributes:
        lengths (FloatArray1_V1_0_1): Length values.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """1D geophysical records.

    Attributes:
        schema (str)
        number_of_layers (int): Number of layers.
        locations (GeophysicalRecords1D_V1_3_0_Locations): Array of locations.
        depths (GeophysicalRecords1D_V1_3_0_Depths): Array of depths.
        line_numbers (CategoryData_V1_0_1, optional): Line numbers.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_3_0_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_3_0_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_3_0_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_3_0_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_3_0_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_3_0_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.3.0/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_1_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_1_0):
    """Array of locations.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_1_0_Depths(Lengths_V1_0_1, AttributeListProperty_V1_1_0):
    """Array of depths.

    Attributes:
        lengths (FloatArray1_V1_0_1): Length values.
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """1D geophysical records.

    Attributes:
        schema (str)
        number_of_layers (int): Number of layers.
        locations (GeophysicalRecords1D_V1_1_0_Locations): Array of locations.
        depths (GeophysicalRecords1D_V1_1_0_Depths): Array of depths.
        line_numbers (CategoryData_V1_0_1, optional): Line numbers.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_1_0_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_1_0_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_1_0_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_1_0_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_1_0_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_1_0_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.1.0/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_0_1_Locations(Locations_V1_0_1, AttributeListProperty_V1_0_1):
    """Array of locations.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_0_1, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_0_1_Depths(Lengths_V1_0_1, AttributeListProperty_V1_0_1):
    """Array of depths.

    Attributes:
        lengths (FloatArray1_V1_0_1): Length values.
        attributes (OneOfAttribute_V1_0_1, optional): Attribute data.
    """

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """1D geophysical records.

    Attributes:
        schema (str)
        number_of_layers (int): Number of layers.
        locations (GeophysicalRecords1D_V1_0_1_Locations): Array of locations.
        depths (GeophysicalRecords1D_V1_0_1_Depths): Array of depths.
        line_numbers (CategoryData_V1_0_1, optional): Line numbers.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_0_1_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_0_1_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_0_1_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_0_1_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_0_1_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_0_1_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.0.1/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_2_0_Locations(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of locations.

    Attributes:
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_2_0_Depths(Lengths_V1_0_1, AttributeListProperty_V1_2_0):
    """Array of depths.

    Attributes:
        lengths (FloatArray1_V1_0_1): Length values.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Lengths_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class GeophysicalRecords1D_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """1D geophysical records.

    Attributes:
        schema (str)
        number_of_layers (int): Number of layers.
        locations (GeophysicalRecords1D_V1_2_0_Locations): Array of locations.
        depths (GeophysicalRecords1D_V1_2_0_Depths): Array of depths.
        line_numbers (CategoryData_V1_0_1, optional): Line numbers.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json"

    number_of_layers: int
    """Number of layers."""
    locations: GeophysicalRecords1D_V1_2_0_Locations
    """Array of locations."""
    depths: GeophysicalRecords1D_V1_2_0_Depths
    """Array of depths."""
    schema: str = "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json"
    line_numbers: CategoryData_V1_0_1 | None = None
    """Line numbers."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.number_of_layers, int):
            raise ValidationFailed("self.number_of_layers is not int")
        if not 0 < self.number_of_layers:
            raise ValidationFailed("0 < self.number_of_layers failed")
        if not isinstance(self.locations, GeophysicalRecords1D_V1_2_0_Locations):
            raise ValidationFailed("self.locations is not GeophysicalRecords1D_V1_2_0_Locations")
        if not isinstance(self.depths, GeophysicalRecords1D_V1_2_0_Depths):
            raise ValidationFailed("self.depths is not GeophysicalRecords1D_V1_2_0_Depths")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geophysical-records-1d/1.2.0/geophysical-records-1d.schema.json" failed'
            )
        if self.line_numbers is not None:
            if not isinstance(self.line_numbers, CategoryData_V1_0_1):
                raise ValidationFailed("self.line_numbers is not CategoryData_V1_0_1")
