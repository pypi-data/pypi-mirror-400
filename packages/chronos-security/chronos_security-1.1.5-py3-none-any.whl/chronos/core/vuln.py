"""
CHRONOS Vulnerability Management
================================

Import, enrich, prioritize, and track vulnerabilities from multiple sources.
Supports SARIF, Trivy JSON, and custom formats.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from chronos.core.database import (
    Finding,
    FindingCategory,
    Severity,
    get_db,
)
from chronos.core.intel import (
    CVEInfo,
    EnrichedVulnerability,
    EPSSScore,
    KEVEntry,
    ThreatIntelAggregator,
)
from chronos.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Models
# =============================================================================

class VulnSource(str, Enum):
    """Vulnerability data sources."""
    SARIF = "sarif"
    TRIVY = "trivy"
    GRYPE = "grype"
    SEMGREP = "semgrep"
    BANDIT = "bandit"
    SNYK = "snyk"
    CUSTOM = "custom"
    CHRONOS_SCAN = "chronos_scan"


class VulnStatus(str, Enum):
    """Vulnerability status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"
    WONT_FIX = "wont_fix"


@dataclass
class Vulnerability:
    """Normalized vulnerability record."""
    id: str
    source: VulnSource
    title: str
    description: str
    severity: Severity
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    cve_ids: List[str] = field(default_factory=list)
    cwe_ids: List[str] = field(default_factory=list)
    cvss_score: Optional[float] = None
    package_name: Optional[str] = None
    package_version: Optional[str] = None
    fixed_version: Optional[str] = None
    rule_id: Optional[str] = None
    
    # Enrichment data (populated by enrichment pipeline)
    epss_score: Optional[float] = None
    epss_percentile: Optional[float] = None
    in_kev: bool = False
    kev_due_date: Optional[datetime] = None
    priority_score: float = 0.0
    priority_level: str = "unknown"
    
    # Tracking
    status: VulnStatus = VulnStatus.OPEN
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def calculate_priority(self) -> float:
        """
        Calculate priority score based on multiple factors.
        
        Priority formula:
        - Base: CVSS * 10 (0-100)
        - EPSS boost: up to +30 for high exploitation likelihood
        - KEV boost: +40 if actively exploited
        - Severity adjustment: Critical +20, High +10
        """
        score = 0.0
        
        # Base CVSS score
        if self.cvss_score:
            score = self.cvss_score * 10
        else:
            # Fallback to severity-based scoring
            severity_scores = {
                Severity.CRITICAL: 90.0,
                Severity.HIGH: 70.0,
                Severity.MEDIUM: 50.0,
                Severity.LOW: 30.0,
                Severity.INFO: 10.0,
            }
            score = severity_scores.get(self.severity, 50.0)
        
        # EPSS boost
        if self.epss_score and self.epss_score > 0.1:
            score += self.epss_score * 30
        
        # KEV boost
        if self.in_kev:
            score += 40
        
        # Severity adjustment
        if self.severity == Severity.CRITICAL:
            score += 20
        elif self.severity == Severity.HIGH:
            score += 10
        
        self.priority_score = min(score, 100.0)
        
        # Set priority level
        if self.priority_score >= 80:
            self.priority_level = "critical"
        elif self.priority_score >= 60:
            self.priority_level = "high"
        elif self.priority_score >= 40:
            self.priority_level = "medium"
        else:
            self.priority_level = "low"
        
        return self.priority_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source.value,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "cve_ids": self.cve_ids,
            "cwe_ids": self.cwe_ids,
            "cvss_score": self.cvss_score,
            "package_name": self.package_name,
            "package_version": self.package_version,
            "fixed_version": self.fixed_version,
            "rule_id": self.rule_id,
            "epss_score": self.epss_score,
            "epss_percentile": self.epss_percentile,
            "in_kev": self.in_kev,
            "kev_due_date": self.kev_due_date.isoformat() if self.kev_due_date else None,
            "priority_score": self.priority_score,
            "priority_level": self.priority_level,
            "status": self.status.value,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }


# =============================================================================
# Importers
# =============================================================================

class VulnImporter:
    """Base class for vulnerability importers."""
    
    source: VulnSource = VulnSource.CUSTOM
    
    def parse(self, data: Union[str, Dict, Path]) -> List[Vulnerability]:
        """Parse vulnerability data from source."""
        raise NotImplementedError
    
    def _generate_id(self, *parts: str) -> str:
        """Generate unique vulnerability ID."""
        import hashlib
        content = "|".join(str(p) for p in parts if p)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _parse_severity(self, severity: str) -> Severity:
        """Parse severity string to enum."""
        severity = severity.upper()
        mapping = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "MODERATE": Severity.MEDIUM,
            "LOW": Severity.LOW,
            "INFO": Severity.INFO,
            "INFORMATIONAL": Severity.INFO,
            "NOTE": Severity.INFO,
            "WARNING": Severity.MEDIUM,
            "ERROR": Severity.HIGH,
        }
        return mapping.get(severity, Severity.MEDIUM)


class SARIFImporter(VulnImporter):
    """
    Import vulnerabilities from SARIF (Static Analysis Results Interchange Format).
    
    Supports SARIF v2.1.0 produced by tools like:
    - Semgrep
    - CodeQL
    - Bandit (with SARIF output)
    - ESLint (with SARIF formatter)
    """
    
    source = VulnSource.SARIF
    
    def parse(self, data: Union[str, Dict, Path]) -> List[Vulnerability]:
        """Parse SARIF file or data."""
        if isinstance(data, Path):
            with open(data) as f:
                sarif_data = json.load(f)
        elif isinstance(data, str):
            sarif_data = json.loads(data)
        else:
            sarif_data = data
        
        vulns = []
        
        for run in sarif_data.get("runs", []):
            tool_name = run.get("tool", {}).get("driver", {}).get("name", "unknown")
            rules = {
                rule["id"]: rule
                for rule in run.get("tool", {}).get("driver", {}).get("rules", [])
            }
            
            for result in run.get("results", []):
                vuln = self._parse_result(result, rules, tool_name)
                if vuln:
                    vulns.append(vuln)
        
        logger.info(f"Imported {len(vulns)} vulnerabilities from SARIF")
        return vulns
    
    def _parse_result(
        self,
        result: Dict[str, Any],
        rules: Dict[str, Dict],
        tool_name: str,
    ) -> Optional[Vulnerability]:
        """Parse single SARIF result."""
        rule_id = result.get("ruleId", "")
        rule = rules.get(rule_id, {})
        
        # Get message
        message = result.get("message", {}).get("text", "")
        if not message and rule:
            message = rule.get("shortDescription", {}).get("text", "")
        
        # Get location
        file_path = None
        line_number = None
        code_snippet = None
        
        locations = result.get("locations", [])
        if locations:
            location = locations[0].get("physicalLocation", {})
            artifact = location.get("artifactLocation", {})
            file_path = artifact.get("uri", "")
            region = location.get("region", {})
            line_number = region.get("startLine")
            code_snippet = region.get("snippet", {}).get("text")
        
        # Get severity
        severity_str = result.get("level", "warning")
        if rule:
            # Check for security-severity in properties
            props = rule.get("properties", {})
            if "security-severity" in props:
                try:
                    sec_sev = float(props["security-severity"])
                    if sec_sev >= 9.0:
                        severity_str = "critical"
                    elif sec_sev >= 7.0:
                        severity_str = "high"
                    elif sec_sev >= 4.0:
                        severity_str = "medium"
                    else:
                        severity_str = "low"
                except:
                    pass
        
        # Extract CWE IDs
        cwe_ids = []
        if rule:
            for tag in rule.get("properties", {}).get("tags", []):
                if tag.startswith("CWE-"):
                    cwe_ids.append(tag)
                elif tag.startswith("external/cwe/cwe-"):
                    cwe_ids.append(f"CWE-{tag.split('-')[-1]}")
        
        # Extract CVE IDs from message
        cve_pattern = r"CVE-\d{4}-\d{4,}"
        cve_ids = list(set(re.findall(cve_pattern, message, re.IGNORECASE)))
        
        return Vulnerability(
            id=self._generate_id(tool_name, rule_id, file_path, str(line_number)),
            source=VulnSource.SARIF,
            title=rule.get("name", rule_id) or rule_id,
            description=message,
            severity=self._parse_severity(severity_str),
            file_path=file_path,
            line_number=line_number,
            code_snippet=code_snippet,
            cve_ids=cve_ids,
            cwe_ids=cwe_ids,
            rule_id=rule_id,
        )


class TrivyImporter(VulnImporter):
    """
    Import vulnerabilities from Trivy JSON output.
    
    Supports Trivy JSON format for:
    - Container image scanning
    - Filesystem scanning
    - Git repository scanning
    """
    
    source = VulnSource.TRIVY
    
    def parse(self, data: Union[str, Dict, Path]) -> List[Vulnerability]:
        """Parse Trivy JSON output."""
        if isinstance(data, Path):
            with open(data) as f:
                trivy_data = json.load(f)
        elif isinstance(data, str):
            trivy_data = json.loads(data)
        else:
            trivy_data = data
        
        vulns = []
        
        # Handle both old and new Trivy formats
        results = trivy_data.get("Results", trivy_data.get("results", []))
        
        for result in results:
            target = result.get("Target", result.get("target", ""))
            target_type = result.get("Type", result.get("type", ""))
            
            for vuln_data in result.get("Vulnerabilities", result.get("vulnerabilities", [])):
                vuln = self._parse_vulnerability(vuln_data, target, target_type)
                if vuln:
                    vulns.append(vuln)
        
        logger.info(f"Imported {len(vulns)} vulnerabilities from Trivy")
        return vulns
    
    def _parse_vulnerability(
        self,
        data: Dict[str, Any],
        target: str,
        target_type: str,
    ) -> Optional[Vulnerability]:
        """Parse single Trivy vulnerability."""
        vuln_id = data.get("VulnerabilityID", data.get("vulnerabilityID", ""))
        pkg_name = data.get("PkgName", data.get("pkgName", ""))
        installed_version = data.get("InstalledVersion", data.get("installedVersion", ""))
        fixed_version = data.get("FixedVersion", data.get("fixedVersion", ""))
        
        title = data.get("Title", data.get("title", vuln_id))
        description = data.get("Description", data.get("description", ""))
        
        severity_str = data.get("Severity", data.get("severity", "MEDIUM"))
        
        # Get CVSS score
        cvss_score = None
        cvss_data = data.get("CVSS", data.get("cvss", {}))
        if cvss_data:
            # Prefer NVD score
            for source in ["nvd", "redhat", "ghsa"]:
                if source in cvss_data:
                    cvss_score = cvss_data[source].get("V3Score", cvss_data[source].get("v3Score"))
                    if cvss_score:
                        break
        
        # Get CWE IDs
        cwe_ids = data.get("CweIDs", data.get("cweIDs", []))
        
        return Vulnerability(
            id=self._generate_id(vuln_id, pkg_name, installed_version),
            source=VulnSource.TRIVY,
            title=title,
            description=description[:500] if description else "",
            severity=self._parse_severity(severity_str),
            file_path=target,
            cve_ids=[vuln_id] if vuln_id.startswith("CVE-") else [],
            cwe_ids=cwe_ids,
            cvss_score=cvss_score,
            package_name=pkg_name,
            package_version=installed_version,
            fixed_version=fixed_version if fixed_version else None,
        )


class GrypeImporter(VulnImporter):
    """Import vulnerabilities from Grype JSON output."""
    
    source = VulnSource.GRYPE
    
    def parse(self, data: Union[str, Dict, Path]) -> List[Vulnerability]:
        """Parse Grype JSON output."""
        if isinstance(data, Path):
            with open(data) as f:
                grype_data = json.load(f)
        elif isinstance(data, str):
            grype_data = json.loads(data)
        else:
            grype_data = data
        
        vulns = []
        
        for match in grype_data.get("matches", []):
            vuln = self._parse_match(match)
            if vuln:
                vulns.append(vuln)
        
        logger.info(f"Imported {len(vulns)} vulnerabilities from Grype")
        return vulns
    
    def _parse_match(self, match: Dict[str, Any]) -> Optional[Vulnerability]:
        """Parse single Grype match."""
        vuln_data = match.get("vulnerability", {})
        artifact = match.get("artifact", {})
        
        vuln_id = vuln_data.get("id", "")
        severity_str = vuln_data.get("severity", "Medium")
        
        # Get CVSS
        cvss_score = None
        for cvss in vuln_data.get("cvss", []):
            if cvss.get("version", "").startswith("3"):
                score_data = cvss.get("metrics", {})
                cvss_score = score_data.get("baseScore")
                break
        
        return Vulnerability(
            id=self._generate_id(vuln_id, artifact.get("name", ""), artifact.get("version", "")),
            source=VulnSource.GRYPE,
            title=vuln_id,
            description=vuln_data.get("description", "")[:500],
            severity=self._parse_severity(severity_str),
            cve_ids=[vuln_id] if vuln_id.startswith("CVE-") else [],
            cvss_score=cvss_score,
            package_name=artifact.get("name"),
            package_version=artifact.get("version"),
            fixed_version=vuln_data.get("fix", {}).get("versions", [None])[0],
        )


class BanditImporter(VulnImporter):
    """Import vulnerabilities from Bandit JSON output."""
    
    source = VulnSource.BANDIT
    
    def parse(self, data: Union[str, Dict, Path]) -> List[Vulnerability]:
        """Parse Bandit JSON output."""
        if isinstance(data, Path):
            with open(data) as f:
                bandit_data = json.load(f)
        elif isinstance(data, str):
            bandit_data = json.loads(data)
        else:
            bandit_data = data
        
        vulns = []
        
        for result in bandit_data.get("results", []):
            vuln = self._parse_result(result)
            if vuln:
                vulns.append(vuln)
        
        logger.info(f"Imported {len(vulns)} vulnerabilities from Bandit")
        return vulns
    
    def _parse_result(self, result: Dict[str, Any]) -> Optional[Vulnerability]:
        """Parse single Bandit result."""
        test_id = result.get("test_id", "")
        test_name = result.get("test_name", "")
        
        # Map Bandit test IDs to CWE
        cwe_mapping = {
            "B101": "CWE-703",  # assert
            "B102": "CWE-78",   # exec
            "B103": "CWE-732",  # chmod
            "B104": "CWE-200",  # bind all interfaces
            "B105": "CWE-259",  # hardcoded password
            "B106": "CWE-259",  # hardcoded password
            "B107": "CWE-259",  # hardcoded password
            "B108": "CWE-377",  # insecure temp file
            "B110": "CWE-703",  # try except pass
            "B112": "CWE-703",  # try except continue
            "B201": "CWE-502",  # flask debug
            "B301": "CWE-502",  # pickle
            "B302": "CWE-502",  # marshal
            "B303": "CWE-327",  # insecure hash (MD5, SHA1)
            "B304": "CWE-327",  # insecure cipher
            "B305": "CWE-327",  # insecure cipher mode
            "B306": "CWE-327",  # mktemp
            "B307": "CWE-78",   # eval
            "B308": "CWE-79",   # mark_safe
            "B310": "CWE-22",   # urllib open
            "B311": "CWE-330",  # random
            "B312": "CWE-295",  # telnetlib
            "B313": "CWE-611",  # xml
            "B314": "CWE-611",  # xml
            "B315": "CWE-611",  # xml
            "B316": "CWE-611",  # xml
            "B317": "CWE-611",  # xml
            "B318": "CWE-611",  # xml
            "B319": "CWE-611",  # xml
            "B320": "CWE-611",  # xml
            "B321": "CWE-295",  # ftplib
            "B322": "CWE-78",   # input
            "B323": "CWE-295",  # ssl unverified
            "B324": "CWE-327",  # hashlib insecure
            "B401": "CWE-295",  # import telnetlib
            "B402": "CWE-295",  # import ftplib
            "B403": "CWE-502",  # import pickle
            "B404": "CWE-78",   # import subprocess
            "B405": "CWE-611",  # import xml
            "B406": "CWE-611",  # import xml
            "B407": "CWE-611",  # import xml
            "B408": "CWE-611",  # import xml
            "B409": "CWE-611",  # import xml
            "B410": "CWE-611",  # import lxml
            "B411": "CWE-611",  # import xmlrpc
            "B412": "CWE-23",   # import httpoxy
            "B413": "CWE-327",  # import pycrypto
            "B501": "CWE-295",  # ssl verify false
            "B502": "CWE-295",  # ssl bad version
            "B503": "CWE-295",  # ssl bad defaults
            "B504": "CWE-295",  # ssl no cert
            "B505": "CWE-326",  # weak key
            "B506": "CWE-20",   # yaml load
            "B507": "CWE-295",  # ssh no host key
            "B601": "CWE-78",   # paramiko exec
            "B602": "CWE-78",   # subprocess popen shell
            "B603": "CWE-78",   # subprocess without shell
            "B604": "CWE-78",   # any other function
            "B605": "CWE-78",   # start process
            "B606": "CWE-78",   # start process no shell
            "B607": "CWE-78",   # start process partial path
            "B608": "CWE-89",   # sql injection
            "B609": "CWE-78",   # wildcard injection
            "B610": "CWE-94",   # django extra
            "B611": "CWE-94",   # django rawsql
            "B701": "CWE-94",   # jinja2 autoescape
            "B702": "CWE-79",   # mako templates
            "B703": "CWE-94",   # django mark_safe
        }
        
        cwe_ids = []
        if test_id in cwe_mapping:
            cwe_ids.append(cwe_mapping[test_id])
        
        return Vulnerability(
            id=self._generate_id(
                test_id,
                result.get("filename", ""),
                str(result.get("line_number", "")),
            ),
            source=VulnSource.BANDIT,
            title=f"{test_id}: {test_name}",
            description=result.get("issue_text", ""),
            severity=self._parse_severity(result.get("issue_severity", "MEDIUM")),
            file_path=result.get("filename"),
            line_number=result.get("line_number"),
            code_snippet=result.get("code"),
            cwe_ids=cwe_ids,
            rule_id=test_id,
        )


# =============================================================================
# Vulnerability Manager
# =============================================================================

class VulnerabilityManager:
    """
    Central vulnerability management system.
    
    Features:
    - Import from multiple sources (SARIF, Trivy, Grype, Bandit)
    - Enrichment with threat intel (EPSS, KEV, NVD)
    - Priority scoring and ranking
    - Status tracking
    - Database persistence
    """
    
    IMPORTERS: Dict[VulnSource, VulnImporter] = {
        VulnSource.SARIF: SARIFImporter(),
        VulnSource.TRIVY: TrivyImporter(),
        VulnSource.GRYPE: GrypeImporter(),
        VulnSource.BANDIT: BanditImporter(),
    }
    
    def __init__(self):
        self._db = get_db()
        self._intel = ThreatIntelAggregator()
        self._vulnerabilities: Dict[str, Vulnerability] = {}
    
    async def close(self) -> None:
        """Close resources."""
        await self._intel.close()
    
    def import_file(
        self,
        file_path: Path,
        source: Optional[VulnSource] = None,
    ) -> List[Vulnerability]:
        """
        Import vulnerabilities from a file.
        
        Args:
            file_path: Path to vulnerability report
            source: Source type (auto-detected if not specified)
        
        Returns:
            List of imported vulnerabilities
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect source
        if source is None:
            source = self._detect_source(file_path)
        
        importer = self.IMPORTERS.get(source)
        if not importer:
            raise ValueError(f"No importer for source: {source}")
        
        vulns = importer.parse(file_path)
        
        # Add to internal storage
        for vuln in vulns:
            self._vulnerabilities[vuln.id] = vuln
        
        # Store in database
        for vuln in vulns:
            self._db.insert_finding(
                category=FindingCategory.VULNERABILITY,
                severity=vuln.severity,
                score=vuln.priority_score,
                title=vuln.title,
                details=vuln.to_dict(),
                cve_id=vuln.cve_ids[0] if vuln.cve_ids else None,
            )
        
        return vulns
    
    def _detect_source(self, file_path: Path) -> VulnSource:
        """Auto-detect vulnerability source from file content."""
        try:
            with open(file_path) as f:
                data = json.load(f)
            
            # SARIF detection
            if "$schema" in data and "sarif" in data.get("$schema", ""):
                return VulnSource.SARIF
            if "runs" in data and isinstance(data["runs"], list):
                return VulnSource.SARIF
            
            # Trivy detection
            if "Results" in data or "results" in data:
                results = data.get("Results", data.get("results", []))
                if results and "Vulnerabilities" in results[0]:
                    return VulnSource.TRIVY
            
            # Grype detection
            if "matches" in data and "source" in data:
                return VulnSource.GRYPE
            
            # Bandit detection
            if "results" in data and "generated_at" in data:
                return VulnSource.BANDIT
            
        except json.JSONDecodeError:
            pass
        
        return VulnSource.CUSTOM
    
    async def enrich_all(self) -> int:
        """
        Enrich all vulnerabilities with threat intelligence.
        
        Returns:
            Number of vulnerabilities enriched
        """
        # Collect all CVE IDs
        cve_to_vulns: Dict[str, List[Vulnerability]] = {}
        for vuln in self._vulnerabilities.values():
            for cve_id in vuln.cve_ids:
                if cve_id not in cve_to_vulns:
                    cve_to_vulns[cve_id] = []
                cve_to_vulns[cve_id].append(vuln)
        
        if not cve_to_vulns:
            logger.info("No CVEs to enrich")
            return 0
        
        logger.info(f"Enriching {len(cve_to_vulns)} unique CVEs...")
        
        # Bulk fetch EPSS scores
        epss_scores = await self._intel.epss.get_scores_bulk(list(cve_to_vulns.keys()))
        
        # Bulk check KEV
        kev_entries = await self._intel.kev.check_cves_bulk(list(cve_to_vulns.keys()))
        
        # Apply enrichment
        enriched_count = 0
        for cve_id, vulns in cve_to_vulns.items():
            epss = epss_scores.get(cve_id)
            kev = kev_entries.get(cve_id)
            
            for vuln in vulns:
                if epss:
                    vuln.epss_score = epss.epss
                    vuln.epss_percentile = epss.percentile
                
                if kev:
                    vuln.in_kev = True
                    vuln.kev_due_date = kev.due_date
                
                vuln.calculate_priority()
                enriched_count += 1
        
        logger.info(f"Enriched {enriched_count} vulnerabilities")
        return enriched_count
    
    async def enrich_vulnerability(self, vuln: Vulnerability) -> Vulnerability:
        """Enrich a single vulnerability."""
        if not vuln.cve_ids:
            vuln.calculate_priority()
            return vuln
        
        # Use first CVE for enrichment
        cve_id = vuln.cve_ids[0]
        enriched = await self._intel.enrich_cve(cve_id)
        
        if enriched.epss_score:
            vuln.epss_score = enriched.epss_score.epss
            vuln.epss_percentile = enriched.epss_score.percentile
        
        if enriched.kev_entry:
            vuln.in_kev = True
            vuln.kev_due_date = enriched.kev_entry.due_date
        
        if enriched.cve_info and enriched.cve_info.cvss_v3_score:
            vuln.cvss_score = enriched.cve_info.cvss_v3_score
        
        vuln.calculate_priority()
        return vuln
    
    def get_prioritized(
        self,
        min_score: float = 0.0,
        severity: Optional[Severity] = None,
        kev_only: bool = False,
        limit: int = 100,
    ) -> List[Vulnerability]:
        """
        Get vulnerabilities sorted by priority.
        
        Args:
            min_score: Minimum priority score
            severity: Filter by severity
            kev_only: Only show KEV entries
            limit: Maximum results
        
        Returns:
            Sorted list of vulnerabilities
        """
        vulns = list(self._vulnerabilities.values())
        
        # Apply filters
        if severity:
            vulns = [v for v in vulns if v.severity == severity]
        if kev_only:
            vulns = [v for v in vulns if v.in_kev]
        if min_score > 0:
            vulns = [v for v in vulns if v.priority_score >= min_score]
        
        # Sort by priority score descending
        vulns.sort(key=lambda v: v.priority_score, reverse=True)
        
        return vulns[:limit]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get vulnerability summary statistics."""
        vulns = list(self._vulnerabilities.values())
        
        by_severity = {}
        by_priority = {}
        by_source = {}
        kev_count = 0
        has_fix_count = 0
        
        for vuln in vulns:
            # By severity
            sev = vuln.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            # By priority level
            prio = vuln.priority_level
            by_priority[prio] = by_priority.get(prio, 0) + 1
            
            # By source
            src = vuln.source.value
            by_source[src] = by_source.get(src, 0) + 1
            
            # KEV count
            if vuln.in_kev:
                kev_count += 1
            
            # Has fix
            if vuln.fixed_version:
                has_fix_count += 1
        
        return {
            "total": len(vulns),
            "by_severity": by_severity,
            "by_priority": by_priority,
            "by_source": by_source,
            "kev_count": kev_count,
            "has_fix_count": has_fix_count,
            "unique_cves": len(set(
                cve for vuln in vulns for cve in vuln.cve_ids
            )),
        }
    
    def update_status(self, vuln_id: str, status: VulnStatus) -> bool:
        """Update vulnerability status."""
        if vuln_id not in self._vulnerabilities:
            return False
        
        self._vulnerabilities[vuln_id].status = status
        return True
