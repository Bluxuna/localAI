from dataclasses import dataclass
from typing import Optional

@dataclass
class GPUInfo:
    name: str
    vram_gb: float
    error: Optional[str] = None