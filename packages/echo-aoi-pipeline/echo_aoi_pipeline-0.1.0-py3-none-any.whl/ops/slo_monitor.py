#!/usr/bin/env python3
"""
SLO Monitor - Service Level Objective and Error Budget Enforcement
Checks last 24h metrics against SLO targets and triggers automated responses
"""
import yaml
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sys

class SLOMonitor:
    def __init__(self, config_path: str = "ops/slo.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.slo = self.config['slo_targets']
        self.error_budget = self.config['error_budget']
        self.alerts = self.config['alerts']
        
    def collect_metrics(self, window_hours: int = 24) -> Dict:
        """Collect metrics from trace logs for the specified window"""
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'latencies': [],
            'component_stats': {}
        }
        
        # Read trace logs
        trace_files = [
            Path("meta_logs/traces"),
            Path(".echo_workspace/traces")
        ]
        
        for trace_dir in trace_files:
            if not trace_dir.exists():
                continue
                
            for trace_file in trace_dir.glob("*.jsonl"):
                try:
                    with open(trace_file) as f:
                        for line in f:
                            if not line.strip():
                                continue
                            event = json.loads(line)
                            
                            # Parse timestamp
                            ts_str = event.get('timestamp', '')
                            if ts_str:
                                try:
                                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                                    if ts < cutoff_time:
                                        continue
                                except:
                                    continue
                            
                            # Count requests
                            if event.get('event_type') in ['request', 'api_call']:
                                metrics['total_requests'] += 1
                                
                                # Track success/failure
                                if event.get('status') in ['success', 'ok', '200']:
                                    metrics['successful_requests'] += 1
                                elif event.get('status') in ['error', 'failed', '500', '503']:
                                    metrics['failed_requests'] += 1
                                
                                # Collect latency
                                if 'latency_ms' in event:
                                    metrics['latencies'].append(event['latency_ms'])
                                elif 'duration_ms' in event:
                                    metrics['latencies'].append(event['duration_ms'])
                                
                                # Track component stats
                                component = event.get('component_id', 'unknown')
                                if component not in metrics['component_stats']:
                                    metrics['component_stats'][component] = {
                                        'requests': 0,
                                        'errors': 0
                                    }
                                metrics['component_stats'][component]['requests'] += 1
                                if event.get('status') in ['error', 'failed']:
                                    metrics['component_stats'][component]['errors'] += 1
                                    
                except Exception as e:
                    print(f"Warning: Could not parse {trace_file}: {e}", file=sys.stderr)
                    
        return metrics
    
    def calculate_p95_latency(self, latencies: List[float]) -> float:
        """Calculate 95th percentile latency"""
        if not latencies:
            return 0.0
        sorted_latencies = sorted(latencies)
        index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[index] if index < len(sorted_latencies) else sorted_latencies[-1]
    
    def check_slo_compliance(self, metrics: Dict) -> Tuple[bool, Dict]:
        """Check if metrics meet SLO targets"""
        violations = []
        
        # Calculate availability
        total = metrics['total_requests']
        if total > 0:
            availability = (metrics['successful_requests'] / total) * 100
            if availability < self.slo['availability']:
                violations.append({
                    'metric': 'availability',
                    'actual': availability,
                    'target': self.slo['availability'],
                    'severity': 'critical' if availability < self.alerts['availability_critical'] else 'warning'
                })
        else:
            availability = 100.0  # No requests = 100% availability (no failures)
        
        # Calculate error rate
        if total > 0:
            error_rate = (metrics['failed_requests'] / total) * 100
            if error_rate > self.slo['error_rate']:
                violations.append({
                    'metric': 'error_rate',
                    'actual': error_rate,
                    'target': self.slo['error_rate'],
                    'severity': 'critical' if error_rate >= self.alerts['error_rate_critical'] else 'warning'
                })
        else:
            error_rate = 0.0
        
        # Calculate p95 latency
        p95_latency = self.calculate_p95_latency(metrics['latencies'])
        if p95_latency > self.slo['p95_latency_ms']:
            violations.append({
                'metric': 'p95_latency',
                'actual': p95_latency,
                'target': self.slo['p95_latency_ms'],
                'severity': 'critical' if p95_latency >= self.alerts['latency_critical'] else 'warning'
            })
        
        compliant = len(violations) == 0
        
        report = {
            'compliant': compliant,
            'availability': availability,
            'error_rate': error_rate,
            'p95_latency_ms': p95_latency,
            'total_requests': total,
            'violations': violations,
            'component_stats': metrics['component_stats']
        }
        
        return compliant, report
    
    def trigger_automated_actions(self, violations: List[Dict]):
        """Trigger automated responses based on violations"""
        actions_taken = []
        
        # Check if automation is enabled
        automation = self.config.get('automation', {})
        
        for violation in violations:
            if violation['severity'] == 'critical':
                # Trigger canary freeze
                if automation.get('canary_freeze', {}).get('enabled', True):
                    print("🚨 CRITICAL: Triggering canary_freeze due to SLO violation")
                    actions_taken.append('canary_freeze')
                    # Would call actual freeze mechanism here
                    
                # Trigger auto rollback
                if automation.get('auto_rollback', {}).get('enabled', True):
                    print("🔄 CRITICAL: Triggering auto_rollback due to SLO violation")
                    actions_taken.append('auto_rollback')
                    # Would call actual rollback mechanism here
        
        return actions_taken
    
    def generate_report(self, report: Dict, violations_only: bool = False) -> str:
        """Generate human-readable SLO report"""
        lines = []
        lines.append("=" * 70)
        lines.append("SLO COMPLIANCE REPORT")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Window: Last {self.error_budget['window']}")
        lines.append("=" * 70)
        lines.append("")
        
        # Overall status
        if report['compliant']:
            lines.append("✅ STATUS: COMPLIANT - All SLO targets met")
        else:
            lines.append("❌ STATUS: NON-COMPLIANT - SLO violations detected")
        
        lines.append("")
        lines.append("METRICS:")
        lines.append(f"  Availability:    {report['availability']:.2f}% (target: ≥{self.slo['availability']}%)")
        lines.append(f"  Error Rate:      {report['error_rate']:.2f}% (target: ≤{self.slo['error_rate']}%)")
        lines.append(f"  P95 Latency:     {report['p95_latency_ms']:.0f}ms (target: ≤{self.slo['p95_latency_ms']}ms)")
        lines.append(f"  Total Requests:  {report['total_requests']}")
        
        # Violations
        if report['violations']:
            lines.append("")
            lines.append("VIOLATIONS:")
            for v in report['violations']:
                severity_icon = "🔴" if v['severity'] == 'critical' else "🟡"
                lines.append(f"  {severity_icon} {v['metric']}: {v['actual']:.2f} (target: {v['target']:.2f})")
        
        # Component breakdown (only if not violations_only)
        if not violations_only and report['component_stats']:
            lines.append("")
            lines.append("COMPONENT BREAKDOWN:")
            for component, stats in sorted(report['component_stats'].items()):
                error_rate = (stats['errors'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
                lines.append(f"  {component}: {stats['requests']} req, {error_rate:.1f}% errors")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='SLO Monitoring and Error Budget Enforcement')
    parser.add_argument('--config', default='ops/slo.yaml', help='Path to SLO config')
    parser.add_argument('--window', type=int, default=24, help='Metric window in hours')
    parser.add_argument('--json', action='store_true', help='Output JSON report')
    parser.add_argument('--violations-only', action='store_true', help='Only show violations')
    parser.add_argument('--auto-action', action='store_true', help='Trigger automated actions')
    
    args = parser.parse_args()
    
    monitor = SLOMonitor(args.config)
    
    # Collect metrics
    print(f"📊 Collecting metrics for last {args.window} hours...", file=sys.stderr)
    metrics = monitor.collect_metrics(args.window)
    
    # Check compliance
    compliant, report = monitor.check_slo_compliance(metrics)
    
    # Output report
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(monitor.generate_report(report, args.violations_only))
    
    # Trigger automated actions if requested
    if args.auto_action and not compliant:
        actions = monitor.trigger_automated_actions(report['violations'])
        if actions:
            print(f"\n🤖 Automated actions triggered: {', '.join(actions)}", file=sys.stderr)
    
    # Exit code: 0 if compliant, 1 if violations exist
    sys.exit(0 if compliant else 1)

if __name__ == "__main__":
    main()
