

from enum import Enum




class AreaUnit(Enum):
    MM2 = 1.0
    CM2 = 100.0          # (10 mm)^2
    M2 = 1_000_000.0     # (1000 mm)^2

    @property
    def factor(self) -> float:
        """How many mm^2 in 1 unit."""
        return float(self.value)

    def __str__(self) -> str:
        return self.name.lower()
