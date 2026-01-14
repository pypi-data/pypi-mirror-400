import dataclasses

from ..elements.float_array_1 import FloatArray1_V1_0_1
from ..elements.serialiser import Serialiser, ValidationFailed
from ..elements.unit_time import UnitTime_V1_0_1_UnitCategories
from .attribute_description import AttributeDescription_V1_0_1
from .base_continuous_attribute import BaseContinuousAttribute_V1_0_0


@dataclasses.dataclass(kw_only=True)
class TimeStepContinuousAttribute_V1_1_0(BaseContinuousAttribute_V1_0_0):
    """A component that represents elapsed time (sec, min, hours, months, etc.) since a start time.

    Attributes:
        attribute_type (str): Type of the attribute.
        values (FloatArray1_V1_0_1): The values of the attributes.
        unit (UnitTime_V1_0_1_UnitCategories): Time step unit.
        start_time (str, optional): start time
        attribute_description (AttributeDescription_V1_0_1, optional): The attribute description record.
        name (str): The name of the attribute
        key (str): An identifier of the attribute, used to keep track of the attribute when it is renamed.
    The identifier must be unique within an attribute list.
    """

    SCHEMA_ID = "/components/time-step-continuous-attribute/1.1.0/time-step-continuous-attribute.schema.json"

    values: FloatArray1_V1_0_1
    """The values of the attributes."""
    unit: UnitTime_V1_0_1_UnitCategories
    """Time step unit."""
    attribute_type: str = "scalar"
    start_time: str | None = None
    """start time"""

    def __post_init__(self):
        BaseContinuousAttribute_V1_0_0.__post_init__(self)
        if not isinstance(self.values, FloatArray1_V1_0_1):
            raise ValidationFailed("self.values is not FloatArray1_V1_0_1")
        if not isinstance(self.unit, UnitTime_V1_0_1_UnitCategories):
            raise ValidationFailed("self.unit is not UnitTime_V1_0_1_UnitCategories")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "scalar":
            raise ValidationFailed('self.attribute_type == "scalar" failed')
        if self.start_time is not None:
            if not isinstance(self.start_time, str):
                raise ValidationFailed("self.start_time is not str")
            if not Serialiser.is_date_time(self.start_time):
                raise ValidationFailed("Serialiser.is_date_time(self.start_time) failed")


@dataclasses.dataclass(kw_only=True)
class TimeStepContinuousAttribute_V1_0_1(Serialiser):
    """A component that represents elapsed time (sec, min, hours, months, etc.) since a start time.

    Attributes:
        name (str): The name of the attribute.
        attribute_type (str): Type of the attribute.
        attribute_description (AttributeDescription_V1_0_1, optional): The attribute description record.
        values (FloatArray1_V1_0_1): The values of the attributes.
        unit (UnitTime_V1_0_1_UnitCategories): Time step unit.
        start_time (str, optional): start time
    """

    SCHEMA_ID = "/components/time-step-continuous-attribute/1.0.1/time-step-continuous-attribute.schema.json"

    name: str
    """The name of the attribute."""
    values: FloatArray1_V1_0_1
    """The values of the attributes."""
    unit: UnitTime_V1_0_1_UnitCategories
    """Time step unit."""
    attribute_type: str = "scalar"
    """Type of the attribute."""
    attribute_description: AttributeDescription_V1_0_1 | None = None
    """The attribute description record."""
    start_time: str | None = None
    """start time"""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.values, FloatArray1_V1_0_1):
            raise ValidationFailed("self.values is not FloatArray1_V1_0_1")
        if not isinstance(self.unit, UnitTime_V1_0_1_UnitCategories):
            raise ValidationFailed("self.unit is not UnitTime_V1_0_1_UnitCategories")
        if not isinstance(self.attribute_type, str):
            raise ValidationFailed("self.attribute_type is not str")
        if not self.attribute_type == "scalar":
            raise ValidationFailed('self.attribute_type == "scalar" failed')
        if self.attribute_description is not None:
            if not isinstance(self.attribute_description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.attribute_description is not AttributeDescription_V1_0_1")
        if self.start_time is not None:
            if not isinstance(self.start_time, str):
                raise ValidationFailed("self.start_time is not str")
            if not Serialiser.is_date_time(self.start_time):
                raise ValidationFailed("Serialiser.is_date_time(self.start_time) failed")
