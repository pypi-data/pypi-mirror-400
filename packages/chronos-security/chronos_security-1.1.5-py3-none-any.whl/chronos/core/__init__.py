"""
CHRONOS Core Module
===================

Core functionality for the CHRONOS quantum security platform.
Contains cryptographic primitives, security engines, and core utilities.
"""

from chronos.core.config import Config, get_config, reset_config
from chronos.core.exceptions import ChronosError, SecurityError, QuantumError
from chronos.core.schema import (
    ChronosConfig,
    SecurityLevel,
    LogLevel,
    CryptoConfig,
    DetectionConfig,
    AnalysisConfig,
    DefenseConfig,
)

# Detection module
from chronos.core.detect import (
    NetworkMonitor,
    PacketCapture,
    TrafficAnalyzer,
    TLSDetector,
    BPFFilter,
    PacketInfo,
    ConnectionInfo,
    TLSHandshakeInfo,
    TrafficMetadata,
    NetworkAlert,
)

__all__ = [
    # Config
    "Config",
    "get_config",
    "reset_config",
    "ChronosConfig",
    "ChronosError",
    "SecurityError", 
    "QuantumError",
    "SecurityLevel",
    "LogLevel",
    "CryptoConfig",
    "DetectionConfig",
    "AnalysisConfig",
    "DefenseConfig",
    # Detection
    "NetworkMonitor",
    "PacketCapture",
    "TrafficAnalyzer",
    "TLSDetector",
    "BPFFilter",
    "PacketInfo",
    "ConnectionInfo",
    "TLSHandshakeInfo",
    "TrafficMetadata",
    "NetworkAlert",
]
