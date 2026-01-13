from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CheckConfig:
    timeout: int
    max_workers: int
    delay: float
    blacklist: List[str]
