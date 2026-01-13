"""
CHRONOS Detection Module
========================

Network monitoring and threat detection components.
"""

from chronos.core.detect.network_monitor import (
    NetworkMonitor,
    PacketCapture,
    TrafficAnalyzer,
    TLSDetector,
    BPFFilter,
    create_tls_filter,
    create_http_filter,
    create_dns_filter,
    quick_capture,
    monitor_tls,
)
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
from chronos.core.detect.darkweb_monitor import (
    DarkWebMonitor,
    TorController,
    AlertDispatcher,
    WebhookConfig,
    MonitoringPattern,
    DataFingerprint,
    PasteEntry,
    MonitoringMatch,
    DarkWebAlert,
    BaseScraper,
    PastebinScraper,
    GenericPasteScraper,
    SourceType,
    MatchType,
    create_monitor,
    quick_scan,
)
from chronos.core.detect.hndl_detector import (
    HNDLDetector,
    BaselineProfiler,
    AnomalyDetector,
    BaselineProfile,
    AnomalyScore,
    HNDLAlert,
    TrafficSample,
    StatisticsTracker,
    TimeSeriesAnalyzer,
    TrafficPatternAnalyzer,
    MLClassification,
    MLModelAdapter,
    HNDLIndicator,
    RiskLevel,
    create_detector,
    quick_analyze,
)

__all__ = [
    # Network Monitor classes
    "NetworkMonitor",
    "PacketCapture",
    "TrafficAnalyzer",
    "TLSDetector",
    "BPFFilter",
    # Network helper functions
    "create_tls_filter",
    "create_http_filter",
    "create_dns_filter",
    "quick_capture",
    "monitor_tls",
    # Network Models
    "PacketInfo",
    "ConnectionInfo",
    "TLSHandshakeInfo",
    "TrafficMetadata",
    "NetworkAlert",
    # Network Enums
    "Protocol",
    "TLSVersion",
    "AlertSeverity",
    "AlertType",
    # Dark Web Monitor classes
    "DarkWebMonitor",
    "TorController",
    "AlertDispatcher",
    "WebhookConfig",
    "MonitoringPattern",
    "DataFingerprint",
    "PasteEntry",
    "MonitoringMatch",
    "DarkWebAlert",
    "BaseScraper",
    "PastebinScraper",
    "GenericPasteScraper",
    # Dark Web Enums
    "SourceType",
    "MatchType",
    # Dark Web helper functions
    "create_monitor",
    "quick_scan",
    # HNDL Detector classes
    "HNDLDetector",
    "BaselineProfiler",
    "AnomalyDetector",
    "BaselineProfile",
    "AnomalyScore",
    "HNDLAlert",
    "TrafficSample",
    "StatisticsTracker",
    "TimeSeriesAnalyzer",
    "TrafficPatternAnalyzer",
    "MLClassification",
    "MLModelAdapter",
    # HNDL Enums
    "HNDLIndicator",
    "RiskLevel",
    # HNDL helper functions
    "create_detector",
    "quick_analyze",
]
