"""Performance metrics collection utilities."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class TimingContext:
    """Context manager for timing operations."""
    name: str
    start_time: float = field(default_factory=time.perf_counter)
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        MetricsCollector.instance().record_timing(self.name, duration)


class MetricsCollector:
    """Collects and manages performance metrics."""
    
    _instance: Optional['MetricsCollector'] = None
    
    def __init__(self):
        self.metrics: list[PerformanceMetric] = []
        self.counters: dict[str, int] = defaultdict(int)
        self.timings: dict[str, list[float]] = defaultdict(list)
        self.gauges: dict[str, float] = {}
        
    @classmethod
    def instance(cls) -> 'MetricsCollector':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def record_timing(self, name: str, duration: float, tags: dict[str, str] | None = None) -> None:
        """Record a timing metric."""
        self.timings[name].append(duration)
        self.metrics.append(PerformanceMetric(
            name=f"{name}_duration",
            value=duration,
            unit="seconds",
            tags=tags or {},
        ))
        
        logger.debug("Recorded timing", name=name, duration=duration)
    
    def increment_counter(self, name: str, value: int = 1, tags: dict[str, str] | None = None) -> None:
        """Increment a counter metric."""
        self.counters[name] += value
        self.metrics.append(PerformanceMetric(
            name=f"{name}_count",
            value=self.counters[name],
            unit="count",
            tags=tags or {},
        ))
        
        logger.debug("Incremented counter", name=name, value=value, total=self.counters[name])
    
    def set_gauge(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Set a gauge metric."""
        self.gauges[name] = value
        self.metrics.append(PerformanceMetric(
            name=f"{name}_gauge",
            value=value,
            unit="value",
            tags=tags or {},
        ))
        
        logger.debug("Set gauge", name=name, value=value)
    
    def timing_context(self, name: str) -> TimingContext:
        """Create a timing context manager."""
        return TimingContext(name)
    
    def get_timing_stats(self, name: str) -> dict[str, float]:
        """Get statistics for a timing metric."""
        if name not in self.timings or not self.timings[name]:
            return {}
        
        values = self.timings[name]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "total": sum(values),
        }
    
    def get_all_stats(self) -> dict[str, Any]:
        """Get all collected statistics."""
        stats = {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timings": {},
        }
        
        for name in self.timings:
            stats["timings"][name] = self.get_timing_stats(name)
        
        return stats
    
    def get_session_metrics(self, session_id: str) -> dict[str, Any]:
        """Get metrics filtered by session ID."""
        session_metrics = []
        
        for metric in self.metrics:
            if metric.tags.get("session_id") == session_id:
                session_metrics.append({
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                })
        
        return {
            "session_id": session_id,
            "metrics": session_metrics,
            "count": len(session_metrics),
        }
    
    def clear_old_metrics(self, max_age_hours: int = 24) -> int:
        """Clear metrics older than specified age."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        original_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff]
        cleared_count = original_count - len(self.metrics)
        
        logger.info("Cleared old metrics", cleared=cleared_count, remaining=len(self.metrics))
        return cleared_count
    
    def export_metrics(self, format: str = "json") -> dict[str, Any] | str:
        """Export metrics in specified format."""
        stats = self.get_all_stats()
        
        if format == "json":
            return {
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "recent_metrics": [
                    {
                        "name": m.name,
                        "value": m.value,
                        "unit": m.unit,
                        "timestamp": m.timestamp.isoformat(),
                        "tags": m.tags,
                    }
                    for m in self.metrics[-100:]  # Last 100 metrics
                ],
            }
        
        elif format == "prometheus":
            # Simple Prometheus format export
            lines = []
            
            for name, value in self.counters.items():
                lines.append(f"# TYPE {name}_total counter")
                lines.append(f"{name}_total {value}")
            
            for name, value in self.gauges.items():
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {value}")
            
            for name, timings in self.timings.items():
                if timings:
                    lines.append(f"# TYPE {name}_duration_seconds histogram")
                    lines.append(f"{name}_duration_seconds_sum {sum(timings)}")
                    lines.append(f"{name}_duration_seconds_count {len(timings)}")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.timings.clear()
        self.gauges.clear()
        
        logger.info("Reset all metrics")


# Convenience functions for common operations
def time_operation(name: str, tags: dict[str, str] | None = None):
    """Decorator for timing function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with MetricsCollector.instance().timing_context(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def record_session_metric(session_id: str, name: str, value: float, unit: str = "value"):
    """Record a metric associated with a session."""
    MetricsCollector.instance().metrics.append(PerformanceMetric(
        name=name,
        value=value,
        unit=unit,
        tags={"session_id": session_id},
    ))


def get_system_metrics() -> dict[str, float]:
    """Get basic system metrics."""
    import psutil
    
    try:
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "load_average": psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0.0,
        }
    except ImportError:
        logger.warning("psutil not available, system metrics disabled")
        return {}
    except Exception as e:
        logger.error("Failed to get system metrics", error=str(e))
        return {}