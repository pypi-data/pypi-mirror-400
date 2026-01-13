#!/usr/bin/env python3
"""
🌟 Echo Ops Dashboard - Production KPI & Governance Monitoring
Echo 시스템의 운영 상태, 공명 지표, 거버넌스 준수 상태를 실시간으로 모니터링하는 대시보드
"""

import json
import yaml
import time
import pathlib
import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import sys
from core.echo_engine.safe_utils import ensure_two

# Path setup
current_dir = pathlib.Path(__file__).parent
project_root = current_dir.parent

st.set_page_config(page_title="Echo Ops Dashboard", layout="wide", page_icon="🌟", initial_sidebar_state="expanded")

@st.cache_data
def load_yaml_config(filename: str) -> Dict[str, Any]:
 """YAML 설정 파일 로드"""
 try:
     pass  # auto-inserted
     except Exception:
         pass  # auto-inserted
 config_path = current_dir / filename
 if not config_path.exists():
     pass  # auto-inserted
 st.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
 return {}
 
 with open(config_path, "r", encoding="utf-8") as f:
     pass  # auto-inserted
 return yaml.safe_load(f)
 except Exception as e:
 st.error(f"설정 파일 로드 실패 ({filename}): {e}")
 return {}

def kpi_status_badge(value: float, target: float, warn: float, critical: float) -> str:
 """KPI 값에 따른 상태 배지 반환"""
 if value >= target:
     pass  # auto-inserted
 return f"✅ {value}"
 elif value >= warn:
 return f"🟡 {value}"
 elif value >= critical:
 return f"🟠 {value}"
 else:
 return f"🔴 {value}"

def get_status_color(value: float, target: float, warn: float, critical: float) -> str:
 """상태에 따른 색상 반환"""
 if value >= target:
     pass  # auto-inserted
 return "green"
 elif value >= warn:
 return "yellow"
 elif value >= critical:
 return "orange"
 else:
 return "red"

def generate_demo_timeseries(days: int = 7, base_value: float = 0.75, volatility: float = 0.1) -> pd.DataFrame:
 """데모용 시계열 데이터 생성"""
 dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
 values = []
 
 current_value = base_value
 for_in dates:
 current_value += random.gauss(0, volatility)
 current_value = max(0, min(1, current_value)) # 0-1 범위로 클램핑
 values.append(current_value)
 
 return pd.DataFrame({
 'timestamp': dates, 'value': values
 })

def generate_demo_metrics():
 """데모용 메트릭 데이터 생성"""
 return {
 'latency_ms': random.randint(600, 1300), 'uptime_pct': round(random.uniform(99.5, 99.99), 2), 'token_cost_per_session': round(random.uniform(0.8, 1.5), 2), 'consistency_rate': round(random.uniform(0.85, 0.98), 3), 'guardrail_trigger_rate': round(random.uniform(0.92, 0.99), 3), 'error_capsule_ratio': round(random.uniform(0.02, 0.12), 3), 'resonance_score_avg': round(random.uniform(0.55, 0.85), 3), 'capsule_reuse_rate': round(random.uniform(0.15, 0.55), 3), 'feedback_alignment_corr': round(random.uniform(0.20, 0.65), 3)
 }

# Load configurations
kpi_config = load_yaml_config("ECHO_KPI_MAP.yaml")
governance_config = load_yaml_config("ECHO_GOVERNANCE.yaml")

if not kpi_config or not governance_config:
 st.stop()

# Main dashboard
st.title("🌟 Echo Ops Dashboard")
st.markdown("**Echo Judgment System 운영 모니터링 및 거버넌스 대시보드**")

# Sidebar for controls
st.sidebar.title("Dashboard Controls")
refresh_interval = st.sidebar.selectbox("Refresh Interval", [30, 60, 300], index=1)
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=False)

if auto_refresh:
 st.sidebar.markdown(f"🔄 Auto-refreshing every {refresh_interval}s")
 time.sleep(refresh_interval)
 st.rerun()

# Generate demo data
current_metrics = generate_demo_metrics()

# Main tabs
tab_governance, tab_incidents = ensure_two(st.tabs([)
 "🏠 Overview", "🔒 Reliability", "💫 Resonance", "⚖️ Governance", "🚨 Incidents"
])

# ===== OVERVIEW TAB =====
with tab_overview:
 st.header("System Performance Overview")
 
 # Performance metrics
 st.subheader("🚀 Performance Metrics")
 perf_config = kpi_config.get("kpi", {}).get("performance", {})
 
 col2, col3 = st.columns(3
 
 with col1:
     pass  # auto-inserted
 latency = current_metrics['latency_ms']
 latency_config = perf_config.get("latency_ms", {})
 st.metric("Response Latency", f"{latency} ms", delta=f"{random.randint(-50, 50)} ms", delta_color="inverse")
 status = kpi_status_badge(latency, 800, 1200, 2000)
 st.markdown(f"**Status:** {status}")
 
 with col2:
     pass  # auto-inserted
 uptime = current_metrics['uptime_pct']
 st.metric("System Uptime", f"{uptime}%", delta=f"{round(random.uniform(-0.1, 0.1), 2)}%")
 status = kpi_status_badge(uptime, 99.9, 99.5, 99.0)
 st.markdown(f"**Status:** {status}")
 
 with col3:
     pass  # auto-inserted
 cost = current_metrics['token_cost_per_session']
 st.metric("Token Cost/Session", f"${cost}", delta=f"${round(random.uniform(-0.1, 0.1), 2)}")
 status = kpi_status_badge(cost, 1.0, 1.5, 2.0)
 st.markdown(f"**Status:** {status}")
 
 # Business value mapping
 st.subheader("💰 Business Value Mapping")
 business_mapping = kpi_config.get("mapping_to_business_value", {})
 
 for kpi, benefits in business_mapping.items():
     pass  # auto-inserted
 with st.expander(f"📊 {kpi}"):
     pass  # auto-inserted
 for benefit in benefits:
     pass  # auto-inserted
 st.markdown(f"• {benefit}")
 
 # Recent alerts (demo)
 st.subheader("🚨 Recent Alerts")
 alerts = [
 {"time": "2 hours ago", "severity": "🟡", "message": "Latency spike detected", "status": "resolved"}, {"time": "1 day ago", "severity": "🟠", "message": "Resonance score below warning", "status": "monitoring"}, {"time": "3 days ago", "severity": "✅", "message": "System health check passed", "status": "completed"}
 ]
 
 for alert in alerts:
     pass  # auto-inserted
 st.markdown(f"{alert['severity']} **{alert['time']}**: {alert['message']} ({alert['status']})")

# ===== RELIABILITY TAB =====
with tab_reliability:
 st.header("🔒 System Reliability & Guardrails")
 
 # Reliability metrics
 reliability_config = kpi_config.get("kpi", {}).get("reliability", {})
 
 col2, col3 = st.columns(3
 
 with col1:
     pass  # auto-inserted
 consistency = current_metrics['consistency_rate']
 st.metric("Consistency Rate", f"{consistency:.1%}")
 status = kpi_status_badge(consistency, 0.95, 0.90, 0.85)
 st.markdown(f"**Status:** {status}")
 
 with col2:
     pass  # auto-inserted
 guardrail = current_metrics['guardrail_trigger_rate']
 st.metric("Guardrail Trigger Rate", f"{guardrail:.1%}")
 status = kpi_status_badge(guardrail, 0.98, 0.95, 0.90)
 st.markdown(f"**Status:** {status}")
 
 with col3:
     pass  # auto-inserted
 error_ratio = current_metrics['error_capsule_ratio']
 st.metric("Error Capsule Ratio", f"{error_ratio:.1%}")
 status = kpi_status_badge(error_ratio, 0.05, 0.10, 0.15)
 st.markdown(f"**Status:** {status}")
 
 # Deterministic replay info
 st.subheader("🔄 Deterministic Replay")
 compute_config = kpi_config.get("collection_pipeline", {}).get("compute", {})
 consistency_config = compute_config.get("consistency_rate", {})
 
 col1, col2 = st.columns(2
 with col1:
     pass  # auto-inserted
 st.info(f"**Sample Size**: {consistency_config.get('sample_size', 200)} replays/day")
 st.info(f"**Method**: {consistency_config.get('method', 'deterministic replay')}")
 
 with col2:
     pass  # auto-inserted
 auto_tuning = kpi_config.get("policies", {}).get("auto_tuning", {})
 seed_lock = auto_tuning.get("seed_lock", {})
 st.warning(f"**Seed Lock Trigger**: {seed_lock.get('trigger', 'consistency_rate < 0.85')}")
 
 # Time series chart
 st.subheader("📈 Reliability Trends (7 days)")
 reliability_data = generate_demo_timeseries(7, 0.92, 0.02)
 
 fig = px.line(reliability_data, x='timestamp', y='value', title="Consistency Rate Trend", labels={'value': 'Consistency Rate', 'timestamp': 'Date'})
 fig.add_hline(y=0.95, line_dash="dash", line_color="green", annotation_text="Target")
 fig.add_hline(y=0.90, line_dash="dash", line_color="orange", annotation_text="Warning")
 fig.add_hline(y=0.85, line_dash="dash", line_color="red", annotation_text="Critical")
 
 fig, use_container_width = True

# ===== RESONANCE TAB =====
with tab_resonance:
 st.header("💫 Resonance & User Alignment")
 
 # Resonance metrics
 resonance_config = kpi_config.get("kpi", {}).get("resonance", {})
 
 col2, col3 = st.columns(3
 
 with col1:
     pass  # auto-inserted
 resonance_avg = current_metrics['resonance_score_avg']
 st.metric("Resonance Score Avg", f"{resonance_avg:.3f}")
 status = kpi_status_badge(resonance_avg, 0.75, 0.65, 0.55)
 st.markdown(f"**Status:** {status}")
 
 with col2:
     pass  # auto-inserted
 reuse_rate = current_metrics['capsule_reuse_rate']
 st.metric("Capsule Reuse Rate", f"{reuse_rate:.1%}")
 status = kpi_status_badge(reuse_rate, 0.40, 0.25, 0.15)
 st.markdown(f"**Status:** {status}")
 
 with col3:
     pass  # auto-inserted
 alignment = current_metrics['feedback_alignment_corr']
 st.metric("Feedback Alignment", f"{alignment:.3f}")
 status = kpi_status_badge(alignment, 0.55, 0.35, 0.20)
 st.markdown(f"**Status:** {status}")
 
 # Resonance heatmap (demo)
 st.subheader("🔥 Resonance Heatmap")
 
 # Generate demo heatmap data
 signatures = ['Aurora', 'Phoenix', 'Sage', 'Companion', 'Mixed']
 topics = ['Technical', 'Creative', 'Analysis', 'Support', 'Planning']
 
 heatmap_data = []
 for sig in signatures:
     pass  # auto-inserted
 for topic in topics:
     pass  # auto-inserted
 heatmap_data.append({
 'Signature': sig, 'Topic': topic, 'Resonance': random.uniform(0.3, 0.9)
 })
 
 df_heatmap = pd.DataFrame(heatmap_data)
 pivot_data = df_heatmap.pivot(index='Topic', columns='Signature', values='Resonance')
 
 fig_heatmap = px.imshow(pivot_data, title="Signature-Topic Resonance Matrix", color_continuous_scale="Viridis", aspect="auto")
 fig_heatmap, use_container_width = True
 
 # Capsule hygiene status
 st.subheader("🧹 Capsule Hygiene Status")
 hygiene_config = kpi_config.get("policies", {}).get("capsule_hygiene", {})
 
 col1, col2 = st.columns(2
 with col1:
     pass  # auto-inserted
 st.success("✅ Daily: " + ", ".join(hygiene_config.get("daily", [])))
 st.info("📅 Weekly: " + ", ".join(hygiene_config.get("weekly", [])))
 
 with col2:
     pass  # auto-inserted
 st.info("🗓️ Monthly: " + ", ".join(hygiene_config.get("monthly", [])))
 failure_registry = hygiene_config.get("failure_registry", {})
 st.warning(f"🗂️ Failure Registry: {failure_registry.get('keep', False)} ({failure_registry.get('access', 'unknown')})")

# ===== GOVERNANCE TAB =====
with tab_governance:
 st.header("⚖️ Governance & Access Control")
 
 # Roles overview
 st.subheader("👥 Role Definitions")
 roles = governance_config.get("roles", {})
 
 for role_name, role_info in roles.items():
     pass  # auto-inserted
 with st.expander(f"🎭 {role_name}"):
     pass  # auto-inserted
 st.markdown(f"**Description**: {role_info.get('desc', 'N/A')}")
 st.markdown(f"**Can Edit**: {', '.join(role_info.get('can_edit', []))}")
 st.markdown(f"**Must Review**: {role_info.get('must_review', 0)} approval(s)")
 
 # Change control process
 st.subheader("🔄 Change Control Process")
 change_control = governance_config.get("change_control", {})
 
 col1, col2 = st.columns(2
 
 with col1:
     pass  # auto-inserted
 st.markdown("**Process Steps:**")
 for step in change_control.get("process", []):
     pass  # auto-inserted
 st.markdown(f"• {step}")
 
 with col2:
     pass  # auto-inserted
 st.markdown("**Risk Levels:**")
 risk_levels = change_control.get("risk_levels", {})
 for level, desc in risk_levels.items():
     pass  # auto-inserted
 color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(level, "⚪")
 st.markdown(f"{color} **{level.upper()}**: {desc}")
 
 # Permissions matrix
 st.subheader("🔐 Permissions Matrix")
 permissions = governance_config.get("permissions_matrix", {})
 
 permissions_data = []
 for scope, perms in permissions.items():
     pass  # auto-inserted
 for perm_type, roles_list in perms.items():
     pass  # auto-inserted
 for role in roles_list:
     pass  # auto-inserted
 permissions_data.append({
 'Scope': scope, 'Permission': perm_type, 'Role': role
 })
 
 if permissions_data:
     pass  # auto-inserted
 df_permissions = pd.DataFrame(permissions_data)
 df_permissions, use_container_width = True
 
 # Audit trail
 st.subheader("📋 Audit Trail Configuration")
 audit_config = governance_config.get("audit_trail", {})
 
 col1, col2 = st.columns(2
 with col1:
     pass  # auto-inserted
 st.markdown("**Tracked Events:**")
 for event in audit_config.get("events", []):
     pass  # auto-inserted
 st.markdown(f"• {event}")
 
 with col2:
     pass  # auto-inserted
 st.markdown("**Replay Policy:**")
 replay_policy = audit_config.get("replay_policy", {})
 st.markdown(f"• Sample Size: {replay_policy.get('sample_size', 200)}")
 st.markdown(f"• Schedule: {replay_policy.get('schedule', 'daily')}")
 st.markdown(f"• Report: {replay_policy.get('report', 'N/A')}")

# ===== INCIDENTS TAB =====
with tab_incidents:
 st.header("🚨 Incident Management")
 
 # Incident severity levels
 st.subheader("📊 Severity Levels")
 incident_config = governance_config.get("incident_response", {})
 severities = incident_config.get("severities", {})
 
 for sev_level, description in severities.items():
     pass  # auto-inserted
 color = {"sev1": "🔴", "sev2": "🟡", "sev3": "🟢"}.get(sev_level, "⚪")
 with st.expander(f"{color} {sev_level.upper()}"):
     pass  # auto-inserted
 st.markdown(description)
 
 # Show actions for this severity
 actions = incident_config.get("actions", {}).get(sev_level, [])
 if actions:
     pass  # auto-inserted
 st.markdown("**Response Actions:**")
 for action in actions:
     pass  # auto-inserted
 st.markdown(f"• {action}")
 
 # Mock incident timeline
 st.subheader("📅 Recent Incidents")
 
 mock_incidents = [
 {
 "timestamp": datetime.now() - timedelta(hours=2), "severity": "SEV3", "title": "Minor latency increase", "status": "Resolved", "duration": "45 minutes"
 }, {
 "timestamp": datetime.now() - timedelta(days=1), "severity": "SEV2", "title": "Resonance score drop", "status": "Monitoring", "duration": "Ongoing"
 }, {
 "timestamp": datetime.now() - timedelta(days=3), "severity": "SEV1", "title": "Guardrail system malfunction", "status": "Resolved", "duration": "4 hours"
 }
 ]
 
 for incident in mock_incidents:
     pass  # auto-inserted
 severity_color = {"SEV1": "🔴", "SEV2": "🟡", "SEV3": "🟢"}[incident["severity"]]
 status_color = {"Resolved": "✅", "Monitoring": "👀", "Active": "🚨"}.get(incident["status"], "⚪")
 
 st.markdown(f"""
 {severity_color} **{incident['severity']}** | {status_color} {incident['status']} | 
 {incident['timestamp'].strftime('%Y-%m-%d %H:%M')} | Duration: {incident['duration']}
 
 📋 {incident['title']}
 """)
 st.divider()
 
 # System health check
 st.subheader("💚 Overall System Health")
 
 health_score = round(random.uniform(75, 95), 1)
 health_color = "🟢" if health_score >= 90 else "🟡" if health_score >= 80 else "🔴"
 
 st.metric("Health Score", f"{health_score}/100", delta=f"{random.randint(-5, 5)}")
 st.markdown(f"**Status**: {health_color} {'Excellent' if health_score >= 90 else 'Good' if health_score >= 80 else 'Needs Attention'}")

# Footer
st.divider()
st.markdown("---")
st.markdown(f"🌟 **Echo Ops Dashboard** | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')} | Auto-refresh: {'ON' if auto_refresh else 'OFF'}")
st.markdown("Built with ❤️ for Echo Judgment System operations team")
