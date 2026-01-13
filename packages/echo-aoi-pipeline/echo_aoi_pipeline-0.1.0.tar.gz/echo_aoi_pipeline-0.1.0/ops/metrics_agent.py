#!/usr/bin/env python3
"""
Metrics Collection Agent - Latency/Error/Cost Tracking
Collects and aggregates system metrics for observability and performance monitoring
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

@dataclass
class MetricData:
    """Single metric data point"""
    timestamp: str
    service: str
    metric_type: str  # latency_ms, error_count, cost_usd
    value: float
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MetricData':
        """Create from stored dictionary"""
        return cls(**data)

@dataclass
class MetricStats:
    """Aggregated metric statistics"""
    service: str
    metric_type: str
    count: int
    total: float
    avg: float
    min: float
    max: float
    p50: float
    p95: float
    p99: float
    window_start: str
    window_end: str

class MetricsStore:
    """Storage backend for metrics data"""
    
    def __init__(self, storage_path: str = "data/metrics"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_metrics_file(self, date: str) -> Path:
        """Get metrics file path for specific date"""
        return self.storage_path / f"metrics_{date}.jsonl"
    
    def append(self, metric: MetricData):
        """Append metric to storage"""
        date = metric.timestamp[:10]  # YYYY-MM-DD
        metrics_file = self._get_metrics_file(date)
        
        try:
            with open(metrics_file, 'a') as f:
                json.dump(metric.to_dict(), f)
                f.write('\n')
        except Exception as e:
            print(f"Warning: Failed to store metric: {e}")
    
    def query(
        self,
        service: Optional[str] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricData]:
        """Query metrics with filters"""
        metrics = []
        
        # Determine date range for files to scan
        if start_time:
            start_date = start_time.date()
        else:
            start_date = (datetime.now() - timedelta(days=7)).date()
        
        if end_time:
            end_date = end_time.date()
        else:
            end_date = datetime.now().date()
        
        # Scan all relevant metric files
        current_date = start_date
        while current_date <= end_date:
            metrics_file = self._get_metrics_file(current_date.isoformat())
            
            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                metric = MetricData.from_dict(data)
                                
                                # Apply filters
                                if service and metric.service != service:
                                    continue
                                if metric_type and metric.metric_type != metric_type:
                                    continue
                                
                                metric_time = datetime.fromisoformat(metric.timestamp)
                                if start_time and metric_time < start_time:
                                    continue
                                if end_time and metric_time > end_time:
                                    continue
                                
                                metrics.append(metric)
                except Exception as e:
                    print(f"Warning: Failed to read {metrics_file}: {e}")
            
            current_date += timedelta(days=1)
        
        return metrics
    
    def cleanup_old(self, retention_days: int = 30):
        """Remove metrics older than retention period"""
        cutoff_date = datetime.now().date() - timedelta(days=retention_days)
        count = 0
        
        for metrics_file in self.storage_path.glob("metrics_*.jsonl"):
            try:
                date_str = metrics_file.stem.replace("metrics_", "")
                file_date = datetime.fromisoformat(date_str).date()
                
                if file_date < cutoff_date:
                    metrics_file.unlink()
                    count += 1
            except Exception as e:
                print(f"Warning: Failed to cleanup {metrics_file}: {e}")
        
        return count

class MetricsCollector:
    """Metrics collection and aggregation manager"""
    
    def __init__(self, store: Optional[MetricsStore] = None):
        self.store = store or MetricsStore()
    
    def collect(
        self,
        service: str,
        metric_type: str,
        value: float,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Collect a single metric"""
        metric = MetricData(
            timestamp=datetime.now().isoformat(),
            service=service,
            metric_type=metric_type,
            value=value,
            trace_id=trace_id,
            request_id=request_id,
            metadata=metadata or {}
        )
        
        self.store.append(metric)
    
    def get_stats(
        self,
        service: Optional[str] = None,
        metric_type: Optional[str] = None,
        window_hours: int = 24
    ) -> List[MetricStats]:
        """Get aggregated statistics for metrics"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=window_hours)
        
        metrics = self.store.query(
            service=service,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time
        )
        
        # Group metrics by service and type
        grouped = defaultdict(list)
        for metric in metrics:
            key = (metric.service, metric.metric_type)
            grouped[key].append(metric.value)
        
        # Calculate statistics for each group
        stats_list = []
        for (svc, mtype), values in grouped.items():
            if not values:
                continue
            
            sorted_values = sorted(values)
            stats = MetricStats(
                service=svc,
                metric_type=mtype,
                count=len(values),
                total=sum(values),
                avg=statistics.mean(values),
                min=min(values),
                max=max(values),
                p50=sorted_values[len(sorted_values) // 2],
                p95=sorted_values[int(len(sorted_values) * 0.95)],
                p99=sorted_values[int(len(sorted_values) * 0.99)],
                window_start=start_time.isoformat(),
                window_end=end_time.isoformat()
            )
            stats_list.append(stats)
        
        return stats_list
    
    def export_prometheus(self, service: Optional[str] = None) -> str:
        """Export metrics in Prometheus format"""
        stats = self.get_stats(service=service, window_hours=1)
        
        lines = []
        lines.append("# HELP echo_metric_total Total count of metrics")
        lines.append("# TYPE echo_metric_total counter")
        lines.append("# HELP echo_metric_avg Average metric value")
        lines.append("# TYPE echo_metric_avg gauge")
        lines.append("# HELP echo_metric_p95 95th percentile metric value")
        lines.append("# TYPE echo_metric_p95 gauge")
        
        for stat in stats:
            labels = f'service="{stat.service}",type="{stat.metric_type}"'
            lines.append(f"echo_metric_total{{{labels}}} {stat.count}")
            lines.append(f"echo_metric_avg{{{labels}}} {stat.avg}")
            lines.append(f"echo_metric_p95{{{labels}}} {stat.p95}")
        
        return "\n".join(lines)

# Global singleton instance
_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get singleton metrics collector instance"""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector

def collect_metric(
    service: str,
    metric_type: str,
    value: float,
    trace_id: Optional[str] = None,
    request_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Convenience function to collect a metric"""
    collector = get_metrics_collector()
    collector.collect(service, metric_type, value, trace_id, request_id, metadata)

# CLI interface for metrics management
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Metrics Collection Agent')
    parser.add_argument('command', choices=['collect', 'report', 'stats', 'reset', 'export', 'cleanup'])
    parser.add_argument('--service', help='Service name')
    parser.add_argument('--metric-type', choices=['latency_ms', 'error_count', 'cost_usd'], help='Metric type')
    parser.add_argument('--value', type=float, help='Metric value')
    parser.add_argument('--trace-id', help='Trace ID')
    parser.add_argument('--request-id', help='Request ID')
    parser.add_argument('--window', type=int, default=24, help='Time window in hours (default: 24)')
    parser.add_argument('--retention-days', type=int, default=30, help='Retention period in days')
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    collector = get_metrics_collector()
    
    if args.command == 'collect':
        if not all([args.service, args.metric_type, args.value is not None]):
            print("Error: --service, --metric-type, and --value required for collect command")
            return
        
        collector.collect(
            service=args.service,
            metric_type=args.metric_type,
            value=args.value,
            trace_id=args.trace_id,
            request_id=args.request_id
        )
        print(f"✅ Collected {args.metric_type} metric for {args.service}: {args.value}")
    
    elif args.command == 'report':
        stats = collector.get_stats(
            service=args.service,
            metric_type=args.metric_type,
            window_hours=args.window
        )
        
        if args.json:
            output = [asdict(stat) for stat in stats]
            print(json.dumps(output, indent=2))
        else:
            print("=" * 100)
            print(f"METRICS REPORT - Last {args.window} hours")
            print("=" * 100)
            
            for stat in stats:
                print(f"\n📊 {stat.service} - {stat.metric_type}")
                print(f"  Count: {stat.count}")
                print(f"  Avg: {stat.avg:.2f}")
                print(f"  Min: {stat.min:.2f}")
                print(f"  Max: {stat.max:.2f}")
                print(f"  P50: {stat.p50:.2f}")
                print(f"  P95: {stat.p95:.2f}")
                print(f"  P99: {stat.p99:.2f}")
                print(f"  Total: {stat.total:.2f}")
    
    elif args.command == 'stats':
        # Alias for report command
        stats = collector.get_stats(
            service=args.service,
            metric_type=args.metric_type,
            window_hours=args.window
        )
        
        if args.json:
            output = [asdict(stat) for stat in stats]
            print(json.dumps(output, indent=2))
        else:
            for stat in stats:
                print(f"{stat.service}/{stat.metric_type}: avg={stat.avg:.2f} p95={stat.p95:.2f} count={stat.count}")
    
    elif args.command == 'export':
        prometheus_output = collector.export_prometheus(service=args.service)
        print(prometheus_output)
    
    elif args.command == 'cleanup':
        count = collector.store.cleanup_old(retention_days=args.retention_days)
        print(f"✅ Cleaned up {count} old metric files (retention: {args.retention_days} days)")
    
    elif args.command == 'reset':
        if args.service:
            # Delete metrics for specific service (not implemented - would need more complex filtering)
            print("⚠️  Service-specific reset not implemented. Use cleanup command.")
        else:
            # Clear all metrics
            for metrics_file in collector.store.storage_path.glob("metrics_*.jsonl"):
                metrics_file.unlink()
            print("✅ Reset all metrics")

if __name__ == "__main__":
    main()
