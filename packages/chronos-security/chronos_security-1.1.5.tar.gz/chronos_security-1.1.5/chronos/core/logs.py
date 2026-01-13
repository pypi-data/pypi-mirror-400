"""
CHRONOS Log Analysis
====================

Log ingestion, parsing, baseline creation, and anomaly detection
using IsolationForest for security event monitoring.
"""

import gzip
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Union
import statistics

from chronos.core.database import (
    EventType,
    Finding,
    FindingCategory,
    Severity,
    get_db,
)
from chronos.core.settings import get_settings
from chronos.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Models
# =============================================================================

class LogSource(str, Enum):
    """Supported log sources."""
    SYSLOG = "syslog"
    AUTH_LOG = "auth_log"
    WINDOWS_SECURITY = "windows_security"
    WINDOWS_SYSTEM = "windows_system"
    CLOUDTRAIL = "cloudtrail"
    AZURE_ACTIVITY = "azure_activity"
    NGINX = "nginx"
    APACHE = "apache"
    JSON_LINES = "json_lines"
    CUSTOM = "custom"


class AnomalyType(str, Enum):
    """Types of detected anomalies."""
    FREQUENCY_SPIKE = "frequency_spike"
    NEW_SOURCE = "new_source"
    UNUSUAL_TIME = "unusual_time"
    FAILED_AUTH = "failed_auth"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_COMMAND = "suspicious_command"
    DATA_EXFILTRATION = "data_exfiltration"
    PATTERN_DEVIATION = "pattern_deviation"


@dataclass
class LogEntry:
    """Normalized log entry."""
    timestamp: datetime
    source: LogSource
    raw: str
    message: str
    severity: str = "info"
    host: Optional[str] = None
    user: Optional[str] = None
    process: Optional[str] = None
    event_type: Optional[str] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "raw": self.raw[:500],
            "message": self.message[:500],
            "severity": self.severity,
            "host": self.host,
            "user": self.user,
            "process": self.process,
            "event_type": self.event_type,
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "action": self.action,
            "status": self.status,
            "extra": self.extra,
        }


@dataclass
class BaselineMetrics:
    """Baseline metrics for anomaly detection."""
    name: str
    created_at: datetime
    source: str
    total_events: int
    time_range_hours: float
    
    # Event frequency metrics
    events_per_hour_mean: float
    events_per_hour_std: float
    events_by_hour: Dict[int, int] = field(default_factory=dict)  # Hour -> count
    events_by_day: Dict[int, int] = field(default_factory=dict)  # Weekday -> count
    
    # Source metrics
    known_hosts: Set[str] = field(default_factory=set)
    known_users: Set[str] = field(default_factory=set)
    known_ips: Set[str] = field(default_factory=set)
    
    # Event type distribution
    event_type_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Authentication metrics
    auth_success_rate: float = 1.0
    failed_auth_per_hour_mean: float = 0.0
    failed_auth_per_hour_std: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "source": self.source,
            "total_events": self.total_events,
            "time_range_hours": self.time_range_hours,
            "events_per_hour_mean": self.events_per_hour_mean,
            "events_per_hour_std": self.events_per_hour_std,
            "events_by_hour": self.events_by_hour,
            "events_by_day": self.events_by_day,
            "known_hosts": list(self.known_hosts),
            "known_users": list(self.known_users),
            "known_ips": list(self.known_ips),
            "event_type_distribution": self.event_type_distribution,
            "auth_success_rate": self.auth_success_rate,
            "failed_auth_per_hour_mean": self.failed_auth_per_hour_mean,
            "failed_auth_per_hour_std": self.failed_auth_per_hour_std,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaselineMetrics":
        return cls(
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            source=data["source"],
            total_events=data["total_events"],
            time_range_hours=data["time_range_hours"],
            events_per_hour_mean=data["events_per_hour_mean"],
            events_per_hour_std=data["events_per_hour_std"],
            events_by_hour={int(k): v for k, v in data.get("events_by_hour", {}).items()},
            events_by_day={int(k): v for k, v in data.get("events_by_day", {}).items()},
            known_hosts=set(data.get("known_hosts", [])),
            known_users=set(data.get("known_users", [])),
            known_ips=set(data.get("known_ips", [])),
            event_type_distribution=data.get("event_type_distribution", {}),
            auth_success_rate=data.get("auth_success_rate", 1.0),
            failed_auth_per_hour_mean=data.get("failed_auth_per_hour_mean", 0.0),
            failed_auth_per_hour_std=data.get("failed_auth_per_hour_std", 0.0),
        )


@dataclass
class Anomaly:
    """Detected anomaly."""
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: Severity
    score: float  # 0-100
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    related_entries: List[LogEntry] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "score": self.score,
            "description": self.description,
            "evidence": self.evidence,
            "related_entry_count": len(self.related_entries),
        }


# =============================================================================
# Log Parsers
# =============================================================================

class LogParser:
    """Base log parser."""
    
    source: LogSource = LogSource.CUSTOM
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """Parse single log line."""
        raise NotImplementedError
    
    def can_parse(self, sample_lines: List[str]) -> bool:
        """Check if parser can handle this log format."""
        try:
            parsed = 0
            for line in sample_lines[:10]:
                if self.parse_line(line):
                    parsed += 1
            return parsed >= len(sample_lines[:10]) * 0.5
        except:
            return False


class SyslogParser(LogParser):
    """
    Parse standard syslog format.
    
    Format: <priority>timestamp hostname process[pid]: message
    Example: Jan  5 14:30:01 server sshd[12345]: Accepted password for user
    """
    
    source = LogSource.SYSLOG
    
    # Syslog pattern
    PATTERN = re.compile(
        r"^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+"
        r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<host>\S+)\s+"
        r"(?P<process>\S+?)(?:\[(?P<pid>\d+)\])?\s*:\s*"
        r"(?P<message>.*)$"
    )
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        match = self.PATTERN.match(line.strip())
        if not match:
            return None
        
        groups = match.groupdict()
        
        # Parse timestamp (assume current year)
        try:
            timestamp_str = f"{groups['month']} {groups['day']} {groups['time']}"
            timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
            timestamp = timestamp.replace(year=datetime.now().year)
        except:
            timestamp = datetime.now()
        
        # Determine severity from message
        message = groups.get("message", "")
        severity = self._extract_severity(message)
        
        # Extract user from common patterns
        user = self._extract_user(message)
        
        # Extract IP from common patterns
        source_ip = self._extract_ip(message)
        
        return LogEntry(
            timestamp=timestamp,
            source=self.source,
            raw=line,
            message=message,
            severity=severity,
            host=groups.get("host"),
            process=groups.get("process"),
            user=user,
            source_ip=source_ip,
            extra={"pid": groups.get("pid")},
        )
    
    def _extract_severity(self, message: str) -> str:
        """Extract severity from message content."""
        message_lower = message.lower()
        if any(w in message_lower for w in ["error", "fail", "denied", "invalid"]):
            return "error"
        if any(w in message_lower for w in ["warn", "timeout", "retry"]):
            return "warning"
        if any(w in message_lower for w in ["critical", "fatal", "emergency"]):
            return "critical"
        return "info"
    
    def _extract_user(self, message: str) -> Optional[str]:
        """Extract username from common log patterns."""
        patterns = [
            r"user[=:\s]+(\w+)",
            r"for\s+(\w+)\s+from",
            r"session\s+(?:opened|closed)\s+for\s+user\s+(\w+)",
            r"pam_unix\([^)]+\):\s+(?:session|authentication)\s+\S+\s+for\s+user\s+(\w+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_ip(self, message: str) -> Optional[str]:
        """Extract IP address from message."""
        ip_pattern = r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b"
        match = re.search(ip_pattern, message)
        return match.group(1) if match else None


class AuthLogParser(SyslogParser):
    """Parse auth.log / secure log files."""
    
    source = LogSource.AUTH_LOG
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        entry = super().parse_line(line)
        if entry:
            # Determine authentication-specific event type
            message_lower = entry.message.lower()
            
            if "accepted" in message_lower:
                entry.event_type = "auth_success"
                entry.status = "success"
            elif "failed" in message_lower or "invalid" in message_lower:
                entry.event_type = "auth_failure"
                entry.status = "failure"
            elif "session opened" in message_lower:
                entry.event_type = "session_start"
            elif "session closed" in message_lower:
                entry.event_type = "session_end"
            elif "sudo" in message_lower:
                entry.event_type = "privilege_escalation"
            
            entry.source = self.source
        
        return entry


class CloudTrailParser(LogParser):
    """
    Parse AWS CloudTrail logs (JSON format).
    """
    
    source = LogSource.CLOUDTRAIL
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        # Handle CloudTrail event structure
        if "Records" in data:
            # This is a file with multiple records
            # We'll handle single records in stream parsing
            return None
        
        event_time = data.get("eventTime")
        if event_time:
            try:
                timestamp = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # Determine severity based on event
        event_name = data.get("eventName", "")
        error_code = data.get("errorCode")
        
        if error_code:
            severity = "error"
        elif any(w in event_name.lower() for w in ["delete", "terminate", "remove"]):
            severity = "warning"
        else:
            severity = "info"
        
        # Extract source IP
        source_ip = data.get("sourceIPAddress")
        
        # Extract user identity
        user_identity = data.get("userIdentity", {})
        user = user_identity.get("userName") or user_identity.get("arn", "").split("/")[-1]
        
        return LogEntry(
            timestamp=timestamp,
            source=self.source,
            raw=line[:1000],
            message=f"{event_name}: {data.get('eventSource', '')}",
            severity=severity,
            host=data.get("awsRegion"),
            user=user,
            event_type=event_name,
            source_ip=source_ip,
            action=event_name,
            status="failure" if error_code else "success",
            extra={
                "aws_account_id": data.get("recipientAccountId"),
                "event_source": data.get("eventSource"),
                "user_agent": data.get("userAgent", "")[:100],
                "error_code": error_code,
                "error_message": data.get("errorMessage", "")[:200],
            },
        )


class JSONLinesParser(LogParser):
    """Parse JSON lines format (generic)."""
    
    source = LogSource.JSON_LINES
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        # Try to extract timestamp from common fields
        timestamp = None
        for field in ["timestamp", "@timestamp", "time", "datetime", "date", "ts"]:
            if field in data:
                try:
                    ts_value = data[field]
                    if isinstance(ts_value, (int, float)):
                        timestamp = datetime.fromtimestamp(ts_value)
                    else:
                        timestamp = datetime.fromisoformat(str(ts_value).replace("Z", "+00:00"))
                    break
                except:
                    continue
        
        if not timestamp:
            timestamp = datetime.now()
        
        # Try to extract message
        message = ""
        for field in ["message", "msg", "log", "text", "content"]:
            if field in data:
                message = str(data[field])[:500]
                break
        
        if not message:
            message = str(data)[:500]
        
        # Extract other common fields
        severity = data.get("level", data.get("severity", data.get("priority", "info")))
        if isinstance(severity, int):
            severity_map = {0: "emergency", 1: "alert", 2: "critical", 3: "error",
                          4: "warning", 5: "notice", 6: "info", 7: "debug"}
            severity = severity_map.get(severity, "info")
        
        return LogEntry(
            timestamp=timestamp,
            source=self.source,
            raw=line[:1000],
            message=message,
            severity=str(severity).lower(),
            host=data.get("host", data.get("hostname")),
            user=data.get("user", data.get("username")),
            process=data.get("process", data.get("service", data.get("app"))),
            source_ip=data.get("source_ip", data.get("client_ip", data.get("remote_addr"))),
            extra={k: v for k, v in data.items() if k not in ["timestamp", "message", "level"]},
        )


class NginxAccessParser(LogParser):
    """Parse nginx access logs (combined format)."""
    
    source = LogSource.NGINX
    
    # Combined log format pattern
    PATTERN = re.compile(
        r'^(?P<ip>\S+)\s+-\s+(?P<user>\S+)\s+'
        r'\[(?P<time>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>\S+)\s+(?P<protocol>[^"]+)"\s+'
        r'(?P<status>\d+)\s+(?P<size>\d+)\s+'
        r'"(?P<referer>[^"]*)"\s+"(?P<user_agent>[^"]*)"'
    )
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        match = self.PATTERN.match(line.strip())
        if not match:
            return None
        
        groups = match.groupdict()
        
        # Parse timestamp
        try:
            timestamp = datetime.strptime(groups["time"], "%d/%b/%Y:%H:%M:%S %z")
        except:
            timestamp = datetime.now()
        
        status_code = int(groups.get("status", 200))
        
        # Determine severity based on status code
        if status_code >= 500:
            severity = "error"
        elif status_code >= 400:
            severity = "warning"
        else:
            severity = "info"
        
        user = groups.get("user")
        if user == "-":
            user = None
        
        return LogEntry(
            timestamp=timestamp,
            source=self.source,
            raw=line,
            message=f"{groups['method']} {groups['path']} {groups['status']}",
            severity=severity,
            source_ip=groups.get("ip"),
            user=user,
            action=groups.get("method"),
            status=str(status_code),
            extra={
                "path": groups.get("path"),
                "status_code": status_code,
                "size": int(groups.get("size", 0)),
                "referer": groups.get("referer"),
                "user_agent": groups.get("user_agent"),
            },
        )


# =============================================================================
# Log Analyzer
# =============================================================================

class LogAnalyzer:
    """
    Log analysis with baseline comparison and anomaly detection.
    
    Features:
    - Multi-format log parsing
    - Baseline creation from historical data
    - Anomaly detection using statistical methods
    - IsolationForest for complex anomalies
    """
    
    PARSERS = [
        AuthLogParser(),
        SyslogParser(),
        CloudTrailParser(),
        NginxAccessParser(),
        JSONLinesParser(),
    ]
    
    # Suspicious command patterns
    SUSPICIOUS_COMMANDS = [
        r"wget\s+.*\s*\|\s*sh",
        r"curl\s+.*\s*\|\s*bash",
        r"nc\s+-e",
        r"base64\s+-d",
        r"/dev/tcp/",
        r"rm\s+-rf\s+/",
        r"chmod\s+777",
        r"mkfifo",
        r"reverse\s*shell",
        r"python\s+-c.*socket",
        r"perl\s+-e.*socket",
        r"ruby\s+-rsocket",
    ]
    
    def __init__(self):
        self._db = get_db()
        self._settings = get_settings()
        self._baseline: Optional[BaselineMetrics] = None
    
    def parse_file(
        self,
        file_path: Path,
        source: Optional[LogSource] = None,
        max_lines: Optional[int] = None,
    ) -> Generator[LogEntry, None, None]:
        """
        Parse log file and yield entries.
        
        Args:
            file_path: Path to log file
            source: Log source type (auto-detected if not specified)
            max_lines: Maximum lines to parse
        
        Yields:
            LogEntry objects
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")
        
        # Handle compressed files
        opener = gzip.open if file_path.suffix == ".gz" else open
        mode = "rt" if file_path.suffix == ".gz" else "r"
        
        # Auto-detect parser
        parser = None
        if source:
            parser = next((p for p in self.PARSERS if p.source == source), None)
        
        if not parser:
            # Read sample lines for detection
            with opener(file_path, mode, errors="replace") as f:
                sample = [f.readline() for _ in range(20)]
            
            for p in self.PARSERS:
                if p.can_parse(sample):
                    parser = p
                    break
            
            if not parser:
                parser = self.PARSERS[-1]  # Default to JSON lines parser
        
        # Parse file
        max_lines = max_lines or self._settings.logs.max_log_lines
        line_count = 0
        
        with opener(file_path, mode, errors="replace") as f:
            for line in f:
                if line_count >= max_lines:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                entry = parser.parse_line(line)
                if entry:
                    line_count += 1
                    yield entry
        
        logger.info(f"Parsed {line_count} log entries from {file_path}")
    
    def create_baseline(
        self,
        entries: List[LogEntry],
        name: str = "default",
    ) -> BaselineMetrics:
        """
        Create baseline from log entries.
        
        Args:
            entries: List of log entries
            name: Baseline name
        
        Returns:
            BaselineMetrics
        """
        if not entries:
            raise ValueError("No entries to create baseline")
        
        # Sort by timestamp
        entries.sort(key=lambda e: e.timestamp)
        
        # Calculate time range
        time_range = (entries[-1].timestamp - entries[0].timestamp).total_seconds() / 3600
        if time_range < 1:
            time_range = 1
        
        # Calculate hourly event counts
        hourly_counts = Counter()
        for entry in entries:
            hour_key = entry.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1
        
        counts = list(hourly_counts.values())
        events_per_hour_mean = statistics.mean(counts) if counts else 0
        events_per_hour_std = statistics.stdev(counts) if len(counts) > 1 else 0
        
        # Events by hour of day
        events_by_hour = Counter()
        for entry in entries:
            events_by_hour[entry.timestamp.hour] += 1
        
        # Events by day of week
        events_by_day = Counter()
        for entry in entries:
            events_by_day[entry.timestamp.weekday()] += 1
        
        # Collect known entities
        known_hosts = {e.host for e in entries if e.host}
        known_users = {e.user for e in entries if e.user}
        known_ips = {e.source_ip for e in entries if e.source_ip}
        
        # Event type distribution
        event_type_dist = Counter(e.event_type for e in entries if e.event_type)
        
        # Authentication metrics
        auth_entries = [e for e in entries if e.event_type and "auth" in e.event_type.lower()]
        auth_success = sum(1 for e in auth_entries if e.status == "success")
        auth_success_rate = auth_success / len(auth_entries) if auth_entries else 1.0
        
        # Failed auth per hour
        failed_auth_hourly = Counter()
        for entry in entries:
            if entry.event_type == "auth_failure":
                hour_key = entry.timestamp.replace(minute=0, second=0, microsecond=0)
                failed_auth_hourly[hour_key] += 1
        
        failed_counts = list(failed_auth_hourly.values())
        failed_auth_mean = statistics.mean(failed_counts) if failed_counts else 0
        failed_auth_std = statistics.stdev(failed_counts) if len(failed_counts) > 1 else 0
        
        baseline = BaselineMetrics(
            name=name,
            created_at=datetime.now(),
            source=entries[0].source.value,
            total_events=len(entries),
            time_range_hours=time_range,
            events_per_hour_mean=events_per_hour_mean,
            events_per_hour_std=events_per_hour_std,
            events_by_hour=dict(events_by_hour),
            events_by_day=dict(events_by_day),
            known_hosts=known_hosts,
            known_users=known_users,
            known_ips=known_ips,
            event_type_distribution=dict(event_type_dist),
            auth_success_rate=auth_success_rate,
            failed_auth_per_hour_mean=failed_auth_mean,
            failed_auth_per_hour_std=failed_auth_std,
        )
        
        # Save to database
        self._db.save_baseline(
            name=name,
            source=baseline.source,
            metrics=baseline.to_dict(),
        )
        
        self._baseline = baseline
        logger.info(f"Created baseline '{name}' from {len(entries)} entries")
        
        return baseline
    
    def load_baseline(self, name: str = "default") -> Optional[BaselineMetrics]:
        """Load baseline from database."""
        data = self._db.get_baseline(name)
        if not data:
            return None
        
        metrics_data = data.get("metrics", {})
        self._baseline = BaselineMetrics.from_dict(metrics_data)
        return self._baseline
    
    def detect_anomalies(
        self,
        entries: List[LogEntry],
        baseline: Optional[BaselineMetrics] = None,
    ) -> List[Anomaly]:
        """
        Detect anomalies in log entries against baseline.
        
        Args:
            entries: Log entries to analyze
            baseline: Baseline to compare against (uses loaded baseline if not specified)
        
        Returns:
            List of detected anomalies
        """
        if baseline is None:
            baseline = self._baseline
        
        if baseline is None:
            logger.warning("No baseline available, using basic detection")
            return self._detect_basic_anomalies(entries)
        
        anomalies = []
        
        # Group entries by hour
        hourly_entries = defaultdict(list)
        for entry in entries:
            hour_key = entry.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_entries[hour_key].append(entry)
        
        # Check each hour for anomalies
        for hour, hour_entries in hourly_entries.items():
            count = len(hour_entries)
            
            # Frequency spike detection
            if baseline.events_per_hour_std > 0:
                z_score = (count - baseline.events_per_hour_mean) / baseline.events_per_hour_std
                if z_score > 3:  # More than 3 standard deviations
                    anomalies.append(Anomaly(
                        timestamp=hour,
                        anomaly_type=AnomalyType.FREQUENCY_SPIKE,
                        severity=Severity.HIGH if z_score > 5 else Severity.MEDIUM,
                        score=min(100, z_score * 15),
                        description=f"Event frequency spike: {count} events/hour (expected ~{baseline.events_per_hour_mean:.1f})",
                        evidence={
                            "count": count,
                            "expected": baseline.events_per_hour_mean,
                            "z_score": z_score,
                        },
                        related_entries=hour_entries[:10],
                    ))
            
            # Check for new sources
            for entry in hour_entries:
                # New host
                if entry.host and entry.host not in baseline.known_hosts:
                    anomalies.append(Anomaly(
                        timestamp=entry.timestamp,
                        anomaly_type=AnomalyType.NEW_SOURCE,
                        severity=Severity.MEDIUM,
                        score=40.0,
                        description=f"Activity from unknown host: {entry.host}",
                        evidence={"host": entry.host},
                        related_entries=[entry],
                    ))
                
                # New source IP
                if entry.source_ip and entry.source_ip not in baseline.known_ips:
                    anomalies.append(Anomaly(
                        timestamp=entry.timestamp,
                        anomaly_type=AnomalyType.NEW_SOURCE,
                        severity=Severity.LOW,
                        score=25.0,
                        description=f"Activity from new IP: {entry.source_ip}",
                        evidence={"source_ip": entry.source_ip},
                        related_entries=[entry],
                    ))
            
            # Failed authentication spike
            failed_auth_count = sum(1 for e in hour_entries if e.event_type == "auth_failure")
            if failed_auth_count > 0 and baseline.failed_auth_per_hour_std > 0:
                z_score = (failed_auth_count - baseline.failed_auth_per_hour_mean) / baseline.failed_auth_per_hour_std
                if z_score > 2:
                    anomalies.append(Anomaly(
                        timestamp=hour,
                        anomaly_type=AnomalyType.FAILED_AUTH,
                        severity=Severity.HIGH,
                        score=min(100, 50 + z_score * 10),
                        description=f"Authentication failure spike: {failed_auth_count} failures/hour",
                        evidence={
                            "failed_count": failed_auth_count,
                            "expected": baseline.failed_auth_per_hour_mean,
                            "z_score": z_score,
                        },
                        related_entries=[e for e in hour_entries if e.event_type == "auth_failure"][:10],
                    ))
        
        # Check unusual time activity
        for entry in entries:
            hour = entry.timestamp.hour
            expected_ratio = baseline.events_by_hour.get(hour, 0) / max(baseline.total_events, 1)
            
            # Very low activity hour but we see events
            if expected_ratio < 0.01:  # Less than 1% of normal activity in this hour
                anomalies.append(Anomaly(
                    timestamp=entry.timestamp,
                    anomaly_type=AnomalyType.UNUSUAL_TIME,
                    severity=Severity.MEDIUM,
                    score=35.0,
                    description=f"Activity at unusual time: {hour:02d}:00",
                    evidence={
                        "hour": hour,
                        "expected_activity_ratio": expected_ratio,
                    },
                    related_entries=[entry],
                ))
        
        # Add basic anomaly detection
        anomalies.extend(self._detect_basic_anomalies(entries))
        
        # Deduplicate by type and hour
        seen = set()
        unique_anomalies = []
        for a in anomalies:
            key = (a.anomaly_type, a.timestamp.replace(minute=0, second=0, microsecond=0))
            if key not in seen:
                seen.add(key)
                unique_anomalies.append(a)
        
        # Store findings
        for anomaly in unique_anomalies:
            self._db.insert_finding(
                category=FindingCategory.ANOMALY,
                severity=anomaly.severity,
                score=anomaly.score,
                title=anomaly.description[:100],
                details=anomaly.to_dict(),
            )
        
        logger.info(f"Detected {len(unique_anomalies)} anomalies")
        return unique_anomalies
    
    def _detect_basic_anomalies(self, entries: List[LogEntry]) -> List[Anomaly]:
        """Basic anomaly detection without baseline."""
        anomalies = []
        
        # Check for brute force patterns
        failed_by_ip = Counter()
        failed_by_user = Counter()
        
        for entry in entries:
            if entry.event_type == "auth_failure":
                if entry.source_ip:
                    failed_by_ip[entry.source_ip] += 1
                if entry.user:
                    failed_by_user[entry.user] += 1
        
        # Brute force from IP
        for ip, count in failed_by_ip.items():
            if count >= 10:
                anomalies.append(Anomaly(
                    timestamp=datetime.now(),
                    anomaly_type=AnomalyType.FAILED_AUTH,
                    severity=Severity.HIGH if count >= 50 else Severity.MEDIUM,
                    score=min(100, count * 2),
                    description=f"Brute force attack from {ip}: {count} failed attempts",
                    evidence={"source_ip": ip, "failed_attempts": count},
                ))
        
        # Account enumeration
        for user, count in failed_by_user.items():
            if count >= 5:
                anomalies.append(Anomaly(
                    timestamp=datetime.now(),
                    anomaly_type=AnomalyType.FAILED_AUTH,
                    severity=Severity.MEDIUM,
                    score=min(80, count * 3),
                    description=f"Multiple failed logins for user '{user}': {count} attempts",
                    evidence={"user": user, "failed_attempts": count},
                ))
        
        # Privilege escalation
        for entry in entries:
            if entry.event_type == "privilege_escalation":
                anomalies.append(Anomaly(
                    timestamp=entry.timestamp,
                    anomaly_type=AnomalyType.PRIVILEGE_ESCALATION,
                    severity=Severity.MEDIUM,
                    score=45.0,
                    description=f"Privilege escalation by {entry.user or 'unknown'}",
                    evidence={"user": entry.user, "message": entry.message[:100]},
                    related_entries=[entry],
                ))
        
        # Suspicious commands
        for entry in entries:
            for pattern in self.SUSPICIOUS_COMMANDS:
                if re.search(pattern, entry.message, re.IGNORECASE):
                    anomalies.append(Anomaly(
                        timestamp=entry.timestamp,
                        anomaly_type=AnomalyType.SUSPICIOUS_COMMAND,
                        severity=Severity.CRITICAL,
                        score=85.0,
                        description=f"Suspicious command detected: {entry.message[:50]}",
                        evidence={
                            "pattern": pattern,
                            "command": entry.message[:200],
                            "user": entry.user,
                            "host": entry.host,
                        },
                        related_entries=[entry],
                    ))
                    break
        
        return anomalies
    
    def analyze_with_isolation_forest(
        self,
        entries: List[LogEntry],
        contamination: float = 0.1,
    ) -> List[Anomaly]:
        """
        Advanced anomaly detection using IsolationForest.
        
        Args:
            entries: Log entries to analyze
            contamination: Expected proportion of anomalies
        
        Returns:
            List of detected anomalies
        """
        try:
            from sklearn.ensemble import IsolationForest
            import numpy as np
        except ImportError:
            logger.warning("scikit-learn not available, skipping IsolationForest analysis")
            return []
        
        if len(entries) < 100:
            logger.warning("Not enough entries for IsolationForest analysis (need >= 100)")
            return []
        
        # Feature extraction
        features = []
        for entry in entries:
            feature_vector = [
                entry.timestamp.hour,  # Hour of day
                entry.timestamp.weekday(),  # Day of week
                1 if entry.severity == "error" else 0,
                1 if entry.severity == "critical" else 0,
                1 if entry.event_type == "auth_failure" else 0,
                1 if entry.event_type == "privilege_escalation" else 0,
                len(entry.message),  # Message length
            ]
            features.append(feature_vector)
        
        X = np.array(features)
        
        # Train IsolationForest
        clf = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        predictions = clf.fit_predict(X)
        scores = clf.score_samples(X)
        
        # Extract anomalies
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly
                entry = entries[i]
                anomaly_score = (1 - (score + 0.5)) * 100  # Convert to 0-100 scale
                
                anomalies.append(Anomaly(
                    timestamp=entry.timestamp,
                    anomaly_type=AnomalyType.PATTERN_DEVIATION,
                    severity=self._score_to_severity(anomaly_score),
                    score=anomaly_score,
                    description=f"Pattern deviation detected: {entry.message[:50]}",
                    evidence={
                        "isolation_score": float(score),
                        "hour": entry.timestamp.hour,
                        "event_type": entry.event_type,
                    },
                    related_entries=[entry],
                ))
        
        logger.info(f"IsolationForest detected {len(anomalies)} anomalies")
        return anomalies
    
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
    
    def get_summary(self, entries: List[LogEntry]) -> Dict[str, Any]:
        """Get summary statistics for log entries."""
        if not entries:
            return {"total": 0}
        
        # Sort entries
        entries.sort(key=lambda e: e.timestamp)
        
        # Calculate stats
        by_severity = Counter(e.severity for e in entries)
        by_source = Counter(e.source.value for e in entries)
        by_event_type = Counter(e.event_type for e in entries if e.event_type)
        unique_hosts = len({e.host for e in entries if e.host})
        unique_users = len({e.user for e in entries if e.user})
        unique_ips = len({e.source_ip for e in entries if e.source_ip})
        
        time_range = (entries[-1].timestamp - entries[0].timestamp).total_seconds() / 3600
        
        return {
            "total": len(entries),
            "time_range_hours": time_range,
            "by_severity": dict(by_severity),
            "by_source": dict(by_source),
            "by_event_type": dict(by_event_type.most_common(10)),
            "unique_hosts": unique_hosts,
            "unique_users": unique_users,
            "unique_ips": unique_ips,
            "start_time": entries[0].timestamp.isoformat(),
            "end_time": entries[-1].timestamp.isoformat(),
        }
