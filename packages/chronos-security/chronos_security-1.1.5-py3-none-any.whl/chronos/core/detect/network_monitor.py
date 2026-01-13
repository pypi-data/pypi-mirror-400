"""
CHRONOS Network Monitor
=======================

Packet capture and real-time network monitoring using Scapy.
Provides TLS/SSL handshake detection, traffic analysis, and metadata extraction.
"""

import threading
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from queue import Queue, Empty
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

try:
    from scapy.all import (
        sniff,
        conf,
        get_if_list,
        get_if_hwaddr,
        IP,
        IPv6,
        TCP,
        UDP,
        ICMP,
        Raw,
        Ether,
        DNS,
        DNSQR,
        DNSRR,
        Packet as ScapyPacket,
    )
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    ScapyPacket = None

from chronos.cli.utils.logger import get_logger
from chronos.core.detect.models import (
    PacketInfo,
    ConnectionInfo,
    TLSHandshakeInfo,
    TrafficMetadata,
    NetworkAlert,
    Protocol,
    TLSVersion,
    AlertSeverity,
    AlertType,
)


logger = get_logger(__name__)


# TLS Constants
TLS_CONTENT_TYPES = {
    20: "change_cipher_spec",
    21: "alert",
    22: "handshake",
    23: "application_data",
}

TLS_HANDSHAKE_TYPES = {
    0: "hello_request",
    1: "client_hello",
    2: "server_hello",
    4: "new_session_ticket",
    8: "encrypted_extensions",
    11: "certificate",
    12: "server_key_exchange",
    13: "certificate_request",
    14: "server_hello_done",
    15: "certificate_verify",
    16: "client_key_exchange",
    20: "finished",
}

TLS_VERSIONS = {
    0x0300: TLSVersion.SSL_3_0,
    0x0301: TLSVersion.TLS_1_0,
    0x0302: TLSVersion.TLS_1_1,
    0x0303: TLSVersion.TLS_1_2,
    0x0304: TLSVersion.TLS_1_3,
}

# Common vulnerable cipher suites
WEAK_CIPHER_SUITES = {
    "TLS_RSA_WITH_NULL_MD5",
    "TLS_RSA_WITH_NULL_SHA",
    "TLS_RSA_EXPORT_WITH_RC4_40_MD5",
    "TLS_RSA_WITH_RC4_128_MD5",
    "TLS_RSA_WITH_RC4_128_SHA",
    "TLS_RSA_EXPORT_WITH_DES40_CBC_SHA",
    "TLS_RSA_WITH_DES_CBC_SHA",
    "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
}


class BPFFilter:
    """
    Builder for Berkeley Packet Filter (BPF) expressions.
    
    Example usage:
        filter = BPFFilter()
        filter.port(443).protocol("tcp").src_net("192.168.1.0/24")
        print(filter.build())  # "port 443 and tcp and src net 192.168.1.0/24"
    """
    
    def __init__(self):
        self._filters: List[str] = []
    
    def raw(self, expression: str) -> "BPFFilter":
        """Add a raw BPF expression."""
        if expression.strip():
            self._filters.append(expression.strip())
        return self
    
    def port(self, port: int) -> "BPFFilter":
        """Filter by port (source or destination)."""
        self._filters.append(f"port {port}")
        return self
    
    def src_port(self, port: int) -> "BPFFilter":
        """Filter by source port."""
        self._filters.append(f"src port {port}")
        return self
    
    def dst_port(self, port: int) -> "BPFFilter":
        """Filter by destination port."""
        self._filters.append(f"dst port {port}")
        return self
    
    def port_range(self, start: int, end: int) -> "BPFFilter":
        """Filter by port range."""
        self._filters.append(f"portrange {start}-{end}")
        return self
    
    def host(self, ip: str) -> "BPFFilter":
        """Filter by host IP (source or destination)."""
        self._filters.append(f"host {ip}")
        return self
    
    def src_host(self, ip: str) -> "BPFFilter":
        """Filter by source IP."""
        self._filters.append(f"src host {ip}")
        return self
    
    def dst_host(self, ip: str) -> "BPFFilter":
        """Filter by destination IP."""
        self._filters.append(f"dst host {ip}")
        return self
    
    def net(self, network: str) -> "BPFFilter":
        """Filter by network (CIDR notation)."""
        self._filters.append(f"net {network}")
        return self
    
    def src_net(self, network: str) -> "BPFFilter":
        """Filter by source network."""
        self._filters.append(f"src net {network}")
        return self
    
    def dst_net(self, network: str) -> "BPFFilter":
        """Filter by destination network."""
        self._filters.append(f"dst net {network}")
        return self
    
    def protocol(self, proto: str) -> "BPFFilter":
        """Filter by protocol (tcp, udp, icmp, etc.)."""
        self._filters.append(proto.lower())
        return self
    
    def tcp(self) -> "BPFFilter":
        """Filter TCP packets only."""
        return self.protocol("tcp")
    
    def udp(self) -> "BPFFilter":
        """Filter UDP packets only."""
        return self.protocol("udp")
    
    def icmp(self) -> "BPFFilter":
        """Filter ICMP packets only."""
        return self.protocol("icmp")
    
    def tcp_flags(self, flags: str) -> "BPFFilter":
        """
        Filter by TCP flags.
        
        Args:
            flags: TCP flags like "syn", "ack", "fin", "rst", "psh", "urg"
                   or combinations like "syn and ack"
        """
        flag_map = {
            "fin": "tcp[tcpflags] & tcp-fin != 0",
            "syn": "tcp[tcpflags] & tcp-syn != 0",
            "rst": "tcp[tcpflags] & tcp-rst != 0",
            "psh": "tcp[tcpflags] & tcp-push != 0",
            "ack": "tcp[tcpflags] & tcp-ack != 0",
            "urg": "tcp[tcpflags] & tcp-urg != 0",
        }
        flags_lower = flags.lower()
        if flags_lower in flag_map:
            self._filters.append(flag_map[flags_lower])
        else:
            self._filters.append(f"tcp[tcpflags] & ({flags}) != 0")
        return self
    
    def not_(self, expression: str) -> "BPFFilter":
        """Negate an expression."""
        self._filters.append(f"not ({expression})")
        return self
    
    def exclude_port(self, port: int) -> "BPFFilter":
        """Exclude traffic on a specific port."""
        self._filters.append(f"not port {port}")
        return self
    
    def exclude_host(self, ip: str) -> "BPFFilter":
        """Exclude traffic from/to a specific host."""
        self._filters.append(f"not host {ip}")
        return self
    
    def tls_only(self) -> "BPFFilter":
        """Filter for TLS/SSL traffic (port 443 or TLS content type)."""
        self._filters.append("(port 443 or port 8443)")
        return self
    
    def http_only(self) -> "BPFFilter":
        """Filter for HTTP traffic."""
        self._filters.append("(port 80 or port 8080)")
        return self
    
    def dns_only(self) -> "BPFFilter":
        """Filter for DNS traffic."""
        self._filters.append("port 53")
        return self
    
    def greater_than(self, bytes_len: int) -> "BPFFilter":
        """Filter packets greater than specified length."""
        self._filters.append(f"greater {bytes_len}")
        return self
    
    def less_than(self, bytes_len: int) -> "BPFFilter":
        """Filter packets less than specified length."""
        self._filters.append(f"less {bytes_len}")
        return self
    
    def build(self, operator: str = "and") -> str:
        """
        Build the final BPF filter string.
        
        Args:
            operator: Logical operator between filters ("and" or "or")
        
        Returns:
            Complete BPF filter expression
        """
        if not self._filters:
            return ""
        return f" {operator} ".join(f"({f})" for f in self._filters)
    
    def __str__(self) -> str:
        return self.build()
    
    def __repr__(self) -> str:
        return f"BPFFilter('{self.build()}')"
    
    @classmethod
    def from_string(cls, expression: str) -> "BPFFilter":
        """Create BPFFilter from raw expression string."""
        instance = cls()
        instance.raw(expression)
        return instance
    
    @classmethod
    def common_filters(cls) -> Dict[str, str]:
        """Get common pre-built filter expressions."""
        return {
            "tls": "(port 443 or port 8443) and tcp",
            "http": "(port 80 or port 8080) and tcp",
            "dns": "port 53",
            "ssh": "port 22 and tcp",
            "smtp": "(port 25 or port 587 or port 465) and tcp",
            "ftp": "(port 20 or port 21) and tcp",
            "web": "(port 80 or port 443 or port 8080 or port 8443) and tcp",
            "syn_scan": "tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0",
            "large_packets": "greater 1400",
            "no_arp": "not arp",
            "no_broadcast": "not broadcast and not multicast",
        }


class TLSDetector:
    """
    Detects and analyzes TLS/SSL handshakes from packet payloads.
    """
    
    def __init__(self):
        self._handshakes: Dict[str, TLSHandshakeInfo] = {}
        self._alerts: List[NetworkAlert] = []
    
    def is_tls_packet(self, payload: bytes) -> bool:
        """Check if payload appears to be TLS."""
        if len(payload) < 5:
            return False
        
        content_type = payload[0]
        if content_type not in TLS_CONTENT_TYPES:
            return False
        
        # Check version bytes
        version = (payload[1] << 8) | payload[2]
        return version in TLS_VERSIONS
    
    def detect_handshake(
        self,
        payload: bytes,
        connection_id: str,
    ) -> Optional[TLSHandshakeInfo]:
        """
        Detect and parse TLS handshake from payload.
        
        Args:
            payload: Raw packet payload
            connection_id: Unique connection identifier
        
        Returns:
            TLSHandshakeInfo if handshake detected, None otherwise
        """
        if not self.is_tls_packet(payload):
            return None
        
        try:
            content_type = payload[0]
            version_raw = (payload[1] << 8) | payload[2]
            version = TLS_VERSIONS.get(version_raw, TLSVersion.UNKNOWN)
            record_length = (payload[3] << 8) | payload[4]
            
            # Get or create handshake info
            if connection_id not in self._handshakes:
                self._handshakes[connection_id] = TLSHandshakeInfo(
                    version=version
                )
            
            info = self._handshakes[connection_id]
            
            # Parse handshake message
            if content_type == 22 and len(payload) > 5:  # Handshake
                handshake_type = payload[5]
                handshake_name = TLS_HANDSHAKE_TYPES.get(
                    handshake_type, f"unknown({handshake_type})"
                )
                
                if handshake_type == 1:  # Client Hello
                    self._parse_client_hello(payload[5:], info)
                elif handshake_type == 2:  # Server Hello
                    self._parse_server_hello(payload[5:], info)
                elif handshake_type == 11:  # Certificate
                    self._parse_certificate(payload[5:], info)
                elif handshake_type == 20:  # Finished
                    info.handshake_complete = True
            
            # Check for security issues
            self._check_security(info, connection_id)
            
            return info
            
        except Exception as e:
            logger.debug(f"TLS parsing error: {e}")
            return None
    
    def _parse_client_hello(
        self,
        data: bytes,
        info: TLSHandshakeInfo,
    ) -> None:
        """Parse Client Hello message for extensions."""
        try:
            if len(data) < 38:
                return
            
            # Skip handshake header (4 bytes) + version (2) + random (32)
            pos = 38
            
            # Session ID length
            if pos >= len(data):
                return
            session_id_len = data[pos]
            pos += 1 + session_id_len
            
            # Cipher suites
            if pos + 2 > len(data):
                return
            cipher_len = (data[pos] << 8) | data[pos + 1]
            pos += 2 + cipher_len
            
            # Compression methods
            if pos >= len(data):
                return
            comp_len = data[pos]
            pos += 1 + comp_len
            
            # Extensions
            if pos + 2 > len(data):
                return
            ext_len = (data[pos] << 8) | data[pos + 1]
            pos += 2
            ext_end = pos + ext_len
            
            while pos + 4 <= ext_end and pos < len(data):
                ext_type = (data[pos] << 8) | data[pos + 1]
                ext_data_len = (data[pos + 2] << 8) | data[pos + 3]
                pos += 4
                
                if ext_type == 0 and ext_data_len > 0:  # SNI
                    self._parse_sni(data[pos:pos + ext_data_len], info)
                elif ext_type == 43:  # Supported versions (TLS 1.3)
                    self._parse_supported_versions(
                        data[pos:pos + ext_data_len], info
                    )
                
                pos += ext_data_len
                
        except Exception as e:
            logger.debug(f"Client Hello parsing error: {e}")
    
    def _parse_server_hello(
        self,
        data: bytes,
        info: TLSHandshakeInfo,
    ) -> None:
        """Parse Server Hello message."""
        try:
            if len(data) < 38:
                return
            
            # Get selected version
            version_raw = (data[4] << 8) | data[5]
            info.version = TLS_VERSIONS.get(version_raw, TLSVersion.UNKNOWN)
            
            # Parse cipher suite selection
            pos = 38
            if pos >= len(data):
                return
            session_id_len = data[pos]
            pos += 1 + session_id_len
            
            if pos + 2 > len(data):
                return
            cipher_suite = (data[pos] << 8) | data[pos + 1]
            info.cipher_suite = f"0x{cipher_suite:04X}"
            
        except Exception as e:
            logger.debug(f"Server Hello parsing error: {e}")
    
    def _parse_certificate(
        self,
        data: bytes,
        info: TLSHandshakeInfo,
    ) -> None:
        """Parse Certificate message for basic info."""
        try:
            # Certificate parsing is complex - just detect presence
            if len(data) > 10:
                info.extensions["has_certificate"] = True
        except Exception:
            pass
    
    def _parse_sni(self, data: bytes, info: TLSHandshakeInfo) -> None:
        """Parse Server Name Indication extension."""
        try:
            if len(data) < 5:
                return
            
            # SNI list length
            list_len = (data[0] << 8) | data[1]
            pos = 2
            
            while pos + 3 < len(data) and pos < list_len + 2:
                name_type = data[pos]
                name_len = (data[pos + 1] << 8) | data[pos + 2]
                pos += 3
                
                if name_type == 0 and pos + name_len <= len(data):
                    info.server_name = data[pos:pos + name_len].decode(
                        'utf-8', errors='ignore'
                    )
                    break
                pos += name_len
                
        except Exception as e:
            logger.debug(f"SNI parsing error: {e}")
    
    def _parse_supported_versions(
        self,
        data: bytes,
        info: TLSHandshakeInfo,
    ) -> None:
        """Parse supported versions extension (TLS 1.3)."""
        try:
            if len(data) < 1:
                return
            
            versions_len = data[0]
            pos = 1
            
            while pos + 2 <= len(data) and pos < versions_len + 1:
                version_raw = (data[pos] << 8) | data[pos + 1]
                version = TLS_VERSIONS.get(version_raw, TLSVersion.UNKNOWN)
                if version != TLSVersion.UNKNOWN:
                    info.supported_versions.append(version)
                pos += 2
                
        except Exception as e:
            logger.debug(f"Supported versions parsing error: {e}")
    
    def _check_security(
        self,
        info: TLSHandshakeInfo,
        connection_id: str,
    ) -> None:
        """Check TLS configuration for security issues."""
        warnings = []
        
        if info.is_deprecated:
            warnings.append(
                f"Deprecated TLS version: {info.version.value}"
            )
            self._generate_alert(
                connection_id,
                AlertType.WEAK_TLS,
                AlertSeverity.HIGH,
                f"Deprecated TLS version {info.version.value} detected",
                info,
            )
        
        if info.cipher_suite and any(
            weak in str(info.cipher_suite)
            for weak in ["NULL", "EXPORT", "RC4", "DES"]
        ):
            warnings.append(f"Weak cipher suite: {info.cipher_suite}")
            self._generate_alert(
                connection_id,
                AlertType.WEAK_TLS,
                AlertSeverity.HIGH,
                f"Weak cipher suite {info.cipher_suite} detected",
                info,
            )
        
        info.warnings.extend(warnings)
    
    def _generate_alert(
        self,
        connection_id: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        tls_info: TLSHandshakeInfo,
    ) -> None:
        """Generate a security alert."""
        alert = NetworkAlert(
            id=str(uuid.uuid4()),
            alert_type=alert_type,
            severity=severity,
            message=message,
            tls_info=tls_info,
            recommendations=[
                "Upgrade to TLS 1.2 or TLS 1.3",
                "Disable deprecated protocols",
                "Use strong cipher suites",
            ],
        )
        self._alerts.append(alert)
        logger.security(f"TLS Alert: {message}")
    
    def get_handshake(self, connection_id: str) -> Optional[TLSHandshakeInfo]:
        """Get handshake info for a connection."""
        return self._handshakes.get(connection_id)
    
    def get_alerts(self) -> List[NetworkAlert]:
        """Get all generated alerts."""
        return self._alerts.copy()
    
    def clear(self) -> None:
        """Clear all tracked handshakes and alerts."""
        self._handshakes.clear()
        self._alerts.clear()


class TrafficAnalyzer:
    """
    Analyzes network traffic patterns and extracts metadata.
    """
    
    def __init__(self, interface: str = ""):
        self.metadata = TrafficMetadata(
            interface=interface,
            start_time=datetime.now(),
        )
        self._connections: Dict[str, ConnectionInfo] = {}
        self._tls_detector = TLSDetector()
        self._callbacks: List[Callable[[PacketInfo], None]] = []
        self._alert_callbacks: List[Callable[[NetworkAlert], None]] = []
    
    def register_callback(
        self,
        callback: Callable[[PacketInfo], None],
    ) -> None:
        """Register a callback for processed packets."""
        self._callbacks.append(callback)
    
    def register_alert_callback(
        self,
        callback: Callable[[NetworkAlert], None],
    ) -> None:
        """Register a callback for alerts."""
        self._alert_callbacks.append(callback)
    
    def process_packet(self, packet_info: PacketInfo) -> PacketInfo:
        """
        Process a packet and update traffic metadata.
        
        Args:
            packet_info: Extracted packet information
        
        Returns:
            Updated PacketInfo with additional analysis
        """
        # Update overall metadata
        self.metadata.update_from_packet(packet_info)
        
        # Track connection
        if packet_info.src_port and packet_info.dst_port:
            conn_id = self._get_connection_id(packet_info)
            
            if conn_id not in self._connections:
                self._connections[conn_id] = ConnectionInfo(
                    src_ip=packet_info.src_ip,
                    src_port=packet_info.src_port,
                    dst_ip=packet_info.dst_ip,
                    dst_port=packet_info.dst_port,
                    protocol=packet_info.protocol,
                    first_seen=packet_info.timestamp,
                )
                self.metadata.unique_connections += 1
            
            conn = self._connections[conn_id]
            conn.update(packet_info)
            
            # Check for TLS
            if packet_info.raw_payload and packet_info.dst_port in (443, 8443):
                tls_info = self._tls_detector.detect_handshake(
                    packet_info.raw_payload,
                    conn_id,
                )
                if tls_info:
                    conn.tls_info = tls_info
                    if not packet_info.metadata.get("tls_detected"):
                        self.metadata.tls_handshakes += 1
                        packet_info.metadata["tls_detected"] = True
                        packet_info.metadata["tls_version"] = tls_info.version.value
                        packet_info.metadata["server_name"] = tls_info.server_name
        
        # Protocol-specific analysis
        self._analyze_protocol(packet_info)
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(packet_info)
            except Exception as e:
                logger.error(f"Packet callback error: {e}")
        
        return packet_info
    
    def _get_connection_id(self, packet: PacketInfo) -> str:
        """Generate unique connection ID."""
        # Normalize to ensure bidirectional matching
        endpoints = sorted([
            (packet.src_ip, packet.src_port),
            (packet.dst_ip, packet.dst_port),
        ])
        return f"{endpoints[0][0]}:{endpoints[0][1]}-{endpoints[1][0]}:{endpoints[1][1]}-{packet.protocol.value}"
    
    def _analyze_protocol(self, packet_info: PacketInfo) -> None:
        """Perform protocol-specific analysis."""
        # DNS detection
        if packet_info.dst_port == 53 or packet_info.src_port == 53:
            self.metadata.dns_queries += 1
            packet_info.metadata["is_dns"] = True
        
        # HTTP detection
        if packet_info.dst_port in (80, 8080):
            if packet_info.raw_payload:
                payload_start = packet_info.raw_payload[:20]
                if any(method in payload_start for method in [
                    b"GET ", b"POST ", b"PUT ", b"DELETE ",
                    b"HEAD ", b"OPTIONS ", b"PATCH "
                ]):
                    self.metadata.http_requests += 1
                    packet_info.metadata["is_http"] = True
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionInfo]:
        """Get connection by ID."""
        return self._connections.get(connection_id)
    
    def get_connections(self) -> List[ConnectionInfo]:
        """Get all tracked connections."""
        return list(self._connections.values())
    
    def get_active_connections(
        self,
        timeout_seconds: float = 60.0,
    ) -> List[ConnectionInfo]:
        """Get connections active within timeout period."""
        now = datetime.now()
        return [
            conn for conn in self._connections.values()
            if (now - conn.last_seen).total_seconds() < timeout_seconds
        ]
    
    def get_tls_connections(self) -> List[ConnectionInfo]:
        """Get all connections with TLS info."""
        return [
            conn for conn in self._connections.values()
            if conn.tls_info is not None
        ]
    
    def get_alerts(self) -> List[NetworkAlert]:
        """Get all security alerts."""
        return self._tls_detector.get_alerts()
    
    def get_metadata(self) -> TrafficMetadata:
        """Get current traffic metadata."""
        self.metadata.end_time = datetime.now()
        return self.metadata
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        return {
            "metadata": self.get_metadata().to_dict(),
            "connections": len(self._connections),
            "active_connections": len(self.get_active_connections()),
            "tls_connections": len(self.get_tls_connections()),
            "alerts": len(self.get_alerts()),
        }
    
    def reset(self) -> None:
        """Reset analyzer state."""
        self.metadata = TrafficMetadata(
            interface=self.metadata.interface,
            start_time=datetime.now(),
        )
        self._connections.clear()
        self._tls_detector.clear()


class PacketCapture:
    """
    Low-level packet capture using Scapy.
    """
    
    def __init__(
        self,
        interface: Optional[str] = None,
        bpf_filter: Optional[Union[str, BPFFilter]] = None,
        promisc: bool = True,
        store_packets: bool = False,
    ):
        """
        Initialize packet capture.
        
        Args:
            interface: Network interface to capture on (None for default)
            bpf_filter: BPF filter expression or BPFFilter object
            promisc: Enable promiscuous mode
            store_packets: Store captured packets in memory
        """
        if not SCAPY_AVAILABLE:
            raise ImportError(
                "Scapy is required for packet capture. "
                "Install with: pip install scapy"
            )
        
        self.interface = interface
        self.bpf_filter = str(bpf_filter) if bpf_filter else ""
        self.promisc = promisc
        self.store_packets = store_packets
        self._packets: List[ScapyPacket] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._packet_queue: Queue = Queue()
        self._callbacks: List[Callable[[ScapyPacket], None]] = []
    
    @staticmethod
    def list_interfaces() -> List[Dict[str, str]]:
        """List available network interfaces."""
        if not SCAPY_AVAILABLE:
            return []
        
        interfaces = []
        for iface in get_if_list():
            try:
                hwaddr = get_if_hwaddr(iface)
                interfaces.append({
                    "name": iface,
                    "mac": hwaddr,
                })
            except Exception:
                interfaces.append({
                    "name": iface,
                    "mac": "unknown",
                })
        return interfaces
    
    def register_callback(
        self,
        callback: Callable[[ScapyPacket], None],
    ) -> None:
        """Register a callback for each captured packet."""
        self._callbacks.append(callback)
    
    def _packet_handler(self, packet: ScapyPacket) -> None:
        """Internal packet handler."""
        if self.store_packets:
            self._packets.append(packet)
        
        self._packet_queue.put(packet)
        
        for callback in self._callbacks:
            try:
                callback(packet)
            except Exception as e:
                logger.error(f"Packet callback error: {e}")
    
    def start(self, count: int = 0, timeout: Optional[float] = None) -> None:
        """
        Start packet capture in background thread.
        
        Args:
            count: Number of packets to capture (0 = infinite)
            timeout: Capture timeout in seconds
        """
        if self._running:
            logger.warning("Capture already running")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._capture_thread,
            args=(count, timeout),
            daemon=True,
        )
        self._thread.start()
        logger.info(
            f"Started packet capture on {self.interface or 'default'} "
            f"with filter: {self.bpf_filter or 'none'}"
        )
    
    def _capture_thread(
        self,
        count: int,
        timeout: Optional[float],
    ) -> None:
        """Background capture thread."""
        try:
            sniff(
                iface=self.interface,
                filter=self.bpf_filter or None,
                prn=self._packet_handler,
                count=count,
                timeout=timeout,
                store=False,
                promisc=self.promisc,
                stop_filter=lambda _: not self._running,
            )
        except Exception as e:
            logger.error(f"Capture error: {e}")
        finally:
            self._running = False
    
    def stop(self) -> None:
        """Stop packet capture."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Stopped packet capture")
    
    def capture_sync(
        self,
        count: int = 10,
        timeout: float = 10.0,
    ) -> List[ScapyPacket]:
        """
        Capture packets synchronously.
        
        Args:
            count: Number of packets to capture
            timeout: Timeout in seconds
        
        Returns:
            List of captured packets
        """
        packets = sniff(
            iface=self.interface,
            filter=self.bpf_filter or None,
            count=count,
            timeout=timeout,
            promisc=self.promisc,
        )
        return list(packets)
    
    def get_packet(
        self,
        timeout: float = 1.0,
    ) -> Optional[ScapyPacket]:
        """Get next packet from queue."""
        try:
            return self._packet_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def packet_generator(
        self,
        timeout: float = 1.0,
    ) -> Generator[ScapyPacket, None, None]:
        """Generator yielding packets as they arrive."""
        while self._running:
            packet = self.get_packet(timeout)
            if packet:
                yield packet
    
    @property
    def is_running(self) -> bool:
        """Check if capture is running."""
        return self._running
    
    @property
    def packet_count(self) -> int:
        """Get number of stored packets."""
        return len(self._packets)
    
    def get_packets(self) -> List[ScapyPacket]:
        """Get all stored packets."""
        return self._packets.copy()
    
    def clear_packets(self) -> None:
        """Clear stored packets."""
        self._packets.clear()


class NetworkMonitor:
    """
    High-level network monitoring interface.
    
    Combines packet capture with traffic analysis for real-time
    network monitoring and threat detection.
    
    Example:
        monitor = NetworkMonitor(interface="eth0")
        monitor.set_filter(BPFFilter().tcp().port(443))
        
        with monitor.capture() as cap:
            for packet in cap.packets():
                print(packet.to_dict())
    """
    
    def __init__(
        self,
        interface: Optional[str] = None,
        bpf_filter: Optional[Union[str, BPFFilter]] = None,
    ):
        """
        Initialize network monitor.
        
        Args:
            interface: Network interface to monitor
            bpf_filter: Initial BPF filter
        """
        self.interface = interface
        self._bpf_filter = bpf_filter
        self._capture: Optional[PacketCapture] = None
        self._analyzer = TrafficAnalyzer(interface or "default")
        self._running = False
        self._packet_callbacks: List[Callable[[PacketInfo], None]] = []
        self._alert_callbacks: List[Callable[[NetworkAlert], None]] = []
    
    def set_filter(self, bpf_filter: Union[str, BPFFilter]) -> "NetworkMonitor":
        """Set BPF filter for capture."""
        self._bpf_filter = bpf_filter
        return self
    
    def set_interface(self, interface: str) -> "NetworkMonitor":
        """Set network interface."""
        self.interface = interface
        self._analyzer.metadata.interface = interface
        return self
    
    def on_packet(
        self,
        callback: Callable[[PacketInfo], None],
    ) -> "NetworkMonitor":
        """Register packet callback."""
        self._packet_callbacks.append(callback)
        return self
    
    def on_alert(
        self,
        callback: Callable[[NetworkAlert], None],
    ) -> "NetworkMonitor":
        """Register alert callback."""
        self._alert_callbacks.append(callback)
        return self
    
    def _extract_packet_info(self, packet: ScapyPacket) -> Optional[PacketInfo]:
        """Extract PacketInfo from Scapy packet."""
        try:
            # Get IP layer
            if IP in packet:
                ip_layer = packet[IP]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
            elif IPv6 in packet:
                ip_layer = packet[IPv6]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
            else:
                return None
            
            # Determine protocol and ports
            src_port = None
            dst_port = None
            protocol = Protocol.OTHER
            flags = {}
            
            if TCP in packet:
                tcp_layer = packet[TCP]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
                protocol = Protocol.TCP
                flags = {
                    "syn": bool(tcp_layer.flags & 0x02),
                    "ack": bool(tcp_layer.flags & 0x10),
                    "fin": bool(tcp_layer.flags & 0x01),
                    "rst": bool(tcp_layer.flags & 0x04),
                    "psh": bool(tcp_layer.flags & 0x08),
                    "urg": bool(tcp_layer.flags & 0x20),
                }
            elif UDP in packet:
                udp_layer = packet[UDP]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
                protocol = Protocol.UDP
            elif ICMP in packet:
                protocol = Protocol.ICMP
            
            # Get payload
            raw_payload = None
            payload_length = 0
            if Raw in packet:
                raw_payload = bytes(packet[Raw].load)
                payload_length = len(raw_payload)
            
            return PacketInfo(
                timestamp=datetime.now(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol,
                length=len(packet),
                payload_length=payload_length,
                flags=flags,
                raw_payload=raw_payload,
            )
            
        except Exception as e:
            logger.debug(f"Packet extraction error: {e}")
            return None
    
    def _process_packet(self, packet: ScapyPacket) -> None:
        """Process a captured packet."""
        packet_info = self._extract_packet_info(packet)
        if packet_info:
            # Run through analyzer
            packet_info = self._analyzer.process_packet(packet_info)
            
            # Notify callbacks
            for callback in self._packet_callbacks:
                try:
                    callback(packet_info)
                except Exception as e:
                    logger.error(f"Packet callback error: {e}")
    
    def start(
        self,
        count: int = 0,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Start network monitoring.
        
        Args:
            count: Number of packets to capture (0 = infinite)
            timeout: Capture timeout in seconds
        """
        if self._running:
            logger.warning("Monitor already running")
            return
        
        self._capture = PacketCapture(
            interface=self.interface,
            bpf_filter=self._bpf_filter,
        )
        self._capture.register_callback(self._process_packet)
        self._capture.start(count=count, timeout=timeout)
        self._running = True
        
        logger.info(
            f"Network monitor started on {self.interface or 'default'}"
        )
    
    def stop(self) -> None:
        """Stop network monitoring."""
        if self._capture:
            self._capture.stop()
        self._running = False
        self._analyzer.metadata.end_time = datetime.now()
        logger.info("Network monitor stopped")
    
    @contextmanager
    def capture(
        self,
        count: int = 0,
        timeout: Optional[float] = None,
    ) -> Generator["CaptureContext", None, None]:
        """
        Context manager for capture session.
        
        Example:
            with monitor.capture(timeout=30) as cap:
                for packet in cap.packets():
                    print(packet)
        """
        ctx = CaptureContext(self, count, timeout)
        try:
            yield ctx
        finally:
            ctx.stop()
    
    def capture_sync(
        self,
        count: int = 10,
        timeout: float = 10.0,
    ) -> List[PacketInfo]:
        """
        Capture packets synchronously.
        
        Args:
            count: Number of packets to capture
            timeout: Timeout in seconds
        
        Returns:
            List of PacketInfo objects
        """
        capture = PacketCapture(
            interface=self.interface,
            bpf_filter=self._bpf_filter,
        )
        raw_packets = capture.capture_sync(count=count, timeout=timeout)
        
        results = []
        for packet in raw_packets:
            info = self._extract_packet_info(packet)
            if info:
                info = self._analyzer.process_packet(info)
                results.append(info)
        
        return results
    
    @property
    def is_running(self) -> bool:
        """Check if monitor is running."""
        return self._running
    
    def get_connections(self) -> List[ConnectionInfo]:
        """Get tracked connections."""
        return self._analyzer.get_connections()
    
    def get_tls_connections(self) -> List[ConnectionInfo]:
        """Get connections with TLS info."""
        return self._analyzer.get_tls_connections()
    
    def get_alerts(self) -> List[NetworkAlert]:
        """Get security alerts."""
        return self._analyzer.get_alerts()
    
    def get_metadata(self) -> TrafficMetadata:
        """Get traffic metadata."""
        return self._analyzer.get_metadata()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        return self._analyzer.get_summary()
    
    def reset_stats(self) -> None:
        """Reset analyzer statistics."""
        self._analyzer.reset()
    
    @staticmethod
    def list_interfaces() -> List[Dict[str, str]]:
        """List available network interfaces."""
        return PacketCapture.list_interfaces()


class CaptureContext:
    """Context for capture sessions."""
    
    def __init__(
        self,
        monitor: NetworkMonitor,
        count: int,
        timeout: Optional[float],
    ):
        self._monitor = monitor
        self._count = count
        self._timeout = timeout
        self._started = False
    
    def start(self) -> None:
        """Start capture."""
        if not self._started:
            self._monitor.start(count=self._count, timeout=self._timeout)
            self._started = True
    
    def stop(self) -> None:
        """Stop capture."""
        if self._started:
            self._monitor.stop()
            self._started = False
    
    def packets(self) -> Generator[PacketInfo, None, None]:
        """Generator yielding captured packets."""
        self.start()
        
        if self._monitor._capture:
            for packet in self._monitor._capture.packet_generator():
                info = self._monitor._extract_packet_info(packet)
                if info:
                    yield self._monitor._analyzer.process_packet(info)
    
    @property
    def metadata(self) -> TrafficMetadata:
        """Get current metadata."""
        return self._monitor.get_metadata()
    
    @property
    def connections(self) -> List[ConnectionInfo]:
        """Get current connections."""
        return self._monitor.get_connections()
    
    @property
    def alerts(self) -> List[NetworkAlert]:
        """Get current alerts."""
        return self._monitor.get_alerts()


# Convenience functions

def create_tls_filter() -> BPFFilter:
    """Create a BPF filter for TLS traffic."""
    return BPFFilter().tcp().tls_only()


def create_http_filter() -> BPFFilter:
    """Create a BPF filter for HTTP/HTTPS traffic."""
    return BPFFilter().tcp().raw("port 80 or port 443 or port 8080 or port 8443")


def create_dns_filter() -> BPFFilter:
    """Create a BPF filter for DNS traffic."""
    return BPFFilter().dns_only()


def quick_capture(
    interface: Optional[str] = None,
    count: int = 10,
    timeout: float = 10.0,
    bpf_filter: Optional[str] = None,
) -> List[PacketInfo]:
    """
    Quick packet capture utility.
    
    Args:
        interface: Network interface
        count: Number of packets
        timeout: Timeout in seconds
        bpf_filter: BPF filter expression
    
    Returns:
        List of captured packets
    """
    monitor = NetworkMonitor(interface=interface, bpf_filter=bpf_filter)
    return monitor.capture_sync(count=count, timeout=timeout)


def monitor_tls(
    interface: Optional[str] = None,
    callback: Optional[Callable[[TLSHandshakeInfo], None]] = None,
) -> NetworkMonitor:
    """
    Create a monitor specifically for TLS traffic.
    
    Args:
        interface: Network interface
        callback: Callback for TLS handshakes
    
    Returns:
        Configured NetworkMonitor
    """
    monitor = NetworkMonitor(
        interface=interface,
        bpf_filter=create_tls_filter(),
    )
    
    if callback:
        def tls_callback(packet: PacketInfo):
            if packet.metadata.get("tls_detected"):
                # Get TLS info from connection
                conns = monitor.get_tls_connections()
                for conn in conns:
                    if conn.tls_info and not conn.tls_info.handshake_complete:
                        callback(conn.tls_info)
        
        monitor.on_packet(tls_callback)
    
    return monitor
