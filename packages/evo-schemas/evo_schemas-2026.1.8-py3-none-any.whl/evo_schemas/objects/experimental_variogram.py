import dataclasses
import typing

from ..components.attribute_list_property import AttributeListProperty_V1_2_0
from ..components.base_object_properties import BaseObjectProperties_V1_1_0, BaseObjectProperties_V1_1_0_Uuid
from ..components.lineage import Lineage_V1_0_0
from ..components.one_of_attribute import OneOfAttribute_V1_2_0
from ..elements.binary_blob import BinaryBlob_V1_0_1, is_binary_blob_v1_0_1
from ..elements.serialiser import ValidationFailed
from ..elements.unit import Unit_V1_0_1, is_unit_v1_0_1
from ..elements.unit_length import UnitLength_V1_0_1_UnitCategories


@dataclasses.dataclass(kw_only=True)
class ExperimentalVariogram_V1_0_0_Directions(AttributeListProperty_V1_2_0):
    """A data-table defining the parameters for each variogram direction.

    Attributes:
        data (BinaryBlob_V1_0_1): Binary blob reference for the directions data table. Columns: offset, count, direction_type, azimuth, dip, azimuth_tolerance, dip_tolerance, bandwidth, bandheight.
        length (int): Number of directions.
        width (int): Number of columns in the core directions data table.
        data_type (str): Data types for the core directions columns.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    data: BinaryBlob_V1_0_1
    """Binary blob reference for the directions data table. Columns: offset, count, direction_type, azimuth, dip, azimuth_tolerance, dip_tolerance, bandwidth, bandheight."""
    length: int
    """Number of directions."""
    width: int = 9
    """Number of columns in the core directions data table."""
    data_type: str = "uint64/uint64/string/float64/float64/float64/float64/float64/float64"
    """Data types for the core directions columns."""

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 9:
            raise ValidationFailed("self.width == 9 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "uint64/uint64/string/float64/float64/float64/float64/float64/float64":
            raise ValidationFailed(
                'self.data_type == "uint64/uint64/string/float64/float64/float64/float64/float64/float64" failed'
            )


@dataclasses.dataclass(kw_only=True)
class ExperimentalVariogram_V1_0_0_Lags(AttributeListProperty_V1_2_0):
    """A data-table containing the calculated values for each lag bin.

    Attributes:
        data (BinaryBlob_V1_0_1): Binary blob reference for the lag data table. The columns must be: start, end, centroid, value, num_pairs.
        length (int): Total number of lag bins across all directions.
        width (int): Number of columns in the core lag data table.
        data_type (str): Data types for the core lag data columns.
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    data: BinaryBlob_V1_0_1
    """Binary blob reference for the lag data table. The columns must be: start, end, centroid, value, num_pairs."""
    length: int
    """Total number of lag bins across all directions."""
    width: int = 5
    """Number of columns in the core lag data table."""
    data_type: str = "float64/float64/float64/float64/uint64"
    """Data types for the core lag data columns."""

    def __post_init__(self):
        AttributeListProperty_V1_2_0.__post_init__(self)
        if not is_binary_blob_v1_0_1(self.data):
            raise ValidationFailed("is_binary_blob_v1_0_1(self.data) failed")
        if not isinstance(self.length, int):
            raise ValidationFailed("self.length is not int")
        if not 0 <= self.length:
            raise ValidationFailed("0 <= self.length failed")
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 5:
            raise ValidationFailed("self.width == 5 failed")
        if not isinstance(self.data_type, str):
            raise ValidationFailed("self.data_type is not str")
        if not self.data_type == "float64/float64/float64/float64/uint64":
            raise ValidationFailed('self.data_type == "float64/float64/float64/float64/uint64" failed')


@dataclasses.dataclass(kw_only=True)
class ExperimentalVariogram_V1_0_0(BaseObjectProperties_V1_1_0):
    """An experimental variogram object representing spatial continuity statistics for a single variable, grouped by direction and lag distance.

    Attributes:
        schema (str)
        domain (str, optional): The domain the experimental variogram is calculated for.
        attribute (str, optional): The attribute the experimental variogram is calculated for.
        data_variance (float): The variance of the source data, often used as the expected sill of the variogram.
        variogram_type (str, optional): The type of calculation performed (e.g., variogram, semi-variogram, covariance, correlogram).
        distance_unit (UnitLength_V1_0_1_UnitCategories, optional): Distance unit.
        attribute_unit (Unit_V1_0_1, optional): Attribute unit
        directions (ExperimentalVariogram_V1_0_0_Directions): A data-table defining the parameters for each variogram direction.
        lags (ExperimentalVariogram_V1_0_0_Lags): A data-table containing the calculated values for each lag bin.
        name (str): Name of the object.
        uuid (BaseObjectProperties_V1_1_0_Uuid): Identifier of the object.
        description (str, optional): Optional field for adding additional description to uniquely identify this object.
        extensions (dict[str, typing.Any], optional): Extended properties that may be associated to the object, but not specified in the schema
        tags (dict[str, str], optional): Key-value pairs of user-defined metadata
        lineage (Lineage_V1_0_0, optional): Information about the history of the object
    """

    SCHEMA_ID = "/objects/experimental-variogram/1.0.0/experimental-variogram.schema.json"

    data_variance: float
    """The variance of the source data, often used as the expected sill of the variogram."""
    directions: ExperimentalVariogram_V1_0_0_Directions
    """A data-table defining the parameters for each variogram direction."""
    lags: ExperimentalVariogram_V1_0_0_Lags
    """A data-table containing the calculated values for each lag bin."""
    schema: str = "/objects/experimental-variogram/1.0.0/experimental-variogram.schema.json"
    domain: str | None = None
    """The domain the experimental variogram is calculated for."""
    attribute: str | None = None
    """The attribute the experimental variogram is calculated for."""
    variogram_type: str = "variogram"
    """The type of calculation performed (e.g., variogram, semi-variogram, covariance, correlogram)."""
    distance_unit: UnitLength_V1_0_1_UnitCategories | None = None
    """Distance unit."""
    attribute_unit: Unit_V1_0_1 | None = None
    """Attribute unit"""

    def __post_init__(self):
        BaseObjectProperties_V1_1_0.__post_init__(self)
        if not isinstance(self.data_variance, float):
            raise ValidationFailed("self.data_variance is not float")
        if not isinstance(self.directions, ExperimentalVariogram_V1_0_0_Directions):
            raise ValidationFailed("self.directions is not ExperimentalVariogram_V1_0_0_Directions")
        if not isinstance(self.lags, ExperimentalVariogram_V1_0_0_Lags):
            raise ValidationFailed("self.lags is not ExperimentalVariogram_V1_0_0_Lags")
        if not isinstance(self.schema, str):
            raise ValidationFailed("self.schema is not str")
        if not self.schema == "/objects/experimental-variogram/1.0.0/experimental-variogram.schema.json":
            raise ValidationFailed(
                'self.schema == "/objects/experimental-variogram/1.0.0/experimental-variogram.schema.json" failed'
            )
        if self.domain is not None:
            if not isinstance(self.domain, str):
                raise ValidationFailed("self.domain is not str")
        if self.attribute is not None:
            if not isinstance(self.attribute, str):
                raise ValidationFailed("self.attribute is not str")
        if not isinstance(self.variogram_type, str):
            raise ValidationFailed("self.variogram_type is not str")
        if self.distance_unit is not None:
            if not isinstance(self.distance_unit, UnitLength_V1_0_1_UnitCategories):
                raise ValidationFailed("self.distance_unit is not UnitLength_V1_0_1_UnitCategories")
        if self.attribute_unit is not None:
            if not is_unit_v1_0_1(self.attribute_unit):
                raise ValidationFailed("is_unit_v1_0_1(self.attribute_unit) failed")
