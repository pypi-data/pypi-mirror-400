import dataclasses

from .binary_blob import BinaryBlob_V1_0_1
from .integer_array_md import IntegerArrayMd_V1_0_1
from .serialiser import ValidationFailed


@dataclasses.dataclass(kw_only=True)
class IntegerArray1_V1_0_1(IntegerArrayMd_V1_0_1):
    """Array of integers.

    Attributes:
        width (int): number of columns
        data (BinaryBlob_V1_0_1): Data stored as a binary blob.
        length (int): length of array
        data_type (str): data type
    """

    SCHEMA_ID = "/elements/integer-array-1/1.0.1/integer-array-1.schema.json"

    width: int = 1
    """number of columns"""

    def __post_init__(self):
        IntegerArrayMd_V1_0_1.__post_init__(self)
        if not isinstance(self.width, int):
            raise ValidationFailed("self.width is not int")
        if not self.width == 1:
            raise ValidationFailed("self.width == 1 failed")
