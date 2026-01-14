import dataclasses

from .binary_blob import BinaryBlob_V1_0_1
from .float_array_md import FloatArrayMd_V1_0_1
from .serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class FloatArray6_V1_0_1(FloatArrayMd_V1_0_1):
    """Array of 6 floats.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
    """

    SCHEMA_ID = "/elements/float-array-6/1.0.1/float-array-6.schema.json"

    width: int = 6
    """number of columns"""

    def __post_init__(self):
        FloatArrayMd_V1_0_1.__post_init__(self)
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 6:
            raise ValidationFailed("self.width == 6 failed")
