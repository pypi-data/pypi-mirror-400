import dataclasses

from ..elements.binary_blob import BinaryBlob_V1_0_1
from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.index_array_1 import IndexArray1_V1_0_1
from ..elements.index_array_2 import IndexArray2_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_list_property import AttributeListProperty_V1_2_0
from .one_of_attribute import OneOfAttribute_V1_2_0


@dataclasses.dataclass(kw_only=True)
class EmbeddedLineGeometry_V1_0_0_Vertices(FloatArray2_V1_0_1, AttributeListProperty_V1_2_0):
    """Vertex coordinates in 2D space. Columns: u, v.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        FloatArray2_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class EmbeddedLineGeometry_V1_0_0_Chunks(IndexArray2_V1_0_1, AttributeListProperty_V1_2_0):
    """A tuple defining the first index and the length of a chunk of vertices, forming a polyline/polygon.

    If indices is defined, the chunk refers to a segment of the indices array.
    Otherwise, the chunk refers to a segment of the vertices array.
    Chunks can overlap.
    Columns: offset, count
    Attributes:
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        width (int): number of columns
        data_type (str): data type
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    def __post_init__(self):
        IndexArray2_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)


@dataclasses.dataclass(kw_only=True)
class EmbeddedLineGeometry_V1_0_0(Serialiser):
    """A set of polylines composed of straight line segments.

    Attributes:
        vertices (EmbeddedLineGeometry_V1_0_0_Vertices): Vertex coordinates in 2D space. Columns: u, v.
        chunks (EmbeddedLineGeometry_V1_0_0_Chunks): A tuple defining the first index and the length of a chunk of vertices, forming a polyline/polygon.
    If indices is defined, the chunk refers to a segment of the indices array.
    Otherwise, the chunk refers to a segment of the vertices array.
    Chunks can overlap.
    Columns: offset, count
        indices (IndexArray1_V1_0_1, optional): An optional index array into the vertices.
    This is used to define chunks if the vertices list do not contain contiguous chunks.
    """

    SCHEMA_ID = "/components/embedded-line-geometry/1.0.0/embedded-line-geometry.schema.json"

    vertices: EmbeddedLineGeometry_V1_0_0_Vertices
    """Vertex coordinates in 2D space. Columns: u, v."""
    chunks: EmbeddedLineGeometry_V1_0_0_Chunks
    """A tuple defining the first index and the length of a chunk of vertices, forming a polyline/polygon.
     
    If indices is defined, the chunk refers to a segment of the indices array.
    Otherwise, the chunk refers to a segment of the vertices array.
    Chunks can overlap.
    Columns: offset, count
    """
    indices: IndexArray1_V1_0_1 | None = None
    """An optional index array into the vertices.
     
    This is used to define chunks if the vertices list do not contain contiguous chunks.
    """

    def __post_init__(self):
        if not isinstance(self.vertices, EmbeddedLineGeometry_V1_0_0_Vertices):
            raise ValidationFailed("self.vertices is not EmbeddedLineGeometry_V1_0_0_Vertices")
        if not isinstance(self.chunks, EmbeddedLineGeometry_V1_0_0_Chunks):
            raise ValidationFailed("self.chunks is not EmbeddedLineGeometry_V1_0_0_Chunks")
        if self.indices is not None:
            if not isinstance(self.indices, IndexArray1_V1_0_1):
                raise ValidationFailed("self.indices is not IndexArray1_V1_0_1")
