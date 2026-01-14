import dataclasses
import typing

from ..components.attribute_list_property import AttributeListProperty_V1_1_0, AttributeListProperty_V1_2_0
from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.lineage import Lineage_V1_0_0
from ..components.one_of_attribute import OneOfAttribute_V1_1_0, OneOfAttribute_V1_2_0
from ..components.segments import Segments_V1_0_1, Segments_V1_1_0, Segments_V1_2_0
from ..elements.index_array_2 import IndexArray2_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class LineSegments_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """List of line segments

    Attributes:
        schema (str)
        segments (Segments_V1_1_0): The line segments.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/line-segments/1.1.0/line-segments.schema.json"

    segments: Segments_V1_1_0
    """The line segments."""
    schema: str = "/objects/line-segments/1.1.0/line-segments.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.segments, Segments_V1_1_0):
            raise ValidationFailed("self.segments is not Segments_V1_1_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/line-segments/1.1.0/line-segments.schema.json":
            raise ValidationFailed('self.schema == "/objects/line-segments/1.1.0/line-segments.schema.json" failed')


@dataclasses.dataclass(kw_only=True)
class LineSegments_V2_1_0_Parts(AttributeListProperty_V1_2_0):
    """A structure defining chunks the line collection is composed of.

    Attributes are associated with each chunk.
    Attributes:
        chunks (IndexArray2_V1_0_1): A list of chunks of segments.
    A chunk consists of consecutive segments, defined by the index of the first segment and the number of segments.
    Chunks do not have to include all segments, and chunks can overlap.
    Columns: offset, count
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    chunks: IndexArray2_V1_0_1
    """A list of chunks of segments.
     
    A chunk consists of consecutive segments, defined by the index of the first segment and the number of segments.
    Chunks do not have to include all segments, and chunks can overlap.
    Columns: offset, count
    """

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class LineSegments_V2_1_0(BaseSpatialDataProperties_V1_0_1):
    """A collection of lines composed of straight segments.

    Optionally, consecutive chunks of segments can be grouped and attributed.
    Attributes:
        schema (str)
        segments (Segments_V1_2_0): Vertices and segments.
        parts (LineSegments_V2_1_0_Parts, optional): An optional structure defining segment chunks the line collection is composed of.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/line-segments/2.1.0/line-segments.schema.json"

    segments: Segments_V1_2_0
    """Vertices and segments."""
    schema: str = "/objects/line-segments/2.1.0/line-segments.schema.json"
    parts: LineSegments_V2_1_0_Parts | None = None
    """An optional structure defining segment chunks the line collection is composed of."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.segments, Segments_V1_2_0):
            raise ValidationFailed("self.segments is not Segments_V1_2_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/line-segments/2.1.0/line-segments.schema.json":
            raise ValidationFailed('self.schema == "/objects/line-segments/2.1.0/line-segments.schema.json" failed')
        if self.parts is not None:
            if not isinstance(self.parts, LineSegments_V2_1_0_Parts):
                raise ValidationFailed("self.parts is not LineSegments_V2_1_0_Parts")


@dataclasses.dataclass(kw_only=True)
class LineSegments_V2_2_0_Parts(AttributeListProperty_V1_2_0):
    """A structure defining chunks the line collection is composed of.

    Attributes are associated with each chunk.
    Attributes:
        chunks (IndexArray2_V1_0_1): A list of chunks of segments.
    A chunk consists of consecutive segments, defined by the index of the first segment and the number of segments.
    Chunks do not have to include all segments, and chunks can overlap.
    Columns: offset, count
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    chunks: IndexArray2_V1_0_1
    """A list of chunks of segments.
     
    A chunk consists of consecutive segments, defined by the index of the first segment and the number of segments.
    Chunks do not have to include all segments, and chunks can overlap.
    Columns: offset, count
    """

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class LineSegments_V2_2_0(BaseSpatialDataProperties_V1_1_0):
    """A collection of lines composed of straight segments.

    Optionally, consecutive chunks of segments can be grouped and attributed.
    Attributes:
        schema (str)
        segments (Segments_V1_2_0): Vertices and segments.
        parts (LineSegments_V2_2_0_Parts, optional): An optional structure defining segment chunks the line collection is composed of.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/line-segments/2.2.0/line-segments.schema.json"

    segments: Segments_V1_2_0
    """Vertices and segments."""
    schema: str = "/objects/line-segments/2.2.0/line-segments.schema.json"
    parts: LineSegments_V2_2_0_Parts | None = None
    """An optional structure defining segment chunks the line collection is composed of."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.segments, Segments_V1_2_0):
            raise ValidationFailed("self.segments is not Segments_V1_2_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/line-segments/2.2.0/line-segments.schema.json":
            raise ValidationFailed('self.schema == "/objects/line-segments/2.2.0/line-segments.schema.json" failed')
        if self.parts is not None:
            if not isinstance(self.parts, LineSegments_V2_2_0_Parts):
                raise ValidationFailed("self.parts is not LineSegments_V2_2_0_Parts")


@dataclasses.dataclass(kw_only=True)
class LineSegments_V2_0_0_Parts(AttributeListProperty_V1_1_0):
    """A structure defining chunks the line collection is composed of.

    Attributes are associated with each chunk.
    Attributes:
        chunks (IndexArray2_V1_0_1): A list of chunks of segments.
    A chunk consists of consecutive segments, defined by the index of the first segment and the number of segments.
    Chunks do not have to include all segments, and chunks can overlap.
    Columns: offset, count
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    chunks: IndexArray2_V1_0_1
    """A list of chunks of segments.
     
    A chunk consists of consecutive segments, defined by the index of the first segment and the number of segments.
    Chunks do not have to include all segments, and chunks can overlap.
    Columns: offset, count
    """

    def __post_init__(self):
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class LineSegments_V2_0_0(BaseSpatialDataProperties_V1_0_1):
    """A collection of lines composed of straight segments.

    Optionally, consecutive chunks of segments can be grouped and attributed.
    Attributes:
        schema (str)
        segments (Segments_V1_1_0): Vertices and segments.
        parts (LineSegments_V2_0_0_Parts, optional): An optional structure defining segment chunks the line collection is composed of.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/line-segments/2.0.0/line-segments.schema.json"

    segments: Segments_V1_1_0
    """Vertices and segments."""
    schema: str = "/objects/line-segments/2.0.0/line-segments.schema.json"
    parts: LineSegments_V2_0_0_Parts | None = None
    """An optional structure defining segment chunks the line collection is composed of."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.segments, Segments_V1_1_0):
            raise ValidationFailed("self.segments is not Segments_V1_1_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/line-segments/2.0.0/line-segments.schema.json":
            raise ValidationFailed('self.schema == "/objects/line-segments/2.0.0/line-segments.schema.json" failed')
        if self.parts is not None:
            if not isinstance(self.parts, LineSegments_V2_0_0_Parts):
                raise ValidationFailed("self.parts is not LineSegments_V2_0_0_Parts")


@dataclasses.dataclass(kw_only=True)
class LineSegments_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """List of line segments

    Attributes:
        schema (str)
        segments (Segments_V1_0_1): The line segments.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/line-segments/1.0.1/line-segments.schema.json"

    segments: Segments_V1_0_1
    """The line segments."""
    schema: str = "/objects/line-segments/1.0.1/line-segments.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.segments, Segments_V1_0_1):
            raise ValidationFailed("self.segments is not Segments_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/line-segments/1.0.1/line-segments.schema.json":
            raise ValidationFailed('self.schema == "/objects/line-segments/1.0.1/line-segments.schema.json" failed')
