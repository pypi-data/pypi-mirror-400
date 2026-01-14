from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class VisionState:
    name: str
    detected: bool
    confidence: float = 0.0

    attempts: int = 0
    elapsed: float = 0.0

    text: Optional[str] = None
    icon: Optional[str] = None
    reason: Optional[str] = None

    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def __bool__(self):
        return self.detected
