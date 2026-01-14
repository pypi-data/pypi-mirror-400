import dataclasses

from ..elements.coordinates_3d import Coordinates3D_V1_0_0
from ..elements.serialiser import Serialiser, ValidationFailed
from .attribute_description import AttributeDescription_V1_0_1


@dataclasses.dataclass(kw_only=True)
class SurveyAttributeDefinition_V1_0_1(Serialiser):
    """Common properties for attributes in survey data.

    Attributes:
        name (str): The name of the attribute.
        key (str): An identifier of the attribute. Must be unique within a list of attributes.
        offset (Coordinates3D_V1_0_0, optional): Offset of attribute measurements relative to the point of reference.
        significant_digits (int, optional): Significant digits.
        description (AttributeDescription_V1_0_1, optional): Attribute-specific properties for survey data.
    """

    SCHEMA_ID = "/components/survey-attribute-definition/1.0.1/survey-attribute-definition.schema.json"

    name: str
    """The name of the attribute."""
    key: str
    """An identifier of the attribute. Must be unique within a list of attributes."""
    offset: Coordinates3D_V1_0_0 | None = None
    """Offset of attribute measurements relative to the point of reference."""
    significant_digits: int | None = None
    """Significant digits."""
    description: AttributeDescription_V1_0_1 | None = None
    """Attribute-specific properties for survey data."""

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise ValidationFailed("self.name is not str")
        if not isinstance(self.key, str):
            raise ValidationFailed("self.key is not str")
        if self.offset is not None:
            if not isinstance(self.offset, Coordinates3D_V1_0_0):
                raise ValidationFailed("self.offset is not Coordinates3D_V1_0_0")
        if self.significant_digits is not None:
            if not isinstance(self.significant_digits, int):
                raise ValidationFailed("self.significant_digits is not int")
            if not 0 <= self.significant_digits:
                raise ValidationFailed("0 <= self.significant_digits failed")
        if self.description is not None:
            if not isinstance(self.description, AttributeDescription_V1_0_1):
                raise ValidationFailed("self.description is not AttributeDescription_V1_0_1")
