import dataclasses
import typing

from ..components.attribute_list_property import AttributeListProperty_V1_1_0, AttributeListProperty_V1_2_0
from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.embedded_triangulated_mesh import (
    EmbeddedTriangulatedMesh_V2_0_0,
    EmbeddedTriangulatedMesh_V2_0_0_Parts,
    EmbeddedTriangulatedMesh_V2_1_0,
    EmbeddedTriangulatedMesh_V2_1_0_Parts,
)
from ..components.lineage import Lineage_V1_0_0
from ..components.one_of_attribute import OneOfAttribute_V1_1_0, OneOfAttribute_V1_2_0
from ..components.triangles import Triangles_V1_0_1, Triangles_V1_1_0, Triangles_V1_2_0
from ..elements.index_array_2 import IndexArray2_V1_0_1
from ..elements.serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A description of a triangular mesh.

    Attributes:
        schema (str)
        triangles (Triangles_V1_1_0): The triangles of the mesh.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/triangle-mesh/1.1.0/triangle-mesh.schema.json"

    triangles: Triangles_V1_1_0
    """The triangles of the mesh."""
    schema: str = "/objects/triangle-mesh/1.1.0/triangle-mesh.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.triangles, Triangles_V1_1_0):
            raise ValidationFailed("self.triangles is not Triangles_V1_1_0")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/triangle-mesh/1.1.0/triangle-mesh.schema.json":
            raise ValidationFailed('self.schema == "/objects/triangle-mesh/1.1.0/triangle-mesh.schema.json" failed')


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_1_0_Edges_EdgeParts(AttributeListProperty_V1_2_0):
    """A structure defining edge chunks of the mesh.

    Attributes:
        chunks (IndexArray2_V1_0_1): A tuple defining the first index and the length of a chunk.
    The chunk refers to a segment of the edges array.
    Chunks do not have to include all edges, and chunks can overlap.
    Columns: offset, count
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    chunks: IndexArray2_V1_0_1
    """A tuple defining the first index and the length of a chunk.
     
    The chunk refers to a segment of the edges array.
    Chunks do not have to include all edges, and chunks can overlap.
    Columns: offset, count
    """

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_1_0_Edges(AttributeListProperty_V1_2_0):
    """A structure defining edges and edge chunks of the mesh.

    Attributes:
        indices (IndexArray2_V1_0_1): Edges defined by tuples of indices into the vertex list. Columns: start, end
        parts (TriangleMesh_V2_1_0_Edges_EdgeParts, optional): An optional structure defining edge chunks the mesh is composed of.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    indices: IndexArray2_V1_0_1
    """Edges defined by tuples of indices into the vertex list. Columns: start, end"""
    parts: TriangleMesh_V2_1_0_Edges_EdgeParts | None = None
    """An optional structure defining edge chunks the mesh is composed of."""

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.indices, IndexArray2_V1_0_1):
            raise ValidationFailed("self.indices is not IndexArray2_V1_0_1")
        if self.parts is not None:
            if not isinstance(self.parts, TriangleMesh_V2_1_0_Edges_EdgeParts):
                raise ValidationFailed("self.parts is not TriangleMesh_V2_1_0_Edges_EdgeParts")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_1_0(BaseSpatialDataProperties_V1_0_1, EmbeddedTriangulatedMesh_V2_1_0):
    """A mesh composed of triangles.

    The triangles are defined by triplets of indices into a vertex list.
    Optionally, parts and edges can be defined.
    Attributes:
        schema (str)
        edges (TriangleMesh_V2_1_0_Edges, optional): An optional structure defining edges and edge chunks of the mesh.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        triangles (Triangles_V1_2_0): The vertices and triangle indices of the mesh.
        parts (EmbeddedTriangulatedMesh_V2_1_0_Parts, optional): A structure defining triangle chunks the mesh is composed of.
    """

    SCHEMA_ID = "/objects/triangle-mesh/2.1.0/triangle-mesh.schema.json"

    schema: str = "/objects/triangle-mesh/2.1.0/triangle-mesh.schema.json"
    edges: TriangleMesh_V2_1_0_Edges | None = None
    """An optional structure defining edges and edge chunks of the mesh."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        EmbeddedTriangulatedMesh_V2_1_0.__post_init__(self)
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/triangle-mesh/2.1.0/triangle-mesh.schema.json":
            raise ValidationFailed('self.schema == "/objects/triangle-mesh/2.1.0/triangle-mesh.schema.json" failed')
        if self.edges is not None:
            if not isinstance(self.edges, TriangleMesh_V2_1_0_Edges):
                raise ValidationFailed("self.edges is not TriangleMesh_V2_1_0_Edges")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_2_0_Edges_EdgeParts(AttributeListProperty_V1_2_0):
    """A structure defining edge chunks of the mesh.

    Attributes:
        chunks (IndexArray2_V1_0_1): A tuple defining the first index and the length of a chunk.
    The chunk refers to a segment of the edges array.
    Chunks do not have to include all edges, and chunks can overlap.
    Columns: offset, count
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    chunks: IndexArray2_V1_0_1
    """A tuple defining the first index and the length of a chunk.
     
    The chunk refers to a segment of the edges array.
    Chunks do not have to include all edges, and chunks can overlap.
    Columns: offset, count
    """

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_2_0_Edges(AttributeListProperty_V1_2_0):
    """A structure defining edges and edge chunks of the mesh.

    Attributes:
        indices (IndexArray2_V1_0_1): Edges defined by tuples of indices into the vertex list. Columns: start, end
        parts (TriangleMesh_V2_2_0_Edges_EdgeParts, optional): An optional structure defining edge chunks the mesh is composed of.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    indices: IndexArray2_V1_0_1
    """Edges defined by tuples of indices into the vertex list. Columns: start, end"""
    parts: TriangleMesh_V2_2_0_Edges_EdgeParts | None = None
    """An optional structure defining edge chunks the mesh is composed of."""

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not isinstance(self.indices, IndexArray2_V1_0_1):
            raise ValidationFailed("self.indices is not IndexArray2_V1_0_1")
        if self.parts is not None:
            if not isinstance(self.parts, TriangleMesh_V2_2_0_Edges_EdgeParts):
                raise ValidationFailed("self.parts is not TriangleMesh_V2_2_0_Edges_EdgeParts")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_2_0(BaseSpatialDataProperties_V1_1_0, EmbeddedTriangulatedMesh_V2_1_0):
    """A mesh composed of triangles.

    The triangles are defined by triplets of indices into a vertex list.
    Optionally, parts and edges can be defined.
    Attributes:
        schema (str)
        edges (TriangleMesh_V2_2_0_Edges, optional): An optional structure defining edges and edge chunks of the mesh.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
        triangles (Triangles_V1_2_0): The vertices and triangle indices of the mesh.
        parts (EmbeddedTriangulatedMesh_V2_1_0_Parts, optional): A structure defining triangle chunks the mesh is composed of.
    """

    SCHEMA_ID = "/objects/triangle-mesh/2.2.0/triangle-mesh.schema.json"

    schema: str = "/objects/triangle-mesh/2.2.0/triangle-mesh.schema.json"
    edges: TriangleMesh_V2_2_0_Edges | None = None
    """An optional structure defining edges and edge chunks of the mesh."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        EmbeddedTriangulatedMesh_V2_1_0.__post_init__(self)
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/triangle-mesh/2.2.0/triangle-mesh.schema.json":
            raise ValidationFailed('self.schema == "/objects/triangle-mesh/2.2.0/triangle-mesh.schema.json" failed')
        if self.edges is not None:
            if not isinstance(self.edges, TriangleMesh_V2_2_0_Edges):
                raise ValidationFailed("self.edges is not TriangleMesh_V2_2_0_Edges")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_0_0_Edges_EdgeParts(AttributeListProperty_V1_1_0):
    """A structure defining edge chunks of the mesh.

    Attributes:
        chunks (IndexArray2_V1_0_1): A tuple defining the first index and the length of a chunk.
    The chunk refers to a segment of the edges array.
    Chunks do not have to include all edges, and chunks can overlap.
    Columns: offset, count
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    chunks: IndexArray2_V1_0_1
    """A tuple defining the first index and the length of a chunk.
     
    The chunk refers to a segment of the edges array.
    Chunks do not have to include all edges, and chunks can overlap.
    Columns: offset, count
    """

    def __post_init__(self):
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not isinstance(self.chunks, IndexArray2_V1_0_1):
            raise ValidationFailed("self.chunks is not IndexArray2_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_0_0_Edges(AttributeListProperty_V1_1_0):
    """A structure defining edges and edge chunks of the mesh.

    Attributes:
        indices (IndexArray2_V1_0_1): Edges defined by tuples of indices into the vertex list. Columns: start, end
        parts (TriangleMesh_V2_0_0_Edges_EdgeParts, optional): An optional structure defining edge chunks the mesh is composed of.
        attributes (OneOfAttribute_V1_1_0, optional): Attribute data.
    """

    indices: IndexArray2_V1_0_1
    """Edges defined by tuples of indices into the vertex list. Columns: start, end"""
    parts: TriangleMesh_V2_0_0_Edges_EdgeParts | None = None
    """An optional structure defining edge chunks the mesh is composed of."""

    def __post_init__(self):
        AttributeListProperty_V1_1_0.__post_init__(self)
        if not isinstance(self.indices, IndexArray2_V1_0_1):
            raise ValidationFailed("self.indices is not IndexArray2_V1_0_1")
        if self.parts is not None:
            if not isinstance(self.parts, TriangleMesh_V2_0_0_Edges_EdgeParts):
                raise ValidationFailed("self.parts is not TriangleMesh_V2_0_0_Edges_EdgeParts")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V2_0_0(BaseSpatialDataProperties_V1_0_1, EmbeddedTriangulatedMesh_V2_0_0):
    """A mesh composed of triangles.

    The triangles are defined by triplets of indices into a vertex list.
    Optionally, parts and edges can be defined.
    Attributes:
        schema (str)
        edges (TriangleMesh_V2_0_0_Edges, optional): An optional structure defining edges and edge chunks of the mesh.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        triangles (Triangles_V1_1_0): The vertices and triangle indices of the mesh.
        parts (EmbeddedTriangulatedMesh_V2_0_0_Parts, optional): A structure defining triangle chunks the mesh is composed of.
    """

    SCHEMA_ID = "/objects/triangle-mesh/2.0.0/triangle-mesh.schema.json"

    schema: str = "/objects/triangle-mesh/2.0.0/triangle-mesh.schema.json"
    edges: TriangleMesh_V2_0_0_Edges | None = None
    """An optional structure defining edges and edge chunks of the mesh."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        EmbeddedTriangulatedMesh_V2_0_0.__post_init__(self)
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/triangle-mesh/2.0.0/triangle-mesh.schema.json":
            raise ValidationFailed('self.schema == "/objects/triangle-mesh/2.0.0/triangle-mesh.schema.json" failed')
        if self.edges is not None:
            if not isinstance(self.edges, TriangleMesh_V2_0_0_Edges):
                raise ValidationFailed("self.edges is not TriangleMesh_V2_0_0_Edges")


@dataclasses.dataclass(kw_only=True)
class TriangleMesh_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A description of a triangular mesh.

    Attributes:
        schema (str)
        triangles (Triangles_V1_0_1): The triangles of the mesh.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/triangle-mesh/1.0.1/triangle-mesh.schema.json"

    triangles: Triangles_V1_0_1
    """The triangles of the mesh."""
    schema: str = "/objects/triangle-mesh/1.0.1/triangle-mesh.schema.json"

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.triangles, Triangles_V1_0_1):
            raise ValidationFailed("self.triangles is not Triangles_V1_0_1")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/triangle-mesh/1.0.1/triangle-mesh.schema.json":
            raise ValidationFailed('self.schema == "/objects/triangle-mesh/1.0.1/triangle-mesh.schema.json" failed')
