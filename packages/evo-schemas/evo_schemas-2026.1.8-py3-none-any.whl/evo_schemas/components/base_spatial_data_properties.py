import dataclasses
import typing

from ..elements.serialiser import ValidationFailed
from .base_object_properties import (
    BaseObjectProperties_V1_0_1,
    BaseObjectProperties_V1_0_1_Uuid,
    BaseObjectProperties_V1_1_0,
    BaseObjectProperties_V1_1_0_Uuid,
)
from .bounding_box import BoundingBox_V1_0_1
from .crs import Crs_V1_0_1, is_crs_v1_0_1
from .lineage import Lineage_V1_0_0


@dataclasses.dataclass(kw_only=True)
class BaseSpatialDataProperties_V1_1_0(BaseObjectProperties_V1_1_0):
    """Properties common to all types of Geoscience spatial data such as name, unique identifier, and bounding box

    Attributes:
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/components/base-spatial-data-properties/1.1.0/base-spatial-data-properties.schema.json"

    bounding_box: BoundingBox_V1_0_1
    """Bounding box of the spatial data."""
    coordinate_reference_system: Crs_V1_0_1
    """Coordinate system of the spatial data"""

    def __post_init__(self):
        BaseObjectProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.bounding_box, BoundingBox_V1_0_1):
            raise ValidationFailed("self.bounding_box is not BoundingBox_V1_0_1")
        if not is_crs_v1_0_1(self.coordinate_reference_system):
            raise ValidationFailed("is_crs_v1_0_1(self.coordinate_reference_system) failed")


@dataclasses.dataclass(kw_only=True)
class BaseSpatialDataProperties_V1_0_1(BaseObjectProperties_V1_0_1):
    """Properties common to all types of Geoscience spatial data such as name, unique identifier, and bounding box

    Attributes:
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/components/base-spatial-data-properties/1.0.1/base-spatial-data-properties.schema.json"

    bounding_box: BoundingBox_V1_0_1
    """Bounding box of the spatial data."""
    coordinate_reference_system: Crs_V1_0_1
    """Coordinate system of the spatial data"""

    def __post_init__(self):
        BaseObjectProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.bounding_box, BoundingBox_V1_0_1):
            raise ValidationFailed("self.bounding_box is not BoundingBox_V1_0_1")
        if not is_crs_v1_0_1(self.coordinate_reference_system):
            raise ValidationFailed("is_crs_v1_0_1(self.coordinate_reference_system) failed")
