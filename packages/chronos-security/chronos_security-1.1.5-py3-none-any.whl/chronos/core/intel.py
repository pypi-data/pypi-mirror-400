"""
CHRONOS Threat Intelligence Clients
===================================

Real API clients for threat intelligence sources:
- EPSS (Exploit Prediction Scoring System)
- NVD (National Vulnerability Database)
- CISA KEV (Known Exploited Vulnerabilities)
- URLhaus (Malicious URL Database)
- VirusTotal (File/URL Reputation)
"""

import asyncio
import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse
import json

import httpx

from chronos.core.database import get_db
from chronos.core.settings import get_api_key, get_settings
from chronos.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class CVEInfo:
    """CVE vulnerability information."""
    cve_id: str
    description: str
    cvss_v3_score: Optional[float] = None
    cvss_v3_vector: Optional[str] = None
    cvss_v2_score: Optional[float] = None
    published: Optional[datetime] = None
    modified: Optional[datetime] = None
    cwe_ids: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    affected_products: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cve_id": self.cve_id,
            "description": self.description,
            "cvss_v3_score": self.cvss_v3_score,
            "cvss_v3_vector": self.cvss_v3_vector,
            "cvss_v2_score": self.cvss_v2_score,
            "published": self.published.isoformat() if self.published else None,
            "modified": self.modified.isoformat() if self.modified else None,
            "cwe_ids": self.cwe_ids,
            "references": self.references,
            "affected_products": self.affected_products,
        }


@dataclass
class EPSSScore:
    """EPSS score for a CVE."""
    cve_id: str
    epss: float  # Probability of exploitation (0-1)
    percentile: float  # Percentile ranking (0-1)
    date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cve_id": self.cve_id,
            "epss": self.epss,
            "percentile": self.percentile,
            "date": self.date.isoformat(),
        }


@dataclass
class KEVEntry:
    """CISA KEV catalog entry."""
    cve_id: str
    vendor: str
    product: str
    vulnerability_name: str
    date_added: datetime
    short_description: str
    required_action: str
    due_date: Optional[datetime] = None
    known_ransomware_use: bool = False
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cve_id": self.cve_id,
            "vendor": self.vendor,
            "product": self.product,
            "vulnerability_name": self.vulnerability_name,
            "date_added": self.date_added.isoformat(),
            "short_description": self.short_description,
            "required_action": self.required_action,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "known_ransomware_use": self.known_ransomware_use,
            "notes": self.notes,
        }


@dataclass
class URLhausResult:
    """URLhaus URL lookup result."""
    url: str
    url_status: str  # online, offline, unknown
    host: str
    date_added: Optional[datetime] = None
    threat: str = ""  # malware_download, phishing, etc.
    tags: List[str] = field(default_factory=list)
    urlhaus_reference: str = ""
    blacklists: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_malicious(self) -> bool:
        return self.url_status == "online" or len(self.tags) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "url_status": self.url_status,
            "host": self.host,
            "date_added": self.date_added.isoformat() if self.date_added else None,
            "threat": self.threat,
            "tags": self.tags,
            "urlhaus_reference": self.urlhaus_reference,
            "blacklists": self.blacklists,
            "is_malicious": self.is_malicious,
        }


@dataclass
class VTResult:
    """VirusTotal analysis result."""
    resource: str
    resource_type: str  # url, file, domain, ip
    positives: int
    total: int
    scan_date: Optional[datetime] = None
    categories: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    threat_names: List[str] = field(default_factory=list)
    community_score: int = 0
    permalink: str = ""
    
    @property
    def detection_ratio(self) -> float:
        return self.positives / self.total if self.total > 0 else 0.0
    
    @property
    def is_malicious(self) -> bool:
        return self.positives > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource": self.resource,
            "resource_type": self.resource_type,
            "positives": self.positives,
            "total": self.total,
            "detection_ratio": self.detection_ratio,
            "scan_date": self.scan_date.isoformat() if self.scan_date else None,
            "categories": self.categories,
            "tags": self.tags,
            "threat_names": self.threat_names,
            "community_score": self.community_score,
            "permalink": self.permalink,
            "is_malicious": self.is_malicious,
        }


@dataclass
class EnrichedVulnerability:
    """Fully enriched vulnerability with all intel sources."""
    cve_id: str
    cve_info: Optional[CVEInfo] = None
    epss_score: Optional[EPSSScore] = None
    kev_entry: Optional[KEVEntry] = None
    priority_score: float = 0.0
    priority_level: str = "unknown"  # critical, high, medium, low
    
    def calculate_priority(self) -> float:
        """
        Calculate priority score combining CVSS, EPSS, and KEV status.
        
        Priority formula:
        - Base: CVSS score * 10 (0-100)
        - EPSS multiplier: 1 + (epss * 0.5) for high exploitation likelihood
        - KEV multiplier: 1.5x if in KEV catalog
        - Ransomware multiplier: 1.2x if known ransomware use
        """
        score = 0.0
        
        # Base CVSS score
        if self.cve_info and self.cve_info.cvss_v3_score:
            score = self.cve_info.cvss_v3_score * 10
        elif self.cve_info and self.cve_info.cvss_v2_score:
            score = self.cve_info.cvss_v2_score * 10
        
        # EPSS multiplier
        if self.epss_score:
            if self.epss_score.epss > 0.1:  # High exploitation likelihood
                score *= (1 + self.epss_score.epss * 0.5)
        
        # KEV multiplier
        if self.kev_entry:
            score *= 1.5
            if self.kev_entry.known_ransomware_use:
                score *= 1.2
        
        self.priority_score = min(score, 100.0)  # Cap at 100
        
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
            "cve_id": self.cve_id,
            "cve_info": self.cve_info.to_dict() if self.cve_info else None,
            "epss_score": self.epss_score.to_dict() if self.epss_score else None,
            "kev_entry": self.kev_entry.to_dict() if self.kev_entry else None,
            "priority_score": self.priority_score,
            "priority_level": self.priority_level,
        }


# =============================================================================
# Base Client
# =============================================================================

class IntelClient(ABC):
    """Base class for threat intelligence clients."""
    
    def __init__(self, timeout: float = 30.0, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self._client: Optional[httpx.AsyncClient] = None
        self._db = get_db()
        self._settings = get_settings()
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
            )
        return self._client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> Optional[httpx.Response]:
        """Make HTTP request with retries."""
        client = await self._get_client()
        
        for attempt in range(self.retries):
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code >= 500:
                    logger.warning(f"Server error {e.response.status_code}, retrying...")
                    await asyncio.sleep(1)
                else:
                    raise
            except httpx.RequestError as e:
                logger.warning(f"Request error: {e}, attempt {attempt + 1}/{self.retries}")
                await asyncio.sleep(1)
        
        return None
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is reachable."""
        pass


# =============================================================================
# EPSS Client
# =============================================================================

class EPSSClient(IntelClient):
    """
    EPSS (Exploit Prediction Scoring System) client.
    
    API: https://api.first.org/data/v1/epss
    No authentication required.
    """
    
    BASE_URL = "https://api.first.org/data/v1/epss"
    CACHE_PREFIX = "epss:"
    
    async def health_check(self) -> bool:
        """Check EPSS API availability."""
        try:
            response = await self._request("GET", f"{self.BASE_URL}?cve=CVE-2021-44228")
            return response is not None and response.status_code == 200
        except Exception:
            return False
    
    async def get_score(self, cve_id: str, use_cache: bool = True) -> Optional[EPSSScore]:
        """
        Get EPSS score for a CVE.
        
        Args:
            cve_id: CVE identifier (e.g., CVE-2021-44228)
            use_cache: Whether to use cached data
        
        Returns:
            EPSSScore or None if not found
        """
        # Normalize CVE ID
        cve_id = cve_id.upper()
        if not cve_id.startswith("CVE-"):
            cve_id = f"CVE-{cve_id}"
        
        # Check cache
        cache_key = f"{self.CACHE_PREFIX}{cve_id}"
        if use_cache:
            cached = self._db.cache_get(cache_key)
            if cached:
                return EPSSScore(
                    cve_id=cached["cve_id"],
                    epss=cached["epss"],
                    percentile=cached["percentile"],
                    date=datetime.fromisoformat(cached["date"]),
                )
        
        # Fetch from API
        try:
            response = await self._request(
                "GET",
                f"{self.BASE_URL}?cve={cve_id}",
            )
            if not response:
                return None
            
            data = response.json()
            if not data.get("data"):
                return None
            
            item = data["data"][0]
            score = EPSSScore(
                cve_id=item["cve"],
                epss=float(item["epss"]),
                percentile=float(item["percentile"]),
                date=datetime.fromisoformat(item["date"]) if item.get("date") else datetime.now(),
            )
            
            # Cache result
            cache_hours = self._settings.intel.epss_cache_hours
            self._db.cache_set(cache_key, score.to_dict(), ttl_seconds=cache_hours * 3600)
            
            logger.debug(f"EPSS score for {cve_id}: {score.epss:.4f} ({score.percentile:.2%} percentile)")
            return score
            
        except Exception as e:
            logger.error(f"Failed to get EPSS score for {cve_id}: {e}")
            return None
    
    async def get_scores_bulk(
        self,
        cve_ids: List[str],
        use_cache: bool = True,
    ) -> Dict[str, EPSSScore]:
        """
        Get EPSS scores for multiple CVEs.
        
        Args:
            cve_ids: List of CVE identifiers
            use_cache: Whether to use cached data
        
        Returns:
            Dictionary of CVE ID -> EPSSScore
        """
        results: Dict[str, EPSSScore] = {}
        uncached: List[str] = []
        
        # Check cache for each CVE
        for cve_id in cve_ids:
            cve_id = cve_id.upper()
            if not cve_id.startswith("CVE-"):
                cve_id = f"CVE-{cve_id}"
            
            if use_cache:
                cache_key = f"{self.CACHE_PREFIX}{cve_id}"
                cached = self._db.cache_get(cache_key)
                if cached:
                    results[cve_id] = EPSSScore(
                        cve_id=cached["cve_id"],
                        epss=cached["epss"],
                        percentile=cached["percentile"],
                        date=datetime.fromisoformat(cached["date"]),
                    )
                    continue
            uncached.append(cve_id)
        
        # Fetch uncached CVEs in batches
        if uncached:
            batch_size = 30  # API limit
            for i in range(0, len(uncached), batch_size):
                batch = uncached[i:i + batch_size]
                try:
                    cve_param = ",".join(batch)
                    response = await self._request(
                        "GET",
                        f"{self.BASE_URL}?cve={cve_param}",
                    )
                    if response:
                        data = response.json()
                        for item in data.get("data", []):
                            score = EPSSScore(
                                cve_id=item["cve"],
                                epss=float(item["epss"]),
                                percentile=float(item["percentile"]),
                                date=datetime.fromisoformat(item["date"]) if item.get("date") else datetime.now(),
                            )
                            results[score.cve_id] = score
                            
                            # Cache result
                            cache_key = f"{self.CACHE_PREFIX}{score.cve_id}"
                            cache_hours = self._settings.intel.epss_cache_hours
                            self._db.cache_set(cache_key, score.to_dict(), ttl_seconds=cache_hours * 3600)
                            
                except Exception as e:
                    logger.error(f"Failed to get EPSS scores for batch: {e}")
        
        return results


# =============================================================================
# NVD Client
# =============================================================================

class NVDClient(IntelClient):
    """
    NVD (National Vulnerability Database) client.
    
    API: https://services.nvd.nist.gov/rest/json/cves/2.0
    Optional API key for higher rate limits.
    """
    
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    CACHE_PREFIX = "nvd:"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._api_key = get_api_key("nvd_api_key")
        self._last_request = datetime.min
    
    async def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        settings = self._settings.intel
        wait_time = (
            settings.nvd_rate_limit_with_key 
            if self._api_key 
            else settings.nvd_rate_limit
        )
        
        elapsed = (datetime.now() - self._last_request).total_seconds()
        if elapsed < wait_time:
            await asyncio.sleep(wait_time - elapsed)
        
        self._last_request = datetime.now()
    
    async def health_check(self) -> bool:
        """Check NVD API availability."""
        try:
            await self._rate_limit()
            headers = {}
            if self._api_key:
                headers["apiKey"] = self._api_key
            
            response = await self._request(
                "GET",
                f"{self.BASE_URL}?cveId=CVE-2021-44228",
                headers=headers,
            )
            return response is not None and response.status_code == 200
        except Exception:
            return False
    
    async def get_cve(self, cve_id: str, use_cache: bool = True) -> Optional[CVEInfo]:
        """
        Get CVE information from NVD.
        
        Args:
            cve_id: CVE identifier
            use_cache: Whether to use cached data
        
        Returns:
            CVEInfo or None if not found
        """
        # Normalize CVE ID
        cve_id = cve_id.upper()
        if not cve_id.startswith("CVE-"):
            cve_id = f"CVE-{cve_id}"
        
        # Check cache
        cache_key = f"{self.CACHE_PREFIX}{cve_id}"
        if use_cache:
            cached = self._db.cache_get(cache_key)
            if cached:
                return self._parse_cached_cve(cached)
        
        # Rate limit
        await self._rate_limit()
        
        # Fetch from API
        try:
            headers = {}
            if self._api_key:
                headers["apiKey"] = self._api_key
            
            response = await self._request(
                "GET",
                f"{self.BASE_URL}?cveId={cve_id}",
                headers=headers,
            )
            if not response:
                return None
            
            data = response.json()
            if not data.get("vulnerabilities"):
                return None
            
            cve_item = data["vulnerabilities"][0]["cve"]
            cve_info = self._parse_nvd_cve(cve_item)
            
            # Cache result (24 hours)
            self._db.cache_set(cache_key, cve_info.to_dict(), ttl_seconds=86400)
            
            logger.debug(f"Fetched NVD data for {cve_id}")
            return cve_info
            
        except Exception as e:
            logger.error(f"Failed to get NVD data for {cve_id}: {e}")
            return None
    
    def _parse_nvd_cve(self, item: Dict[str, Any]) -> CVEInfo:
        """Parse NVD CVE 2.0 API response."""
        # Get description
        description = ""
        for desc in item.get("descriptions", []):
            if desc.get("lang") == "en":
                description = desc.get("value", "")
                break
        
        # Get CVSS scores
        cvss_v3_score = None
        cvss_v3_vector = None
        cvss_v2_score = None
        
        metrics = item.get("metrics", {})
        if "cvssMetricV31" in metrics:
            cvss_data = metrics["cvssMetricV31"][0].get("cvssData", {})
            cvss_v3_score = cvss_data.get("baseScore")
            cvss_v3_vector = cvss_data.get("vectorString")
        elif "cvssMetricV30" in metrics:
            cvss_data = metrics["cvssMetricV30"][0].get("cvssData", {})
            cvss_v3_score = cvss_data.get("baseScore")
            cvss_v3_vector = cvss_data.get("vectorString")
        
        if "cvssMetricV2" in metrics:
            cvss_data = metrics["cvssMetricV2"][0].get("cvssData", {})
            cvss_v2_score = cvss_data.get("baseScore")
        
        # Get CWE IDs
        cwe_ids = []
        for weakness in item.get("weaknesses", []):
            for desc in weakness.get("description", []):
                cwe_value = desc.get("value", "")
                if cwe_value.startswith("CWE-"):
                    cwe_ids.append(cwe_value)
        
        # Get references
        references = [
            ref.get("url", "")
            for ref in item.get("references", [])
            if ref.get("url")
        ]
        
        # Get affected products
        affected_products = []
        for config in item.get("configurations", []):
            for node in config.get("nodes", []):
                for cpe_match in node.get("cpeMatch", []):
                    criteria = cpe_match.get("criteria", "")
                    if criteria:
                        affected_products.append(criteria)
        
        # Parse dates
        published = None
        modified = None
        if item.get("published"):
            try:
                published = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
            except:
                pass
        if item.get("lastModified"):
            try:
                modified = datetime.fromisoformat(item["lastModified"].replace("Z", "+00:00"))
            except:
                pass
        
        return CVEInfo(
            cve_id=item.get("id", ""),
            description=description,
            cvss_v3_score=cvss_v3_score,
            cvss_v3_vector=cvss_v3_vector,
            cvss_v2_score=cvss_v2_score,
            published=published,
            modified=modified,
            cwe_ids=cwe_ids,
            references=references[:10],  # Limit references
            affected_products=affected_products[:20],  # Limit products
        )
    
    def _parse_cached_cve(self, cached: Dict[str, Any]) -> CVEInfo:
        """Parse cached CVE data."""
        return CVEInfo(
            cve_id=cached["cve_id"],
            description=cached["description"],
            cvss_v3_score=cached.get("cvss_v3_score"),
            cvss_v3_vector=cached.get("cvss_v3_vector"),
            cvss_v2_score=cached.get("cvss_v2_score"),
            published=datetime.fromisoformat(cached["published"]) if cached.get("published") else None,
            modified=datetime.fromisoformat(cached["modified"]) if cached.get("modified") else None,
            cwe_ids=cached.get("cwe_ids", []),
            references=cached.get("references", []),
            affected_products=cached.get("affected_products", []),
        )
    
    async def search_cves(
        self,
        keyword: Optional[str] = None,
        cwe_id: Optional[str] = None,
        cvss_severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20,
    ) -> List[CVEInfo]:
        """
        Search for CVEs with filters.
        
        Args:
            keyword: Search keyword
            cwe_id: Filter by CWE ID
            cvss_severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
            start_date: Published after this date
            end_date: Published before this date
            limit: Maximum results
        
        Returns:
            List of CVEInfo
        """
        await self._rate_limit()
        
        params = {"resultsPerPage": min(limit, 100)}
        
        if keyword:
            params["keywordSearch"] = keyword
        if cwe_id:
            params["cweId"] = cwe_id
        if cvss_severity:
            params["cvssV3Severity"] = cvss_severity.upper()
        if start_date:
            params["pubStartDate"] = start_date.isoformat() + "Z"
        if end_date:
            params["pubEndDate"] = end_date.isoformat() + "Z"
        
        try:
            headers = {}
            if self._api_key:
                headers["apiKey"] = self._api_key
            
            response = await self._request(
                "GET",
                self.BASE_URL,
                params=params,
                headers=headers,
            )
            if not response:
                return []
            
            data = response.json()
            return [
                self._parse_nvd_cve(vuln["cve"])
                for vuln in data.get("vulnerabilities", [])
            ]
            
        except Exception as e:
            logger.error(f"NVD search failed: {e}")
            return []


# =============================================================================
# CISA KEV Client
# =============================================================================

class KEVClient(IntelClient):
    """
    CISA Known Exploited Vulnerabilities (KEV) catalog client.
    
    Catalog URL: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
    No authentication required.
    """
    
    CACHE_KEY = "kev:catalog"
    
    async def health_check(self) -> bool:
        """Check KEV catalog availability."""
        try:
            response = await self._request("HEAD", self._settings.intel.kev_url)
            return response is not None and response.status_code == 200
        except Exception:
            return False
    
    async def get_catalog(self, use_cache: bool = True) -> List[KEVEntry]:
        """
        Get the full KEV catalog.
        
        Args:
            use_cache: Whether to use cached data
        
        Returns:
            List of KEVEntry
        """
        # Check cache
        if use_cache:
            cached = self._db.cache_get(self.CACHE_KEY)
            if cached:
                return [self._parse_cached_entry(e) for e in cached]
        
        # Fetch catalog
        try:
            response = await self._request("GET", self._settings.intel.kev_url)
            if not response:
                return []
            
            data = response.json()
            entries = [
                self._parse_kev_entry(vuln)
                for vuln in data.get("vulnerabilities", [])
            ]
            
            # Cache result
            cache_hours = self._settings.intel.kev_cache_hours
            self._db.cache_set(
                self.CACHE_KEY,
                [e.to_dict() for e in entries],
                ttl_seconds=cache_hours * 3600,
            )
            
            logger.info(f"Loaded {len(entries)} entries from CISA KEV catalog")
            return entries
            
        except Exception as e:
            logger.error(f"Failed to fetch KEV catalog: {e}")
            return []
    
    async def check_cve(self, cve_id: str) -> Optional[KEVEntry]:
        """
        Check if a CVE is in the KEV catalog.
        
        Args:
            cve_id: CVE identifier
        
        Returns:
            KEVEntry if found, None otherwise
        """
        cve_id = cve_id.upper()
        if not cve_id.startswith("CVE-"):
            cve_id = f"CVE-{cve_id}"
        
        catalog = await self.get_catalog()
        for entry in catalog:
            if entry.cve_id == cve_id:
                return entry
        
        return None
    
    async def check_cves_bulk(self, cve_ids: List[str]) -> Dict[str, KEVEntry]:
        """
        Check multiple CVEs against KEV catalog.
        
        Args:
            cve_ids: List of CVE identifiers
        
        Returns:
            Dictionary of CVE ID -> KEVEntry for found CVEs
        """
        # Normalize CVE IDs
        normalized = set()
        for cve_id in cve_ids:
            cve_id = cve_id.upper()
            if not cve_id.startswith("CVE-"):
                cve_id = f"CVE-{cve_id}"
            normalized.add(cve_id)
        
        catalog = await self.get_catalog()
        results = {}
        for entry in catalog:
            if entry.cve_id in normalized:
                results[entry.cve_id] = entry
        
        return results
    
    def _parse_kev_entry(self, data: Dict[str, Any]) -> KEVEntry:
        """Parse KEV catalog entry."""
        date_added = None
        due_date = None
        
        if data.get("dateAdded"):
            try:
                date_added = datetime.strptime(data["dateAdded"], "%Y-%m-%d")
            except:
                pass
        
        if data.get("dueDate"):
            try:
                due_date = datetime.strptime(data["dueDate"], "%Y-%m-%d")
            except:
                pass
        
        return KEVEntry(
            cve_id=data.get("cveID", ""),
            vendor=data.get("vendorProject", ""),
            product=data.get("product", ""),
            vulnerability_name=data.get("vulnerabilityName", ""),
            date_added=date_added or datetime.now(),
            short_description=data.get("shortDescription", ""),
            required_action=data.get("requiredAction", ""),
            due_date=due_date,
            known_ransomware_use=data.get("knownRansomwareCampaignUse", "Unknown").lower() == "known",
            notes=data.get("notes", ""),
        )
    
    def _parse_cached_entry(self, data: Dict[str, Any]) -> KEVEntry:
        """Parse cached KEV entry."""
        return KEVEntry(
            cve_id=data["cve_id"],
            vendor=data["vendor"],
            product=data["product"],
            vulnerability_name=data["vulnerability_name"],
            date_added=datetime.fromisoformat(data["date_added"]),
            short_description=data["short_description"],
            required_action=data["required_action"],
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            known_ransomware_use=data.get("known_ransomware_use", False),
            notes=data.get("notes", ""),
        )


# =============================================================================
# URLhaus Client
# =============================================================================

class URLhausClient(IntelClient):
    """
    URLhaus malicious URL database client.
    
    API: https://urlhaus-api.abuse.ch/v1/
    No authentication required for basic lookups.
    """
    
    async def health_check(self) -> bool:
        """Check URLhaus API availability."""
        try:
            response = await self._request(
                "POST",
                f"{self._settings.intel.urlhaus_api_url}url/",
                data={"url": "https://example.com"},
            )
            return response is not None
        except Exception:
            return False
    
    async def lookup_url(self, url: str) -> Optional[URLhausResult]:
        """
        Look up a URL in URLhaus.
        
        Args:
            url: URL to check
        
        Returns:
            URLhausResult or None if not found/error
        """
        try:
            response = await self._request(
                "POST",
                f"{self._settings.intel.urlhaus_api_url}url/",
                data={"url": url},
            )
            if not response:
                return None
            
            data = response.json()
            if data.get("query_status") == "no_results":
                return None
            
            if data.get("query_status") != "ok":
                logger.warning(f"URLhaus query status: {data.get('query_status')}")
                return None
            
            date_added = None
            if data.get("date_added"):
                try:
                    date_added = datetime.strptime(data["date_added"], "%Y-%m-%d %H:%M:%S UTC")
                except:
                    pass
            
            return URLhausResult(
                url=data.get("url", url),
                url_status=data.get("url_status", "unknown"),
                host=data.get("host", urlparse(url).netloc),
                date_added=date_added,
                threat=data.get("threat", ""),
                tags=data.get("tags", []),
                urlhaus_reference=data.get("urlhaus_reference", ""),
                blacklists=data.get("blacklists", {}),
            )
            
        except Exception as e:
            logger.error(f"URLhaus lookup failed for {url}: {e}")
            return None
    
    async def lookup_host(self, host: str) -> List[URLhausResult]:
        """
        Look up all malicious URLs for a host.
        
        Args:
            host: Domain or IP to check
        
        Returns:
            List of URLhausResult
        """
        try:
            response = await self._request(
                "POST",
                f"{self._settings.intel.urlhaus_api_url}host/",
                data={"host": host},
            )
            if not response:
                return []
            
            data = response.json()
            if data.get("query_status") != "ok":
                return []
            
            results = []
            for url_item in data.get("urls", []):
                date_added = None
                if url_item.get("date_added"):
                    try:
                        date_added = datetime.strptime(url_item["date_added"], "%Y-%m-%d %H:%M:%S UTC")
                    except:
                        pass
                
                results.append(URLhausResult(
                    url=url_item.get("url", ""),
                    url_status=url_item.get("url_status", "unknown"),
                    host=host,
                    date_added=date_added,
                    threat=url_item.get("threat", ""),
                    tags=url_item.get("tags", []),
                    urlhaus_reference=url_item.get("urlhaus_reference", ""),
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"URLhaus host lookup failed for {host}: {e}")
            return []


# =============================================================================
# VirusTotal Client
# =============================================================================

class VirusTotalClient(IntelClient):
    """
    VirusTotal v3 API client.
    
    API: https://www.virustotal.com/api/v3/
    Requires API key.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._api_key = get_api_key("virustotal_api_key")
    
    @property
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return self._api_key is not None
    
    async def health_check(self) -> bool:
        """Check VirusTotal API availability."""
        if not self.is_configured:
            return False
        try:
            response = await self._request(
                "GET",
                f"{self._settings.intel.virustotal_api_url}urls/aHR0cHM6Ly9leGFtcGxlLmNvbQ==",
                headers={"x-apikey": self._api_key},
            )
            return response is not None
        except Exception:
            return False
    
    async def lookup_url(self, url: str) -> Optional[VTResult]:
        """
        Look up a URL in VirusTotal.
        
        Args:
            url: URL to check
        
        Returns:
            VTResult or None if not found/error
        """
        if not self.is_configured:
            logger.warning("VirusTotal API key not configured")
            return None
        
        import base64
        
        try:
            # URL ID is base64 of the URL without padding
            url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
            
            response = await self._request(
                "GET",
                f"{self._settings.intel.virustotal_api_url}urls/{url_id}",
                headers={"x-apikey": self._api_key},
            )
            if not response:
                return None
            
            data = response.json()
            attributes = data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            
            positives = stats.get("malicious", 0) + stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 0
            
            scan_date = None
            if attributes.get("last_analysis_date"):
                scan_date = datetime.fromtimestamp(attributes["last_analysis_date"])
            
            return VTResult(
                resource=url,
                resource_type="url",
                positives=positives,
                total=total,
                scan_date=scan_date,
                categories=attributes.get("categories", {}),
                tags=attributes.get("tags", []),
                threat_names=[
                    result.get("result", "")
                    for result in attributes.get("last_analysis_results", {}).values()
                    if result.get("category") in ("malicious", "suspicious") and result.get("result")
                ],
                community_score=attributes.get("reputation", 0),
                permalink=f"https://www.virustotal.com/gui/url/{url_id}",
            )
            
        except Exception as e:
            logger.error(f"VirusTotal URL lookup failed: {e}")
            return None
    
    async def lookup_file_hash(self, file_hash: str) -> Optional[VTResult]:
        """
        Look up a file hash in VirusTotal.
        
        Args:
            file_hash: MD5, SHA1, or SHA256 hash
        
        Returns:
            VTResult or None if not found/error
        """
        if not self.is_configured:
            logger.warning("VirusTotal API key not configured")
            return None
        
        try:
            response = await self._request(
                "GET",
                f"{self._settings.intel.virustotal_api_url}files/{file_hash}",
                headers={"x-apikey": self._api_key},
            )
            if not response:
                return None
            
            data = response.json()
            attributes = data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            
            positives = stats.get("malicious", 0) + stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 0
            
            scan_date = None
            if attributes.get("last_analysis_date"):
                scan_date = datetime.fromtimestamp(attributes["last_analysis_date"])
            
            return VTResult(
                resource=file_hash,
                resource_type="file",
                positives=positives,
                total=total,
                scan_date=scan_date,
                tags=attributes.get("tags", []),
                threat_names=attributes.get("popular_threat_classification", {}).get("suggested_threat_label", "").split("/"),
                community_score=attributes.get("reputation", 0),
                permalink=f"https://www.virustotal.com/gui/file/{file_hash}",
            )
            
        except Exception as e:
            logger.error(f"VirusTotal file lookup failed: {e}")
            return None
    
    async def lookup_domain(self, domain: str) -> Optional[VTResult]:
        """
        Look up a domain in VirusTotal.
        
        Args:
            domain: Domain to check
        
        Returns:
            VTResult or None if not found/error
        """
        if not self.is_configured:
            logger.warning("VirusTotal API key not configured")
            return None
        
        try:
            response = await self._request(
                "GET",
                f"{self._settings.intel.virustotal_api_url}domains/{domain}",
                headers={"x-apikey": self._api_key},
            )
            if not response:
                return None
            
            data = response.json()
            attributes = data.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            
            positives = stats.get("malicious", 0) + stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 0
            
            return VTResult(
                resource=domain,
                resource_type="domain",
                positives=positives,
                total=total,
                categories=attributes.get("categories", {}),
                tags=attributes.get("tags", []),
                community_score=attributes.get("reputation", 0),
                permalink=f"https://www.virustotal.com/gui/domain/{domain}",
            )
            
        except Exception as e:
            logger.error(f"VirusTotal domain lookup failed: {e}")
            return None


# =============================================================================
# Intel Aggregator
# =============================================================================

class ThreatIntelAggregator:
    """
    Aggregates threat intelligence from all sources.
    
    Provides unified interface for vulnerability enrichment
    and IOC lookups.
    """
    
    def __init__(self):
        self.epss = EPSSClient()
        self.nvd = NVDClient()
        self.kev = KEVClient()
        self.urlhaus = URLhausClient()
        self.virustotal = VirusTotalClient()
    
    async def close(self) -> None:
        """Close all clients."""
        await asyncio.gather(
            self.epss.close(),
            self.nvd.close(),
            self.kev.close(),
            self.urlhaus.close(),
            self.virustotal.close(),
        )
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all intel sources."""
        results = await asyncio.gather(
            self.epss.health_check(),
            self.nvd.health_check(),
            self.kev.health_check(),
            self.urlhaus.health_check(),
            self.virustotal.health_check(),
            return_exceptions=True,
        )
        
        return {
            "epss": results[0] if not isinstance(results[0], Exception) else False,
            "nvd": results[1] if not isinstance(results[1], Exception) else False,
            "kev": results[2] if not isinstance(results[2], Exception) else False,
            "urlhaus": results[3] if not isinstance(results[3], Exception) else False,
            "virustotal": results[4] if not isinstance(results[4], Exception) else False,
        }
    
    async def enrich_cve(self, cve_id: str) -> EnrichedVulnerability:
        """
        Fully enrich a CVE with all intel sources.
        
        Args:
            cve_id: CVE identifier
        
        Returns:
            EnrichedVulnerability with all available data
        """
        cve_id = cve_id.upper()
        if not cve_id.startswith("CVE-"):
            cve_id = f"CVE-{cve_id}"
        
        # Fetch all data in parallel
        cve_info_task = self.nvd.get_cve(cve_id)
        epss_task = self.epss.get_score(cve_id)
        kev_task = self.kev.check_cve(cve_id)
        
        cve_info, epss_score, kev_entry = await asyncio.gather(
            cve_info_task,
            epss_task,
            kev_task,
            return_exceptions=True,
        )
        
        # Handle exceptions
        if isinstance(cve_info, Exception):
            cve_info = None
        if isinstance(epss_score, Exception):
            epss_score = None
        if isinstance(kev_entry, Exception):
            kev_entry = None
        
        enriched = EnrichedVulnerability(
            cve_id=cve_id,
            cve_info=cve_info,
            epss_score=epss_score,
            kev_entry=kev_entry,
        )
        enriched.calculate_priority()
        
        return enriched
    
    async def enrich_cves_bulk(
        self,
        cve_ids: List[str],
    ) -> List[EnrichedVulnerability]:
        """
        Enrich multiple CVEs in parallel.
        
        Args:
            cve_ids: List of CVE identifiers
        
        Returns:
            List of EnrichedVulnerability
        """
        tasks = [self.enrich_cve(cve_id) for cve_id in cve_ids]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    async def check_url_reputation(self, url: str) -> Dict[str, Any]:
        """
        Check URL reputation across multiple sources.
        
        Args:
            url: URL to check
        
        Returns:
            Combined reputation data
        """
        urlhaus_task = self.urlhaus.lookup_url(url)
        vt_task = self.virustotal.lookup_url(url) if self.virustotal.is_configured else None
        
        tasks = [urlhaus_task]
        if vt_task:
            tasks.append(vt_task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        urlhaus_result = results[0] if not isinstance(results[0], Exception) else None
        vt_result = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None
        
        is_malicious = False
        threat_score = 0.0
        sources_checked = 0
        
        if urlhaus_result:
            sources_checked += 1
            if urlhaus_result.is_malicious:
                is_malicious = True
                threat_score += 50.0
        
        if vt_result:
            sources_checked += 1
            if vt_result.is_malicious:
                is_malicious = True
                threat_score += vt_result.detection_ratio * 50.0
        
        return {
            "url": url,
            "is_malicious": is_malicious,
            "threat_score": threat_score,
            "sources_checked": sources_checked,
            "urlhaus": urlhaus_result.to_dict() if urlhaus_result else None,
            "virustotal": vt_result.to_dict() if vt_result else None,
        }
