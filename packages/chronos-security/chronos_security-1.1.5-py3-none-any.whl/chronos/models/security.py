"""
CHRONOS Security Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class VulnerabilitySeverity(Enum):
    """Vulnerability severity classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""
    
    id: str
    title: str
    severity: VulnerabilitySeverity
    description: str
    affected_component: str
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    quantum_impact: bool = False
    remediation: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert vulnerability to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "affected_component": self.affected_component,
            "cve_id": self.cve_id,
            "cvss_score": self.cvss_score,
            "quantum_impact": self.quantum_impact,
            "remediation": self.remediation,
            "discovered_at": self.discovered_at.isoformat(),
        }


@dataclass
class SecurityReport:
    """Security assessment report."""
    
    id: str
    title: str
    generated_at: datetime = field(default_factory=datetime.now)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    risk_score: float = 0.0
    quantum_readiness_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def critical_count(self) -> int:
        """Count of critical vulnerabilities."""
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        """Count of high severity vulnerabilities."""
        return sum(1 for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.HIGH)
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "generated_at": self.generated_at.isoformat(),
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "risk_score": self.risk_score,
            "quantum_readiness_score": self.quantum_readiness_score,
            "recommendations": self.recommendations,
            "summary": {
                "total": len(self.vulnerabilities),
                "critical": self.critical_count,
                "high": self.high_count,
            }
        }
