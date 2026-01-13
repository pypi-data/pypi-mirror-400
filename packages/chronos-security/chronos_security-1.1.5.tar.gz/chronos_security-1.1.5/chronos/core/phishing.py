"""
CHRONOS Phishing Scanner
========================

Email phishing detection with header analysis, URL reputation checking,
and suspicious content scoring.
"""

import email
import hashlib
import mailbox
import re
from dataclasses import dataclass, field
from datetime import datetime
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

from chronos.core.database import (
    EventType,
    Finding,
    FindingCategory,
    Severity,
    get_db,
)
from chronos.core.intel import ThreatIntelAggregator, URLhausResult, VTResult
from chronos.core.settings import get_settings
from chronos.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class EmailHeader:
    """Parsed email header information."""
    from_addr: str
    from_name: str
    to_addrs: List[str]
    reply_to: Optional[str] = None
    return_path: Optional[str] = None
    subject: str = ""
    date: Optional[datetime] = None
    message_id: str = ""
    received_chain: List[str] = field(default_factory=list)
    authentication_results: Dict[str, str] = field(default_factory=dict)
    x_originating_ip: Optional[str] = None
    x_mailer: Optional[str] = None


@dataclass
class PhishingIndicator:
    """Single phishing indicator."""
    type: str  # header, content, url, attachment
    name: str
    description: str
    severity: Severity
    score: float  # 0-100
    evidence: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "score": self.score,
            "evidence": self.evidence,
        }


@dataclass
class URLAnalysis:
    """URL analysis result."""
    url: str
    domain: str
    is_shortener: bool = False
    is_suspicious_tld: bool = False
    has_ip_address: bool = False
    has_long_subdomain: bool = False
    urlhaus_result: Optional[URLhausResult] = None
    vt_result: Optional[VTResult] = None
    reputation_score: float = 0.0  # 0-100, higher = more suspicious
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "domain": self.domain,
            "is_shortener": self.is_shortener,
            "is_suspicious_tld": self.is_suspicious_tld,
            "has_ip_address": self.has_ip_address,
            "has_long_subdomain": self.has_long_subdomain,
            "urlhaus": self.urlhaus_result.to_dict() if self.urlhaus_result else None,
            "virustotal": self.vt_result.to_dict() if self.vt_result else None,
            "reputation_score": self.reputation_score,
        }


@dataclass
class PhishingAnalysis:
    """Complete phishing analysis result."""
    email_hash: str
    subject: str
    from_addr: str
    headers: EmailHeader
    indicators: List[PhishingIndicator] = field(default_factory=list)
    urls_found: List[str] = field(default_factory=list)
    url_analysis: List[URLAnalysis] = field(default_factory=list)
    total_score: float = 0.0  # 0-100
    verdict: str = "unknown"  # clean, suspicious, likely_phishing, phishing
    analysis_time: datetime = field(default_factory=datetime.now)
    
    def calculate_verdict(self) -> str:
        """Calculate verdict based on total score."""
        if self.total_score >= 80:
            self.verdict = "phishing"
        elif self.total_score >= 60:
            self.verdict = "likely_phishing"
        elif self.total_score >= 30:
            self.verdict = "suspicious"
        else:
            self.verdict = "clean"
        return self.verdict
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "email_hash": self.email_hash,
            "subject": self.subject,
            "from_addr": self.from_addr,
            "indicators": [i.to_dict() for i in self.indicators],
            "urls_found": self.urls_found,
            "url_analysis": [u.to_dict() for u in self.url_analysis],
            "total_score": self.total_score,
            "verdict": self.verdict,
            "analysis_time": self.analysis_time.isoformat(),
        }


# =============================================================================
# Email Parser
# =============================================================================

class EmailParser:
    """Parse email files (.eml, .mbox) into structured data."""
    
    def parse_eml(self, file_path: Path) -> email.message.Message:
        """Parse single .eml file."""
        with open(file_path, "rb") as f:
            return email.message_from_bytes(f.read())
    
    def parse_mbox(self, file_path: Path) -> List[email.message.Message]:
        """Parse .mbox file into list of messages."""
        mbox = mailbox.mbox(str(file_path))
        return list(mbox)
    
    def parse_string(self, content: str) -> email.message.Message:
        """Parse email from string."""
        return email.message_from_string(content)
    
    def parse_bytes(self, content: bytes) -> email.message.Message:
        """Parse email from bytes."""
        return email.message_from_bytes(content)
    
    def extract_headers(self, msg: email.message.Message) -> EmailHeader:
        """Extract relevant headers from email message."""
        # From
        from_raw = msg.get("From", "")
        from_name, from_addr = parseaddr(from_raw)
        from_name = self._decode_header(from_name)
        
        # To
        to_raw = msg.get("To", "")
        to_addrs = [addr.strip() for addr in to_raw.split(",") if addr.strip()]
        
        # Reply-To
        reply_to = msg.get("Reply-To")
        if reply_to:
            _, reply_to = parseaddr(reply_to)
        
        # Return-Path
        return_path = msg.get("Return-Path")
        if return_path:
            return_path = return_path.strip("<>")
        
        # Subject
        subject = self._decode_header(msg.get("Subject", ""))
        
        # Date
        date = None
        date_str = msg.get("Date")
        if date_str:
            try:
                date = parsedate_to_datetime(date_str)
            except:
                pass
        
        # Message-ID
        message_id = msg.get("Message-ID", "").strip("<>")
        
        # Received chain
        received_chain = msg.get_all("Received", [])
        
        # Authentication results
        auth_results = {}
        auth_header = msg.get("Authentication-Results", "")
        if auth_header:
            # Parse SPF, DKIM, DMARC results
            if "spf=" in auth_header.lower():
                match = re.search(r"spf=(\w+)", auth_header, re.IGNORECASE)
                if match:
                    auth_results["spf"] = match.group(1)
            if "dkim=" in auth_header.lower():
                match = re.search(r"dkim=(\w+)", auth_header, re.IGNORECASE)
                if match:
                    auth_results["dkim"] = match.group(1)
            if "dmarc=" in auth_header.lower():
                match = re.search(r"dmarc=(\w+)", auth_header, re.IGNORECASE)
                if match:
                    auth_results["dmarc"] = match.group(1)
        
        # X-Originating-IP
        x_orig_ip = msg.get("X-Originating-IP", "").strip("[]")
        
        # X-Mailer
        x_mailer = msg.get("X-Mailer", "")
        
        return EmailHeader(
            from_addr=from_addr,
            from_name=from_name,
            to_addrs=to_addrs,
            reply_to=reply_to,
            return_path=return_path,
            subject=subject,
            date=date,
            message_id=message_id,
            received_chain=received_chain,
            authentication_results=auth_results,
            x_originating_ip=x_orig_ip if x_orig_ip else None,
            x_mailer=x_mailer if x_mailer else None,
        )
    
    def extract_body(self, msg: email.message.Message) -> Tuple[str, str]:
        """
        Extract plain text and HTML body from email.
        
        Returns:
            Tuple of (plain_text, html_text)
        """
        plain_text = ""
        html_text = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        text = payload.decode(charset, errors="replace")
                        
                        if content_type == "text/plain":
                            plain_text = text
                        elif content_type == "text/html":
                            html_text = text
                except Exception as e:
                    logger.debug(f"Failed to decode email part: {e}")
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    text = payload.decode(charset, errors="replace")
                    
                    if msg.get_content_type() == "text/html":
                        html_text = text
                    else:
                        plain_text = text
            except Exception as e:
                logger.debug(f"Failed to decode email body: {e}")
        
        return plain_text, html_text
    
    def extract_urls(self, plain_text: str, html_text: str) -> List[str]:
        """Extract all URLs from email content."""
        urls = set()
        
        # URL regex pattern
        url_pattern = r'https?://[^\s<>"\')\]]+|www\.[^\s<>"\')\]]+'
        
        # Extract from plain text
        for match in re.findall(url_pattern, plain_text, re.IGNORECASE):
            if not match.startswith("http"):
                match = "http://" + match
            urls.add(match.rstrip(".,;:"))
        
        # Extract from HTML (href attributes)
        href_pattern = r'href=["\']([^"\']+)["\']'
        for match in re.findall(href_pattern, html_text, re.IGNORECASE):
            if match.startswith(("http://", "https://", "www.")):
                if not match.startswith("http"):
                    match = "http://" + match
                urls.add(match)
        
        return list(urls)
    
    def extract_attachments(
        self,
        msg: email.message.Message,
    ) -> List[Dict[str, Any]]:
        """Extract attachment metadata."""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                    
                    content_type = part.get_content_type()
                    size = len(part.get_payload(decode=True) or b"")
                    
                    attachments.append({
                        "filename": filename or "unnamed",
                        "content_type": content_type,
                        "size": size,
                    })
        
        return attachments
    
    def _decode_header(self, header: str) -> str:
        """Decode email header value."""
        if not header:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(encoding or "utf-8", errors="replace"))
            else:
                decoded_parts.append(part)
        
        return "".join(decoded_parts)


# =============================================================================
# Phishing Analyzer
# =============================================================================

class PhishingAnalyzer:
    """
    Analyze emails for phishing indicators.
    
    Checks:
    - Header anomalies (SPF, DKIM, DMARC failures, mismatched addresses)
    - Suspicious content (urgency keywords, threats, requests)
    - URL reputation (malicious URLs, shorteners, suspicious TLDs)
    - Attachment analysis (dangerous extensions)
    """
    
    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = {
        ".exe", ".bat", ".cmd", ".com", ".scr", ".pif",
        ".vbs", ".vbe", ".js", ".jse", ".ws", ".wsf",
        ".msc", ".msi", ".msp", ".hta", ".cpl",
        ".jar", ".ps1", ".psm1", ".reg", ".lnk",
        ".docm", ".xlsm", ".pptm",  # Macro-enabled Office
    }
    
    # Brand impersonation patterns
    BRAND_PATTERNS = {
        "microsoft": ["microsoft", "office365", "outlook", "onedrive", "sharepoint"],
        "google": ["google", "gmail", "drive", "docs"],
        "apple": ["apple", "icloud", "itunes", "appstore"],
        "amazon": ["amazon", "aws", "prime"],
        "paypal": ["paypal"],
        "netflix": ["netflix"],
        "facebook": ["facebook", "meta", "instagram", "whatsapp"],
        "bank": ["bank", "banking", "secure", "account"],
    }
    
    def __init__(self):
        self._parser = EmailParser()
        self._intel = ThreatIntelAggregator()
        self._settings = get_settings()
        self._db = get_db()
    
    async def close(self) -> None:
        """Close resources."""
        await self._intel.close()
    
    async def analyze_file(self, file_path: Path) -> List[PhishingAnalysis]:
        """
        Analyze email file(s).
        
        Args:
            file_path: Path to .eml or .mbox file
        
        Returns:
            List of PhishingAnalysis results
        """
        results = []
        
        if file_path.suffix.lower() == ".mbox":
            messages = self._parser.parse_mbox(file_path)
        else:
            messages = [self._parser.parse_eml(file_path)]
        
        for msg in messages:
            result = await self.analyze_message(msg)
            results.append(result)
            
            # Store finding if suspicious
            if result.total_score >= 30:
                self._db.insert_finding(
                    category=FindingCategory.PHISHING,
                    severity=self._score_to_severity(result.total_score),
                    score=result.total_score,
                    title=f"Phishing email: {result.subject[:50]}",
                    details=result.to_dict(),
                )
        
        return results
    
    async def analyze_message(
        self,
        msg: email.message.Message,
    ) -> PhishingAnalysis:
        """
        Analyze a single email message.
        
        Args:
            msg: Email message object
        
        Returns:
            PhishingAnalysis result
        """
        # Extract components
        headers = self._parser.extract_headers(msg)
        plain_text, html_text = self._parser.extract_body(msg)
        urls = self._parser.extract_urls(plain_text, html_text)
        attachments = self._parser.extract_attachments(msg)
        
        # Generate email hash
        email_hash = hashlib.sha256(
            f"{headers.message_id}{headers.from_addr}{headers.subject}".encode()
        ).hexdigest()[:16]
        
        # Initialize analysis
        analysis = PhishingAnalysis(
            email_hash=email_hash,
            subject=headers.subject,
            from_addr=headers.from_addr,
            headers=headers,
            urls_found=urls,
        )
        
        # Run all checks
        analysis.indicators.extend(self._check_headers(headers))
        analysis.indicators.extend(self._check_content(plain_text, html_text, headers.subject))
        analysis.indicators.extend(self._check_attachments(attachments))
        
        # Analyze URLs
        url_analyses = await self._analyze_urls(urls)
        analysis.url_analysis = url_analyses
        
        # Add URL indicators
        for url_analysis in url_analyses:
            if url_analysis.reputation_score > 0:
                analysis.indicators.append(PhishingIndicator(
                    type="url",
                    name="malicious_url",
                    description=f"Suspicious URL detected: {url_analysis.domain}",
                    severity=self._score_to_severity(url_analysis.reputation_score),
                    score=url_analysis.reputation_score,
                    evidence=url_analysis.url[:100],
                ))
        
        # Calculate total score
        analysis.total_score = min(100.0, sum(i.score for i in analysis.indicators))
        analysis.calculate_verdict()
        
        logger.info(f"Email analysis: {analysis.verdict} (score: {analysis.total_score:.1f})")
        return analysis
    
    def _check_headers(self, headers: EmailHeader) -> List[PhishingIndicator]:
        """Check email headers for phishing indicators."""
        indicators = []
        
        # Check authentication results
        auth = headers.authentication_results
        
        # SPF failure
        if auth.get("spf") in ("fail", "softfail", "none"):
            indicators.append(PhishingIndicator(
                type="header",
                name="spf_failure",
                description=f"SPF check failed: {auth.get('spf')}",
                severity=Severity.HIGH,
                score=25.0,
                evidence=f"SPF={auth.get('spf')}",
            ))
        
        # DKIM failure
        if auth.get("dkim") in ("fail", "none"):
            indicators.append(PhishingIndicator(
                type="header",
                name="dkim_failure",
                description=f"DKIM check failed: {auth.get('dkim')}",
                severity=Severity.HIGH,
                score=25.0,
                evidence=f"DKIM={auth.get('dkim')}",
            ))
        
        # DMARC failure
        if auth.get("dmarc") in ("fail", "none"):
            indicators.append(PhishingIndicator(
                type="header",
                name="dmarc_failure",
                description=f"DMARC check failed: {auth.get('dmarc')}",
                severity=Severity.HIGH,
                score=20.0,
                evidence=f"DMARC={auth.get('dmarc')}",
            ))
        
        # Mismatched Reply-To
        if headers.reply_to and headers.reply_to != headers.from_addr:
            from_domain = headers.from_addr.split("@")[-1] if "@" in headers.from_addr else ""
            reply_domain = headers.reply_to.split("@")[-1] if "@" in headers.reply_to else ""
            
            if from_domain and reply_domain and from_domain.lower() != reply_domain.lower():
                indicators.append(PhishingIndicator(
                    type="header",
                    name="reply_to_mismatch",
                    description="Reply-To domain differs from From domain",
                    severity=Severity.MEDIUM,
                    score=15.0,
                    evidence=f"From: {from_domain}, Reply-To: {reply_domain}",
                ))
        
        # Mismatched Return-Path
        if headers.return_path and headers.from_addr:
            from_domain = headers.from_addr.split("@")[-1] if "@" in headers.from_addr else ""
            return_domain = headers.return_path.split("@")[-1] if "@" in headers.return_path else ""
            
            if from_domain and return_domain and from_domain.lower() != return_domain.lower():
                indicators.append(PhishingIndicator(
                    type="header",
                    name="return_path_mismatch",
                    description="Return-Path domain differs from From domain",
                    severity=Severity.MEDIUM,
                    score=10.0,
                    evidence=f"From: {from_domain}, Return-Path: {return_domain}",
                ))
        
        # Display name spoofing (name contains email address)
        if headers.from_name and "@" in headers.from_name:
            name_email = headers.from_name.split("@")[-1].split(">")[0].split()[0]
            from_email_domain = headers.from_addr.split("@")[-1] if "@" in headers.from_addr else ""
            
            if name_email and from_email_domain and name_email.lower() != from_email_domain.lower():
                indicators.append(PhishingIndicator(
                    type="header",
                    name="display_name_spoofing",
                    description="Display name contains different email address",
                    severity=Severity.HIGH,
                    score=30.0,
                    evidence=f"Name: {headers.from_name}, Actual: {headers.from_addr}",
                ))
        
        # Brand impersonation in display name
        from_name_lower = headers.from_name.lower()
        from_domain = (headers.from_addr.split("@")[-1] if "@" in headers.from_addr else "").lower()
        
        for brand, patterns in self.BRAND_PATTERNS.items():
            for pattern in patterns:
                if pattern in from_name_lower:
                    # Check if actual domain matches the brand
                    legitimate_domains = {
                        "microsoft": ["microsoft.com", "outlook.com", "live.com", "hotmail.com"],
                        "google": ["google.com", "gmail.com"],
                        "apple": ["apple.com", "icloud.com"],
                        "amazon": ["amazon.com", "amazon.co.uk", "aws.amazon.com"],
                        "paypal": ["paypal.com"],
                        "netflix": ["netflix.com"],
                        "facebook": ["facebook.com", "fb.com", "meta.com"],
                    }
                    
                    if brand in legitimate_domains:
                        if not any(from_domain.endswith(d) for d in legitimate_domains.get(brand, [])):
                            indicators.append(PhishingIndicator(
                                type="header",
                                name="brand_impersonation",
                                description=f"Possible {brand.title()} impersonation",
                                severity=Severity.HIGH,
                                score=35.0,
                                evidence=f"Name: {headers.from_name}, Domain: {from_domain}",
                            ))
                            break
        
        return indicators
    
    def _check_content(
        self,
        plain_text: str,
        html_text: str,
        subject: str,
    ) -> List[PhishingIndicator]:
        """Check email content for phishing indicators."""
        indicators = []
        content = f"{subject} {plain_text} {html_text}".lower()
        
        settings = self._settings.phishing
        
        # Check suspicious keywords
        keyword_count = 0
        found_keywords = []
        for keyword in settings.suspicious_keywords:
            if keyword.lower() in content:
                keyword_count += 1
                found_keywords.append(keyword)
        
        if keyword_count >= 3:
            indicators.append(PhishingIndicator(
                type="content",
                name="suspicious_keywords",
                description=f"Multiple suspicious keywords detected ({keyword_count})",
                severity=Severity.MEDIUM,
                score=min(20.0, keyword_count * 5),
                evidence=", ".join(found_keywords[:5]),
            ))
        
        # Urgency language
        urgency_patterns = [
            r"act\s+now",
            r"immediate\s+action",
            r"urgent",
            r"expires?\s+(today|soon|in\s+\d+)",
            r"limited\s+time",
            r"within\s+\d+\s+hours?",
            r"account\s+(will\s+be\s+)?(suspended|closed|terminated)",
            r"verify\s+(your\s+)?(account|identity)",
        ]
        
        urgency_found = []
        for pattern in urgency_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                urgency_found.append(pattern)
        
        if urgency_found:
            indicators.append(PhishingIndicator(
                type="content",
                name="urgency_language",
                description=f"Urgency tactics detected",
                severity=Severity.MEDIUM,
                score=min(15.0, len(urgency_found) * 5),
                evidence=f"Found {len(urgency_found)} urgency patterns",
            ))
        
        # Credential request
        credential_patterns = [
            r"(enter|provide|confirm|verify)\s+(your\s+)?(password|credentials|pin|ssn|social\s+security)",
            r"(sign|log)\s*in\s+(to\s+)?(verify|confirm|secure)",
            r"update\s+(your\s+)?(payment|billing|credit\s+card)",
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                indicators.append(PhishingIndicator(
                    type="content",
                    name="credential_request",
                    description="Requests credentials or sensitive information",
                    severity=Severity.HIGH,
                    score=25.0,
                    evidence=pattern[:50],
                ))
                break
        
        # Threat language
        threat_patterns = [
            r"legal\s+action",
            r"account\s+will\s+be\s+(suspended|terminated|closed)",
            r"unauthorized\s+(access|activity|transaction)",
            r"security\s+(breach|incident|alert)",
        ]
        
        for pattern in threat_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                indicators.append(PhishingIndicator(
                    type="content",
                    name="threat_language",
                    description="Contains threatening language",
                    severity=Severity.MEDIUM,
                    score=10.0,
                    evidence=pattern[:50],
                ))
                break
        
        # Hidden text (white text, small font) - HTML only
        if html_text:
            hidden_text_patterns = [
                r'color\s*:\s*(#fff|#ffffff|white)',
                r'font-size\s*:\s*[0-2]px',
                r'display\s*:\s*none',
                r'visibility\s*:\s*hidden',
            ]
            
            for pattern in hidden_text_patterns:
                if re.search(pattern, html_text, re.IGNORECASE):
                    indicators.append(PhishingIndicator(
                        type="content",
                        name="hidden_content",
                        description="Contains hidden or invisible content",
                        severity=Severity.HIGH,
                        score=20.0,
                        evidence="Hidden text CSS detected",
                    ))
                    break
        
        return indicators
    
    def _check_attachments(
        self,
        attachments: List[Dict[str, Any]],
    ) -> List[PhishingIndicator]:
        """Check attachments for suspicious files."""
        indicators = []
        
        for attachment in attachments:
            filename = attachment.get("filename", "").lower()
            extension = Path(filename).suffix.lower()
            
            if extension in self.DANGEROUS_EXTENSIONS:
                indicators.append(PhishingIndicator(
                    type="attachment",
                    name="dangerous_attachment",
                    description=f"Dangerous file type: {extension}",
                    severity=Severity.CRITICAL,
                    score=40.0,
                    evidence=filename,
                ))
            
            # Double extension (e.g., .pdf.exe)
            if filename.count(".") >= 2:
                parts = filename.rsplit(".", 2)
                if len(parts) >= 2 and f".{parts[-1]}" in self.DANGEROUS_EXTENSIONS:
                    indicators.append(PhishingIndicator(
                        type="attachment",
                        name="double_extension",
                        description="File has misleading double extension",
                        severity=Severity.CRITICAL,
                        score=35.0,
                        evidence=filename,
                    ))
            
            # Password-protected archives (often used to evade scanning)
            if extension in (".zip", ".rar", ".7z"):
                indicators.append(PhishingIndicator(
                    type="attachment",
                    name="archive_attachment",
                    description="Contains archive file (may bypass scanning)",
                    severity=Severity.LOW,
                    score=5.0,
                    evidence=filename,
                ))
        
        return indicators
    
    async def _analyze_urls(self, urls: List[str]) -> List[URLAnalysis]:
        """Analyze URLs for malicious indicators."""
        results = []
        settings = self._settings.phishing
        
        for url in urls[:20]:  # Limit to 20 URLs
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                analysis = URLAnalysis(
                    url=url,
                    domain=domain,
                )
                
                # Check if URL shortener
                for shortener in settings.url_shorteners:
                    if domain == shortener or domain.endswith(f".{shortener}"):
                        analysis.is_shortener = True
                        analysis.reputation_score += 15.0
                        break
                
                # Check suspicious TLDs
                for tld in settings.suspicious_tlds:
                    if domain.endswith(tld):
                        analysis.is_suspicious_tld = True
                        analysis.reputation_score += 10.0
                        break
                
                # Check for IP address in URL
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
                    analysis.has_ip_address = True
                    analysis.reputation_score += 20.0
                
                # Check for very long subdomain
                subdomain_parts = domain.split(".")[:-2]  # Remove TLD and domain
                if subdomain_parts and any(len(p) > 20 for p in subdomain_parts):
                    analysis.has_long_subdomain = True
                    analysis.reputation_score += 10.0
                
                # Query URLhaus
                if settings.urlhaus_enabled:
                    urlhaus_result = await self._intel.urlhaus.lookup_url(url)
                    if urlhaus_result:
                        analysis.urlhaus_result = urlhaus_result
                        if urlhaus_result.is_malicious:
                            analysis.reputation_score += 50.0
                
                # Query VirusTotal
                if settings.virustotal_enabled and self._intel.virustotal.is_configured:
                    vt_result = await self._intel.virustotal.lookup_url(url)
                    if vt_result:
                        analysis.vt_result = vt_result
                        if vt_result.is_malicious:
                            analysis.reputation_score += vt_result.detection_ratio * 50.0
                
                analysis.reputation_score = min(100.0, analysis.reputation_score)
                results.append(analysis)
                
            except Exception as e:
                logger.debug(f"URL analysis failed for {url}: {e}")
        
        return results
    
    def _score_to_severity(self, score: float) -> Severity:
        """Convert score to severity level."""
        if score >= 80:
            return Severity.CRITICAL
        elif score >= 60:
            return Severity.HIGH
        elif score >= 40:
            return Severity.MEDIUM
        elif score >= 20:
            return Severity.LOW
        else:
            return Severity.INFO
