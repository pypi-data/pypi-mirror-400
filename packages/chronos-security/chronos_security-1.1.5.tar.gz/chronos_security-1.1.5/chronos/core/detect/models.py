"""
CHRONOS Network Detection Models
================================

Data models for network monitoring and packet analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class Protocol(str, Enum):
    """Network protocol types."""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    DNS = "dns"
    HTTP = "http"
    HTTPS = "https"
    TLS = "tls"
    SSH = "ssh"
    FTP = "ftp"
    SMTP = "smtp"
    OTHER = "other"


class TLSVersion(str, Enum):
    """TLS protocol versions."""
    SSL_3_0 = "SSL 3.0"
    TLS_1_0 = "TLS 1.0"
    TLS_1_1 = "TLS 1.1"
    TLS_1_2 = "TLS 1.2"
    TLS_1_3 = "TLS 1.3"
    UNKNOWN = "Unknown"


class AlertSeverity(str, Enum):
    """Network alert severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of network alerts."""
    SUSPICIOUS_CONNECTION = "suspicious_connection"
    PORT_SCAN = "port_scan"
    WEAK_TLS = "weak_tls"
    DEPRECATED_PROTOCOL = "deprecated_protocol"
    DATA_EXFILTRATION = "data_exfiltration"
    DNS_ANOMALY = "dns_anomaly"
    MALFORMED_PACKET = "malformed_packet"
    HIGH_TRAFFIC = "high_traffic"
    UNKNOWN_SERVICE = "unknown_service"
    CERT_ERROR = "certificate_error"


@dataclass
class PacketInfo:
    """Information extracted from a captured packet."""
    
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: Protocol
    length: int
    payload_length: int
    flags: Dict[str, bool] = field(default_factory=dict)
    raw_payload: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_tcp(self) -> bool:
        """Check if packet is TCP."""
        return self.protocol == Protocol.TCP
    
    @property
    def is_udp(self) -> bool:
        """Check if packet is UDP."""
        return self.protocol == Protocol.UDP
    
    @property
    def connection_tuple(self) -> Tuple[str, int, str, int]:
        """Get connection 4-tuple (src_ip, src_port, dst_ip, dst_port)."""
        return (
            self.src_ip,
            self.src_port or 0,
            self.dst_ip,
            self.dst_port or 0,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol.value,
            "length": self.length,
            "payload_length": self.payload_length,
            "flags": self.flags,
            "metadata": self.metadata,
        }


@dataclass
class ConnectionInfo:
    """Information about a network connection."""
    
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: Protocol
    state: str = "unknown"
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    packets_sent: int = 0
    packets_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    tls_info: Optional["TLSHandshakeInfo"] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def connection_id(self) -> str:
        """Generate unique connection identifier."""
        return f"{self.src_ip}:{self.src_port}-{self.dst_ip}:{self.dst_port}-{self.protocol.value}"
    
    @property
    def duration(self) -> float:
        """Get connection duration in seconds."""
        return (self.last_seen - self.first_seen).total_seconds()
    
    @property
    def total_bytes(self) -> int:
        """Get total bytes transferred."""
        return self.bytes_sent + self.bytes_received
    
    @property
    def total_packets(self) -> int:
        """Get total packets."""
        return self.packets_sent + self.packets_received
    
    def update(self, packet: PacketInfo, is_outbound: bool = True) -> None:
        """Update connection stats with new packet."""
        self.last_seen = packet.timestamp
        if is_outbound:
            self.packets_sent += 1
            self.bytes_sent += packet.length
        else:
            self.packets_received += 1
            self.bytes_received += packet.length
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "connection_id": self.connection_id,
            "src_ip": self.src_ip,
            "src_port": self.src_port,
            "dst_ip": self.dst_ip,
            "dst_port": self.dst_port,
            "protocol": self.protocol.value,
            "state": self.state,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "duration": self.duration,
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "total_bytes": self.total_bytes,
            "tls_info": self.tls_info.to_dict() if self.tls_info else None,
            "metadata": self.metadata,
        }


@dataclass
class TLSHandshakeInfo:
    """Information extracted from TLS handshake."""
    
    version: TLSVersion
    cipher_suite: Optional[str] = None
    server_name: Optional[str] = None  # SNI
    certificate_subject: Optional[str] = None
    certificate_issuer: Optional[str] = None
    certificate_expiry: Optional[datetime] = None
    certificate_valid: bool = True
    handshake_complete: bool = False
    supported_versions: List[TLSVersion] = field(default_factory=list)
    extensions: Dict[str, Any] = field(default_factory=dict)
    is_quantum_safe: bool = False
    warnings: List[str] = field(default_factory=list)
    
    @property
    def is_deprecated(self) -> bool:
        """Check if TLS version is deprecated."""
        deprecated = {TLSVersion.SSL_3_0, TLSVersion.TLS_1_0, TLSVersion.TLS_1_1}
        return self.version in deprecated
    
    @property
    def security_score(self) -> int:
        """Calculate TLS security score (0-100)."""
        score = 50  # Base score
        
        # Version scoring
        version_scores = {
            TLSVersion.SSL_3_0: -30,
            TLSVersion.TLS_1_0: -20,
            TLSVersion.TLS_1_1: -10,
            TLSVersion.TLS_1_2: 20,
            TLSVersion.TLS_1_3: 30,
        }
        score += version_scores.get(self.version, 0)
        
        # Certificate validity
        if not self.certificate_valid:
            score -= 20
        
        # Quantum safety bonus
        if self.is_quantum_safe:
            score += 20
        
        # Warnings penalty
        score -= len(self.warnings) * 5
        
        return max(0, min(100, score))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version.value,
            "cipher_suite": self.cipher_suite,
            "server_name": self.server_name,
            "certificate_subject": self.certificate_subject,
            "certificate_issuer": self.certificate_issuer,
            "certificate_expiry": self.certificate_expiry.isoformat() if self.certificate_expiry else None,
            "certificate_valid": self.certificate_valid,
            "handshake_complete": self.handshake_complete,
            "is_deprecated": self.is_deprecated,
            "is_quantum_safe": self.is_quantum_safe,
            "security_score": self.security_score,
            "warnings": self.warnings,
            "extensions": self.extensions,
        }


@dataclass
class TrafficMetadata:
    """Aggregated traffic metadata and statistics."""
    
    interface: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_packets: int = 0
    total_bytes: int = 0
    tcp_packets: int = 0
    udp_packets: int = 0
    icmp_packets: int = 0
    other_packets: int = 0
    unique_src_ips: set = field(default_factory=set)
    unique_dst_ips: set = field(default_factory=set)
    unique_connections: int = 0
    tls_handshakes: int = 0
    http_requests: int = 0
    dns_queries: int = 0
    alerts_generated: int = 0
    top_talkers: Dict[str, int] = field(default_factory=dict)
    port_distribution: Dict[int, int] = field(default_factory=dict)
    protocol_distribution: Dict[str, int] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get capture duration in seconds."""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def packets_per_second(self) -> float:
        """Calculate packets per second."""
        if self.duration > 0:
            return self.total_packets / self.duration
        return 0.0
    
    @property
    def bytes_per_second(self) -> float:
        """Calculate bytes per second."""
        if self.duration > 0:
            return self.total_bytes / self.duration
        return 0.0
    
    def update_from_packet(self, packet: PacketInfo) -> None:
        """Update metadata from a packet."""
        self.total_packets += 1
        self.total_bytes += packet.length
        
        # Protocol stats
        if packet.protocol == Protocol.TCP:
            self.tcp_packets += 1
        elif packet.protocol == Protocol.UDP:
            self.udp_packets += 1
        elif packet.protocol == Protocol.ICMP:
            self.icmp_packets += 1
        else:
            self.other_packets += 1
        
        # IP tracking
        self.unique_src_ips.add(packet.src_ip)
        self.unique_dst_ips.add(packet.dst_ip)
        
        # Port distribution
        if packet.dst_port:
            self.port_distribution[packet.dst_port] = (
                self.port_distribution.get(packet.dst_port, 0) + 1
            )
        
        # Protocol distribution
        proto = packet.protocol.value
        self.protocol_distribution[proto] = (
            self.protocol_distribution.get(proto, 0) + 1
        )
        
        # Top talkers
        self.top_talkers[packet.src_ip] = (
            self.top_talkers.get(packet.src_ip, 0) + packet.length
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "interface": self.interface,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "total_packets": self.total_packets,
            "total_bytes": self.total_bytes,
            "packets_per_second": round(self.packets_per_second, 2),
            "bytes_per_second": round(self.bytes_per_second, 2),
            "protocol_counts": {
                "tcp": self.tcp_packets,
                "udp": self.udp_packets,
                "icmp": self.icmp_packets,
                "other": self.other_packets,
            },
            "unique_src_ips": len(self.unique_src_ips),
            "unique_dst_ips": len(self.unique_dst_ips),
            "unique_connections": self.unique_connections,
            "tls_handshakes": self.tls_handshakes,
            "http_requests": self.http_requests,
            "dns_queries": self.dns_queries,
            "alerts_generated": self.alerts_generated,
            "top_talkers": dict(sorted(
                self.top_talkers.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "port_distribution": dict(sorted(
                self.port_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]),
        }


@dataclass
class NetworkAlert:
    """Network security alert."""
    
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[Protocol] = None
    packet_info: Optional[PacketInfo] = None
    connection_info: Optional[ConnectionInfo] = None
    tls_info: Optional[TLSHandshakeInfo] = None
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol.value if self.protocol else None,
            "details": self.details,
            "recommendations": self.recommendations,
            "acknowledged": self.acknowledged,
        }
