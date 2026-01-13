"""
CHRONOS HNDL Attack Detector
============================

Detects "Harvest Now, Decrypt Later" (HNDL) attacks where adversaries
capture encrypted traffic with the intent to decrypt it once quantum
computers become capable.

Key Detection Strategies:
1. Baseline behavior profiling - Learn normal traffic patterns
2. Anomaly detection for data transfer patterns
3. Statistical analysis of traffic volumes
4. Statistical analysis of traffic patterns
5. Time-series analysis for volume anomalies
6. ML model integration for classification
7. Detection of bulk data exfiltration indicators
"""

import math
import statistics
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

from chronos.cli.utils.logger import get_logger
from chronos.core.detect.models import (
    PacketInfo,
    ConnectionInfo,
    Protocol,
    AlertSeverity,
    AlertType,
    NetworkAlert,
)

logger = get_logger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class HNDLIndicator(str, Enum):
    """Indicators of potential HNDL attack."""
    HIGH_VOLUME_TRANSFER = "high_volume_transfer"
    UNUSUAL_DESTINATION = "unusual_destination"
    BULK_ENCRYPTION = "bulk_encryption"
    PATTERN_ANOMALY = "pattern_anomaly"
    TIME_ANOMALY = "time_anomaly"
    FREQUENCY_ANOMALY = "frequency_anomaly"
    SIZE_ANOMALY = "size_anomaly"
    PROTOCOL_ANOMALY = "protocol_anomaly"
    DESTINATION_CONCENTRATION = "destination_concentration"
    DATA_STAGING = "data_staging"


class RiskLevel(str, Enum):
    """Risk level assessment."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Default thresholds for anomaly detection
DEFAULT_THRESHOLDS = {
    "volume_std_multiplier": 3.0,  # Standard deviations from mean
    "min_baseline_samples": 100,   # Minimum samples for baseline
    "time_window_seconds": 300,    # 5 minute analysis window
    "max_transfer_rate_mbps": 100, # Max expected transfer rate
    "unusual_port_threshold": 0.1, # 10% of traffic to unusual ports
    "concentration_threshold": 0.8, # 80% to single destination
    "frequency_multiplier": 5.0,   # 5x normal frequency
    "size_percentile": 99,         # 99th percentile for size anomaly
    "volume_time_series_window": 12,  # Rolling window for volume analysis
    "volume_time_series_std_multiplier": 3.0,  # Std dev threshold for spikes
    "volume_time_series_ratio": 3.0,  # Ratio threshold when variance is low
    "pattern_js_threshold": 0.2,    # JS divergence threshold for patterns
    "pattern_entropy_min": 0.4,     # Min normalized entropy for patterns
    "pattern_weight": 0.1,          # Weight for pattern anomaly scoring
}


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TrafficSample:
    """Single traffic measurement sample."""
    
    timestamp: datetime
    bytes_transferred: int
    packet_count: int
    connection_count: int
    unique_destinations: int
    encrypted_ratio: float  # Ratio of encrypted traffic
    avg_packet_size: float
    protocol_distribution: Dict[str, float] = field(default_factory=dict)
    port_distribution: Dict[int, int] = field(default_factory=dict)
    destination_distribution: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "bytes_transferred": self.bytes_transferred,
            "packet_count": self.packet_count,
            "connection_count": self.connection_count,
            "unique_destinations": self.unique_destinations,
            "encrypted_ratio": self.encrypted_ratio,
            "avg_packet_size": self.avg_packet_size,
        }


@dataclass
class BaselineProfile:
    """Baseline behavior profile for normal traffic patterns."""
    
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    sample_count: int = 0
    
    # Volume statistics
    mean_bytes_per_window: float = 0.0
    std_bytes_per_window: float = 0.0
    mean_packets_per_window: float = 0.0
    std_packets_per_window: float = 0.0
    
    # Connection statistics
    mean_connections: float = 0.0
    std_connections: float = 0.0
    mean_destinations: float = 0.0
    std_destinations: float = 0.0
    
    # Packet size statistics
    mean_packet_size: float = 0.0
    std_packet_size: float = 0.0
    
    # Encryption ratio
    mean_encrypted_ratio: float = 0.0
    std_encrypted_ratio: float = 0.0
    
    # Normal port distribution
    normal_ports: Dict[int, float] = field(default_factory=dict)
    
    # Normal destination IPs
    known_destinations: Set[str] = field(default_factory=set)
    
    # Time-based patterns (hour of day -> average bytes)
    hourly_pattern: Dict[int, float] = field(default_factory=dict)
    
    # Protocol distribution baseline
    protocol_baseline: Dict[str, float] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if baseline has enough samples."""
        return self.sample_count >= DEFAULT_THRESHOLDS["min_baseline_samples"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "sample_count": self.sample_count,
            "is_valid": self.is_valid,
            "mean_bytes_per_window": self.mean_bytes_per_window,
            "std_bytes_per_window": self.std_bytes_per_window,
            "mean_packets_per_window": self.mean_packets_per_window,
            "mean_connections": self.mean_connections,
            "mean_destinations": self.mean_destinations,
            "mean_encrypted_ratio": self.mean_encrypted_ratio,
            "known_destinations_count": len(self.known_destinations),
        }


@dataclass
class AnomalyScore:
    """Anomaly detection score with breakdown."""
    
    total_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    indicators: List[HNDLIndicator]
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def calculate_risk_level(cls, score: float) -> RiskLevel:
        """Calculate risk level from score."""
        if score < 0.2:
            return RiskLevel.NONE
        elif score < 0.4:
            return RiskLevel.LOW
        elif score < 0.6:
            return RiskLevel.MEDIUM
        elif score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_score": self.total_score,
            "risk_level": self.risk_level.value,
            "indicators": [i.value for i in self.indicators],
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HNDLAlert:
    """Alert for potential HNDL attack detection."""
    
    id: str
    timestamp: datetime
    risk_level: RiskLevel
    anomaly_score: AnomalyScore
    indicators: List[HNDLIndicator]
    description: str
    affected_destinations: List[str]
    bytes_transferred: int
    duration_seconds: float
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "risk_level": self.risk_level.value,
            "anomaly_score": self.anomaly_score.to_dict(),
            "indicators": [i.value for i in self.indicators],
            "description": self.description,
            "affected_destinations": self.affected_destinations,
            "bytes_transferred": self.bytes_transferred,
            "duration_seconds": self.duration_seconds,
            "recommendations": self.recommendations,
            "acknowledged": self.acknowledged,
        }


@dataclass
class MLClassification:
    """ML classification result for HNDL detection."""

    label: str
    confidence: float
    probabilities: Dict[str, float] = field(default_factory=dict)
    model_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "label": self.label,
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "model_metadata": self.model_metadata,
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================================
# Statistical Utilities
# ============================================================================

class StatisticsTracker:
    """Online statistics tracker using Welford's algorithm."""
    
    def __init__(self, max_samples: int = 10000):
        self.max_samples = max_samples
        self._count = 0
        self._mean = 0.0
        self._m2 = 0.0  # Sum of squares of differences from mean
        self._min = float('inf')
        self._max = float('-inf')
        self._samples: Deque[float] = deque(maxlen=max_samples)
    
    def add(self, value: float) -> None:
        """Add a value using Welford's online algorithm."""
        self._count += 1
        self._samples.append(value)
        
        delta = value - self._mean
        self._mean += delta / self._count
        delta2 = value - self._mean
        self._m2 += delta * delta2
        
        self._min = min(self._min, value)
        self._max = max(self._max, value)
    
    @property
    def count(self) -> int:
        """Get sample count."""
        return self._count
    
    @property
    def mean(self) -> float:
        """Get current mean."""
        return self._mean
    
    @property
    def variance(self) -> float:
        """Get current variance."""
        if self._count < 2:
            return 0.0
        return self._m2 / (self._count - 1)
    
    @property
    def std(self) -> float:
        """Get current standard deviation."""
        return math.sqrt(self.variance)
    
    @property
    def min_value(self) -> float:
        """Get minimum value."""
        return self._min if self._count > 0 else 0.0
    
    @property
    def max_value(self) -> float:
        """Get maximum value."""
        return self._max if self._count > 0 else 0.0
    
    def percentile(self, p: float) -> float:
        """Get approximate percentile from samples."""
        if not self._samples:
            return 0.0
        sorted_samples = sorted(self._samples)
        idx = int(len(sorted_samples) * p / 100)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]
    
    def z_score(self, value: float) -> float:
        """Calculate z-score for a value."""
        if self.std == 0:
            return 0.0
        return (value - self.mean) / self.std
    
    def is_anomaly(self, value: float, threshold: float = 3.0) -> bool:
        """Check if value is anomalous based on z-score."""
        return abs(self.z_score(value)) > threshold


class TimeSeriesAnalyzer:
    """Analyzes time series data for anomalies."""
    
    def __init__(self, window_size: int = 24):
        self.window_size = window_size
        self._values: Deque[Tuple[datetime, float]] = deque(maxlen=1000)
        self._hourly_stats: Dict[int, StatisticsTracker] = defaultdict(StatisticsTracker)
    
    def add(self, timestamp: datetime, value: float) -> None:
        """Add a time series value."""
        self._values.append((timestamp, value))
        hour = timestamp.hour
        self._hourly_stats[hour].add(value)
    
    def get_hourly_baseline(self, hour: int) -> Tuple[float, float]:
        """Get mean and std for specific hour."""
        if hour in self._hourly_stats:
            tracker = self._hourly_stats[hour]
            return tracker.mean, tracker.std
        return 0.0, 0.0
    
    def is_time_anomaly(self, timestamp: datetime, value: float) -> Tuple[bool, float]:
        """
        Check if value is anomalous for the given time.
        
        Returns:
            Tuple of (is_anomaly, deviation_score)
        """
        hour = timestamp.hour
        mean, std = self.get_hourly_baseline(hour)
        
        if std == 0 or self._hourly_stats[hour].count < 10:
            return False, 0.0
        
        z_score = (value - mean) / std
        is_anomaly = abs(z_score) > DEFAULT_THRESHOLDS["volume_std_multiplier"]

        return is_anomaly, abs(z_score)

    def _recent_values(self, window: Optional[int] = None) -> List[float]:
        """Get recent values for rolling analysis."""
        window = window or self.window_size
        if window <= 0:
            return []
        if len(self._values) < window:
            return []
        return [value for _, value in list(self._values)[-window:]]

    def volume_anomaly_score(
        self,
        value: float,
        window: Optional[int] = None,
        std_multiplier: Optional[float] = None,
        ratio_threshold: Optional[float] = None,
    ) -> Tuple[bool, float, Dict[str, float]]:
        """
        Analyze volume anomalies using rolling statistics.

        Returns:
            Tuple of (is_anomaly, deviation_score, details)
        """
        window = window or self.window_size
        std_multiplier = std_multiplier or DEFAULT_THRESHOLDS["volume_std_multiplier"]
        ratio_threshold = ratio_threshold or DEFAULT_THRESHOLDS["volume_time_series_ratio"]

        recent = self._recent_values(window)
        if len(recent) < window or not recent:
            return False, 0.0, {}

        mean = statistics.mean(recent)
        std = statistics.pstdev(recent) if len(recent) > 1 else 0.0
        details = {"window": window, "mean": mean, "std": std}

        if std == 0.0:
            if mean > 0 and ratio_threshold:
                ratio = value / mean
                details["ratio"] = ratio
                if ratio > ratio_threshold:
                    score = ratio - 1.0
                    details["z_score"] = score
                    return True, score, details
            return False, 0.0, details

        z_score = (value - mean) / std
        details["z_score"] = z_score
        is_anomaly = abs(z_score) > std_multiplier

        return is_anomaly, abs(z_score), details

    def detect_trend(self, window: int = 10) -> str:
        """Detect recent trend in values."""
        if len(self._values) < window:
            return "insufficient_data"
        
        recent = list(self._values)[-window:]
        values = [v[1] for v in recent]
        
        # Simple linear regression
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # Normalize slope by mean
        if y_mean > 0:
            normalized_slope = slope / y_mean
        else:
            normalized_slope = 0
        
        if normalized_slope > 0.1:
            return "increasing"
        elif normalized_slope < -0.1:
            return "decreasing"
        else:
            return "stable"


# ============================================================================
# Pattern Analysis Utilities
# ============================================================================

class TrafficPatternAnalyzer:
    """Statistical analysis of traffic patterns for anomaly scoring."""

    def __init__(self, thresholds: Dict[str, float]):
        self.thresholds = thresholds

    @staticmethod
    def _normalize_distribution(distribution: Dict[Any, float]) -> Dict[Any, float]:
        total = sum(distribution.values())
        if total <= 0:
            return {}
        return {k: v / total for k, v in distribution.items() if v > 0}

    @staticmethod
    def _entropy(distribution: Dict[Any, float]) -> float:
        if not distribution:
            return 0.0
        return -sum(p * math.log2(p) for p in distribution.values() if p > 0)

    def _normalized_entropy(self, distribution: Dict[Any, float]) -> float:
        if not distribution:
            return 0.0
        entropy = self._entropy(distribution)
        size = len(distribution)
        if size <= 1:
            return 0.0
        return entropy / math.log2(size)

    @staticmethod
    def _kl_divergence(p_dist: Dict[Any, float], q_dist: Dict[Any, float]) -> float:
        epsilon = 1e-12
        divergence = 0.0
        for key, p_val in p_dist.items():
            if p_val <= 0:
                continue
            q_val = q_dist.get(key, 0.0)
            divergence += p_val * math.log2((p_val + epsilon) / (q_val + epsilon))
        return divergence

    def _js_divergence(
        self,
        p_raw: Dict[Any, float],
        q_raw: Dict[Any, float],
    ) -> float:
        p_dist = self._normalize_distribution(p_raw)
        q_dist = self._normalize_distribution(q_raw)
        if not p_dist or not q_dist:
            return 0.0

        keys = set(p_dist) | set(q_dist)
        m_dist = {
            key: 0.5 * (p_dist.get(key, 0.0) + q_dist.get(key, 0.0))
            for key in keys
        }
        return 0.5 * self._kl_divergence(p_dist, m_dist) + 0.5 * self._kl_divergence(q_dist, m_dist)

    @staticmethod
    def _concentration(distribution: Dict[Any, float]) -> float:
        total = sum(distribution.values())
        if total <= 0:
            return 0.0
        return max(distribution.values()) / total

    def analyze(
        self,
        sample: "TrafficSample",
        baseline: "BaselineProfile",
    ) -> Tuple[float, List[HNDLIndicator], Dict[str, float]]:
        """Analyze pattern statistics and return anomaly score."""
        port_dist = self._normalize_distribution(sample.port_distribution)
        proto_dist = self._normalize_distribution(sample.protocol_distribution)
        dest_dist = self._normalize_distribution(sample.destination_distribution)

        stats = {
            "port_entropy": self._entropy(port_dist),
            "protocol_entropy": self._entropy(proto_dist),
            "destination_entropy": self._entropy(dest_dist),
            "port_entropy_norm": self._normalized_entropy(port_dist),
            "protocol_entropy_norm": self._normalized_entropy(proto_dist),
            "destination_entropy_norm": self._normalized_entropy(dest_dist),
            "port_js_divergence": self._js_divergence(port_dist, baseline.normal_ports),
            "protocol_js_divergence": self._js_divergence(proto_dist, baseline.protocol_baseline),
            "destination_concentration": self._concentration(sample.destination_distribution),
            "port_concentration": self._concentration(sample.port_distribution),
            "protocol_concentration": self._concentration(sample.protocol_distribution),
        }

        indicators: List[HNDLIndicator] = []
        score = 0.0

        if baseline.is_valid:
            js_threshold = self.thresholds["pattern_js_threshold"]
            entropy_min = self.thresholds["pattern_entropy_min"]

            if stats["port_js_divergence"] > js_threshold:
                indicators.append(HNDLIndicator.PATTERN_ANOMALY)
                score = max(score, min(1.0, stats["port_js_divergence"] / (js_threshold * 2)))

            if stats["protocol_js_divergence"] > js_threshold:
                indicators.append(HNDLIndicator.PATTERN_ANOMALY)
                score = max(score, min(1.0, stats["protocol_js_divergence"] / (js_threshold * 2)))

            if 0 < stats["destination_entropy_norm"] < entropy_min:
                indicators.append(HNDLIndicator.PATTERN_ANOMALY)
                score = max(
                    score,
                    min(1.0, (entropy_min - stats["destination_entropy_norm"]) / entropy_min),
                )

            if (
                baseline.mean_bytes_per_window > 0
                and sample.bytes_transferred > baseline.mean_bytes_per_window * 2
                and stats["destination_concentration"] > self.thresholds["concentration_threshold"]
            ):
                indicators.append(HNDLIndicator.DATA_STAGING)
                score = max(score, min(1.0, stats["destination_concentration"]))

        return score, indicators, stats


# ============================================================================
# ML Model Integration
# ============================================================================

class MLModelAdapter:
    """Adapter for integrating external ML classifiers."""

    def __init__(
        self,
        model: Any,
        labels: Optional[List[str]] = None,
        feature_order: Optional[List[str]] = None,
    ):
        self.model = model
        self.labels = labels or []
        self.feature_order = feature_order

    def _resolve_labels(self, count: int) -> List[str]:
        if self.labels and len(self.labels) == count:
            return list(self.labels)
        if hasattr(self.model, "classes_"):
            classes = [str(c) for c in self.model.classes_]
            if len(classes) == count:
                return classes
        return [f"class_{idx}" for idx in range(count)]

    def _feature_order(self, features: Dict[str, float]) -> List[str]:
        if self.feature_order:
            return list(self.feature_order)
        if hasattr(self.model, "feature_names_in_"):
            return [str(name) for name in self.model.feature_names_in_]
        if hasattr(self.model, "feature_names_"):
            return [str(name) for name in self.model.feature_names_]
        return sorted(features.keys())

    def _build_vector(self, features: Dict[str, float]) -> Tuple[List[float], List[str]]:
        order = self._feature_order(features)
        vector = [float(features.get(name, 0.0)) for name in order]
        return vector, order

    def _normalize_result(self, result: Any) -> Optional[MLClassification]:
        if isinstance(result, MLClassification):
            return result
        if isinstance(result, dict):
            probabilities = {str(k): float(v) for k, v in result.items()}
            if not probabilities:
                return None
            label = max(probabilities, key=probabilities.get)
            return MLClassification(
                label=label,
                confidence=probabilities[label],
                probabilities=probabilities,
            )
        if isinstance(result, (tuple, list)) and len(result) >= 2:
            label = str(result[0])
            confidence = float(result[1])
            return MLClassification(
                label=label,
                confidence=confidence,
                probabilities={label: confidence},
            )
        if isinstance(result, str):
            return MLClassification(
                label=result,
                confidence=1.0,
                probabilities={result: 1.0},
            )
        if isinstance(result, (int, float)):
            score = max(0.0, min(1.0, float(result)))
            probabilities = {"hndl": score, "benign": 1.0 - score}
            label = "hndl" if score >= 0.5 else "benign"
            return MLClassification(
                label=label,
                confidence=probabilities[label],
                probabilities=probabilities,
            )
        return None

    def classify(self, features: Dict[str, float]) -> Optional[MLClassification]:
        if self.model is None:
            return None
        try:
            if callable(self.model) and not hasattr(self.model, "predict"):
                return self._normalize_result(self.model(features))

            if hasattr(self.model, "predict_proba"):
                vector, order = self._build_vector(features)
                probabilities = self.model.predict_proba([vector])[0]
                labels = self._resolve_labels(len(probabilities))
                mapped = {
                    label: float(prob)
                    for label, prob in zip(labels, probabilities)
                }
                label = max(mapped, key=mapped.get)
                return MLClassification(
                    label=label,
                    confidence=mapped[label],
                    probabilities=mapped,
                    model_metadata={"feature_order": order},
                )

            if hasattr(self.model, "predict"):
                vector, order = self._build_vector(features)
                predicted = self.model.predict([vector])[0]
                label = str(predicted)
                return MLClassification(
                    label=label,
                    confidence=1.0,
                    probabilities={label: 1.0},
                    model_metadata={"feature_order": order},
                )
        except Exception as exc:
            logger.error(f"ML classification failed: {exc}")

        return None


# ============================================================================
# Baseline Profiler
# ============================================================================

class BaselineProfiler:
    """
    Builds and maintains baseline behavior profiles.
    
    Learns normal traffic patterns to detect deviations that may
    indicate HNDL attacks.
    """
    
    def __init__(
        self,
        profile_name: str = "default",
        window_seconds: int = 300,
    ):
        """
        Initialize baseline profiler.
        
        Args:
            profile_name: Name for this baseline profile
            window_seconds: Time window for aggregating samples
        """
        self.window_seconds = window_seconds
        
        # Current baseline profile
        self.profile = BaselineProfile(
            id=str(uuid.uuid4()),
            name=profile_name,
        )
        
        # Statistics trackers
        self._bytes_tracker = StatisticsTracker()
        self._packets_tracker = StatisticsTracker()
        self._connections_tracker = StatisticsTracker()
        self._destinations_tracker = StatisticsTracker()
        self._packet_size_tracker = StatisticsTracker()
        self._encrypted_ratio_tracker = StatisticsTracker()
        
        # Time series analyzer
        self._time_series = TimeSeriesAnalyzer()
        
        # Current window accumulator
        self._current_window_start: Optional[datetime] = None
        self._window_bytes = 0
        self._window_packets = 0
        self._window_connections: Set[str] = set()
        self._window_destinations: Set[str] = set()
        self._window_encrypted_bytes = 0
        self._window_packet_sizes: List[int] = []
        self._window_ports: Dict[int, int] = defaultdict(int)
        self._window_protocols: Dict[str, int] = defaultdict(int)
        
        # Learning mode
        self._learning = True
    
    def process_packet(self, packet: PacketInfo) -> None:
        """Process a packet for baseline learning."""
        now = packet.timestamp
        
        # Initialize window if needed
        if self._current_window_start is None:
            self._current_window_start = now
        
        # Check if window has elapsed
        window_elapsed = (now - self._current_window_start).total_seconds()
        if window_elapsed >= self.window_seconds:
            self._finalize_window()
            self._current_window_start = now
        
        # Accumulate window data
        self._window_bytes += packet.length
        self._window_packets += 1
        self._window_packet_sizes.append(packet.length)
        
        # Track connections
        if packet.src_port and packet.dst_port:
            conn_id = f"{packet.src_ip}:{packet.src_port}-{packet.dst_ip}:{packet.dst_port}"
            self._window_connections.add(conn_id)
        
        # Track destinations
        self._window_destinations.add(packet.dst_ip)
        
        # Track encrypted traffic (TLS ports)
        if packet.dst_port in (443, 8443, 993, 995, 465, 587):
            self._window_encrypted_bytes += packet.length
        
        # Track ports and protocols
        if packet.dst_port:
            self._window_ports[packet.dst_port] += 1
        self._window_protocols[packet.protocol.value] += 1
    
    def _finalize_window(self) -> None:
        """Finalize current window and update statistics."""
        if self._window_packets == 0:
            self._reset_window()
            return
        
        # Calculate window metrics
        encrypted_ratio = (
            self._window_encrypted_bytes / self._window_bytes
            if self._window_bytes > 0 else 0.0
        )
        avg_packet_size = (
            sum(self._window_packet_sizes) / len(self._window_packet_sizes)
            if self._window_packet_sizes else 0.0
        )
        
        # Create sample
        sample = TrafficSample(
            timestamp=self._current_window_start or datetime.now(),
            bytes_transferred=self._window_bytes,
            packet_count=self._window_packets,
            connection_count=len(self._window_connections),
            unique_destinations=len(self._window_destinations),
            encrypted_ratio=encrypted_ratio,
            avg_packet_size=avg_packet_size,
            port_distribution=dict(self._window_ports),
            protocol_distribution={
                k: v / self._window_packets 
                for k, v in self._window_protocols.items()
            },
        )
        
        # Update statistics trackers
        self._bytes_tracker.add(sample.bytes_transferred)
        self._packets_tracker.add(sample.packet_count)
        self._connections_tracker.add(sample.connection_count)
        self._destinations_tracker.add(sample.unique_destinations)
        self._packet_size_tracker.add(avg_packet_size)
        self._encrypted_ratio_tracker.add(encrypted_ratio)
        
        # Update time series
        self._time_series.add(sample.timestamp, sample.bytes_transferred)
        
        # Update profile
        self._update_profile(sample)
        
        # Reset window
        self._reset_window()
    
    def _update_profile(self, sample: TrafficSample) -> None:
        """Update baseline profile with new sample."""
        self.profile.sample_count += 1
        self.profile.updated_at = datetime.now()
        
        # Update statistics from trackers
        self.profile.mean_bytes_per_window = self._bytes_tracker.mean
        self.profile.std_bytes_per_window = self._bytes_tracker.std
        self.profile.mean_packets_per_window = self._packets_tracker.mean
        self.profile.std_packets_per_window = self._packets_tracker.std
        self.profile.mean_connections = self._connections_tracker.mean
        self.profile.std_connections = self._connections_tracker.std
        self.profile.mean_destinations = self._destinations_tracker.mean
        self.profile.std_destinations = self._destinations_tracker.std
        self.profile.mean_packet_size = self._packet_size_tracker.mean
        self.profile.std_packet_size = self._packet_size_tracker.std
        self.profile.mean_encrypted_ratio = self._encrypted_ratio_tracker.mean
        self.profile.std_encrypted_ratio = self._encrypted_ratio_tracker.std
        
        # Update known destinations
        for dst in sample.destination_distribution.keys():
            self.profile.known_destinations.add(dst)
        
        # Update port distribution (exponential moving average)
        alpha = 0.1  # Smoothing factor
        for port, count in sample.port_distribution.items():
            ratio = count / sample.packet_count if sample.packet_count > 0 else 0
            current = self.profile.normal_ports.get(port, 0.0)
            self.profile.normal_ports[port] = alpha * ratio + (1 - alpha) * current
        
        # Update hourly pattern
        hour = sample.timestamp.hour
        current_hourly = self.profile.hourly_pattern.get(hour, 0.0)
        self.profile.hourly_pattern[hour] = (
            alpha * sample.bytes_transferred + (1 - alpha) * current_hourly
        )
        
        # Update protocol baseline
        for proto, ratio in sample.protocol_distribution.items():
            current = self.profile.protocol_baseline.get(proto, 0.0)
            self.profile.protocol_baseline[proto] = alpha * ratio + (1 - alpha) * current
    
    def _reset_window(self) -> None:
        """Reset window accumulators."""
        self._window_bytes = 0
        self._window_packets = 0
        self._window_connections.clear()
        self._window_destinations.clear()
        self._window_encrypted_bytes = 0
        self._window_packet_sizes.clear()
        self._window_ports.clear()
        self._window_protocols.clear()
    
    def get_current_sample(self) -> Optional[TrafficSample]:
        """Get current window as a sample without finalizing."""
        if self._window_packets == 0:
            return None
        
        encrypted_ratio = (
            self._window_encrypted_bytes / self._window_bytes
            if self._window_bytes > 0 else 0.0
        )
        avg_packet_size = (
            sum(self._window_packet_sizes) / len(self._window_packet_sizes)
            if self._window_packet_sizes else 0.0
        )
        
        return TrafficSample(
            timestamp=self._current_window_start or datetime.now(),
            bytes_transferred=self._window_bytes,
            packet_count=self._window_packets,
            connection_count=len(self._window_connections),
            unique_destinations=len(self._window_destinations),
            encrypted_ratio=encrypted_ratio,
            avg_packet_size=avg_packet_size,
            port_distribution=dict(self._window_ports),
            destination_distribution={
                dst: 1 for dst in self._window_destinations
            },
        )
    
    def is_baseline_valid(self) -> bool:
        """Check if baseline has enough data."""
        return self.profile.is_valid
    
    def get_profile(self) -> BaselineProfile:
        """Get current baseline profile."""
        return self.profile
    
    def export_profile(self) -> Dict[str, Any]:
        """Export profile as dictionary."""
        return self.profile.to_dict()


# ============================================================================
# Anomaly Detector
# ============================================================================

class AnomalyDetector:
    """
    Detects anomalies in network traffic patterns.
    
    Uses statistical analysis to identify deviations from baseline
    that may indicate HNDL attack activity.
    """
    
    def __init__(
        self,
        baseline: BaselineProfile,
        thresholds: Optional[Dict[str, float]] = None,
        ml_model: Optional[Any] = None,
        ml_labels: Optional[List[str]] = None,
        ml_feature_order: Optional[List[str]] = None,
        ml_weight: float = 0.0,
    ):
        """
        Initialize anomaly detector.
        
        Args:
            baseline: Baseline profile to compare against
            thresholds: Custom detection thresholds
        """
        self.baseline = baseline
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

        # Time series analyzer for real-time detection
        self._time_series = TimeSeriesAnalyzer()

        # Pattern analyzer for statistical traffic patterns
        self._pattern_analyzer = TrafficPatternAnalyzer(self.thresholds)

        # Optional ML classifier
        self._ml_classifier = (
            MLModelAdapter(
                ml_model,
                labels=ml_labels,
                feature_order=ml_feature_order,
            )
            if ml_model is not None
            else None
        )
        self._ml_weight = ml_weight

        # Recent anomalies for correlation
        self._recent_anomalies: Deque[AnomalyScore] = deque(maxlen=100)

    def set_ml_model(
        self,
        model: Optional[Any],
        labels: Optional[List[str]] = None,
        feature_order: Optional[List[str]] = None,
        weight: Optional[float] = None,
    ) -> None:
        """Update ML classifier configuration."""
        if model is None:
            self._ml_classifier = None
        else:
            self._ml_classifier = MLModelAdapter(
                model,
                labels=labels,
                feature_order=feature_order,
            )
        if weight is not None:
            self._ml_weight = weight

    def analyze(self, sample: TrafficSample) -> AnomalyScore:
        """
        Analyze a traffic sample for anomalies.
        
        Args:
            sample: Traffic sample to analyze
        
        Returns:
            AnomalyScore with detection results
        """
        indicators: List[HNDLIndicator] = []
        details: Dict[str, Any] = {}
        component_scores: List[float] = []

        volume_details: Dict[str, Any] = {}
        pattern_stats: Dict[str, float] = {}

        # 1. Volume anomaly detection
        volume_score, volume_indicators, volume_details = self._check_volume_anomaly(sample)
        indicators.extend(volume_indicators)
        component_scores.append(volume_score)
        details["volume_score"] = volume_score
        if volume_details:
            details["volume_details"] = volume_details

        # 2. Destination anomaly detection
        dest_score, dest_indicators = self._check_destination_anomaly(sample)
        indicators.extend(dest_indicators)
        component_scores.append(dest_score)
        details["destination_score"] = dest_score

        # 3. Time-based anomaly detection
        time_score, time_indicators = self._check_time_anomaly(sample)
        indicators.extend(time_indicators)
        component_scores.append(time_score)
        details["time_score"] = time_score

        # 4. Protocol anomaly detection
        proto_score, proto_indicators = self._check_protocol_anomaly(sample)
        indicators.extend(proto_indicators)
        component_scores.append(proto_score)
        details["protocol_score"] = proto_score

        # 5. Encryption ratio anomaly
        enc_score, enc_indicators = self._check_encryption_anomaly(sample)
        indicators.extend(enc_indicators)
        component_scores.append(enc_score)
        details["encryption_score"] = enc_score

        # 6. Packet size anomaly
        size_score, size_indicators = self._check_size_anomaly(sample)
        indicators.extend(size_indicators)
        component_scores.append(size_score)
        details["size_score"] = size_score

        # 7. Statistical pattern analysis
        pattern_score, pattern_indicators, pattern_stats = self._check_pattern_anomaly(sample)
        indicators.extend(pattern_indicators)
        details["pattern_score"] = pattern_score
        if pattern_stats:
            details["pattern_stats"] = pattern_stats

        # Calculate total score (weighted average)
        weights = [0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
        base_score = sum(s * w for s, w in zip(component_scores, weights))
        total_score = min(1.0, max(0.0, base_score))

        if pattern_score > 0:
            total_score = min(
                1.0,
                total_score + pattern_score * self.thresholds["pattern_weight"],
            )

        # Optional ML classification
        if self._ml_classifier:
            features = self._build_ml_features(
                sample,
                details,
                pattern_stats,
                volume_details,
            )
            classification = self._ml_classifier.classify(features)
            if classification:
                details["ml_classification"] = classification.to_dict()
                ml_score = self._ml_score_from_classification(classification)
                details["ml_score"] = ml_score
                if self._ml_weight > 0:
                    total_score = min(1.0, total_score + ml_score * self._ml_weight)

        # Determine risk level
        risk_level = AnomalyScore.calculate_risk_level(total_score)

        # Create anomaly score
        anomaly = AnomalyScore(
            total_score=total_score,
            risk_level=risk_level,
            indicators=list(set(indicators)),  # Remove duplicates
            details=details,
            timestamp=sample.timestamp,
        )

        # Track for correlation
        self._recent_anomalies.append(anomaly)
        self._time_series.add(sample.timestamp, sample.bytes_transferred)

        return anomaly
    
    def _check_volume_anomaly(
        self,
        sample: TrafficSample,
    ) -> Tuple[float, List[HNDLIndicator], Dict[str, Any]]:
        """Check for volume-based anomalies."""
        indicators = []
        score = 0.0
        details: Dict[str, Any] = {}

        if self.baseline.is_valid:
            # Calculate z-score for bytes
            if self.baseline.std_bytes_per_window > 0:
                z_bytes = (
                    (sample.bytes_transferred - self.baseline.mean_bytes_per_window) /
                    self.baseline.std_bytes_per_window
                )
                details["bytes_z_score"] = z_bytes

                if z_bytes > self.thresholds["volume_std_multiplier"]:
                    indicators.append(HNDLIndicator.HIGH_VOLUME_TRANSFER)
                    score = min(1.0, z_bytes / 10)  # Normalize to 0-1

            # Check packets
            if self.baseline.std_packets_per_window > 0:
                z_packets = (
                    (sample.packet_count - self.baseline.mean_packets_per_window) /
                    self.baseline.std_packets_per_window
                )
                details["packets_z_score"] = z_packets

                if z_packets > self.thresholds["volume_std_multiplier"]:
                    indicators.append(HNDLIndicator.FREQUENCY_ANOMALY)
                    score = max(score, min(1.0, z_packets / 10))

        # Time-series volume anomaly detection
        ts_is_anomaly, ts_score, ts_details = self._time_series.volume_anomaly_score(
            sample.bytes_transferred,
            window=self.thresholds["volume_time_series_window"],
            std_multiplier=self.thresholds["volume_time_series_std_multiplier"],
            ratio_threshold=self.thresholds["volume_time_series_ratio"],
        )
        if ts_details:
            details["time_series"] = ts_details
        if ts_is_anomaly:
            indicators.append(HNDLIndicator.HIGH_VOLUME_TRANSFER)
            score = max(score, min(1.0, ts_score / 10))

        return score, indicators, details
    
    def _check_destination_anomaly(
        self,
        sample: TrafficSample,
    ) -> Tuple[float, List[HNDLIndicator]]:
        """Check for destination-based anomalies."""
        indicators = []
        score = 0.0
        
        if not self.baseline.is_valid:
            return 0.0, []
        
        # Check for unusual destinations
        unknown_dests = set(sample.destination_distribution.keys()) - self.baseline.known_destinations
        if unknown_dests:
            unknown_ratio = len(unknown_dests) / max(1, sample.unique_destinations)
            if unknown_ratio > 0.5:  # More than 50% unknown
                indicators.append(HNDLIndicator.UNUSUAL_DESTINATION)
                score = unknown_ratio
        
        # Check for destination concentration
        if sample.destination_distribution:
            total_to_dests = sum(sample.destination_distribution.values())
            max_to_single = max(sample.destination_distribution.values())
            concentration = max_to_single / total_to_dests if total_to_dests > 0 else 0
            
            if concentration > self.thresholds["concentration_threshold"]:
                indicators.append(HNDLIndicator.DESTINATION_CONCENTRATION)
                score = max(score, concentration)
        
        # Check for sudden increase in destinations
        if self.baseline.std_destinations > 0:
            z_dests = (
                (sample.unique_destinations - self.baseline.mean_destinations) /
                self.baseline.std_destinations
            )
            if z_dests > self.thresholds["volume_std_multiplier"]:
                indicators.append(HNDLIndicator.PATTERN_ANOMALY)
                score = max(score, min(1.0, z_dests / 10))
        
        return score, indicators
    
    def _check_time_anomaly(
        self,
        sample: TrafficSample,
    ) -> Tuple[float, List[HNDLIndicator]]:
        """Check for time-based anomalies."""
        indicators = []
        score = 0.0
        
        hour = sample.timestamp.hour
        expected = self.baseline.hourly_pattern.get(hour, 0)
        
        if expected > 0:
            deviation = sample.bytes_transferred / expected
            
            # Check if significantly higher than expected for this hour
            if deviation > self.thresholds["frequency_multiplier"]:
                indicators.append(HNDLIndicator.TIME_ANOMALY)
                score = min(1.0, (deviation - 1) / 10)
        
        # Use time series analyzer
        is_anomaly, deviation_score = self._time_series.is_time_anomaly(
            sample.timestamp,
            sample.bytes_transferred,
        )
        if is_anomaly:
            indicators.append(HNDLIndicator.TIME_ANOMALY)
            score = max(score, min(1.0, deviation_score / 10))
        
        return score, indicators
    
    def _check_protocol_anomaly(
        self,
        sample: TrafficSample,
    ) -> Tuple[float, List[HNDLIndicator]]:
        """Check for protocol distribution anomalies."""
        indicators = []
        score = 0.0
        
        if not self.baseline.protocol_baseline:
            return 0.0, []
        
        # Compare protocol distribution
        for proto, ratio in sample.protocol_distribution.items():
            baseline_ratio = self.baseline.protocol_baseline.get(proto, 0)
            
            if baseline_ratio > 0:
                deviation = abs(ratio - baseline_ratio) / baseline_ratio
                if deviation > 1.0:  # More than 100% deviation
                    indicators.append(HNDLIndicator.PROTOCOL_ANOMALY)
                    score = max(score, min(1.0, deviation / 5))
        
        return score, indicators
    
    def _check_encryption_anomaly(
        self,
        sample: TrafficSample,
    ) -> Tuple[float, List[HNDLIndicator]]:
        """Check for encryption ratio anomalies."""
        indicators = []
        score = 0.0
        
        if not self.baseline.is_valid:
            return 0.0, []
        
        if self.baseline.std_encrypted_ratio > 0:
            z_enc = (
                (sample.encrypted_ratio - self.baseline.mean_encrypted_ratio) /
                self.baseline.std_encrypted_ratio
            )
            
            # High encrypted ratio might indicate bulk encrypted data capture
            if z_enc > self.thresholds["volume_std_multiplier"]:
                indicators.append(HNDLIndicator.BULK_ENCRYPTION)
                score = min(1.0, z_enc / 10)
        
        return score, indicators
    
    def _check_size_anomaly(
        self,
        sample: TrafficSample,
    ) -> Tuple[float, List[HNDLIndicator]]:
        """Check for packet size anomalies."""
        indicators = []
        score = 0.0
        
        if not self.baseline.is_valid:
            return 0.0, []
        
        if self.baseline.std_packet_size > 0:
            z_size = (
                (sample.avg_packet_size - self.baseline.mean_packet_size) /
                self.baseline.std_packet_size
            )
            
            if abs(z_size) > self.thresholds["volume_std_multiplier"]:
                indicators.append(HNDLIndicator.SIZE_ANOMALY)
                score = min(1.0, abs(z_size) / 10)
        
        return score, indicators

    def _check_pattern_anomaly(
        self,
        sample: TrafficSample,
    ) -> Tuple[float, List[HNDLIndicator], Dict[str, float]]:
        """Check for statistical pattern anomalies."""
        return self._pattern_analyzer.analyze(sample, self.baseline)

    def _build_ml_features(
        self,
        sample: TrafficSample,
        details: Dict[str, Any],
        pattern_stats: Dict[str, float],
        volume_details: Dict[str, Any],
    ) -> Dict[str, float]:
        """Build ML feature vector from current analysis."""
        trend = self.get_trend()
        trend_score = {
            "increasing": 1.0,
            "decreasing": -1.0,
            "stable": 0.0,
        }.get(trend, 0.0)

        time_series = volume_details.get("time_series", {}) if volume_details else {}

        return {
            "bytes_transferred": float(sample.bytes_transferred),
            "packet_count": float(sample.packet_count),
            "connection_count": float(sample.connection_count),
            "unique_destinations": float(sample.unique_destinations),
            "encrypted_ratio": float(sample.encrypted_ratio),
            "avg_packet_size": float(sample.avg_packet_size),
            "bytes_z_score": float(volume_details.get("bytes_z_score", 0.0)),
            "packets_z_score": float(volume_details.get("packets_z_score", 0.0)),
            "volume_ts_z_score": float(time_series.get("z_score", 0.0)),
            "volume_score": float(details.get("volume_score", 0.0)),
            "destination_score": float(details.get("destination_score", 0.0)),
            "time_score": float(details.get("time_score", 0.0)),
            "protocol_score": float(details.get("protocol_score", 0.0)),
            "encryption_score": float(details.get("encryption_score", 0.0)),
            "size_score": float(details.get("size_score", 0.0)),
            "pattern_score": float(details.get("pattern_score", 0.0)),
            "trend": trend_score,
            "port_entropy_norm": float(pattern_stats.get("port_entropy_norm", 0.0)),
            "protocol_entropy_norm": float(pattern_stats.get("protocol_entropy_norm", 0.0)),
            "destination_entropy_norm": float(pattern_stats.get("destination_entropy_norm", 0.0)),
            "port_js_divergence": float(pattern_stats.get("port_js_divergence", 0.0)),
            "protocol_js_divergence": float(pattern_stats.get("protocol_js_divergence", 0.0)),
            "destination_concentration": float(pattern_stats.get("destination_concentration", 0.0)),
            "baseline_bytes_mean": float(self.baseline.mean_bytes_per_window),
            "baseline_bytes_std": float(self.baseline.std_bytes_per_window),
            "baseline_encrypted_ratio": float(self.baseline.mean_encrypted_ratio),
            "baseline_valid": 1.0 if self.baseline.is_valid else 0.0,
        }

    @staticmethod
    def _ml_score_from_classification(classification: MLClassification) -> float:
        """Convert ML classification into a normalized risk score."""
        label = classification.label.lower()
        if label in ("benign", "normal"):
            return 0.0

        if classification.probabilities:
            for key in ("hndl", "malicious", "attack"):
                if key in classification.probabilities:
                    return classification.probabilities[key]
            if "suspicious" in classification.probabilities:
                return classification.probabilities["suspicious"] * 0.7

        if label in ("suspicious", "anomalous"):
            return classification.confidence * 0.7

        return classification.confidence
    
    def get_trend(self) -> str:
        """Get current traffic trend."""
        return self._time_series.detect_trend()
    
    def get_recent_anomalies(
        self,
        min_score: float = 0.5,
    ) -> List[AnomalyScore]:
        """Get recent anomalies above threshold."""
        return [a for a in self._recent_anomalies if a.total_score >= min_score]


# ============================================================================
# HNDL Detector
# ============================================================================

class HNDLDetector:
    """
    Main HNDL attack detector.
    
    Combines baseline profiling and anomaly detection to identify
    potential "Harvest Now, Decrypt Later" attack patterns.
    
    Example:
        detector = HNDLDetector()
        
        # Learning phase
        for packet in training_packets:
            detector.learn(packet)
        
        # Detection phase
        detector.start_detection()
        for packet in live_packets:
            alert = detector.analyze(packet)
            if alert:
                print(f"HNDL Alert: {alert.description}")
    """
    
    def __init__(
        self,
        profile_name: str = "default",
        window_seconds: int = 300,
        auto_learn: bool = True,
        ml_model: Optional[Any] = None,
        ml_labels: Optional[List[str]] = None,
        ml_feature_order: Optional[List[str]] = None,
        ml_weight: float = 0.0,
    ):
        """
        Initialize HNDL detector.
        
        Args:
            profile_name: Name for baseline profile
            window_seconds: Time window for analysis
            auto_learn: Continue learning during detection
            ml_model: Optional ML model or callable for classification
            ml_labels: Optional labels for ML model outputs
            ml_feature_order: Optional feature order for ML models
            ml_weight: Weight to apply to ML classification score
        """
        self.window_seconds = window_seconds
        self.auto_learn = auto_learn

        # ML model configuration
        self._ml_model = ml_model
        self._ml_labels = ml_labels
        self._ml_feature_order = ml_feature_order
        self._ml_weight = ml_weight
        
        # Baseline profiler
        self._profiler = BaselineProfiler(
            profile_name=profile_name,
            window_seconds=window_seconds,
        )
        
        # Anomaly detector (initialized after baseline is ready)
        self._detector: Optional[AnomalyDetector] = None
        
        # Alert tracking
        self._alerts: List[HNDLAlert] = []
        self._alert_callbacks: List[Callable[[HNDLAlert], None]] = []
        
        # State
        self._mode = "learning"  # "learning" or "detection"
        self._running = False
        
        # Statistics
        self._stats = {
            "packets_processed": 0,
            "windows_analyzed": 0,
            "alerts_generated": 0,
            "learning_samples": 0,
        }
    
    def learn(self, packet: PacketInfo) -> None:
        """
        Process packet for baseline learning.
        
        Args:
            packet: Packet to learn from
        """
        self._profiler.process_packet(packet)
        self._stats["packets_processed"] += 1
        self._stats["learning_samples"] = self._profiler.profile.sample_count
    
    def start_detection(self) -> bool:
        """
        Start detection mode.
        
        Returns:
            True if detection started, False if baseline not ready
        """
        if not self._profiler.is_baseline_valid():
            logger.warning(
                f"Baseline not ready. Need {DEFAULT_THRESHOLDS['min_baseline_samples']} "
                f"samples, have {self._profiler.profile.sample_count}"
            )
            return False
        
        self._detector = AnomalyDetector(
            baseline=self._profiler.profile,
            ml_model=self._ml_model,
            ml_labels=self._ml_labels,
            ml_feature_order=self._ml_feature_order,
            ml_weight=self._ml_weight,
        )
        self._mode = "detection"
        self._running = True
        
        logger.info("HNDL detection started")
        return True

    def set_ml_model(
        self,
        model: Optional[Any],
        labels: Optional[List[str]] = None,
        feature_order: Optional[List[str]] = None,
        weight: Optional[float] = None,
    ) -> None:
        """Update ML model integration."""
        self._ml_model = model
        if labels is not None:
            self._ml_labels = labels
        if feature_order is not None:
            self._ml_feature_order = feature_order
        if weight is not None:
            self._ml_weight = weight

        if self._detector is not None:
            self._detector.set_ml_model(
                model,
                labels=self._ml_labels,
                feature_order=self._ml_feature_order,
                weight=self._ml_weight,
            )

    def stop_detection(self) -> None:
        """Stop detection mode."""
        self._running = False
        self._mode = "learning"
        logger.info("HNDL detection stopped")
    
    def analyze(self, packet: PacketInfo) -> Optional[HNDLAlert]:
        """
        Analyze packet for HNDL indicators.
        
        Args:
            packet: Packet to analyze
        
        Returns:
            HNDLAlert if anomaly detected, None otherwise
        """
        # Always update profiler if auto-learning
        if self.auto_learn or self._mode == "learning":
            self._profiler.process_packet(packet)
        
        self._stats["packets_processed"] += 1
        
        # Skip detection if not in detection mode
        if self._mode != "detection" or self._detector is None:
            return None
        
        # Get current sample
        sample = self._profiler.get_current_sample()
        if sample is None:
            return None
        
        # Analyze for anomalies
        anomaly = self._detector.analyze(sample)
        self._stats["windows_analyzed"] += 1
        
        # Generate alert if risk is high enough
        if anomaly.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            alert = self._generate_alert(sample, anomaly)
            self._alerts.append(alert)
            self._stats["alerts_generated"] += 1
            
            # Notify callbacks
            for callback in self._alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")
            
            return alert
        
        return None
    
    def _generate_alert(
        self,
        sample: TrafficSample,
        anomaly: AnomalyScore,
    ) -> HNDLAlert:
        """Generate HNDL alert from anomaly."""
        # Build description
        indicator_names = [i.value.replace("_", " ").title() for i in anomaly.indicators]
        description = (
            f"Potential HNDL attack detected. "
            f"Risk level: {anomaly.risk_level.value.upper()}. "
            f"Indicators: {', '.join(indicator_names)}. "
            f"Anomaly score: {anomaly.total_score:.2f}"
        )
        
        # Build recommendations
        recommendations = [
            "Review traffic to identified destinations",
            "Check for unauthorized data access",
            "Verify TLS/encryption configurations",
            "Consider implementing post-quantum cryptography",
        ]
        
        if HNDLIndicator.HIGH_VOLUME_TRANSFER in anomaly.indicators:
            recommendations.append(
                "Investigate high-volume data transfers"
            )
        
        if HNDLIndicator.UNUSUAL_DESTINATION in anomaly.indicators:
            recommendations.append(
                "Verify legitimacy of new destination IPs"
            )
        
        if HNDLIndicator.BULK_ENCRYPTION in anomaly.indicators:
            recommendations.append(
                "Check for bulk encrypted data exfiltration"
            )
        
        # Get affected destinations
        affected = list(sample.destination_distribution.keys())[:10]
        
        metadata = {
            "sample": sample.to_dict(),
            "trend": self._detector.get_trend() if self._detector else "unknown",
        }
        if "ml_classification" in anomaly.details:
            metadata["ml_classification"] = anomaly.details["ml_classification"]

        return HNDLAlert(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            risk_level=anomaly.risk_level,
            anomaly_score=anomaly,
            indicators=anomaly.indicators,
            description=description,
            affected_destinations=affected,
            bytes_transferred=sample.bytes_transferred,
            duration_seconds=self.window_seconds,
            recommendations=recommendations,
            metadata=metadata,
        )
    
    def on_alert(self, callback: Callable[[HNDLAlert], None]) -> None:
        """Register alert callback."""
        self._alert_callbacks.append(callback)
    
    def get_baseline(self) -> BaselineProfile:
        """Get current baseline profile."""
        return self._profiler.profile
    
    def get_alerts(
        self,
        limit: int = 100,
        min_risk: Optional[RiskLevel] = None,
    ) -> List[HNDLAlert]:
        """Get generated alerts."""
        alerts = self._alerts
        
        if min_risk:
            risk_order = {
                RiskLevel.NONE: 0,
                RiskLevel.LOW: 1,
                RiskLevel.MEDIUM: 2,
                RiskLevel.HIGH: 3,
                RiskLevel.CRITICAL: 4,
            }
            min_order = risk_order.get(min_risk, 0)
            alerts = [a for a in alerts if risk_order.get(a.risk_level, 0) >= min_order]
        
        return alerts[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            **self._stats,
            "mode": self._mode,
            "baseline_valid": self._profiler.is_baseline_valid(),
            "baseline_samples": self._profiler.profile.sample_count,
        }
    
    def get_current_risk(self) -> RiskLevel:
        """Get current risk assessment."""
        if self._detector is None:
            return RiskLevel.NONE
        
        recent = self._detector.get_recent_anomalies(min_score=0.5)
        if not recent:
            return RiskLevel.NONE
        
        # Return highest recent risk
        return max(a.risk_level for a in recent)
    
    @property
    def is_baseline_ready(self) -> bool:
        """Check if baseline is ready for detection."""
        return self._profiler.is_baseline_valid()
    
    @property
    def mode(self) -> str:
        """Get current mode (learning/detection)."""
        return self._mode


# ============================================================================
# Convenience Functions
# ============================================================================

def create_detector(
    profile_name: str = "default",
    window_seconds: int = 300,
) -> HNDLDetector:
    """Create an HNDL detector instance."""
    return HNDLDetector(
        profile_name=profile_name,
        window_seconds=window_seconds,
    )


def quick_analyze(
    packets: List[PacketInfo],
    learning_ratio: float = 0.7,
) -> List[HNDLAlert]:
    """
    Quick analysis of packet list for HNDL indicators.
    
    Args:
        packets: List of packets to analyze
        learning_ratio: Ratio of packets for learning (0.0-1.0)
    
    Returns:
        List of generated alerts
    """
    detector = HNDLDetector(auto_learn=False)
    
    # Split packets for learning and detection
    split_idx = int(len(packets) * learning_ratio)
    learning_packets = packets[:split_idx]
    detection_packets = packets[split_idx:]
    
    # Learning phase
    for packet in learning_packets:
        detector.learn(packet)
    
    # Force baseline validity for small datasets
    if not detector.is_baseline_ready:
        logger.warning("Insufficient data for proper baseline")
        return []
    
    # Detection phase
    detector.start_detection()
    alerts = []
    
    for packet in detection_packets:
        alert = detector.analyze(packet)
        if alert:
            alerts.append(alert)
    
    return alerts
