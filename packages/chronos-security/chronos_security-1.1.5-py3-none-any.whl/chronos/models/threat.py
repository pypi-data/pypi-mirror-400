"""
CHRONOS Threat Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class ThreatLevel(Enum):
    """Threat severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Threat:
    """Represents a security threat."""
    
    id: str
    name: str
    level: ThreatLevel
    description: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    quantum_vulnerable: bool = False
    mitigations: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def is_critical(self) -> bool:
        """Check if threat is critical."""
        return self.level == ThreatLevel.CRITICAL
    
    def is_quantum_threat(self) -> bool:
        """Check if threat is quantum-related."""
        return self.quantum_vulnerable
    
    def to_dict(self) -> Dict:
        """Convert threat to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "description": self.description,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "quantum_vulnerable": self.quantum_vulnerable,
            "mitigations": self.mitigations,
            "metadata": self.metadata,
        }
