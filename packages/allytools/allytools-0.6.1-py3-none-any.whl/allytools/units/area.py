from dataclasses import dataclass
from allytools.units.quantity import Quantity
from allytools.units.area_unit import AreaUnit
@dataclass(frozen=True)
class Area(Quantity[AreaUnit]):
    value_mm2: float
    _original_unit: AreaUnit = AreaUnit.MM2

    def __init__(self, value: float, unit: AreaUnit = AreaUnit.MM2):
        object.__setattr__(self, "value_mm2", value * unit.factor)
        object.__setattr__(self, "_original_unit", unit)

    @property
    def value(self) -> float:
        return self.to(self._original_unit)

    @property
    def unit(self) -> AreaUnit:
        return self._original_unit

    def original_unit(self) -> AreaUnit:
        return self._original_unit

    def to(self, unit: AreaUnit) -> float:
        return self.value_mm2 / unit.factor

    def to_area(self, unit: AreaUnit) -> "Area":
        return Area(self.to(unit), unit)

    def __str__(self) -> str:
        v = self.to(self._original_unit)
        return f"{v:.2f} {self._original_unit}"

    def __add__(self, other: object) -> "Area":
        if not isinstance(other, Area):
            return NotImplemented
        return Area(self.value_mm2 + other.value_mm2)

    def __sub__(self, other: object) -> "Area":
        if not isinstance(other, Area):
            return NotImplemented
        return Area(self.value_mm2 - other.value_mm2)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Area(self.value_mm2 * other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        # Area / Area -> dimensionless
        if isinstance(other, Area):
            return self.value_mm2 / other.value_mm2

        # Area / scalar -> Area
        if isinstance(other, (int, float)):
            return Area(self.value_mm2 / other)

        # Area / Length -> Length
        from allytools.units.length import Length  # adjust import path to your project
        if isinstance(other, Length):
            return Length(self.value_mm2 / other.value_mm)

        return NotImplemented
