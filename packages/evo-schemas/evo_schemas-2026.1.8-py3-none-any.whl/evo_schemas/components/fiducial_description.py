import dataclasses

from ..elements.serialiser import Serialiser, ValidationFailed


@dataclasses.dataclass(kw_only=True)
class FiducialDescription_V1_0_1(Serialiser):
    """A fiducial is a value which uniquely describes data acquired at a specific instance.

    Attributes:
        start (float): Starting fiducial number.
        increment (float): Fiducial increment amount.
    """

    SCHEMA_ID = "/components/fiducial-description/1.0.1/fiducial-description.schema.json"

    start: float
    """Starting fiducial number."""
    increment: float
    """Fiducial increment amount."""

    def __post_init__(self):
        if not isinstance(self.start, float):
            raise ValidationFailed("self.start is not float")
        if not isinstance(self.increment, float):
            raise ValidationFailed("self.increment is not float")
        if not 0.0 < self.increment:
            raise ValidationFailed("0.0 < self.increment failed")
