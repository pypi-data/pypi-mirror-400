from __future__ import annotations

import dataclasses
import typing

from ..components.base_object_properties import BaseObjectProperties_V1_0_1_Uuid, BaseObjectProperties_V1_1_0_Uuid
from ..components.base_spatial_data_properties import BaseSpatialDataProperties_V1_0_1, BaseSpatialDataProperties_V1_1_0
from ..components.bounding_box import BoundingBox_V1_0_1
from ..components.crs import Crs_V1_0_1
from ..components.embedded_mesh_object import EmbeddedMeshObject_V1_0_0
from ..components.embedded_triangulated_mesh import (
    EmbeddedTriangulatedMesh_V1_0_1,
    EmbeddedTriangulatedMesh_V1_1_0,
    EmbeddedTriangulatedMesh_V2_1_0,
    EmbeddedTriangulatedMesh_V2_1_0_Parts,
)
from ..components.lineage import Lineage_V1_0_0
from ..components.material import Material_V1_0_1
from ..components.mesh_quality import MeshQuality_V1_0_1
from ..components.one_of_attribute import OneOfAttribute_V1_2_0, OneOfAttribute_V1_2_0_Item
from ..components.triangles import Triangles_V1_2_0
from ..elements.reversible_index import ReversibleIndex_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V1_1_0_Folder(Serialiser):
    """Attributes:

    name (str): Name of the folder.
    items (list[GeologicalModelMeshes_V1_1_0_Folder_Items]): A list of folders containing meshes and subfolders.
    """

    name: str
    """Name of the folder."""
    items: list[GeologicalModelMeshes_V1_1_0_Folder_Items]
    """A list of folders containing meshes and subfolders."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.items, list):
            raise ValidationFailed("self.items is not a list")
        for v in self.items:
            if not isinstance(v, GeologicalModelMeshes_V1_1_0_Folder_Items):
                raise ValidationFailed("v is not GeologicalModelMeshes_V1_1_0_Folder_Items")


GeologicalModelMeshes_V1_1_0_Folder_Items = GeologicalModelMeshes_V1_1_0_Folder | EmbeddedTriangulatedMesh_V1_1_0


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V1_1_0(BaseSpatialDataProperties_V1_0_1):
    """A collection of geological meshes.

    Attributes:
        schema (str)
        folders (list[GeologicalModelMeshes_V1_1_0_Folder]): A recursive list of folders containing meshes.
        materials (list[Material_V1_0_1], optional): Materials used by this mesh collection.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/geological-model-meshes/1.1.0/geological-model-meshes.schema.json"

    folders: list[GeologicalModelMeshes_V1_1_0_Folder]
    """A recursive list of folders containing meshes."""
    schema: str = "/objects/geological-model-meshes/1.1.0/geological-model-meshes.schema.json"
    materials: list[Material_V1_0_1] | None = None
    """Materials used by this mesh collection."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.folders, list):
            raise ValidationFailed("self.folders is not a list")
        for v in self.folders:
            if not isinstance(v, GeologicalModelMeshes_V1_1_0_Folder):
                raise ValidationFailed("v is not GeologicalModelMeshes_V1_1_0_Folder")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geological-model-meshes/1.1.0/geological-model-meshes.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geological-model-meshes/1.1.0/geological-model-meshes.schema.json" failed'
            )
        if self.materials is not None:
            if not isinstance(self.materials, list):
                raise ValidationFailed("self.materials is not a list")
            for v in self.materials:
                if not isinstance(v, Material_V1_0_1):
                    raise ValidationFailed("v is not Material_V1_0_1")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_1_0_Folder_Items_VolumeIndex(Serialiser):
    """Attributes:

    volume_index (int): The index of the volume in the list of embedded volumes
    """

    volume_index: int
    """The index of the volume in the list of embedded volumes"""

    def __post_init__(self):
        if not isinstance(self.volume_index, int):
            raise ValidationFailed("self.volume_index is not int")
        if not 0 <= self.volume_index:
            raise ValidationFailed("0 <= self.volume_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_1_0_Folder_Items_SurfaceIndex(Serialiser):
    """Attributes:

    surface_index (int): The index of the surface in the list of embedded surfaces
    """

    surface_index: int
    """The index of the surface in the list of embedded surfaces"""

    def __post_init__(self):
        if not isinstance(self.surface_index, int):
            raise ValidationFailed("self.surface_index is not int")
        if not 0 <= self.surface_index:
            raise ValidationFailed("0 <= self.surface_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_1_0_Folder(Serialiser):
    """Attributes:

    name (str): Name of the folder.
    items (list[GeologicalModelMeshes_V2_1_0_Folder_Items]): A list of folders containing meshes and subfolders.
    """

    name: str
    """Name of the folder."""
    items: list[GeologicalModelMeshes_V2_1_0_Folder_Items]
    """A list of folders containing meshes and subfolders."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.items, list):
            raise ValidationFailed("self.items is not a list")
        for v in self.items:
            if not isinstance(v, GeologicalModelMeshes_V2_1_0_Folder_Items):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_1_0_Folder_Items")


GeologicalModelMeshes_V2_1_0_Folder_Items = (
    GeologicalModelMeshes_V2_1_0_Folder
    | GeologicalModelMeshes_V2_1_0_Folder_Items_VolumeIndex
    | GeologicalModelMeshes_V2_1_0_Folder_Items_SurfaceIndex
)


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_1_0_TriangleGeometry(EmbeddedTriangulatedMesh_V2_1_0):
    """The embedded mesh, defining vertices, triangles and parts.

    Attributes:
        triangles (Triangles_V1_2_0): The vertices and triangle indices of the mesh.
        parts (EmbeddedTriangulatedMesh_V2_1_0_Parts): A structure defining triangle chunks the mesh is composed of.
    """

    def __post_init__(self):
        EmbeddedTriangulatedMesh_V2_1_0.__post_init__(self)
        if self.parts is None:
            raise ValidationFailed("self.parts is required")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_1_0_GmEmbeddedVolume(EmbeddedMeshObject_V1_0_0):
    """Attributes:

    material_key (str, optional): Unique identifier of the material.
    feature (str): Kind of feature.
    name (str): Name of the object.
    description (str, optional): Optional field for adding additional description to uniquely identify this object.
    quality (MeshQuality_V1_0_1, optional): Mesh quality.
    parts (list[ReversibleIndex_V1_0_0]): A list of parts and whether they are reversed.
    """

    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedMeshObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in ("Void", "OutputVolume", "Vein", "VeinSystem"):
            raise ValidationFailed('self.feature in ("Void", "OutputVolume", "Vein", "VeinSystem") failed')
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_1_0_GmEmbeddedSurface(EmbeddedMeshObject_V1_0_0):
    """Attributes:

    material_key (str, optional): Unique identifier of the material.
    feature (str): Kind of feature.
    name (str): Name of the object.
    description (str, optional): Optional field for adding additional description to uniquely identify this object.
    quality (MeshQuality_V1_0_1, optional): Mesh quality.
    parts (list[ReversibleIndex_V1_0_0]): A list of parts and whether they are reversed.
    """

    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedMeshObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in (
            "Fault",
            "ContactSurface",
            "Topography",
            "BoundarySurface",
            "StratigraphicContactSurface",
        ):
            raise ValidationFailed(
                'self.feature in ("Fault", "ContactSurface", "Topography", "BoundarySurface", "StratigraphicContactSurface") failed'
            )
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_1_0(BaseSpatialDataProperties_V1_1_0):
    """A collection of geological volumes and surfaces.

    Attributes:
        schema (str)
        folders (list[GeologicalModelMeshes_V2_1_0_Folder]): A recursive list of folders containing indices into the volume and surface lists.
        triangle_geometry (GeologicalModelMeshes_V2_1_0_TriangleGeometry): The embedded mesh, defining vertices, triangles and parts.
        materials (list[Material_V1_0_1], optional): Materials used by this mesh collection.
        volumes (list[GeologicalModelMeshes_V2_1_0_GmEmbeddedVolume]): A list of embedded volumes. Each volume consists of a number of parts.
        volume_attributes (OneOfAttribute_V1_2_0, optional): Attributes associated with each volume. The attribute tables have one row per volume.
        surfaces (list[GeologicalModelMeshes_V2_1_0_GmEmbeddedSurface]): A list of embedded surfaces. Each surface consists of a number of parts.
        surface_attributes (OneOfAttribute_V1_2_0, optional): Attributes associated with each surface. The attribute tables have one row per surface.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/geological-model-meshes/2.1.0/geological-model-meshes.schema.json"

    folders: list[GeologicalModelMeshes_V2_1_0_Folder]
    """A recursive list of folders containing indices into the volume and surface lists."""
    triangle_geometry: GeologicalModelMeshes_V2_1_0_TriangleGeometry
    """The embedded mesh, defining vertices, triangles and parts."""
    volumes: list[GeologicalModelMeshes_V2_1_0_GmEmbeddedVolume]
    """A list of embedded volumes. Each volume consists of a number of parts."""
    surfaces: list[GeologicalModelMeshes_V2_1_0_GmEmbeddedSurface]
    """A list of embedded surfaces. Each surface consists of a number of parts."""
    schema: str = "/objects/geological-model-meshes/2.1.0/geological-model-meshes.schema.json"
    materials: list[Material_V1_0_1] | None = None
    """Materials used by this mesh collection."""
    volume_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each volume. The attribute tables have one row per volume."""
    surface_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each surface. The attribute tables have one row per surface."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.folders, list):
            raise ValidationFailed("self.folders is not a list")
        for v in self.folders:
            if not isinstance(v, GeologicalModelMeshes_V2_1_0_Folder):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_1_0_Folder")
        if not isinstance(self.triangle_geometry, GeologicalModelMeshes_V2_1_0_TriangleGeometry):
            raise ValidationFailed("self.triangle_geometry is not GeologicalModelMeshes_V2_1_0_TriangleGeometry")
        if not isinstance(self.volumes, list):
            raise ValidationFailed("self.volumes is not a list")
        for v in self.volumes:
            if not isinstance(v, GeologicalModelMeshes_V2_1_0_GmEmbeddedVolume):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_1_0_GmEmbeddedVolume")
        if not isinstance(self.surfaces, list):
            raise ValidationFailed("self.surfaces is not a list")
        for v in self.surfaces:
            if not isinstance(v, GeologicalModelMeshes_V2_1_0_GmEmbeddedSurface):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_1_0_GmEmbeddedSurface")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geological-model-meshes/2.1.0/geological-model-meshes.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geological-model-meshes/2.1.0/geological-model-meshes.schema.json" failed'
            )
        if self.materials is not None:
            if not isinstance(self.materials, list):
                raise ValidationFailed("self.materials is not a list")
            for v in self.materials:
                if not isinstance(v, Material_V1_0_1):
                    raise ValidationFailed("v is not Material_V1_0_1")
        if self.volume_attributes is not None:
            if not isinstance(self.volume_attributes, list):
                raise ValidationFailed("self.volume_attributes is not a list")
            for v in self.volume_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.surface_attributes is not None:
            if not isinstance(self.surface_attributes, list):
                raise ValidationFailed("self.surface_attributes is not a list")
            for v in self.surface_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_2_0_Folder_Items_VolumeIndex(Serialiser):
    """Attributes:

    volume_index (int): The index of the volume in the list of embedded volumes
    """

    volume_index: int
    """The index of the volume in the list of embedded volumes"""

    def __post_init__(self):
        if not isinstance(self.volume_index, int):
            raise ValidationFailed("self.volume_index is not int")
        if not 0 <= self.volume_index:
            raise ValidationFailed("0 <= self.volume_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_2_0_Folder_Items_SurfaceIndex(Serialiser):
    """Attributes:

    surface_index (int): The index of the surface in the list of embedded surfaces
    """

    surface_index: int
    """The index of the surface in the list of embedded surfaces"""

    def __post_init__(self):
        if not isinstance(self.surface_index, int):
            raise ValidationFailed("self.surface_index is not int")
        if not 0 <= self.surface_index:
            raise ValidationFailed("0 <= self.surface_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_2_0_Folder(Serialiser):
    """Attributes:

    name (str): Name of the folder.
    items (list[GeologicalModelMeshes_V2_2_0_Folder_Items]): A list of folders containing meshes and subfolders.
    """

    name: str
    """Name of the folder."""
    items: list[GeologicalModelMeshes_V2_2_0_Folder_Items]
    """A list of folders containing meshes and subfolders."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.items, list):
            raise ValidationFailed("self.items is not a list")
        for v in self.items:
            if not isinstance(v, GeologicalModelMeshes_V2_2_0_Folder_Items):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_2_0_Folder_Items")


GeologicalModelMeshes_V2_2_0_Folder_Items = (
    GeologicalModelMeshes_V2_2_0_Folder
    | GeologicalModelMeshes_V2_2_0_Folder_Items_VolumeIndex
    | GeologicalModelMeshes_V2_2_0_Folder_Items_SurfaceIndex
)


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_2_0_TriangleGeometry(EmbeddedTriangulatedMesh_V2_1_0):
    """The embedded mesh, defining vertices, triangles and parts.

    Attributes:
        triangles (Triangles_V1_2_0): The vertices and triangle indices of the mesh.
        parts (EmbeddedTriangulatedMesh_V2_1_0_Parts): A structure defining triangle chunks the mesh is composed of.
    """

    def __post_init__(self):
        EmbeddedTriangulatedMesh_V2_1_0.__post_init__(self)
        if self.parts is None:
            raise ValidationFailed("self.parts is required")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_2_0_GmEmbeddedVolume(EmbeddedMeshObject_V1_0_0):
    """Attributes:

    material_key (str, optional): Unique identifier of the material.
    feature (str): Kind of feature.
    name (str): Name of the object.
    description (str, optional): Optional field for adding additional description to uniquely identify this object.
    quality (MeshQuality_V1_0_1, optional): Mesh quality.
    parts (list[ReversibleIndex_V1_0_0]): A list of parts and whether they are reversed.
    """

    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedMeshObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in ("Void", "OutputVolume", "Vein", "VeinSystem", "Generic"):
            raise ValidationFailed('self.feature in ("Void", "OutputVolume", "Vein", "VeinSystem", "Generic") failed')
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_2_0_GmEmbeddedSurface(EmbeddedMeshObject_V1_0_0):
    """Attributes:

    material_key (str, optional): Unique identifier of the material.
    feature (str): Kind of feature.
    name (str): Name of the object.
    description (str, optional): Optional field for adding additional description to uniquely identify this object.
    quality (MeshQuality_V1_0_1, optional): Mesh quality.
    parts (list[ReversibleIndex_V1_0_0]): A list of parts and whether they are reversed.
    """

    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedMeshObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in (
            "Fault",
            "ContactSurface",
            "Topography",
            "BoundarySurface",
            "StratigraphicContactSurface",
            "Generic",
        ):
            raise ValidationFailed(
                'self.feature in ("Fault", "ContactSurface", "Topography", "BoundarySurface", "StratigraphicContactSurface", "Generic") failed'
            )
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_2_0(BaseSpatialDataProperties_V1_1_0):
    """A collection of geological volumes and surfaces.

    Attributes:
        schema (str)
        folders (list[GeologicalModelMeshes_V2_2_0_Folder]): A recursive list of folders containing indices into the volume and surface lists.
        triangle_geometry (GeologicalModelMeshes_V2_2_0_TriangleGeometry): The embedded mesh, defining vertices, triangles and parts.
        materials (list[Material_V1_0_1], optional): Materials used by this mesh collection.
        volumes (list[GeologicalModelMeshes_V2_2_0_GmEmbeddedVolume]): A list of embedded volumes. Each volume consists of a number of parts.
        volume_attributes (OneOfAttribute_V1_2_0, optional): Attributes associated with each volume. The attribute tables have one row per volume.
        surfaces (list[GeologicalModelMeshes_V2_2_0_GmEmbeddedSurface]): A list of embedded surfaces. Each surface consists of a number of parts.
        surface_attributes (OneOfAttribute_V1_2_0, optional): Attributes associated with each surface. The attribute tables have one row per surface.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/geological-model-meshes/2.2.0/geological-model-meshes.schema.json"

    folders: list[GeologicalModelMeshes_V2_2_0_Folder]
    """A recursive list of folders containing indices into the volume and surface lists."""
    triangle_geometry: GeologicalModelMeshes_V2_2_0_TriangleGeometry
    """The embedded mesh, defining vertices, triangles and parts."""
    volumes: list[GeologicalModelMeshes_V2_2_0_GmEmbeddedVolume]
    """A list of embedded volumes. Each volume consists of a number of parts."""
    surfaces: list[GeologicalModelMeshes_V2_2_0_GmEmbeddedSurface]
    """A list of embedded surfaces. Each surface consists of a number of parts."""
    schema: str = "/objects/geological-model-meshes/2.2.0/geological-model-meshes.schema.json"
    materials: list[Material_V1_0_1] | None = None
    """Materials used by this mesh collection."""
    volume_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each volume. The attribute tables have one row per volume."""
    surface_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each surface. The attribute tables have one row per surface."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.folders, list):
            raise ValidationFailed("self.folders is not a list")
        for v in self.folders:
            if not isinstance(v, GeologicalModelMeshes_V2_2_0_Folder):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_2_0_Folder")
        if not isinstance(self.triangle_geometry, GeologicalModelMeshes_V2_2_0_TriangleGeometry):
            raise ValidationFailed("self.triangle_geometry is not GeologicalModelMeshes_V2_2_0_TriangleGeometry")
        if not isinstance(self.volumes, list):
            raise ValidationFailed("self.volumes is not a list")
        for v in self.volumes:
            if not isinstance(v, GeologicalModelMeshes_V2_2_0_GmEmbeddedVolume):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_2_0_GmEmbeddedVolume")
        if not isinstance(self.surfaces, list):
            raise ValidationFailed("self.surfaces is not a list")
        for v in self.surfaces:
            if not isinstance(v, GeologicalModelMeshes_V2_2_0_GmEmbeddedSurface):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_2_0_GmEmbeddedSurface")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geological-model-meshes/2.2.0/geological-model-meshes.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geological-model-meshes/2.2.0/geological-model-meshes.schema.json" failed'
            )
        if self.materials is not None:
            if not isinstance(self.materials, list):
                raise ValidationFailed("self.materials is not a list")
            for v in self.materials:
                if not isinstance(v, Material_V1_0_1):
                    raise ValidationFailed("v is not Material_V1_0_1")
        if self.volume_attributes is not None:
            if not isinstance(self.volume_attributes, list):
                raise ValidationFailed("self.volume_attributes is not a list")
            for v in self.volume_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.surface_attributes is not None:
            if not isinstance(self.surface_attributes, list):
                raise ValidationFailed("self.surface_attributes is not a list")
            for v in self.surface_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_0_0_Folder_Items_VolumeIndex(Serialiser):
    """Attributes:

    volume_index (int): The index of the volume in the list of embedded volumes
    """

    volume_index: int
    """The index of the volume in the list of embedded volumes"""

    def __post_init__(self):
        if not isinstance(self.volume_index, int):
            raise ValidationFailed("self.volume_index is not int")
        if not 0 <= self.volume_index:
            raise ValidationFailed("0 <= self.volume_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_0_0_Folder_Items_SurfaceIndex(Serialiser):
    """Attributes:

    surface_index (int): The index of the surface in the list of embedded surfaces
    """

    surface_index: int
    """The index of the surface in the list of embedded surfaces"""

    def __post_init__(self):
        if not isinstance(self.surface_index, int):
            raise ValidationFailed("self.surface_index is not int")
        if not 0 <= self.surface_index:
            raise ValidationFailed("0 <= self.surface_index failed")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_0_0_Folder(Serialiser):
    """Attributes:

    name (str): Name of the folder.
    items (list[GeologicalModelMeshes_V2_0_0_Folder_Items]): A list of folders containing meshes and subfolders.
    """

    name: str
    """Name of the folder."""
    items: list[GeologicalModelMeshes_V2_0_0_Folder_Items]
    """A list of folders containing meshes and subfolders."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.items, list):
            raise ValidationFailed("self.items is not a list")
        for v in self.items:
            if not isinstance(v, GeologicalModelMeshes_V2_0_0_Folder_Items):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_0_0_Folder_Items")


GeologicalModelMeshes_V2_0_0_Folder_Items = (
    GeologicalModelMeshes_V2_0_0_Folder
    | GeologicalModelMeshes_V2_0_0_Folder_Items_VolumeIndex
    | GeologicalModelMeshes_V2_0_0_Folder_Items_SurfaceIndex
)


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_0_0_TriangleGeometry(EmbeddedTriangulatedMesh_V2_1_0):
    """The embedded mesh, defining vertices, triangles and parts.

    Attributes:
        triangles (Triangles_V1_2_0): The vertices and triangle indices of the mesh.
        parts (EmbeddedTriangulatedMesh_V2_1_0_Parts): A structure defining triangle chunks the mesh is composed of.
    """

    def __post_init__(self):
        EmbeddedTriangulatedMesh_V2_1_0.__post_init__(self)
        if self.parts is None:
            raise ValidationFailed("self.parts is required")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_0_0_GmEmbeddedVolume(EmbeddedMeshObject_V1_0_0):
    """Attributes:

    material_key (str, optional): Unique identifier of the material.
    feature (str): Kind of feature.
    name (str): Name of the object.
    description (str, optional): Optional field for adding additional description to uniquely identify this object.
    quality (MeshQuality_V1_0_1, optional): Mesh quality.
    parts (list[ReversibleIndex_V1_0_0]): A list of parts and whether they are reversed.
    """

    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedMeshObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in ("Void", "OutputVolume", "Vein", "VeinSystem"):
            raise ValidationFailed('self.feature in ("Void", "OutputVolume", "Vein", "VeinSystem") failed')
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_0_0_GmEmbeddedSurface(EmbeddedMeshObject_V1_0_0):
    """Attributes:

    material_key (str, optional): Unique identifier of the material.
    feature (str): Kind of feature.
    name (str): Name of the object.
    description (str, optional): Optional field for adding additional description to uniquely identify this object.
    quality (MeshQuality_V1_0_1, optional): Mesh quality.
    parts (list[ReversibleIndex_V1_0_0]): A list of parts and whether they are reversed.
    """

    feature: str
    """Kind of feature."""
    material_key: str | None = None
    """Unique identifier of the material."""

    def __post_init__(self):
        EmbeddedMeshObject_V1_0_0.__post_init__(self)
        if not isinstance(self.feature, str):
            raise ValidationFailed("self.feature is not str")
        if self.feature not in (
            "Fault",
            "ContactSurface",
            "Topography",
            "BoundarySurface",
            "StratigraphicContactSurface",
        ):
            raise ValidationFailed(
                'self.feature in ("Fault", "ContactSurface", "Topography", "BoundarySurface", "StratigraphicContactSurface") failed'
            )
        if self.material_key is not None:
            if not isinstance(self.material_key, str):
                raise ValidationFailed("self.material_key is not str")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V2_0_0(BaseSpatialDataProperties_V1_0_1):
    """A collection of geological volumes and surfaces.

    Attributes:
        schema (str)
        folders (list[GeologicalModelMeshes_V2_0_0_Folder]): A recursive list of folders containing indices into the volume and surface lists.
        triangle_geometry (GeologicalModelMeshes_V2_0_0_TriangleGeometry): The embedded mesh, defining vertices, triangles and parts.
        materials (list[Material_V1_0_1], optional): Materials used by this mesh collection.
        volumes (list[GeologicalModelMeshes_V2_0_0_GmEmbeddedVolume]): A list of embedded volumes. Each volume consists of a number of parts.
        volume_attributes (OneOfAttribute_V1_2_0, optional): Attributes associated with each volume. The attribute tables have one row per volume.
        surfaces (list[GeologicalModelMeshes_V2_0_0_GmEmbeddedSurface]): A list of embedded surfaces. Each surface consists of a number of parts.
        surface_attributes (OneOfAttribute_V1_2_0, optional): Attributes associated with each surface. The attribute tables have one row per surface.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/geological-model-meshes/2.0.0/geological-model-meshes.schema.json"

    folders: list[GeologicalModelMeshes_V2_0_0_Folder]
    """A recursive list of folders containing indices into the volume and surface lists."""
    triangle_geometry: GeologicalModelMeshes_V2_0_0_TriangleGeometry
    """The embedded mesh, defining vertices, triangles and parts."""
    volumes: list[GeologicalModelMeshes_V2_0_0_GmEmbeddedVolume]
    """A list of embedded volumes. Each volume consists of a number of parts."""
    surfaces: list[GeologicalModelMeshes_V2_0_0_GmEmbeddedSurface]
    """A list of embedded surfaces. Each surface consists of a number of parts."""
    schema: str = "/objects/geological-model-meshes/2.0.0/geological-model-meshes.schema.json"
    materials: list[Material_V1_0_1] | None = None
    """Materials used by this mesh collection."""
    volume_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each volume. The attribute tables have one row per volume."""
    surface_attributes: OneOfAttribute_V1_2_0 | None = None
    """Attributes associated with each surface. The attribute tables have one row per surface."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.folders, list):
            raise ValidationFailed("self.folders is not a list")
        for v in self.folders:
            if not isinstance(v, GeologicalModelMeshes_V2_0_0_Folder):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_0_0_Folder")
        if not isinstance(self.triangle_geometry, GeologicalModelMeshes_V2_0_0_TriangleGeometry):
            raise ValidationFailed("self.triangle_geometry is not GeologicalModelMeshes_V2_0_0_TriangleGeometry")
        if not isinstance(self.volumes, list):
            raise ValidationFailed("self.volumes is not a list")
        for v in self.volumes:
            if not isinstance(v, GeologicalModelMeshes_V2_0_0_GmEmbeddedVolume):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_0_0_GmEmbeddedVolume")
        if not isinstance(self.surfaces, list):
            raise ValidationFailed("self.surfaces is not a list")
        for v in self.surfaces:
            if not isinstance(v, GeologicalModelMeshes_V2_0_0_GmEmbeddedSurface):
                raise ValidationFailed("v is not GeologicalModelMeshes_V2_0_0_GmEmbeddedSurface")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geological-model-meshes/2.0.0/geological-model-meshes.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geological-model-meshes/2.0.0/geological-model-meshes.schema.json" failed'
            )
        if self.materials is not None:
            if not isinstance(self.materials, list):
                raise ValidationFailed("self.materials is not a list")
            for v in self.materials:
                if not isinstance(v, Material_V1_0_1):
                    raise ValidationFailed("v is not Material_V1_0_1")
        if self.volume_attributes is not None:
            if not isinstance(self.volume_attributes, list):
                raise ValidationFailed("self.volume_attributes is not a list")
            for v in self.volume_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")
        if self.surface_attributes is not None:
            if not isinstance(self.surface_attributes, list):
                raise ValidationFailed("self.surface_attributes is not a list")
            for v in self.surface_attributes:
                if not isinstance(v, OneOfAttribute_V1_2_0_Item):
                    raise ValidationFailed("v is not OneOfAttribute_V1_2_0_Item")


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V1_0_1_Folder(Serialiser):
    """Attributes:

    name (str): Name of the folder.
    items (list[GeologicalModelMeshes_V1_0_1_Folder_Items]): A list of folders containing meshes and subfolders.
    """

    name: str
    """Name of the folder."""
    items: list[GeologicalModelMeshes_V1_0_1_Folder_Items]
    """A list of folders containing meshes and subfolders."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.items, list):
            raise ValidationFailed("self.items is not a list")
        for v in self.items:
            if not isinstance(v, GeologicalModelMeshes_V1_0_1_Folder_Items):
                raise ValidationFailed("v is not GeologicalModelMeshes_V1_0_1_Folder_Items")


GeologicalModelMeshes_V1_0_1_Folder_Items = GeologicalModelMeshes_V1_0_1_Folder | EmbeddedTriangulatedMesh_V1_0_1


@dataclasses.dataclass(kw_only=True)
class GeologicalModelMeshes_V1_0_1(BaseSpatialDataProperties_V1_0_1):
    """A collection of geological meshes.

    Attributes:
        schema (str)
        folders (list[GeologicalModelMeshes_V1_0_1_Folder]): A recursive list of folders containing meshes.
        materials (list[Material_V1_0_1], optional): Materials used by this mesh collection.
        bounding_box (BoundingBox_V1_0_1): Bounding box of the spatial data.
        coordinate_reference_system (Crs_V1_0_1): Coordinate system of the spatial data
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_0_1_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
    """

    SCHEMA_ID = "/objects/geological-model-meshes/1.0.1/geological-model-meshes.schema.json"

    folders: list[GeologicalModelMeshes_V1_0_1_Folder]
    """A recursive list of folders containing meshes."""
    schema: str = "/objects/geological-model-meshes/1.0.1/geological-model-meshes.schema.json"
    materials: list[Material_V1_0_1] | None = None
    """Materials used by this mesh collection."""

    def __post_init__(self):
        BaseSpatialDataProperties_V1_0_1.__post_init__(self)
        if not isinstance(self.folders, list):
            raise ValidationFailed("self.folders is not a list")
        for v in self.folders:
            if not isinstance(v, GeologicalModelMeshes_V1_0_1_Folder):
                raise ValidationFailed("v is not GeologicalModelMeshes_V1_0_1_Folder")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/geological-model-meshes/1.0.1/geological-model-meshes.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/geological-model-meshes/1.0.1/geological-model-meshes.schema.json" failed'
            )
        if self.materials is not None:
            if not isinstance(self.materials, list):
                raise ValidationFailed("self.materials is not a list")
            for v in self.materials:
                if not isinstance(v, Material_V1_0_1):
                    raise ValidationFailed("v is not Material_V1_0_1")
