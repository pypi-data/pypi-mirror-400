import dataclasses

from ..elements.bool_array_1 import BoolArray1_V1_0_1
from ..elements.float_array_2 import FloatArray2_V1_0_1
from ..elements.float_array_3 import FloatArray3_V1_0_1
from ..elements.serialiser import ValidationFailed
from .data_table import DataTable_V1_2_0
from .distance_table import DistanceTable_V1_2_0, DistanceTable_V1_2_0_Distance
from .hole_chunks import HoleChunks_V1_0_0
from .interval_table import IntervalTable_V1_2_0, IntervalTable_V1_2_0_FromTo
from .one_of_attribute import OneOfAttribute_V1_2_0
from .relative_lineation_data_table import RelativeLineationDataTable_V1_2_0, RelativeLineationDataTable_V1_2_0_Distance
from .relative_planar_data_table import RelativePlanarDataTable_V1_2_0, RelativePlanarDataTable_V1_2_0_Distance


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_DataTable(DataTable_V1_2_0):
    """Attributes:

    holes (HoleChunks_V1_0_0): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        DataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_DistanceTable(DistanceTable_V1_2_0):
    """Attributes:

    holes (HoleChunks_V1_0_0): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (DistanceTable_V1_2_0_Distance): The distance.
    """

    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        DistanceTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_IntervalTable(IntervalTable_V1_2_0):
    """Attributes:

    holes (HoleChunks_V1_0_0): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    from_to (IntervalTable_V1_2_0_FromTo): The from-to of the intervals.
    """

    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        IntervalTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_RelativePlanarDataTable(RelativePlanarDataTable_V1_2_0):
    """Attributes:

    holes (HoleChunks_V1_0_0): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativePlanarDataTable_V1_2_0_Distance): The distance down the drillhole.
    relative_plane_angles (FloatArray2_V1_0_1): Planar measurements relative to the drillhole. Columns: alpha, beta
    plane_polarity (BoolArray1_V1_0_1, optional): Polarity of the planar measurements. Column: has_positive_polarity
    """

    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        RelativePlanarDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


@dataclasses.dataclass(kw_only=True)
class DownholeAttributes_V1_0_0_Item_RelativeLineationDataTable(RelativeLineationDataTable_V1_2_0):
    """Attributes:

    holes (HoleChunks_V1_0_0): The data describing the holes.
    name (str): The name of the table.
    collection_type (str): The type of the collection.
    distance (RelativeLineationDataTable_V1_2_0_Distance): The distance down the drillhole.
    relative_lineation_angles (FloatArray3_V1_0_1): Lineation measurements relative to the drillhole. Columns: alpha, beta, gamma
    """

    holes: HoleChunks_V1_0_0
    """The data describing the holes."""

    def __post_init__(self):
        RelativeLineationDataTable_V1_2_0.__post_init__(self)
        if not isinstance(self.holes, HoleChunks_V1_0_0):
            raise ValidationFailed("self.holes is not HoleChunks_V1_0_0")


DownholeAttributes_V1_0_0_Item = (
    DownholeAttributes_V1_0_0_Item_DataTable
    | DownholeAttributes_V1_0_0_Item_DistanceTable
    | DownholeAttributes_V1_0_0_Item_IntervalTable
    | DownholeAttributes_V1_0_0_Item_RelativePlanarDataTable
    | DownholeAttributes_V1_0_0_Item_RelativeLineationDataTable
)
DownholeAttributes_V1_0_0 = list[DownholeAttributes_V1_0_0_Item]
