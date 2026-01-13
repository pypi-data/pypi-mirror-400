"""
CHRONOS Dark Web Monitor
========================

Monitors dark web sources and paste sites for leaked credentials,
sensitive data, and threat intelligence.

IMPORTANT: This module is intended for legitimate security research
and organizational asset protection only. Always comply with applicable
laws and terms of service.
"""

import asyncio
import hashlib
import json
import re
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Pattern,
    Set,
    Tuple,
    Union,
)
from urllib.parse import urljoin, urlparse
import queue

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from stem import Signal
    from stem.control import Controller
    STEM_AVAILABLE = True
except ImportError:
    STEM_AVAILABLE = False

try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

from chronos.cli.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SourceType(str, Enum):
    """Dark web source types."""
    PASTE_SITE = "paste_site"
    FORUM = "forum"
    MARKETPLACE = "marketplace"
    ONION_SITE = "onion_site"
    LEAK_SITE = "leak_site"
    SOCIAL = "social"
    OTHER = "other"


class MatchType(str, Enum):
    """Type of pattern match."""
    KEYWORD = "keyword"
    REGEX = "regex"
    FINGERPRINT = "fingerprint"
    EMAIL_DOMAIN = "email_domain"
    CREDIT_CARD = "credit_card"
    API_KEY = "api_key"
    CREDENTIAL = "credential"


# Common patterns for sensitive data detection
BUILTIN_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "api_key_generic": r"(?:api[_-]?key|apikey|access[_-]?token)['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{20,})",
    "aws_key": r"(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}",
    "aws_secret": r"[a-zA-Z0-9/+]{40}",
    "github_token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
    "jwt": r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
    "private_key": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
    "password_field": r"(?:password|passwd|pwd)['\"]?\s*[:=]\s*['\"]?([^\s'\"]{4,})",
    "hash_md5": r"\b[a-fA-F0-9]{32}\b",
    "hash_sha1": r"\b[a-fA-F0-9]{40}\b",
    "hash_sha256": r"\b[a-fA-F0-9]{64}\b",
    "bitcoin_address": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",
    "ethereum_address": r"\b0x[a-fA-F0-9]{40}\b",
}


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class MonitoringPattern:
    """Pattern for monitoring."""
    
    id: str
    name: str
    pattern: str
    match_type: MatchType
    severity: AlertSeverity = AlertSeverity.MEDIUM
    enabled: bool = True
    description: str = ""
    tags: List[str] = field(default_factory=list)
    compiled_regex: Optional[Pattern] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Compile regex pattern if applicable."""
        if self.match_type in (MatchType.REGEX, MatchType.EMAIL_DOMAIN):
            try:
                self.compiled_regex = re.compile(self.pattern, re.IGNORECASE)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{self.pattern}': {e}")
                self.enabled = False
    
    def matches(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Find all matches in text.
        
        Returns:
            List of (matched_text, start_pos, end_pos)
        """
        matches = []
        
        if not self.enabled:
            return matches
        
        if self.match_type == MatchType.KEYWORD:
            # Simple keyword search
            lower_text = text.lower()
            lower_pattern = self.pattern.lower()
            start = 0
            while True:
                pos = lower_text.find(lower_pattern, start)
                if pos == -1:
                    break
                matches.append((
                    text[pos:pos + len(self.pattern)],
                    pos,
                    pos + len(self.pattern)
                ))
                start = pos + 1
        
        elif self.compiled_regex:
            for match in self.compiled_regex.finditer(text):
                matches.append((
                    match.group(0),
                    match.start(),
                    match.end()
                ))
        
        return matches
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "pattern": self.pattern,
            "match_type": self.match_type.value,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "description": self.description,
            "tags": self.tags,
        }


@dataclass
class DataFingerprint:
    """Fingerprint for detecting specific data assets."""
    
    id: str
    name: str
    fingerprint_type: str  # "hash", "partial_hash", "bloom_filter"
    hash_value: str
    algorithm: str = "sha256"
    description: str = ""
    asset_type: str = ""  # "document", "database", "source_code", etc.
    sensitivity: AlertSeverity = AlertSeverity.HIGH
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_content(
        cls,
        content: Union[str, bytes],
        name: str,
        algorithm: str = "sha256",
        **kwargs,
    ) -> "DataFingerprint":
        """Create fingerprint from content."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        if algorithm == "md5":
            hash_value = hashlib.md5(content).hexdigest()
        elif algorithm == "sha1":
            hash_value = hashlib.sha1(content).hexdigest()
        elif algorithm == "sha256":
            hash_value = hashlib.sha256(content).hexdigest()
        elif algorithm == "sha512":
            hash_value = hashlib.sha512(content).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            fingerprint_type="hash",
            hash_value=hash_value,
            algorithm=algorithm,
            **kwargs,
        )
    
    @classmethod
    def from_file(
        cls,
        file_path: Union[str, Path],
        name: Optional[str] = None,
        algorithm: str = "sha256",
        **kwargs,
    ) -> "DataFingerprint":
        """Create fingerprint from file."""
        path = Path(file_path)
        content = path.read_bytes()
        return cls.from_content(
            content,
            name or path.name,
            algorithm,
            asset_type="file",
            metadata={"original_path": str(path)},
            **kwargs,
        )
    
    def matches(self, content: Union[str, bytes]) -> bool:
        """Check if content matches this fingerprint."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        if self.algorithm == "md5":
            content_hash = hashlib.md5(content).hexdigest()
        elif self.algorithm == "sha1":
            content_hash = hashlib.sha1(content).hexdigest()
        elif self.algorithm == "sha256":
            content_hash = hashlib.sha256(content).hexdigest()
        elif self.algorithm == "sha512":
            content_hash = hashlib.sha512(content).hexdigest()
        else:
            return False
        
        return content_hash.lower() == self.hash_value.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "fingerprint_type": self.fingerprint_type,
            "hash_value": self.hash_value,
            "algorithm": self.algorithm,
            "description": self.description,
            "asset_type": self.asset_type,
            "sensitivity": self.sensitivity.value,
            "metadata": self.metadata,
        }


@dataclass
class PasteEntry:
    """Represents a paste from a paste site."""
    
    id: str
    source: str
    title: Optional[str]
    author: Optional[str]
    content: str
    url: str
    timestamp: datetime
    language: Optional[str] = None
    size: int = 0
    views: int = 0
    expires: Optional[datetime] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.size == 0 and self.content:
            self.size = len(self.content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "author": self.author,
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "language": self.language,
            "size": self.size,
            "views": self.views,
            "expires": self.expires.isoformat() if self.expires else None,
        }


@dataclass
class MonitoringMatch:
    """Represents a match found during monitoring."""
    
    id: str
    pattern: MonitoringPattern
    source: str
    source_type: SourceType
    url: str
    matched_text: str
    context: str  # Surrounding text
    position: Tuple[int, int]
    timestamp: datetime = field(default_factory=datetime.now)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    paste_entry: Optional[PasteEntry] = None
    fingerprint: Optional[DataFingerprint] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "pattern_id": self.pattern.id,
            "pattern_name": self.pattern.name,
            "match_type": self.pattern.match_type.value,
            "source": self.source,
            "source_type": self.source_type.value,
            "url": self.url,
            "matched_text": self.matched_text,
            "context": self.context,
            "position": self.position,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "acknowledged": self.acknowledged,
            "metadata": self.metadata,
        }


@dataclass 
class DarkWebAlert:
    """Alert generated from dark web monitoring."""
    
    id: str
    title: str
    description: str
    severity: AlertSeverity
    matches: List[MonitoringMatch]
    source: str
    source_type: SourceType
    timestamp: datetime = field(default_factory=datetime.now)
    url: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    webhook_sent: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "matches": [m.to_dict() for m in self.matches],
            "source": self.source,
            "source_type": self.source_type.value,
            "timestamp": self.timestamp.isoformat(),
            "url": self.url,
            "recommendations": self.recommendations,
            "acknowledged": self.acknowledged,
            "webhook_sent": self.webhook_sent,
        }


# ============================================================================
# Tor Network Integration
# ============================================================================

class TorController:
    """
    Manages Tor network connections using stem library.
    
    Requires:
        - Tor service running locally
        - stem library: pip install stem
        - PySocks for SOCKS proxy: pip install pysocks
    """
    
    DEFAULT_SOCKS_PORT = 9050
    DEFAULT_CONTROL_PORT = 9051
    
    def __init__(
        self,
        socks_port: int = DEFAULT_SOCKS_PORT,
        control_port: int = DEFAULT_CONTROL_PORT,
        control_password: Optional[str] = None,
    ):
        """
        Initialize Tor controller.
        
        Args:
            socks_port: Tor SOCKS proxy port
            control_port: Tor control port
            control_password: Control port password (if set)
        """
        self.socks_port = socks_port
        self.control_port = control_port
        self.control_password = control_password
        self._controller: Optional[Controller] = None
        self._connected = False
    
    @property
    def is_available(self) -> bool:
        """Check if Tor integration is available."""
        return STEM_AVAILABLE and SOCKS_AVAILABLE
    
    def connect(self) -> bool:
        """
        Connect to Tor control port.
        
        Returns:
            True if connected successfully
        """
        if not STEM_AVAILABLE:
            logger.error("stem library not available. Install with: pip install stem")
            return False
        
        try:
            self._controller = Controller.from_port(port=self.control_port)
            if self.control_password:
                self._controller.authenticate(password=self.control_password)
            else:
                self._controller.authenticate()
            self._connected = True
            logger.info(f"Connected to Tor control port {self.control_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Tor: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Tor control port."""
        if self._controller:
            self._controller.close()
            self._controller = None
        self._connected = False
    
    def new_identity(self) -> bool:
        """
        Request new Tor circuit (new exit IP).
        
        Returns:
            True if successful
        """
        if not self._connected or not self._controller:
            logger.warning("Not connected to Tor control port")
            return False
        
        try:
            self._controller.signal(Signal.NEWNYM)
            logger.info("Requested new Tor identity")
            time.sleep(1)  # Wait for circuit to be established
            return True
        except Exception as e:
            logger.error(f"Failed to get new identity: {e}")
            return False
    
    def get_exit_ip(self) -> Optional[str]:
        """Get current exit node IP address."""
        if not self._connected:
            return None
        
        try:
            # This would require making an external request through Tor
            # Simplified: just return circuit info
            return "tor-exit"
        except Exception:
            return None
    
    def get_proxy_config(self) -> Dict[str, Any]:
        """Get proxy configuration for requests."""
        return {
            "http": f"socks5h://127.0.0.1:{self.socks_port}",
            "https": f"socks5h://127.0.0.1:{self.socks_port}",
        }
    
    def get_aiohttp_connector(self) -> Optional[Any]:
        """Get aiohttp connector for Tor proxy."""
        if not AIOHTTP_AVAILABLE:
            return None
        
        try:
            from aiohttp_socks import ProxyConnector
            return ProxyConnector.from_url(
                f"socks5://127.0.0.1:{self.socks_port}"
            )
        except ImportError:
            logger.warning("aiohttp_socks not available")
            return None
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Tor."""
        return self._connected


# ============================================================================
# Paste Site Scrapers
# ============================================================================

class BaseScraper(ABC):
    """Base class for paste site scrapers."""
    
    def __init__(
        self,
        name: str,
        base_url: str,
        rate_limit: float = 1.0,  # requests per second
        use_tor: bool = False,
        tor_controller: Optional[TorController] = None,
    ):
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.use_tor = use_tor
        self.tor_controller = tor_controller
        self._last_request_time = 0.0
        self._session: Optional[Any] = None  # aiohttp.ClientSession when available
    
    async def _get_session(self) -> Any:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            connector = None
            if self.use_tor and self.tor_controller:
                connector = self.tor_controller.get_aiohttp_connector()
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
                },
            )
        return self._session
    
    async def _rate_limit_wait(self) -> None:
        """Wait to respect rate limit."""
        if self.rate_limit > 0:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self._last_request_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
        self._last_request_time = time.time()
    
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch content from URL."""
        await self._rate_limit_wait()
        
        try:
            session = await self._get_session()
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    @abstractmethod
    async def get_recent_pastes(self, limit: int = 100) -> List[PasteEntry]:
        """Get recent pastes."""
        pass
    
    @abstractmethod
    async def get_paste_content(self, paste_id: str) -> Optional[PasteEntry]:
        """Get specific paste content."""
        pass
    
    async def search(self, query: str) -> List[PasteEntry]:
        """Search for pastes (if supported)."""
        return []
    
    async def close(self) -> None:
        """Close session."""
        if self._session and not self._session.closed:
            await self._session.close()


class PastebinScraper(BaseScraper):
    """
    Scraper for Pastebin-like sites.
    
    Note: Many paste sites have rate limits and may require API keys.
    This implementation uses public scraping endpoints.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            name="pastebin",
            base_url="https://pastebin.com",
            **kwargs,
        )
        self.api_key = api_key
    
    async def get_recent_pastes(self, limit: int = 100) -> List[PasteEntry]:
        """
        Get recent public pastes.
        
        Note: Pastebin requires PRO account for scraping API.
        This is a simplified implementation.
        """
        pastes = []
        
        # Pastebin archive page (public pastes)
        archive_url = f"{self.base_url}/archive"
        content = await self.fetch(archive_url)
        
        if not content:
            return pastes
        
        # Parse paste links from archive
        # Pattern: /paste_id
        paste_pattern = re.compile(r'href="/([a-zA-Z0-9]{8})"')
        
        for match in paste_pattern.finditer(content)[:limit]:
            paste_id = match.group(1)
            paste = await self.get_paste_content(paste_id)
            if paste:
                pastes.append(paste)
        
        return pastes
    
    async def get_paste_content(self, paste_id: str) -> Optional[PasteEntry]:
        """Get paste content by ID."""
        raw_url = f"{self.base_url}/raw/{paste_id}"
        content = await self.fetch(raw_url)
        
        if not content:
            return None
        
        return PasteEntry(
            id=paste_id,
            source=self.name,
            title=None,
            author=None,
            content=content,
            url=f"{self.base_url}/{paste_id}",
            timestamp=datetime.now(),
        )


class GhostbinScraper(BaseScraper):
    """Scraper for Ghostbin-like paste sites."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="ghostbin",
            base_url="https://ghostbin.com",
            **kwargs,
        )
    
    async def get_recent_pastes(self, limit: int = 100) -> List[PasteEntry]:
        """Get recent pastes (if available)."""
        # Ghostbin doesn't have public archive
        return []
    
    async def get_paste_content(self, paste_id: str) -> Optional[PasteEntry]:
        """Get paste content by ID."""
        raw_url = f"{self.base_url}/paste/{paste_id}/raw"
        content = await self.fetch(raw_url)
        
        if not content:
            return None
        
        return PasteEntry(
            id=paste_id,
            source=self.name,
            title=None,
            author=None,
            content=content,
            url=f"{self.base_url}/paste/{paste_id}",
            timestamp=datetime.now(),
        )


class GenericPasteScraper(BaseScraper):
    """
    Generic scraper that can be configured for various paste sites.
    """
    
    def __init__(
        self,
        name: str,
        base_url: str,
        archive_path: str = "/archive",
        raw_path: str = "/raw/{paste_id}",
        paste_pattern: str = r'href="[/]?([a-zA-Z0-9]{6,})"',
        **kwargs,
    ):
        super().__init__(name=name, base_url=base_url, **kwargs)
        self.archive_path = archive_path
        self.raw_path = raw_path
        self.paste_pattern = re.compile(paste_pattern)
    
    async def get_recent_pastes(self, limit: int = 100) -> List[PasteEntry]:
        """Get recent pastes from archive."""
        pastes = []
        
        archive_url = urljoin(self.base_url, self.archive_path)
        content = await self.fetch(archive_url)
        
        if not content:
            return pastes
        
        seen_ids = set()
        for match in self.paste_pattern.finditer(content):
            if len(pastes) >= limit:
                break
            
            paste_id = match.group(1)
            if paste_id in seen_ids:
                continue
            seen_ids.add(paste_id)
            
            paste = await self.get_paste_content(paste_id)
            if paste:
                pastes.append(paste)
        
        return pastes
    
    async def get_paste_content(self, paste_id: str) -> Optional[PasteEntry]:
        """Get paste content by ID."""
        raw_url = urljoin(
            self.base_url,
            self.raw_path.format(paste_id=paste_id)
        )
        content = await self.fetch(raw_url)
        
        if not content:
            return None
        
        return PasteEntry(
            id=paste_id,
            source=self.name,
            title=None,
            author=None,
            content=content,
            url=f"{self.base_url}/{paste_id}",
            timestamp=datetime.now(),
        )


# ============================================================================
# Webhook Alert System
# ============================================================================

class WebhookConfig:
    """Configuration for webhook notifications."""
    
    def __init__(
        self,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        template: Optional[str] = None,
        min_severity: AlertSeverity = AlertSeverity.MEDIUM,
        enabled: bool = True,
        retry_count: int = 3,
        retry_delay: float = 5.0,
    ):
        self.url = url
        self.method = method.upper()
        self.headers = headers or {"Content-Type": "application/json"}
        self.auth = auth
        self.template = template
        self.min_severity = min_severity
        self.enabled = enabled
        self.retry_count = retry_count
        self.retry_delay = retry_delay
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "method": self.method,
            "min_severity": self.min_severity.value,
            "enabled": self.enabled,
        }


class AlertDispatcher:
    """
    Dispatches alerts through various channels.
    """
    
    SEVERITY_ORDER = {
        AlertSeverity.INFO: 0,
        AlertSeverity.LOW: 1,
        AlertSeverity.MEDIUM: 2,
        AlertSeverity.HIGH: 3,
        AlertSeverity.CRITICAL: 4,
    }
    
    def __init__(self):
        self._webhooks: List[WebhookConfig] = []
        self._callbacks: List[Callable[[DarkWebAlert], None]] = []
        self._alert_queue: queue.Queue = queue.Queue()
        self._history: List[DarkWebAlert] = []
        self._max_history = 1000
    
    def add_webhook(self, config: WebhookConfig) -> None:
        """Add webhook configuration."""
        self._webhooks.append(config)
        logger.info(f"Added webhook: {config.url}")
    
    def add_callback(self, callback: Callable[[DarkWebAlert], None]) -> None:
        """Add alert callback."""
        self._callbacks.append(callback)
    
    def remove_webhook(self, url: str) -> bool:
        """Remove webhook by URL."""
        for i, webhook in enumerate(self._webhooks):
            if webhook.url == url:
                self._webhooks.pop(i)
                return True
        return False
    
    def _should_send(
        self,
        alert: DarkWebAlert,
        webhook: WebhookConfig,
    ) -> bool:
        """Check if alert should be sent to webhook."""
        if not webhook.enabled:
            return False
        
        alert_level = self.SEVERITY_ORDER.get(alert.severity, 0)
        min_level = self.SEVERITY_ORDER.get(webhook.min_severity, 0)
        
        return alert_level >= min_level
    
    def _format_payload(
        self,
        alert: DarkWebAlert,
        webhook: WebhookConfig,
    ) -> Dict[str, Any]:
        """Format alert payload for webhook."""
        if webhook.template:
            # Custom template (simplified)
            return {"text": webhook.template.format(**alert.to_dict())}
        
        # Default payload format
        return {
            "alert_id": alert.id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value,
            "source": alert.source,
            "source_type": alert.source_type.value,
            "timestamp": alert.timestamp.isoformat(),
            "url": alert.url,
            "match_count": len(alert.matches),
            "recommendations": alert.recommendations,
        }
    
    async def _send_webhook(
        self,
        alert: DarkWebAlert,
        webhook: WebhookConfig,
    ) -> bool:
        """Send alert to webhook."""
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp not available for webhook")
            return False
        
        payload = self._format_payload(alert, webhook)
        
        for attempt in range(webhook.retry_count):
            try:
                async with aiohttp.ClientSession() as session:
                    auth = None
                    if webhook.auth:
                        auth = aiohttp.BasicAuth(*webhook.auth)
                    
                    async with session.request(
                        method=webhook.method,
                        url=webhook.url,
                        json=payload,
                        headers=webhook.headers,
                        auth=auth,
                        timeout=30,
                    ) as response:
                        if response.status < 300:
                            logger.info(
                                f"Webhook sent successfully to {webhook.url}"
                            )
                            return True
                        else:
                            logger.warning(
                                f"Webhook returned {response.status}: "
                                f"{await response.text()}"
                            )
            except Exception as e:
                logger.error(f"Webhook error (attempt {attempt + 1}): {e}")
                if attempt < webhook.retry_count - 1:
                    await asyncio.sleep(webhook.retry_delay)
        
        return False
    
    async def dispatch(self, alert: DarkWebAlert) -> None:
        """Dispatch alert to all configured channels."""
        # Store in history
        self._history.append(alert)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        # Execute callbacks
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
        
        # Send to webhooks
        for webhook in self._webhooks:
            if self._should_send(alert, webhook):
                success = await self._send_webhook(alert, webhook)
                if success:
                    alert.webhook_sent = True
        
        logger.security(
            f"Alert dispatched: [{alert.severity.value.upper()}] {alert.title}"
        )
    
    def get_history(
        self,
        limit: int = 100,
        severity: Optional[AlertSeverity] = None,
        since: Optional[datetime] = None,
    ) -> List[DarkWebAlert]:
        """Get alert history."""
        alerts = self._history
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if since:
            alerts = [a for a in alerts if a.timestamp >= since]
        
        return alerts[-limit:]


# ============================================================================
# Dark Web Monitor
# ============================================================================

class DarkWebMonitor:
    """
    Main dark web monitoring system.
    
    Coordinates paste site scraping, pattern matching, fingerprint detection,
    and alert dispatch.
    
    Example:
        monitor = DarkWebMonitor()
        
        # Add patterns to monitor
        monitor.add_keyword("company-secret", severity=AlertSeverity.CRITICAL)
        monitor.add_email_domain("company.com", severity=AlertSeverity.HIGH)
        
        # Add fingerprints of sensitive documents
        monitor.add_fingerprint_from_file("secrets.txt")
        
        # Configure webhooks
        monitor.add_webhook("https://slack.webhook.url")
        
        # Start monitoring
        await monitor.start_monitoring()
    """
    
    def __init__(
        self,
        use_tor: bool = False,
        tor_socks_port: int = 9050,
        tor_control_port: int = 9051,
        tor_password: Optional[str] = None,
    ):
        """
        Initialize dark web monitor.
        
        Args:
            use_tor: Whether to route requests through Tor
            tor_socks_port: Tor SOCKS proxy port
            tor_control_port: Tor control port
            tor_password: Tor control password
        """
        self.use_tor = use_tor
        
        # Tor controller
        self._tor = TorController(
            socks_port=tor_socks_port,
            control_port=tor_control_port,
            control_password=tor_password,
        )
        
        # Scrapers
        self._scrapers: Dict[str, BaseScraper] = {}
        
        # Monitoring patterns
        self._patterns: Dict[str, MonitoringPattern] = {}
        
        # Data fingerprints
        self._fingerprints: Dict[str, DataFingerprint] = {}
        
        # Alert system
        self._dispatcher = AlertDispatcher()
        
        # State
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._scan_interval = 300  # 5 minutes default
        self._last_scan: Optional[datetime] = None
        
        # Statistics
        self._stats = {
            "scans_completed": 0,
            "pastes_scanned": 0,
            "matches_found": 0,
            "alerts_generated": 0,
        }
        
        # Initialize default scrapers
        self._init_default_scrapers()
        
        # Add built-in patterns
        self._init_builtin_patterns()
    
    def _init_default_scrapers(self) -> None:
        """Initialize default paste site scrapers."""
        self._scrapers["pastebin"] = PastebinScraper(
            use_tor=self.use_tor,
            tor_controller=self._tor,
            rate_limit=0.5,  # 1 request per 2 seconds
        )
    
    def _init_builtin_patterns(self) -> None:
        """Add built-in detection patterns (disabled by default)."""
        for name, pattern in BUILTIN_PATTERNS.items():
            self._patterns[f"builtin_{name}"] = MonitoringPattern(
                id=f"builtin_{name}",
                name=f"Built-in: {name}",
                pattern=pattern,
                match_type=MatchType.REGEX,
                severity=AlertSeverity.MEDIUM,
                enabled=False,  # Disabled by default
                description=f"Built-in pattern for detecting {name}",
                tags=["builtin", name],
            )
    
    # ========================================================================
    # Pattern Management
    # ========================================================================
    
    def add_pattern(self, pattern: MonitoringPattern) -> None:
        """Add monitoring pattern."""
        self._patterns[pattern.id] = pattern
        logger.info(f"Added pattern: {pattern.name}")
    
    def add_keyword(
        self,
        keyword: str,
        name: Optional[str] = None,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Add keyword to monitor.
        
        Returns:
            Pattern ID
        """
        pattern_id = f"keyword_{uuid.uuid4().hex[:8]}"
        pattern = MonitoringPattern(
            id=pattern_id,
            name=name or f"Keyword: {keyword}",
            pattern=keyword,
            match_type=MatchType.KEYWORD,
            severity=severity,
            tags=tags or ["keyword"],
        )
        self.add_pattern(pattern)
        return pattern_id
    
    def add_regex(
        self,
        regex: str,
        name: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Add regex pattern to monitor.
        
        Returns:
            Pattern ID
        """
        pattern_id = f"regex_{uuid.uuid4().hex[:8]}"
        pattern = MonitoringPattern(
            id=pattern_id,
            name=name,
            pattern=regex,
            match_type=MatchType.REGEX,
            severity=severity,
            tags=tags or ["regex"],
        )
        self.add_pattern(pattern)
        return pattern_id
    
    def add_email_domain(
        self,
        domain: str,
        severity: AlertSeverity = AlertSeverity.HIGH,
    ) -> str:
        """
        Add email domain to monitor for leaked credentials.
        
        Returns:
            Pattern ID
        """
        pattern_id = f"email_{uuid.uuid4().hex[:8]}"
        # Match emails with this domain
        regex = rf"[a-zA-Z0-9._%+-]+@{re.escape(domain)}"
        pattern = MonitoringPattern(
            id=pattern_id,
            name=f"Email Domain: {domain}",
            pattern=regex,
            match_type=MatchType.EMAIL_DOMAIN,
            severity=severity,
            tags=["email", "credential", domain],
        )
        self.add_pattern(pattern)
        return pattern_id
    
    def enable_builtin_pattern(self, name: str) -> bool:
        """Enable a built-in pattern."""
        key = f"builtin_{name}"
        if key in self._patterns:
            self._patterns[key].enabled = True
            return True
        return False
    
    def disable_pattern(self, pattern_id: str) -> bool:
        """Disable a pattern."""
        if pattern_id in self._patterns:
            self._patterns[pattern_id].enabled = False
            return True
        return False
    
    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern."""
        if pattern_id in self._patterns:
            del self._patterns[pattern_id]
            return True
        return False
    
    def get_patterns(self) -> List[MonitoringPattern]:
        """Get all patterns."""
        return list(self._patterns.values())
    
    # ========================================================================
    # Fingerprint Management
    # ========================================================================
    
    def add_fingerprint(self, fingerprint: DataFingerprint) -> None:
        """Add data fingerprint."""
        self._fingerprints[fingerprint.id] = fingerprint
        logger.info(f"Added fingerprint: {fingerprint.name}")
    
    def add_fingerprint_from_content(
        self,
        content: Union[str, bytes],
        name: str,
        **kwargs,
    ) -> str:
        """
        Create and add fingerprint from content.
        
        Returns:
            Fingerprint ID
        """
        fingerprint = DataFingerprint.from_content(content, name, **kwargs)
        self.add_fingerprint(fingerprint)
        return fingerprint.id
    
    def add_fingerprint_from_file(
        self,
        file_path: Union[str, Path],
        name: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Create and add fingerprint from file.
        
        Returns:
            Fingerprint ID
        """
        fingerprint = DataFingerprint.from_file(file_path, name, **kwargs)
        self.add_fingerprint(fingerprint)
        return fingerprint.id
    
    def remove_fingerprint(self, fingerprint_id: str) -> bool:
        """Remove a fingerprint."""
        if fingerprint_id in self._fingerprints:
            del self._fingerprints[fingerprint_id]
            return True
        return False
    
    def get_fingerprints(self) -> List[DataFingerprint]:
        """Get all fingerprints."""
        return list(self._fingerprints.values())
    
    # ========================================================================
    # Webhook Management
    # ========================================================================
    
    def add_webhook(
        self,
        url: str,
        min_severity: AlertSeverity = AlertSeverity.MEDIUM,
        **kwargs,
    ) -> None:
        """Add webhook for alerts."""
        config = WebhookConfig(url=url, min_severity=min_severity, **kwargs)
        self._dispatcher.add_webhook(config)
    
    def add_slack_webhook(
        self,
        webhook_url: str,
        min_severity: AlertSeverity = AlertSeverity.MEDIUM,
    ) -> None:
        """Add Slack webhook."""
        template = (
            ":warning: *CHRONOS Dark Web Alert*\n"
            "*{title}*\n"
            "Severity: `{severity}`\n"
            "Source: {source}\n"
            "{description}"
        )
        config = WebhookConfig(
            url=webhook_url,
            min_severity=min_severity,
            template=template,
        )
        self._dispatcher.add_webhook(config)
    
    def add_alert_callback(
        self,
        callback: Callable[[DarkWebAlert], None],
    ) -> None:
        """Add callback for alerts."""
        self._dispatcher.add_callback(callback)
    
    # ========================================================================
    # Scraper Management
    # ========================================================================
    
    def add_scraper(self, scraper: BaseScraper) -> None:
        """Add custom scraper."""
        self._scrapers[scraper.name] = scraper
        logger.info(f"Added scraper: {scraper.name}")
    
    def remove_scraper(self, name: str) -> bool:
        """Remove scraper."""
        if name in self._scrapers:
            del self._scrapers[name]
            return True
        return False
    
    # ========================================================================
    # Scanning
    # ========================================================================
    
    def _get_context(
        self,
        text: str,
        start: int,
        end: int,
        context_chars: int = 100,
    ) -> str:
        """Extract context around a match."""
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(text), end + context_chars)
        
        context = text[ctx_start:ctx_end]
        
        # Add ellipsis if truncated
        if ctx_start > 0:
            context = "..." + context
        if ctx_end < len(text):
            context = context + "..."
        
        return context
    
    async def _scan_paste(
        self,
        paste: PasteEntry,
    ) -> List[MonitoringMatch]:
        """Scan a single paste for matches."""
        matches = []
        
        # Pattern matching
        for pattern in self._patterns.values():
            if not pattern.enabled:
                continue
            
            for matched_text, start, end in pattern.matches(paste.content):
                match = MonitoringMatch(
                    id=str(uuid.uuid4()),
                    pattern=pattern,
                    source=paste.source,
                    source_type=SourceType.PASTE_SITE,
                    url=paste.url,
                    matched_text=matched_text,
                    context=self._get_context(paste.content, start, end),
                    position=(start, end),
                    severity=pattern.severity,
                    paste_entry=paste,
                )
                matches.append(match)
        
        # Fingerprint matching
        for fingerprint in self._fingerprints.values():
            if fingerprint.matches(paste.content):
                # Create a synthetic pattern for the match
                fp_pattern = MonitoringPattern(
                    id=fingerprint.id,
                    name=fingerprint.name,
                    pattern=fingerprint.hash_value,
                    match_type=MatchType.FINGERPRINT,
                    severity=fingerprint.sensitivity,
                )
                match = MonitoringMatch(
                    id=str(uuid.uuid4()),
                    pattern=fp_pattern,
                    source=paste.source,
                    source_type=SourceType.PASTE_SITE,
                    url=paste.url,
                    matched_text=f"[Fingerprint: {fingerprint.name}]",
                    context=paste.content[:200] + "...",
                    position=(0, len(paste.content)),
                    severity=fingerprint.sensitivity,
                    paste_entry=paste,
                    fingerprint=fingerprint,
                )
                matches.append(match)
        
        return matches
    
    async def _generate_alert(
        self,
        matches: List[MonitoringMatch],
        paste: PasteEntry,
    ) -> DarkWebAlert:
        """Generate alert from matches."""
        # Determine highest severity
        severity = max(m.severity for m in matches)
        
        # Group matches by type
        match_types = set(m.pattern.match_type.value for m in matches)
        
        title = f"Sensitive data detected on {paste.source}"
        description = (
            f"Found {len(matches)} match(es) in paste from {paste.source}.\n"
            f"Match types: {', '.join(match_types)}\n"
            f"URL: {paste.url}"
        )
        
        recommendations = [
            "Review the detected content immediately",
            "Determine if this is a legitimate leak",
            "If credentials are exposed, rotate them immediately",
            "Consider engaging incident response procedures",
        ]
        
        if any(m.fingerprint for m in matches):
            recommendations.append(
                "Fingerprint match detected - verify asset integrity"
            )
        
        return DarkWebAlert(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            severity=severity,
            matches=matches,
            source=paste.source,
            source_type=SourceType.PASTE_SITE,
            url=paste.url,
            recommendations=recommendations,
        )
    
    async def scan_all_sources(self) -> List[DarkWebAlert]:
        """
        Scan all configured sources for matches.
        
        Returns:
            List of generated alerts
        """
        alerts = []
        
        for name, scraper in self._scrapers.items():
            logger.info(f"Scanning source: {name}")
            
            try:
                pastes = await scraper.get_recent_pastes(limit=50)
                self._stats["pastes_scanned"] += len(pastes)
                
                for paste in pastes:
                    matches = await self._scan_paste(paste)
                    
                    if matches:
                        self._stats["matches_found"] += len(matches)
                        alert = await self._generate_alert(matches, paste)
                        alerts.append(alert)
                        self._stats["alerts_generated"] += 1
                        
                        # Dispatch alert
                        await self._dispatcher.dispatch(alert)
                
            except Exception as e:
                logger.error(f"Error scanning {name}: {e}")
        
        self._stats["scans_completed"] += 1
        self._last_scan = datetime.now()
        
        return alerts
    
    async def scan_content(
        self,
        content: str,
        source: str = "manual",
        url: str = "",
    ) -> List[MonitoringMatch]:
        """
        Scan arbitrary content for matches.
        
        Args:
            content: Text content to scan
            source: Source name
            url: Source URL
        
        Returns:
            List of matches found
        """
        paste = PasteEntry(
            id=str(uuid.uuid4()),
            source=source,
            title=None,
            author=None,
            content=content,
            url=url,
            timestamp=datetime.now(),
        )
        return await self._scan_paste(paste)
    
    async def scan_recent_pastes(self, limit: int = 50) -> List[PasteEntry]:
        """
        Fetch recent pastes from all configured scrapers.
        
        Args:
            limit: Maximum number of pastes to fetch per source
        
        Returns:
            List of paste entries
        """
        all_pastes = []
        
        for name, scraper in self._scrapers.items():
            try:
                pastes = await scraper.get_recent_pastes(limit=limit)
                all_pastes.extend(pastes)
                self._stats["pastes_scanned"] += len(pastes)
            except Exception as e:
                logger.error(f"Error fetching from {name}: {e}")
        
        return all_pastes
    
    # ========================================================================
    # Monitoring Loop
    # ========================================================================
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self.scan_all_sources()
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
            
            # Wait for next scan
            await asyncio.sleep(self._scan_interval)
    
    def start_monitoring(
        self,
        scan_interval: int = 300,
        background: bool = True,
    ) -> None:
        """
        Start continuous monitoring.
        
        Args:
            scan_interval: Seconds between scans
            background: Run in background thread
        """
        if self._running:
            logger.warning("Monitoring already running")
            return
        
        self._scan_interval = scan_interval
        self._running = True
        
        # Connect to Tor if enabled
        if self.use_tor:
            self._tor.connect()
        
        if background:
            def run_loop():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._monitoring_loop())
            
            self._monitor_thread = threading.Thread(
                target=run_loop,
                daemon=True,
            )
            self._monitor_thread.start()
            logger.info(
                f"Dark web monitoring started (interval: {scan_interval}s)"
            )
        else:
            asyncio.run(self._monitoring_loop())
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self._running = False
        
        if self._tor.is_connected:
            self._tor.disconnect()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        
        # Close scrapers
        for scraper in self._scrapers.values():
            asyncio.run(scraper.close())
        
        logger.info("Dark web monitoring stopped")
    
    @property
    def is_running(self) -> bool:
        """Check if monitoring is running."""
        return self._running
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            **self._stats,
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "patterns_active": sum(
                1 for p in self._patterns.values() if p.enabled
            ),
            "fingerprints_active": len(self._fingerprints),
            "scrapers_active": len(self._scrapers),
            "webhooks_configured": len(self._dispatcher._webhooks),
        }
    
    def get_alert_history(
        self,
        limit: int = 100,
        severity: Optional[AlertSeverity] = None,
    ) -> List[DarkWebAlert]:
        """Get alert history."""
        return self._dispatcher.get_history(limit=limit, severity=severity)


# ============================================================================
# Convenience Functions
# ============================================================================

def create_monitor(
    use_tor: bool = False,
    **kwargs,
) -> DarkWebMonitor:
    """Create a dark web monitor instance."""
    return DarkWebMonitor(use_tor=use_tor, **kwargs)


def quick_scan(
    content: str,
    keywords: Optional[List[str]] = None,
    email_domains: Optional[List[str]] = None,
) -> List[MonitoringMatch]:
    """
    Quick scan of content for sensitive data.
    
    Args:
        content: Text to scan
        keywords: Keywords to search for
        email_domains: Email domains to detect
    
    Returns:
        List of matches
    """
    monitor = DarkWebMonitor()
    
    # Add patterns
    if keywords:
        for keyword in keywords:
            monitor.add_keyword(keyword)
    
    if email_domains:
        for domain in email_domains:
            monitor.add_email_domain(domain)
    
    # Enable some builtin patterns
    monitor.enable_builtin_pattern("api_key_generic")
    monitor.enable_builtin_pattern("aws_key")
    monitor.enable_builtin_pattern("private_key")
    
    # Scan
    return asyncio.run(monitor.scan_content(content))
