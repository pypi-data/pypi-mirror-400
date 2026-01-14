import dataclasses

from ..elements.binary_blob import BinaryBlob_V1_0_1
from ..elements.float_array_3 import FloatArray3_V1_0_1
from .attribute_list_property import AttributeListProperty_V1_2_0
from .one_of_attribute import OneOfAttribute_V1_2_0


@dataclasses.dataclass(kw_only=True)
class DownholeDirectionVector_V1_0_0(FloatArray3_V1_0_1, AttributeListProperty_V1_2_0):
    """Represents the direction and size of a downhole segment and any associated attributes. Columns: distance, azimuth, dip.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
        attributes (OneOfAttribute_V1_2_0, optional): Attribute data.
    """

    SCHEMA_ID = "/components/downhole-direction-vector/1.0.0/downhole-direction-vector.schema.json"

    def __post_init__(self):
        FloatArray3_V1_0_1.__post_init__(self)
        AttributeListProperty_V1_2_0.__post_init__(self)
