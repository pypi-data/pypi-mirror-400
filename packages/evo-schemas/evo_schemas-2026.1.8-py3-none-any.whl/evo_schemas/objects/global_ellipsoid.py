import dataclasses
import typing

from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.ellipsoid import (
    Ellipsoid_V1_0_1,
    Ellipsoid_V1_0_1_EllipsoidRanges,
    Ellipsoid_V1_1_0,
    Ellipsoid_V1_1_0_EllipsoidRanges,
)
from ..components.lineage import Lineage_V1_0_0
from ..components.rotation import Rotation_V1_0_1, Rotation_V1_1_0
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class GlobalEllipsoid_V1_1_0(BaseSpatialDataProperties_V1_0_1, Ellipsoid_V1_1_0):
    """Global ellipsoid.

    Attributes:
        schema (str)
        domain (str): The domain the ellipsoid is modelled for
        attribute (str): The attribute the ellipsoid is modelled for
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        ellipsoid_ranges (Ellipsoid_V1_1_0_EllipsoidRanges): An ellipsoid as defined by three lengths, for the major, semi-major and minor axes rotated in space as defined by the rotation.
        rotation (Rotation_V1_1_0): Rotation of the ellipsoid
    """

    SCHEMA_ID = "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json"

    domain: str
    """The domain the ellipsoid is modelled for"""
    attribute: str
    """The attribute the ellipsoid is modelled for"""
    schema: str = "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        Ellipsoid_V1_1_0.__post_init__(self)
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/global-ellipsoid/1.1.0/global-ellipsoid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class GlobalEllipsoid_V1_0_1(BaseSpatialDataProperties_V1_0_1, Ellipsoid_V1_0_1):
    """Global ellipsoid.

    Attributes:
        schema (str)
        domain (str): The domain the ellipsoid is modelled for
        attribute (str): The attribute the ellipsoid is modelled for
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        ellipsoid_ranges (Ellipsoid_V1_0_1_EllipsoidRanges): An ellipsoid as defined by three lengths, for the major, semi-major and minor axes rotated in space as defined by the rotation.
        rotation (Rotation_V1_0_1): Rotation of the ellipsoid
    """

    SCHEMA_ID = "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json"

    domain: str
    """The domain the ellipsoid is modelled for"""
    attribute: str
    """The attribute the ellipsoid is modelled for"""
    schema: str = "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        Ellipsoid_V1_0_1.__post_init__(self)
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/global-ellipsoid/1.0.1/global-ellipsoid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class GlobalEllipsoid_V1_2_0(BaseSpatialDataProperties_V1_1_0, Ellipsoid_V1_1_0):
    """Global ellipsoid.

    Attributes:
        schema (str)
        domain (str): The domain the ellipsoid is modelled for
        attribute (str): The attribute the ellipsoid is modelled for
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
        ellipsoid_ranges (Ellipsoid_V1_1_0_EllipsoidRanges): An ellipsoid as defined by three lengths, for the major, semi-major and minor axes rotated in space as defined by the rotation.
        rotation (Rotation_V1_1_0): Rotation of the ellipsoid
    """

    SCHEMA_ID = "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json"

    domain: str
    """The domain the ellipsoid is modelled for"""
    attribute: str
    """The attribute the ellipsoid is modelled for"""
    schema: str = "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        Ellipsoid_V1_1_0.__post_init__(self)
        if not isinstance(self.domain, str):
            raise ValidationFailed("self.domain is not str")
        if not isinstance(self.attribute, str):
            raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/global-ellipsoid/1.2.0/global-ellipsoid.schema.json" failed'
            )
