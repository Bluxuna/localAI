from dataclasses import dataclass
from typing import Optional

@dataclass
class RAMInfo:
    total_gb: float
    error: Optional[str] = None