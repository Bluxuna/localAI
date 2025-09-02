
from dataclasses import dataclass
from typing import Optional

@dataclass
class StorageInfo:
    total_gb: float
    error: Optional[str] = None