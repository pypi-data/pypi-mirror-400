from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from allytools.units import Length, LengthUnit
from typing import Any, SupportsIndex, overload, Union
from numpy.typing import NDArray

_IntIndexArray = NDArray[np.integer]
_BoolIndexArray = NDArray[np.bool_]

@dataclass(frozen=True, slots=True)
class LengthArray:
    values_mm: np.ndarray
    unit: LengthUnit = LengthUnit.MM

    @classmethod
    def from_value(cls, value: np.ndarray, unit: LengthUnit) -> LengthArray:
        value = np.asarray(value, dtype=np.float64)
        return cls(values_mm=value * unit.factor, unit=unit)

    def to(self, unit: LengthUnit) -> np.ndarray:
        return self.values_mm / unit.factor

    def to_length(self, unit: LengthUnit) -> LengthArray:
        return LengthArray(self.values_mm, unit)

    def copy(self) -> LengthArray:
        return LengthArray(values_mm=self.values_mm.copy(), unit=self.unit)

    def mean(self, axis=None, where=None, keep_dims: bool = False):
        val_mm = np.mean(self.values_mm, axis=axis, where=where, keepdims=keep_dims)
        if np.isscalar(val_mm) or getattr(val_mm, "shape", ()) == ():
            return Length(float(val_mm)).to_length(self.unit)
        return LengthArray(values_mm=np.asarray(val_mm, dtype=np.float64), unit=self.unit)

    def __array__(self, dtype=None) -> np.ndarray:
        arr = self.values_mm
        if dtype is None:
            return arr
        return arr.astype(dtype, copy=False)

    @property
    def shape(self) -> tuple[int, ...]:
        return self.values_mm.shape

    @overload
    def __getitem__(self, idx: SupportsIndex) -> Length: ...
    @overload
    def __getitem__(self, idx: slice) -> "LengthArray": ...
    @overload
    def __getitem__(self, idx: _IntIndexArray) -> "LengthArray": ...
    @overload
    def __getitem__(self, idx: _BoolIndexArray) -> "LengthArray": ...
    @overload
    def __getitem__(self, idx: tuple[SupportsIndex, ...]) -> Length: ...
    @overload
    def __getitem__(self, idx: tuple[Any, ...]) -> "LengthArray": ...

    def __getitem__(self, idx: Any) -> Union[Length, "LengthArray"]:
        out = self.values_mm[idx]

        # NumPy scalar / 0-d array -> Length
        if np.isscalar(out) or (isinstance(out, np.ndarray) and out.ndim == 0):
            return Length(float(out)).to_length(self.unit)

        # Anything array-like -> LengthArray (preserve unit)
        return LengthArray(values_mm=np.asarray(out, dtype=np.float64), unit=self.unit)

    @overload
    def __setitem__(self, idx: Any, value: "LengthArray") -> None: ...
    @overload
    def __setitem__(self, idx: Any, value: Length) -> None: ...
    @overload
    def __setitem__(self, idx: Any, value: Any) -> None: ...

    def __setitem__(self, idx: Any, value: Any) -> None:
        # dataclass(frozen=True) -> still allow internal ndarray mutation
        arr = object.__getattribute__(self, "values_mm")

        if isinstance(value, LengthArray):
            arr[idx] = value.values_mm
            return

        if isinstance(value, Length):
            arr[idx] = value.value_mm
            return

        # Numeric (scalar or array): assume it's expressed in *self.unit* (not mm)
        v = np.asarray(value, dtype=np.float64)
        arr[idx] = v * self.unit.factor

    def __truediv__(self, other):
        if isinstance(other, Length):
            return self.values_mm / other.value_mm
        if np.isscalar(other):
            return LengthArray(values_mm=self.values_mm / float(other), unit=self.unit)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Length):
            mm = other.value_mm
            return LengthArray(self.values_mm - mm, self.unit)
        if isinstance(other, LengthArray):
            return LengthArray(self.values_mm - other.values_mm, self.unit)
        # numeric: assume in self.unit
        return LengthArray(self.values_mm - float(other) * self.unit.factor, self.unit)

    def __rsub__(self, other):
        if isinstance(other, Length):
            mm = other.value_mm
            return LengthArray(mm - self.values_mm, self.unit)
        if isinstance(other, LengthArray):
            return LengthArray(other.values_mm - self.values_mm, self.unit)
        return LengthArray(float(other) * self.unit.factor - self.values_mm, self.unit)