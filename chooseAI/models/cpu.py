from dataclasses import dataclass
from typing import Optional
@dataclass
class CPUInfo:
    name: str
    physical_cores: Optional[int]
    logical_cores: Optional[int]
    clock_speed_ghz: Optional[float]
    error: Optional[str] = None