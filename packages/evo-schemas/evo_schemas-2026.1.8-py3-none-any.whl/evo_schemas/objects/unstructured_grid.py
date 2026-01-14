import dataclasses
import typing

from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.lineage import Lineage_V1_0_0
from ..components.unstructured_grid_geometry import (
    UnstructuredGridGeometry_V1_0_1,
    UnstructuredGridGeometry_V1_1_0,
    UnstructuredGridGeometry_V1_2_0,
)
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class UnstructuredGrid_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """An unstructured grid.

    Attributes:
        schema (str)
        geometry (UnstructuredGridGeometry_V1_2_0): The geometry information of the unstructured grid.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/unstructured-grid/1.3.0/unstructured-grid.schema.json"

    geometry: UnstructuredGridGeometry_V1_2_0
    """The geometry information of the unstructured grid."""
    schema: str = "/objects/unstructured-grid/1.3.0/unstructured-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.geometry, UnstructuredGridGeometry_V1_2_0):
            raise ValidationFailed("self.geometry is not UnstructuredGridGeometry_V1_2_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-grid/1.3.0/unstructured-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-grid/1.3.0/unstructured-grid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class UnstructuredGrid_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """An unstructured grid.

    Attributes:
        schema (str)
        geometry (UnstructuredGridGeometry_V1_1_0): The geometry information of the unstructured grid.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/unstructured-grid/1.1.0/unstructured-grid.schema.json"

    geometry: UnstructuredGridGeometry_V1_1_0
    """The geometry information of the unstructured grid."""
    schema: str = "/objects/unstructured-grid/1.1.0/unstructured-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.geometry, UnstructuredGridGeometry_V1_1_0):
            raise ValidationFailed("self.geometry is not UnstructuredGridGeometry_V1_1_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-grid/1.1.0/unstructured-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-grid/1.1.0/unstructured-grid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class UnstructuredGrid_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """An unstructured grid.

    Attributes:
        schema (str)
        geometry (UnstructuredGridGeometry_V1_0_1): The geometry information of the unstructured grid.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/unstructured-grid/1.0.1/unstructured-grid.schema.json"

    geometry: UnstructuredGridGeometry_V1_0_1
    """The geometry information of the unstructured grid."""
    schema: str = "/objects/unstructured-grid/1.0.1/unstructured-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.geometry, UnstructuredGridGeometry_V1_0_1):
            raise ValidationFailed("self.geometry is not UnstructuredGridGeometry_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-grid/1.0.1/unstructured-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-grid/1.0.1/unstructured-grid.schema.json" failed'
            )


@dataclasses.dataclass(kw_only=True)
class UnstructuredGrid_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """An unstructured grid.

    Attributes:
        schema (str)
        geometry (UnstructuredGridGeometry_V1_2_0): The geometry information of the unstructured grid.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/unstructured-grid/1.2.0/unstructured-grid.schema.json"

    geometry: UnstructuredGridGeometry_V1_2_0
    """The geometry information of the unstructured grid."""
    schema: str = "/objects/unstructured-grid/1.2.0/unstructured-grid.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.geometry, UnstructuredGridGeometry_V1_2_0):
            raise ValidationFailed("self.geometry is not UnstructuredGridGeometry_V1_2_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/unstructured-grid/1.2.0/unstructured-grid.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/unstructured-grid/1.2.0/unstructured-grid.schema.json" failed'
            )
