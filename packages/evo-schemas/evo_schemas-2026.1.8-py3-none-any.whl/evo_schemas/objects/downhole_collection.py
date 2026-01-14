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
from ..components.data_table import DataTable_V1_0_1, DataTable_V1_1_0, DataTable_V1_2_0
from ..components.desurvey_method import DesurveyMethod_V1_0_0
from ..components.distance_table import (
    DistanceTable_V1_0_1,
    DistanceTable_V1_0_1_Distance,
    DistanceTable_V1_1_0,
    DistanceTable_V1_1_0_Distance,
    DistanceTable_V1_2_0,
    DistanceTable_V1_2_0_Distance,
)
from ..components.downhole_attributes import DownholeAttributes_V1_0_0, DownholeAttributes_V1_0_0_Item
from ..components.downhole_direction_vector import DownholeDirectionVector_V1_0_0
from ..components.hole_chunks import HoleChunks_V1_0_0
from ..components.hole_collars import HoleCollars_V1_0_0
from ..components.interval_table import (
    IntervalTable_V1_0_1,
    IntervalTable_V1_0_1_FromTo,
    IntervalTable_V1_1_0,
    IntervalTable_V1_1_0_FromTo,
    IntervalTable_V1_2_0,
    IntervalTable_V1_2_0_FromTo,
)
from ..components.lineage import Lineage_V1_0_0
from ..components.locations import Locations_V1_0_1
from ..components.one_of_attribute import OneOfAttribute_V1_0_1, OneOfAttribute_V1_1_0, OneOfAttribute_V1_2_0
from ..components.relative_lineation_data_table import (
    RelativeLineationDataTable_V1_0_1,
    RelativeLineationDataTable_V1_0_1_Distance,
    RelativeLineationDataTable_V1_1_0,
    RelativeLineationDataTable_V1_1_0_Distance,
    RelativeLineationDataTable_V1_2_0,
    RelativeLineationDataTable_V1_2_0_Distance,
)
from ..components.relative_planar_data_table import (
    RelativePlanarDataTable_V1_0_1,
    RelativePlanarDataTable_V1_0_1_Distance,
    RelativePlanarDataTable_V1_1_0,
    RelativePlanarDataTable_V1_1_0_Distance,
    RelativePlanarDataTable_V1_2_0,
    RelativePlanarDataTable_V1_2_0_Distance,
)
from ..elements.binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from ..elements.bool_array_1 import BoolArray1_V1_0_1
from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.unit_length import UnitLength_V1_0_1_UnitCategories


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Location_Holes(Serialiser):
    """The indices, counts, and offsets into locations of each hole. Columns: hole_index, offset, count.

    Attributes:
        data (BinaryBlob_V1_0_1): The binary data for the holes. Columns: hole_index, offset, count.
        length (int): length of array
        width (int): number of columns
        data_type (str): Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64.
    """

    data: BinaryBlob_V1_0_1
    """The binary data for the holes. Columns: hole_index, offset, count."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/uint64"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64."""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/uint64":
            raise ValidationFailed('self.data_type == "int32/uint64/uint64" failed')


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Location_Path(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """The path taken by the downhole location. Columns: distance, azimuth, dip.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Location(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """The locations of the downholes in the collection.

    Attributes:
        distances (FloatArray3_V1_0_1): The distances stored in columns final, target, current.
        holes (DownholeCollection_V1_3_0_Location_Holes): The data describing the holes.
        hole_id (CategoryData_V1_0_1): Hole IDs.
        path (DownholeCollection_V1_3_0_Location_Path): The path taken by the downhole location. Columns: distance, azimuth, dip.
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    distances: FloatArray3_V1_0_1
    """The distances stored in columns final, target, current."""
    holes: DownholeCollection_V1_3_0_Location_Holes
    """The data describing the holes."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    path: DownholeCollection_V1_3_0_Location_Path
    """The path taken by the downhole location. Columns: distance, azimuth, dip."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.distances, FloatArray3_V1_0_1):
            raise ValidationFailed("self.distances is not FloatArray3_V1_0_1")
        if not isinstance(self.holes, DownholeCollection_V1_3_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_3_0_Location_Holes")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.path, DownholeCollection_V1_3_0_Location_Path):
            raise ValidationFailed("self.path is not DownholeCollection_V1_3_0_Location_Path")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Collections_DataTable(DataTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_3_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    holes: DownholeCollection_V1_3_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_3_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_3_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Collections_DistanceTable(DistanceTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_3_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (DistanceTable_V1_2_0_Distance): The distance.
    """

    holes: DownholeCollection_V1_3_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DistanceTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_3_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_3_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Collections_IntervalTable(IntervalTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_3_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    from_to (IntervalTable_V1_2_0_FromTo): The from-to of the intervals.
    """

    holes: DownholeCollection_V1_3_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        IntervalTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_3_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_3_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Collections_RelativePlanarDataTable(RelativePlanarDataTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_3_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativePlanarDataTable_V1_2_0_Distance): The distance down the drillhole.
    relative_plane_angles (FloatArray2_V1_0_1): Planar measurements relative to the drillhole. Columns: alpha, beta
    plane_polarity (BoolArray1_V1_0_1, optional): Polarity of the planar measurements. Column: has_positive_polarity
    """

    holes: DownholeCollection_V1_3_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativePlanarDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_3_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_3_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0_Collections_RelativeLineationDataTable(RelativeLineationDataTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_3_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativeLineationDataTable_V1_2_0_Distance): The distance down the drillhole.
    relative_lineation_angles (FloatArray3_V1_0_1): Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma
    """

    holes: DownholeCollection_V1_3_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativeLineationDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_3_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_3_0_Location_Holes")


DownholeCollection_V1_3_0_Collections = (
    DownholeCollection_V1_3_0_Collections_DataTable
    | DownholeCollection_V1_3_0_Collections_DistanceTable
    | DownholeCollection_V1_3_0_Collections_IntervalTable
    | DownholeCollection_V1_3_0_Collections_RelativePlanarDataTable
    | DownholeCollection_V1_3_0_Collections_RelativeLineationDataTable
)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_0(BaseSpatialDataProperties_V1_1_0):
    """A collection of downhole locations.

    Attributes:
        schema (str)
        type (str): The type of the collection.
        distance_unit (UnitLength_V1_0_1_UnitCategories, optional): Distance unit.
        desurvey (str, optional): The desurvey algorithm.
        location (DownholeCollection_V1_3_0_Location): The locations of the downholes in the collection.
        collections (list[DownholeCollection_V1_3_0_Collections]): The collections of data associated with the downhole collection.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/downhole-collection/1.3.0/downhole-collection.schema.json"

    location: DownholeCollection_V1_3_0_Location
    """The locations of the downholes in the collection."""
    collections: list[DownholeCollection_V1_3_0_Collections]
    """The collections of data associated with the downhole collection."""
    schema: str = "/objects/downhole-collection/1.3.0/downhole-collection.schema.json"
    type: str = "downhole"
    """The type of the collection."""
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    desurvey: str | None = None
    """The desurvey algorithm."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.location, DownholeCollection_V1_3_0_Location):
            raise ValidationFailed("self.location is not DownholeCollection_V1_3_0_Location")
        if not isinstance(self.collections, list):
            raise ValidationFailed("self.collections is not a list")
        for v in self.collections:
            if not isinstance(v, DownholeCollection_V1_3_0_Collections):
                raise ValidationFailed("v is not DownholeCollection_V1_3_0_Collections")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-collection/1.3.0/downhole-collection.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-collection/1.3.0/downhole-collection.schema.json" failed'
            )
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "downhole":
            raise ValidationFailed('self.type == "downhole" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.desurvey is not None:
            if not isinstance(self.desurvey, str):
                raise ValidationFailed("self.desurvey is not str")
            if self.desurvey not in ("minimum_curvature", "balanced_tangent", "trench"):
                raise ValidationFailed('self.desurvey in ("minimum_curvature", "balanced_tangent", "trench") failed')


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Location_Holes(Serialiser):
    """The indices, counts, and offsets into locations of each hole. Columns: hole_index, offset, count.

    Attributes:
        data (BinaryBlob_V1_0_1): The binary data for the holes. Columns: hole_index, offset, count.
        length (int): length of array
        width (int): number of columns
        data_type (str): Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64.
    """

    data: BinaryBlob_V1_0_1
    """The binary data for the holes. Columns: hole_index, offset, count."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/uint64"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64."""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/uint64":
            raise ValidationFailed('self.data_type == "int32/uint64/uint64" failed')


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Location_Path(FloatArray3_V1_0_1, AttributeListProperty_V1_1_0):
    """The path taken by the downhole location. Columns: distance, azimuth, dip.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Location(Locations_V1_0_1, AttributeListProperty_V1_1_0):
    """The locations of the downholes in the collection.

    Attributes:
        distances (FloatArray3_V1_0_1): The distances stored in columns final, target, current.
        holes (DownholeCollection_V1_1_0_Location_Holes): The data describing the holes.
        hole_id (CategoryData_V1_0_1): Hole IDs.
        path (DownholeCollection_V1_1_0_Location_Path): The path taken by the downhole location. Columns: distance, azimuth, dip.
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    distances: FloatArray3_V1_0_1
    """The distances stored in columns final, target, current."""
    holes: DownholeCollection_V1_1_0_Location_Holes
    """The data describing the holes."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    path: DownholeCollection_V1_1_0_Location_Path
    """The path taken by the downhole location. Columns: distance, azimuth, dip."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not isinstance(self.distances, FloatArray3_V1_0_1):
            raise ValidationFailed("self.distances is not FloatArray3_V1_0_1")
        if not isinstance(self.holes, DownholeCollection_V1_1_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_1_0_Location_Holes")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.path, DownholeCollection_V1_1_0_Location_Path):
            raise ValidationFailed("self.path is not DownholeCollection_V1_1_0_Location_Path")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Collections_DataTable(DataTable_V1_1_0):
    """Attributes:

    holes (DownholeCollection_V1_1_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    holes: DownholeCollection_V1_1_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DataTable_V1_1_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_1_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_1_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Collections_DistanceTable(DistanceTable_V1_1_0):
    """Attributes:

    holes (DownholeCollection_V1_1_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (DistanceTable_V1_1_0_Distance): The distance.
    """

    holes: DownholeCollection_V1_1_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DistanceTable_V1_1_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_1_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_1_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Collections_IntervalTable(IntervalTable_V1_1_0):
    """Attributes:

    holes (DownholeCollection_V1_1_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    from_to (IntervalTable_V1_1_0_FromTo): The from-to of the intervals.
    """

    holes: DownholeCollection_V1_1_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        IntervalTable_V1_1_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_1_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_1_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Collections_RelativePlanarDataTable(RelativePlanarDataTable_V1_1_0):
    """Attributes:

    holes (DownholeCollection_V1_1_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativePlanarDataTable_V1_1_0_Distance): The distance down the drillhole.
    relative_plane_angles (FloatArray2_V1_0_1): Planar measurements relative to the drillhole. Columns: alpha, beta
    plane_polarity (BoolArray1_V1_0_1, optional): Polarity of the planar measurements. Column: has_positive_polarity
    """

    holes: DownholeCollection_V1_1_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativePlanarDataTable_V1_1_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_1_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_1_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0_Collections_RelativeLineationDataTable(RelativeLineationDataTable_V1_1_0):
    """Attributes:

    holes (DownholeCollection_V1_1_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativeLineationDataTable_V1_1_0_Distance): The distance down the drillhole.
    relative_lineation_angles (FloatArray3_V1_0_1): Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma
    """

    holes: DownholeCollection_V1_1_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativeLineationDataTable_V1_1_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_1_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_1_0_Location_Holes")


DownholeCollection_V1_1_0_Collections = (
    DownholeCollection_V1_1_0_Collections_DataTable
    | DownholeCollection_V1_1_0_Collections_DistanceTable
    | DownholeCollection_V1_1_0_Collections_IntervalTable
    | DownholeCollection_V1_1_0_Collections_RelativePlanarDataTable
    | DownholeCollection_V1_1_0_Collections_RelativeLineationDataTable
)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A collection of downhole locations.

    Attributes:
        schema (str)
        type (str): The type of the collection.
        distance_unit (UnitLength_V1_0_1_UnitCategories, optional): Distance unit.
        desurvey (str, optional): The desurvey algorithm.
        location (DownholeCollection_V1_1_0_Location): The locations of the downholes in the collection.
        collections (list[DownholeCollection_V1_1_0_Collections]): The collections of data associated with the downhole collection.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/downhole-collection/1.1.0/downhole-collection.schema.json"

    location: DownholeCollection_V1_1_0_Location
    """The locations of the downholes in the collection."""
    collections: list[DownholeCollection_V1_1_0_Collections]
    """The collections of data associated with the downhole collection."""
    schema: str = "/objects/downhole-collection/1.1.0/downhole-collection.schema.json"
    type: str = "downhole"
    """The type of the collection."""
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    desurvey: str | None = None
    """The desurvey algorithm."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.location, DownholeCollection_V1_1_0_Location):
            raise ValidationFailed("self.location is not DownholeCollection_V1_1_0_Location")
        if not isinstance(self.collections, list):
            raise ValidationFailed("self.collections is not a list")
        for v in self.collections:
            if not isinstance(v, DownholeCollection_V1_1_0_Collections):
                raise ValidationFailed("v is not DownholeCollection_V1_1_0_Collections")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-collection/1.1.0/downhole-collection.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-collection/1.1.0/downhole-collection.schema.json" failed'
            )
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "downhole":
            raise ValidationFailed('self.type == "downhole" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.desurvey is not None:
            if not isinstance(self.desurvey, str):
                raise ValidationFailed("self.desurvey is not str")
            if self.desurvey not in ("minimum_curvature", "balanced_tangent", "trench"):
                raise ValidationFailed('self.desurvey in ("minimum_curvature", "balanced_tangent", "trench") failed')


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_1_Location(HoleCollars_V1_0_0):
    """The locations of the downholes in the collection.

    Attributes:
        hole_id (CategoryData_V1_0_1): Hole IDs.
        path (DownholeDirectionVector_V1_0_0): The path taken by the downhole location. Columns: distance, azimuth, dip.
        distances (FloatArray3_V1_0_1): The depth values for each drillhole. Columns: final, target, current.
        holes (HoleChunks_V1_0_0): The data describing the hole paths.
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    path: DownholeDirectionVector_V1_0_0
    """The path taken by the downhole location. Columns: distance, azimuth, dip."""

    def __post_init__(self):
        HoleCollars_V1_0_0.__post_init__(self)
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.path, DownholeDirectionVector_V1_0_0):
            raise ValidationFailed("self.path is not DownholeDirectionVector_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_3_1(BaseSpatialDataProperties_V1_1_0):
    """A collection of downhole locations.

    Attributes:
        schema (str)
        type (str): The type of the collection.
        distance_unit (UnitLength_V1_0_1_UnitCategories, optional): Distance unit.
        desurvey (DesurveyMethod_V1_0_0, optional): The desurvey method used to calculate the drillhole geometry.
        location (DownholeCollection_V1_3_1_Location): The locations of the downholes in the collection.
        collections (DownholeAttributes_V1_0_0): The collections of data associated with the downhole collection.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/downhole-collection/1.3.1/downhole-collection.schema.json"

    location: DownholeCollection_V1_3_1_Location
    """The locations of the downholes in the collection."""
    collections: DownholeAttributes_V1_0_0
    """The collections of data associated with the downhole collection."""
    schema: str = "/objects/downhole-collection/1.3.1/downhole-collection.schema.json"
    type: str = "downhole"
    """The type of the collection."""
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    desurvey: DesurveyMethod_V1_0_0 | None = None
    """The desurvey method used to calculate the drillhole geometry."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.location, DownholeCollection_V1_3_1_Location):
            raise ValidationFailed("self.location is not DownholeCollection_V1_3_1_Location")
        if not isinstance(self.collections, list):
            raise ValidationFailed("self.collections is not a list")
        for v in self.collections:
            if not isinstance(v, DownholeAttributes_V1_0_0_Item):
                raise ValidationFailed("v is not DownholeAttributes_V1_0_0_Item")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-collection/1.3.1/downhole-collection.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-collection/1.3.1/downhole-collection.schema.json" failed'
            )
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "downhole":
            raise ValidationFailed('self.type == "downhole" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.desurvey is not None:
            if not isinstance(self.desurvey, DesurveyMethod_V1_0_0):
                raise ValidationFailed("self.desurvey is not DesurveyMethod_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Location_Holes(Serialiser):
    """The indices, counts, and offsets into locations of each hole. Columns: hole_index, offset, count.

    Attributes:
        data (BinaryBlob_V1_0_1): The binary data for the holes. Columns: hole_index, offset, count.
        length (int): length of array
        width (int): number of columns
        data_type (str): Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64.
    """

    data: BinaryBlob_V1_0_1
    """The binary data for the holes. Columns: hole_index, offset, count."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/uint64"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64."""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/uint64":
            raise ValidationFailed('self.data_type == "int32/uint64/uint64" failed')


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Location_Path(FloatArray3_V1_0_1, AttributeListProperty_V1_0_1):
    """The path taken by the downhole location. Columns: distance, azimuth, dip.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
        attributes (OneOfAttribute_V1_0_1, optional): Attribute data.
    """

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Location(Locations_V1_0_1, AttributeListProperty_V1_0_1):
    """The locations of the downholes in the collection.

    Attributes:
        distances (FloatArray3_V1_0_1): The distances stored in columns final, target, current.
        holes (DownholeCollection_V1_0_1_Location_Holes): The data describing the holes.
        hole_id (CategoryData_V1_0_1): Hole IDs.
        path (DownholeCollection_V1_0_1_Location_Path): The path taken by the downhole location. Columns: distance, azimuth, dip.
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_0_1, optional): Attribute data.
    """

    distances: FloatArray3_V1_0_1
    """The distances stored in columns final, target, current."""
    holes: DownholeCollection_V1_0_1_Location_Holes
    """The data describing the holes."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    path: DownholeCollection_V1_0_1_Location_Path
    """The path taken by the downhole location. Columns: distance, azimuth, dip."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_0_1.__post_init__(self)
        if not isinstance(self.distances, FloatArray3_V1_0_1):
            raise ValidationFailed("self.distances is not FloatArray3_V1_0_1")
        if not isinstance(self.holes, DownholeCollection_V1_0_1_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_0_1_Location_Holes")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.path, DownholeCollection_V1_0_1_Location_Path):
            raise ValidationFailed("self.path is not DownholeCollection_V1_0_1_Location_Path")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Collections_DataTable(DataTable_V1_0_1):
    """Attributes:

    holes (DownholeCollection_V1_0_1_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    attributes (OneOfAttribute_V1_0_1, optional): Attribute data.
    """

    holes: DownholeCollection_V1_0_1_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DataTable_V1_0_1.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_0_1_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_0_1_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Collections_DistanceTable(DistanceTable_V1_0_1):
    """Attributes:

    holes (DownholeCollection_V1_0_1_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (DistanceTable_V1_0_1_Distance): The distance.
    """

    holes: DownholeCollection_V1_0_1_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DistanceTable_V1_0_1.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_0_1_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_0_1_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Collections_IntervalTable(IntervalTable_V1_0_1):
    """Attributes:

    holes (DownholeCollection_V1_0_1_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    from_to (IntervalTable_V1_0_1_FromTo): The from-to of the intervals.
    """

    holes: DownholeCollection_V1_0_1_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        IntervalTable_V1_0_1.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_0_1_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_0_1_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Collections_RelativePlanarDataTable(RelativePlanarDataTable_V1_0_1):
    """Attributes:

    holes (DownholeCollection_V1_0_1_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativePlanarDataTable_V1_0_1_Distance): The distance down the drillhole.
    relative_plane_angles (FloatArray2_V1_0_1): Planar measurements relative to the drillhole. Columns: alpha, beta
    plane_polarity (BoolArray1_V1_0_1, optional): Polarity of the planar measurements. Column: has_positive_polarity
    """

    holes: DownholeCollection_V1_0_1_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativePlanarDataTable_V1_0_1.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_0_1_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_0_1_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1_Collections_RelativeLineationDataTable(RelativeLineationDataTable_V1_0_1):
    """Attributes:

    holes (DownholeCollection_V1_0_1_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativeLineationDataTable_V1_0_1_Distance): The distance down the drillhole.
    relative_lineation_angles (FloatArray3_V1_0_1): Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma
    """

    holes: DownholeCollection_V1_0_1_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativeLineationDataTable_V1_0_1.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_0_1_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_0_1_Location_Holes")


DownholeCollection_V1_0_1_Collections = (
    DownholeCollection_V1_0_1_Collections_DataTable
    | DownholeCollection_V1_0_1_Collections_DistanceTable
    | DownholeCollection_V1_0_1_Collections_IntervalTable
    | DownholeCollection_V1_0_1_Collections_RelativePlanarDataTable
    | DownholeCollection_V1_0_1_Collections_RelativeLineationDataTable
)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A collection of downhole locations.

    Attributes:
        schema (str)
        type (str): The type of the collection.
        distance_unit (UnitLength_V1_0_1_UnitCategories, optional): Distance unit.
        desurvey (str, optional): The desurvey algorithm.
        location (DownholeCollection_V1_0_1_Location): The locations of the downholes in the collection.
        collections (list[DownholeCollection_V1_0_1_Collections]): The collections of data associated with the downhole collection.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/downhole-collection/1.0.1/downhole-collection.schema.json"

    location: DownholeCollection_V1_0_1_Location
    """The locations of the downholes in the collection."""
    collections: list[DownholeCollection_V1_0_1_Collections]
    """The collections of data associated with the downhole collection."""
    schema: str = "/objects/downhole-collection/1.0.1/downhole-collection.schema.json"
    type: str = "downhole"
    """The type of the collection."""
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    desurvey: str | None = None
    """The desurvey algorithm."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.location, DownholeCollection_V1_0_1_Location):
            raise ValidationFailed("self.location is not DownholeCollection_V1_0_1_Location")
        if not isinstance(self.collections, list):
            raise ValidationFailed("self.collections is not a list")
        for v in self.collections:
            if not isinstance(v, DownholeCollection_V1_0_1_Collections):
                raise ValidationFailed("v is not DownholeCollection_V1_0_1_Collections")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-collection/1.0.1/downhole-collection.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-collection/1.0.1/downhole-collection.schema.json" failed'
            )
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "downhole":
            raise ValidationFailed('self.type == "downhole" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.desurvey is not None:
            if not isinstance(self.desurvey, str):
                raise ValidationFailed("self.desurvey is not str")
            if self.desurvey not in ("minimum_curvature", "balanced_tangent", "trench"):
                raise ValidationFailed('self.desurvey in ("minimum_curvature", "balanced_tangent", "trench") failed')


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Location_Holes(Serialiser):
    """The indices, counts, and offsets into locations of each hole. Columns: hole_index, offset, count.

    Attributes:
        data (BinaryBlob_V1_0_1): The binary data for the holes. Columns: hole_index, offset, count.
        length (int): length of array
        width (int): number of columns
        data_type (str): Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64.
    """

    data: BinaryBlob_V1_0_1
    """The binary data for the holes. Columns: hole_index, offset, count."""
    length: int = 0
    """length of array"""
    width: int = 3
    """number of columns"""
    data_type: str = "int32/uint64/uint64"
    """Data type for the columns. 1st column is of type int32, 2nd is uint64 and 3rd is uint64."""

    def __post_init__(self):
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 3:
            raise ValidationFailed("self.width == 3 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "int32/uint64/uint64":
            raise ValidationFailed('self.data_type == "int32/uint64/uint64" failed')


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Location_Path(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """The path taken by the downhole location. Columns: distance, azimuth, dip.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Location(Locations_V1_0_1, AttributeListProperty_V1_2_0):
    """The locations of the downholes in the collection.

    Attributes:
        distances (FloatArray3_V1_0_1): The distances stored in columns final, target, current.
        holes (DownholeCollection_V1_2_0_Location_Holes): The data describing the holes.
        hole_id (CategoryData_V1_0_1): Hole IDs.
        path (DownholeCollection_V1_2_0_Location_Path): The path taken by the downhole location. Columns: distance, azimuth, dip.
        coordinates (FloatArray3_V1_0_1): Coordinates. Columns: x, y, z.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    distances: FloatArray3_V1_0_1
    """The distances stored in columns final, target, current."""
    holes: DownholeCollection_V1_2_0_Location_Holes
    """The data describing the holes."""
    hole_id: CategoryData_V1_0_1
    """Hole IDs."""
    path: DownholeCollection_V1_2_0_Location_Path
    """The path taken by the downhole location. Columns: distance, azimuth, dip."""

    def __post_init__(self):
        Locations_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.distances, FloatArray3_V1_0_1):
            raise ValidationFailed("self.distances is not FloatArray3_V1_0_1")
        if not isinstance(self.holes, DownholeCollection_V1_2_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_2_0_Location_Holes")
        if not isinstance(self.hole_id, CategoryData_V1_0_1):
            raise ValidationFailed("self.hole_id is not CategoryData_V1_0_1")
        if not isinstance(self.path, DownholeCollection_V1_2_0_Location_Path):
            raise ValidationFailed("self.path is not DownholeCollection_V1_2_0_Location_Path")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Collections_DataTable(DataTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_2_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    holes: DownholeCollection_V1_2_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_2_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_2_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Collections_DistanceTable(DistanceTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_2_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (DistanceTable_V1_2_0_Distance): The distance.
    """

    holes: DownholeCollection_V1_2_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        DistanceTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_2_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_2_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Collections_IntervalTable(IntervalTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_2_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    from_to (IntervalTable_V1_2_0_FromTo): The from-to of the intervals.
    """

    holes: DownholeCollection_V1_2_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        IntervalTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_2_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_2_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Collections_RelativePlanarDataTable(RelativePlanarDataTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_2_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativePlanarDataTable_V1_2_0_Distance): The distance down the drillhole.
    relative_plane_angles (FloatArray2_V1_0_1): Planar measurements relative to the drillhole. Columns: alpha, beta
    plane_polarity (BoolArray1_V1_0_1, optional): Polarity of the planar measurements. Column: has_positive_polarity
    """

    holes: DownholeCollection_V1_2_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativePlanarDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_2_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_2_0_Location_Holes")


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0_Collections_RelativeLineationDataTable(RelativeLineationDataTable_V1_2_0):
    """Attributes:

    holes (DownholeCollection_V1_2_0_Location_Holes): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativeLineationDataTable_V1_2_0_Distance): The distance down the drillhole.
    relative_lineation_angles (FloatArray3_V1_0_1): Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma
    """

    holes: DownholeCollection_V1_2_0_Location_Holes
    """The data describing the holes."""

    def __post_init__(self):
        RelativeLineationDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, DownholeCollection_V1_2_0_Location_Holes):
            raise ValidationFailed("self.holes is not DownholeCollection_V1_2_0_Location_Holes")


DownholeCollection_V1_2_0_Collections = (
    DownholeCollection_V1_2_0_Collections_DataTable
    | DownholeCollection_V1_2_0_Collections_DistanceTable
    | DownholeCollection_V1_2_0_Collections_IntervalTable
    | DownholeCollection_V1_2_0_Collections_RelativePlanarDataTable
    | DownholeCollection_V1_2_0_Collections_RelativeLineationDataTable
)


@dataclasses.dataclass(kw_only=True)
class DownholeCollection_V1_2_0(BaseSpatialDataProperties_V1_0_1):
    """A collection of downhole locations.

    Attributes:
        schema (str)
        type (str): The type of the collection.
        distance_unit (UnitLength_V1_0_1_UnitCategories, optional): Distance unit.
        desurvey (str, optional): The desurvey algorithm.
        location (DownholeCollection_V1_2_0_Location): The locations of the downholes in the collection.
        collections (list[DownholeCollection_V1_2_0_Collections]): The collections of data associated with the downhole collection.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/downhole-collection/1.2.0/downhole-collection.schema.json"

    location: DownholeCollection_V1_2_0_Location
    """The locations of the downholes in the collection."""
    collections: list[DownholeCollection_V1_2_0_Collections]
    """The collections of data associated with the downhole collection."""
    schema: str = "/objects/downhole-collection/1.2.0/downhole-collection.schema.json"
    type: str = "downhole"
    """The type of the collection."""
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    desurvey: str | None = None
    """The desurvey algorithm."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.location, DownholeCollection_V1_2_0_Location):
            raise ValidationFailed("self.location is not DownholeCollection_V1_2_0_Location")
        if not isinstance(self.collections, list):
            raise ValidationFailed("self.collections is not a list")
        for v in self.collections:
            if not isinstance(v, DownholeCollection_V1_2_0_Collections):
                raise ValidationFailed("v is not DownholeCollection_V1_2_0_Collections")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/downhole-collection/1.2.0/downhole-collection.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/downhole-collection/1.2.0/downhole-collection.schema.json" failed'
            )
        if not isinstance(self.type, str):
            raise ValidationFailed("self.type is not str")
        if not self.type == "downhole":
            raise ValidationFailed('self.type == "downhole" failed')
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.desurvey is not None:
            if not isinstance(self.desurvey, str):
                raise ValidationFailed("self.desurvey is not str")
            if self.desurvey not in ("minimum_curvature", "balanced_tangent", "trench"):
                raise ValidationFailed('self.desurvey in ("minimum_curvature", "balanced_tangent", "trench") failed')
