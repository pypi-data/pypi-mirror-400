"""
CHRONOS Database Layer
======================

SQLite database for storing events, findings, actions, and cached intel data.
Provides audit trail and persistence for all security operations.
"""

import json
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
import uuid

from chronos.utils.logging import get_logger

logger = get_logger(__name__)


class EventType(str, Enum):
    """Types of security events."""
    LOG_INGESTED = "log_ingested"
    SCAN_COMPLETED = "scan_completed"
    PHISH_ANALYZED = "phish_analyzed"
    VULN_IMPORTED = "vuln_imported"
    VULN_ENRICHED = "vuln_enriched"
    IOC_DETECTED = "ioc_detected"
    ALERT_GENERATED = "alert_generated"
    REPORT_GENERATED = "report_generated"
    IR_TRIGGERED = "ir_triggered"


class FindingCategory(str, Enum):
    """Categories of security findings."""
    VULNERABILITY = "vulnerability"
    PHISHING = "phishing"
    MALWARE = "malware"
    ANOMALY = "anomaly"
    IOC = "ioc"
    CRYPTO_WEAKNESS = "crypto_weakness"
    SECRET_EXPOSURE = "secret_exposure"
    INJECTION = "injection"


class Severity(str, Enum):
    """Severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ActionStatus(str, Enum):
    """Status of IR actions."""
    PENDING = "pending"
    DRY_RUN = "dry_run"
    EXECUTED = "executed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Event:
    """Security event record."""
    id: str
    timestamp: datetime
    event_type: EventType
    source: str
    raw_json: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "source": self.source,
            "raw_json": self.raw_json,
        }


@dataclass
class Finding:
    """Security finding record."""
    id: str
    timestamp: datetime
    category: FindingCategory
    severity: Severity
    score: float
    title: str
    details: Dict[str, Any]
    cve_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category.value,
            "severity": self.severity.value,
            "score": self.score,
            "title": self.title,
            "details": self.details,
            "cve_id": self.cve_id,
        }


@dataclass
class Action:
    """IR action audit record."""
    id: str
    timestamp: datetime
    playbook: str
    action_name: str
    target: str
    status: ActionStatus
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "playbook": self.playbook,
            "action_name": self.action_name,
            "target": self.target,
            "status": self.status.value,
            "details": self.details,
        }


class ChronosDB:
    """
    SQLite database manager for CHRONOS.
    
    Stores:
    - Events: All security events with timestamps
    - Findings: Detected security issues with scores
    - Actions: IR playbook audit trail
    - Cache: Threat intel data caching
    """
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        source TEXT NOT NULL,
        raw_json TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        score REAL NOT NULL,
        title TEXT NOT NULL,
        details_json TEXT NOT NULL,
        cve_id TEXT
    );
    
    CREATE TABLE IF NOT EXISTS actions (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        playbook TEXT NOT NULL,
        action_name TEXT NOT NULL,
        target TEXT NOT NULL,
        status TEXT NOT NULL,
        details_json TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS intel_cache (
        key TEXT PRIMARY KEY,
        data_json TEXT NOT NULL,
        cached_at TEXT NOT NULL,
        expires_at TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS baselines (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        source TEXT NOT NULL,
        metrics_json TEXT NOT NULL
    );
    
    CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
    CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
    CREATE INDEX IF NOT EXISTS idx_findings_timestamp ON findings(timestamp);
    CREATE INDEX IF NOT EXISTS idx_findings_category ON findings(category);
    CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
    CREATE INDEX IF NOT EXISTS idx_findings_cve ON findings(cve_id);
    CREATE INDEX IF NOT EXISTS idx_actions_timestamp ON actions(timestamp);
    CREATE INDEX IF NOT EXISTS idx_actions_playbook ON actions(playbook);
    CREATE INDEX IF NOT EXISTS idx_cache_expires ON intel_cache(expires_at);
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database. Defaults to ~/.chronos/chronos.db
        """
        if db_path is None:
            db_path = Path.home() / ".chronos" / "chronos.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._local = threading.local()
        self._init_schema()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _init_schema(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        conn.executescript(self.SCHEMA)
        conn.commit()
    
    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    # ========================================================================
    # Events
    # ========================================================================
    
    def insert_event(
        self,
        event_type: EventType,
        source: str,
        raw_data: Dict[str, Any],
    ) -> Event:
        """Insert a new event."""
        event = Event(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            source=source,
            raw_json=raw_data,
        )
        
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO events (id, timestamp, event_type, source, raw_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.timestamp.isoformat(),
                    event.event_type.value,
                    event.source,
                    json.dumps(event.raw_json),
                ),
            )
        
        logger.debug(f"Inserted event: {event.id} ({event.event_type.value})")
        return event
    
    def query_events(
        self,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Event]:
        """Query events with filters."""
        query = "SELECT * FROM events WHERE 1=1"
        params: List[Any] = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)
        if source:
            query += " AND source = ?"
            params.append(source)
        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        if until:
            query += " AND timestamp <= ?"
            params.append(until.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        conn = self._get_connection()
        rows = conn.execute(query, params).fetchall()
        
        return [
            Event(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                event_type=EventType(row["event_type"]),
                source=row["source"],
                raw_json=json.loads(row["raw_json"]),
            )
            for row in rows
        ]
    
    # ========================================================================
    # Findings
    # ========================================================================
    
    def insert_finding(
        self,
        category: FindingCategory,
        severity: Severity,
        score: float,
        title: str,
        details: Dict[str, Any],
        cve_id: Optional[str] = None,
    ) -> Finding:
        """Insert a new finding."""
        finding = Finding(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            score=score,
            title=title,
            details=details,
            cve_id=cve_id,
        )
        
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO findings (id, timestamp, category, severity, score, title, details_json, cve_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding.id,
                    finding.timestamp.isoformat(),
                    finding.category.value,
                    finding.severity.value,
                    finding.score,
                    finding.title,
                    json.dumps(finding.details),
                    finding.cve_id,
                ),
            )
        
        logger.debug(f"Inserted finding: {finding.id} ({finding.category.value})")
        return finding
    
    def query_findings(
        self,
        category: Optional[FindingCategory] = None,
        severity: Optional[Severity] = None,
        min_score: Optional[float] = None,
        cve_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Finding]:
        """Query findings with filters."""
        query = "SELECT * FROM findings WHERE 1=1"
        params: List[Any] = []
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        if severity:
            query += " AND severity = ?"
            params.append(severity.value)
        if min_score is not None:
            query += " AND score >= ?"
            params.append(min_score)
        if cve_id:
            query += " AND cve_id = ?"
            params.append(cve_id)
        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        
        query += " ORDER BY score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        conn = self._get_connection()
        rows = conn.execute(query, params).fetchall()
        
        return [
            Finding(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                category=FindingCategory(row["category"]),
                severity=Severity(row["severity"]),
                score=row["score"],
                title=row["title"],
                details=json.loads(row["details_json"]),
                cve_id=row["cve_id"],
            )
            for row in rows
        ]
    
    def get_findings_summary(
        self,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get summary statistics for findings."""
        conn = self._get_connection()
        
        where_clause = ""
        params: List[Any] = []
        if since:
            where_clause = "WHERE timestamp >= ?"
            params.append(since.isoformat())
        
        # Count by severity
        severity_query = f"""
            SELECT severity, COUNT(*) as count
            FROM findings {where_clause}
            GROUP BY severity
        """
        severity_counts = {row["severity"]: row["count"] for row in conn.execute(severity_query, params)}
        
        # Count by category
        category_query = f"""
            SELECT category, COUNT(*) as count
            FROM findings {where_clause}
            GROUP BY category
        """
        category_counts = {row["category"]: row["count"] for row in conn.execute(category_query, params)}
        
        # Top CVEs
        cve_query = f"""
            SELECT cve_id, COUNT(*) as count, MAX(score) as max_score
            FROM findings {where_clause} AND cve_id IS NOT NULL
            GROUP BY cve_id
            ORDER BY max_score DESC
            LIMIT 10
        """
        top_cves = [
            {"cve_id": row["cve_id"], "count": row["count"], "max_score": row["max_score"]}
            for row in conn.execute(cve_query, params)
        ]
        
        return {
            "by_severity": severity_counts,
            "by_category": category_counts,
            "top_cves": top_cves,
            "total": sum(severity_counts.values()),
        }
    
    # ========================================================================
    # Actions (IR Audit Trail)
    # ========================================================================
    
    def insert_action(
        self,
        playbook: str,
        action_name: str,
        target: str,
        status: ActionStatus,
        details: Dict[str, Any],
    ) -> Action:
        """Insert an IR action audit record."""
        action = Action(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            playbook=playbook,
            action_name=action_name,
            target=target,
            status=status,
            details=details,
        )
        
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO actions (id, timestamp, playbook, action_name, target, status, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    action.id,
                    action.timestamp.isoformat(),
                    action.playbook,
                    action.action_name,
                    action.target,
                    action.status.value,
                    json.dumps(action.details),
                ),
            )
        
        logger.info(f"IR Action: {action.action_name} on {action.target} [{action.status.value}]")
        return action
    
    def query_actions(
        self,
        playbook: Optional[str] = None,
        status: Optional[ActionStatus] = None,
        since: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Action]:
        """Query IR actions."""
        query = "SELECT * FROM actions WHERE 1=1"
        params: List[Any] = []
        
        if playbook:
            query += " AND playbook = ?"
            params.append(playbook)
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        conn = self._get_connection()
        rows = conn.execute(query, params).fetchall()
        
        return [
            Action(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                playbook=row["playbook"],
                action_name=row["action_name"],
                target=row["target"],
                status=ActionStatus(row["status"]),
                details=json.loads(row["details_json"]),
            )
            for row in rows
        ]
    
    # ========================================================================
    # Intel Cache
    # ========================================================================
    
    def cache_set(
        self,
        key: str,
        data: Any,
        ttl_seconds: int = 3600,
    ) -> None:
        """Set a cache entry."""
        now = datetime.now()
        expires = now + timedelta(seconds=ttl_seconds)
        
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO intel_cache (key, data_json, cached_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (key, json.dumps(data), now.isoformat(), expires.isoformat()),
            )
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get a cache entry if not expired."""
        conn = self._get_connection()
        row = conn.execute(
            "SELECT data_json, expires_at FROM intel_cache WHERE key = ?",
            (key,),
        ).fetchone()
        
        if row is None:
            return None
        
        if datetime.fromisoformat(row["expires_at"]) < datetime.now():
            # Expired - delete it
            conn.execute("DELETE FROM intel_cache WHERE key = ?", (key,))
            conn.commit()
            return None
        
        return json.loads(row["data_json"])
    
    def cache_clear_expired(self) -> int:
        """Clear expired cache entries. Returns count deleted."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM intel_cache WHERE expires_at < ?",
                (datetime.now().isoformat(),),
            )
            return cursor.rowcount
    
    # ========================================================================
    # Baselines
    # ========================================================================
    
    def save_baseline(
        self,
        name: str,
        source: str,
        metrics: Dict[str, Any],
    ) -> str:
        """Save a baseline profile."""
        baseline_id = str(uuid.uuid4())
        
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines (id, name, created_at, source, metrics_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (baseline_id, name, datetime.now().isoformat(), source, json.dumps(metrics)),
            )
        
        logger.info(f"Saved baseline: {name}")
        return baseline_id
    
    def get_baseline(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a baseline by name."""
        conn = self._get_connection()
        row = conn.execute(
            "SELECT * FROM baselines WHERE name = ?",
            (name,),
        ).fetchone()
        
        if row is None:
            return None
        
        return {
            "id": row["id"],
            "name": row["name"],
            "created_at": row["created_at"],
            "source": row["source"],
            "metrics": json.loads(row["metrics_json"]),
        }
    
    def list_baselines(self) -> List[Dict[str, Any]]:
        """List all baselines."""
        conn = self._get_connection()
        rows = conn.execute("SELECT id, name, created_at, source FROM baselines").fetchall()
        return [dict(row) for row in rows]


# Global database instance
_db: Optional[ChronosDB] = None


def get_db() -> ChronosDB:
    """Get or create the global database instance."""
    global _db
    if _db is None:
        _db = ChronosDB()
    return _db


def init_db(db_path: Optional[Path] = None) -> ChronosDB:
    """Initialize database with custom path."""
    global _db
    _db = ChronosDB(db_path)
    return _db
