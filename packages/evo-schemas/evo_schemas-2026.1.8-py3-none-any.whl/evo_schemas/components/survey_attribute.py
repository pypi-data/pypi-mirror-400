import dataclasses

from ..elements.bool_array_md import BoolArrayMd_V1_0_1
from ..elements.color_array import ColorArray_V1_0_1
from ..elements.date_time_array import DateTimeArray_V1_0_1
from ..elements.float_array_md import FloatArrayMd_V1_0_1
from ..elements.integer_array_md import IntegerArrayMd_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.string_array import StringArray_V1_0_1
from .fiducial_description import FiducialDescription_V1_0_1

SurveyAttribute_V1_0_1_Values = (
    BoolArrayMd_V1_0_1
    | FloatArrayMd_V1_0_1
    | IntegerArrayMd_V1_0_1
    | DateTimeArray_V1_0_1
    | StringArray_V1_0_1
    | ColorArray_V1_0_1
)


@dataclasses.dataclass(kw_only=True)
class SurveyAttribute_V1_0_1(Serialiser):
    """A list of values corresponding to survey data.

    Attributes:
        key (str): A key that identifies the attribute definition.
        fiducial (FiducialDescription_V1_0_1): The fiducial properties of the attribute.
        values (SurveyAttribute_V1_0_1_Values): Values associated with the attribute.
    """

    SCHEMA_ID = "/components/survey-attribute/1.0.1/survey-attribute.schema.json"

    key: str
    """A key that identifies the attribute definition."""
    fiducial: FiducialDescription_V1_0_1
    """The fiducial properties of the attribute."""
    values: SurveyAttribute_V1_0_1_Values
    """Values associated with the attribute."""

    def __post_init__(self):
        if not isinstance(self.key, str):
            raise ValidationFailed("self.key is not str")
        if not isinstance(self.fiducial, FiducialDescription_V1_0_1):
            raise ValidationFailed("self.fiducial is not FiducialDescription_V1_0_1")
        if not isinstance(self.values, SurveyAttribute_V1_0_1_Values):
            raise ValidationFailed("self.values is not SurveyAttribute_V1_0_1_Values")
