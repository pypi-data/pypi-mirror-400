from __future__ import annotations
from dataclasses import dataclass
from math import isinf
import numbers
from allytools.units.quantity import Quantity
from allytools.units.angle import Angle
from allytools.units.angle_unit import AngleUnit
from allytools.units.length_unit import LengthUnit
from allytools.units.length_unit import length_unit_from_token

def make_length(value: float | None, token: str | None) -> Length | None:
    if value is None or token is None:
        return None
    unit = length_unit_from_token(token)
    return Length(value, unit)

def average_length(a: Length | None, b: Length | None) -> Length | None:
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    avg_mm = 0.5 * (a.value_mm + b.value_mm)
    return Length(avg_mm)

class UnitConverter:
    def __init__(self, length: Length):
        self.length = length

    def __call__(self, unit: LengthUnit) -> float:
        return self.length.value_mm / unit.factor

    def __getitem__(self, unit: LengthUnit) -> float:
        return self(unit)


@dataclass(frozen=True)
class Length(Quantity[LengthUnit]):
    value_mm: float
    _original_unit: LengthUnit = LengthUnit.MM  # Default if not set

    def __init__(self, value: float, unit: LengthUnit = LengthUnit.MM):
        object.__setattr__(self, "value_mm", value * unit.factor)
        object.__setattr__(self, "_original_unit", unit)

    @property
    def value(self) -> float:
        return self.to(self._original_unit)

    @property
    def unit(self) -> LengthUnit:
        return self._original_unit

    def original_unit(self) -> LengthUnit:
        return self._original_unit

    @staticmethod
    def infinity() -> Length:
        return Length(float("inf"))

    def is_infinite(self) -> bool:
        return isinf(self.value_mm)

    def to(self, unit: LengthUnit) -> float:
        return self.value_mm / unit.factor

    def to_length(self, unit: LengthUnit) -> Length:
        return Length(self.to(unit), unit)

    def _with_value_mm(self, value_mm: float) -> Length:
        unit = self._original_unit
        value_in_unit = value_mm / unit.factor
        return Length(value_in_unit, unit)

    def is_zero(self, *, atol_mm: float = 1e-12) -> bool:
        return abs(self.value_mm) <= atol_mm

    def zero_like(self) -> Length:
        return Length(0.0, self.unit)

    def __str__(self) -> str:
        if self.is_infinite():
            return f"∞ {self._original_unit}"
        value = self.to(self._original_unit)
        return f"{value:.2f} {self._original_unit}"

    def __add__(self, other: Length) -> Length:
        if not type(other) is Length:
            return NotImplemented
        return self._with_value_mm(self.value_mm + other.value_mm)

    def __sub__(self, other: Length) -> Length:
        if not type(other) is Length:
            return NotImplemented
        return self._with_value_mm(self.value_mm - other.value_mm)

    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            return self._with_value_mm(self.value_mm * float(other))
        elif type(other) is Angle:
            if other.original_unit() != AngleUnit.RAD:
                raise ValueError("Length can only be multiplied by angles in radians.")
            angle_rad = other.to(AngleUnit.RAD)
            return Length(self.value_mm * angle_rad)
        elif type(other) is Length:
            from allytools.units.area import Area
            return Area(self.value_mm * other.value_mm)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other: object) -> bool:
        if not type(other) is Length:
            return NotImplemented
        return abs(self.value_mm - other.value_mm) < 1e-6

    def __lt__(self, other: "Length") -> bool:
        return self.value_mm < other.value_mm

    def __truediv__(self, other):
        if type(other) is Length:
            return self.value_mm / other.value_mm  # dimensionless
        elif isinstance(other, numbers.Real):
            return self._with_value_mm(self.value_mm / float(other))
        return NotImplemented

    def __le__(self, other: Length) -> bool:
        return self.value_mm <= other.value_mm

    def __gt__(self, other: Length) -> bool:
        return self.value_mm > other.value_mm

    def __ge__(self, other: Length) -> bool:
        return self.value_mm >= other.value_mm
