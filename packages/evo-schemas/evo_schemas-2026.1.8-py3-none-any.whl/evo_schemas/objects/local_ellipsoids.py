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
from ..components.ellipsoids import Ellipsoids_V1_0_1
from ..components.lineage import Lineage_V1_0_0
from ..components.locations import Locations_V1_0_1
from ..components.one_of_attribute import OneOfAttribute_V1_0_1, OneOfAttribute_V1_1_0, OneOfAttribute_V1_2_0
from ..elements.float_array_6 import FloatArray6_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_3_0_Ellipsoids(Ellipsoids_V1_0_1, AttributeListProperty_V1_2_0):
    """Ellipsoid properties.

    Attributes:
        values (FloatArray6_V1_0_1): Array of ellipsoids. Columns: dip_azimuth, dip, pitch, major, semi_major, minor.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Ellipsoids_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """Local ellipsoids.

    Attributes:
        schema (str)
        locations (Locations_V1_0_1, optional): The locations of the ellipsoids.
        ellipsoids (LocalEllipsoids_V1_3_0_Ellipsoids): Ellipsoid properties.
        domain (str): The domain the local ellipsoids are modelled for
        attribute (str): The attribute the local ellipsoids are modelled for
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/local-ellipsoids/1.3.0/local-ellipsoids.schema.json"

    ellipsoids: LocalEllipsoids_V1_3_0_Ellipsoids
    """Ellipsoid properties."""
    domain: str
    """The domain the local ellipsoids are modelled for"""
    attribute: str
    """The attribute the local ellipsoids are modelled for"""
    schema: str = "/objects/local-ellipsoids/1.3.0/local-ellipsoids.schema.json"
    locations: Locations_V1_0_1 | None = None
    """The locations of the ellipsoids."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.ellipsoids, LocalEllipsoids_V1_3_0_Ellipsoids):
            raise ValidationFailed("self.ellipsoids is not LocalEllipsoids_V1_3_0_Ellipsoids")
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/local-ellipsoids/1.3.0/local-ellipsoids.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/local-ellipsoids/1.3.0/local-ellipsoids.schema.json" failed'
            )
        if self.locations is not None:
            if not isinstance(self.locations, Locations_V1_0_1):
                raise ValidationFailed("self.locations is not Locations_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_1_0_Ellipsoids(Ellipsoids_V1_0_1, AttributeListProperty_V1_1_0):
    """Ellipsoid properties.

    Attributes:
        values (FloatArray6_V1_0_1): Array of ellipsoids. Columns: dip_azimuth, dip, pitch, major, semi_major, minor.
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    def __post_init__(self):
        Ellipsoids_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """Local ellipsoids.

    Attributes:
        schema (str)
        locations (Locations_V1_0_1, optional): The locations of the ellipsoids.
        ellipsoids (LocalEllipsoids_V1_1_0_Ellipsoids): Ellipsoid properties.
        domain (str): The domain the local ellipsoids are modelled for
        attribute (str): The attribute the local ellipsoids are modelled for
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/local-ellipsoids/1.1.0/local-ellipsoids.schema.json"

    ellipsoids: LocalEllipsoids_V1_1_0_Ellipsoids
    """Ellipsoid properties."""
    domain: str
    """The domain the local ellipsoids are modelled for"""
    attribute: str
    """The attribute the local ellipsoids are modelled for"""
    schema: str = "/objects/local-ellipsoids/1.1.0/local-ellipsoids.schema.json"
    locations: Locations_V1_0_1 | None = None
    """The locations of the ellipsoids."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.ellipsoids, LocalEllipsoids_V1_1_0_Ellipsoids):
            raise ValidationFailed("self.ellipsoids is not LocalEllipsoids_V1_1_0_Ellipsoids")
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/local-ellipsoids/1.1.0/local-ellipsoids.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/local-ellipsoids/1.1.0/local-ellipsoids.schema.json" failed'
            )
        if self.locations is not None:
            if not isinstance(self.locations, Locations_V1_0_1):
                raise ValidationFailed("self.locations is not Locations_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_0_1_Ellipsoids(Ellipsoids_V1_0_1, AttributeListProperty_V1_0_1):
    """Ellipsoid properties.

    Attributes:
        values (FloatArray6_V1_0_1): Array of ellipsoids. Columns: dip_azimuth, dip, pitch, major, semi_major, minor.
        attributes (OneOfAttribute_V1_0_1, optional): Attribute data.
    """

    def __post_init__(self):
        Ellipsoids_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """Local ellipsoids.

    Attributes:
        schema (str)
        locations (Locations_V1_0_1, optional): The locations of the ellipsoids.
        ellipsoids (LocalEllipsoids_V1_0_1_Ellipsoids): Ellipsoid properties.
        domain (str): The domain the local ellipsoids are modelled for
        attribute (str): The attribute the local ellipsoids are modelled for
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/local-ellipsoids/1.0.1/local-ellipsoids.schema.json"

    ellipsoids: LocalEllipsoids_V1_0_1_Ellipsoids
    """Ellipsoid properties."""
    domain: str
    """The domain the local ellipsoids are modelled for"""
    attribute: str
    """The attribute the local ellipsoids are modelled for"""
    schema: str = "/objects/local-ellipsoids/1.0.1/local-ellipsoids.schema.json"
    locations: Locations_V1_0_1 | None = None
    """The locations of the ellipsoids."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.ellipsoids, LocalEllipsoids_V1_0_1_Ellipsoids):
            raise ValidationFailed("self.ellipsoids is not LocalEllipsoids_V1_0_1_Ellipsoids")
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/local-ellipsoids/1.0.1/local-ellipsoids.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/local-ellipsoids/1.0.1/local-ellipsoids.schema.json" failed'
            )
        if self.locations is not None:
            if not isinstance(self.locations, Locations_V1_0_1):
                raise ValidationFailed("self.locations is not Locations_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_2_0_Ellipsoids(Ellipsoids_V1_0_1, AttributeListProperty_V1_2_0):
    """Ellipsoid properties.

    Attributes:
        values (FloatArray6_V1_0_1): Array of ellipsoids. Columns: dip_azimuth, dip, pitch, major, semi_major, minor.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        Ellipsoids_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class LocalEllipsoids_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """Local ellipsoids.

    Attributes:
        schema (str)
        locations (Locations_V1_0_1, optional): The locations of the ellipsoids.
        ellipsoids (LocalEllipsoids_V1_2_0_Ellipsoids): Ellipsoid properties.
        domain (str): The domain the local ellipsoids are modelled for
        attribute (str): The attribute the local ellipsoids are modelled for
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/local-ellipsoids/1.2.0/local-ellipsoids.schema.json"

    ellipsoids: LocalEllipsoids_V1_2_0_Ellipsoids
    """Ellipsoid properties."""
    domain: str
    """The domain the local ellipsoids are modelled for"""
    attribute: str
    """The attribute the local ellipsoids are modelled for"""
    schema: str = "/objects/local-ellipsoids/1.2.0/local-ellipsoids.schema.json"
    locations: Locations_V1_0_1 | None = None
    """The locations of the ellipsoids."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.ellipsoids, LocalEllipsoids_V1_2_0_Ellipsoids):
            raise ValidationFailed("self.ellipsoids is not LocalEllipsoids_V1_2_0_Ellipsoids")
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/local-ellipsoids/1.2.0/local-ellipsoids.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/local-ellipsoids/1.2.0/local-ellipsoids.schema.json" failed'
            )
        if self.locations is not None:
            if not isinstance(self.locations, Locations_V1_0_1):
                raise ValidationFailed("self.locations is not Locations_V1_0_1")
