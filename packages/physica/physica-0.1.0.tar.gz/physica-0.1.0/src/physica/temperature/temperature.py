from __future__ import annotations
from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True, slots=True)
class Temperature:
    _kelvin: float
    _KELVIN_OFFSET: Final[float] = 273.15

    @classmethod
    def from_kelvin(cls, value: float) -> Temperature:
        if value < 0:
            raise ValueError("Temperature in Kelvin cannot be negative")
        return cls(value)

    @classmethod
    def from_celsius(cls, value: float) -> Temperature:
        return cls.from_kelvin(value + cls._KELVIN_OFFSET)

    @classmethod
    def from_fahrenheit(cls, value: float) -> Temperature:
        return cls.from_kelvin((value - 32.0) * 5.0 / 9.0 + cls._KELVIN_OFFSET)
    @property
    def kelvin(self) -> float:
        return self._kelvin

    @property
    def celsius(self) -> float:
        return self._kelvin - self._KELVIN_OFFSET

    @property
    def fahrenheit(self) -> float:
        return (self.celsius * 9.0 / 5.0) + 32.0

    def __add__(self, delta: float) -> Temperature:
        """Add temperature difference (in Kelvin)."""
        return Temperature.from_kelvin(self._kelvin + delta)

    def __sub__(self, other: Temperature | float) -> float | Temperature:
        if isinstance(other, Temperature):
            return self._kelvin - other._kelvin  # ΔT in Kelvin
        return Temperature.from_kelvin(self._kelvin - other)

    def __lt__(self, other: Temperature) -> bool:
        return self._kelvin < other._kelvin

    def __le__(self, other: Temperature) -> bool:
        return self._kelvin <= other._kelvin

    def __gt__(self, other: Temperature) -> bool:
        return self._kelvin > other._kelvin

    def __ge__(self, other: Temperature) -> bool:
        return self._kelvin >= other._kelvin

    def __repr__(self) -> str:
        return f"Temperature({self.celsius:.2f} °C)"
