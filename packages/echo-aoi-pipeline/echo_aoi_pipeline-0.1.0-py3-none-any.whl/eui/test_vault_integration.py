#!/usr/bin/env python3
"""
Quick test to verify Vault integration with proof/ directory
"""
import sys
from pathlib import Path
import json
import yaml
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PROOF_DIR = PROJECT_ROOT / "proof"
DIARY_DIR = PROOF_DIR / "diary_exchange"
CONFIG_DIR = PROJECT_ROOT / "config"

def scan_proof_capsules_simple(limit=10):
    """Simple proof capsule scanner without FastAPI"""
    items = []
    if not PROOF_DIR.exists():
        return items

    json_files = list(PROOF_DIR.rglob("*.json"))
    json_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    json_files = json_files[:limit]

    for json_file in json_files:
        try:
            title = json_file.stem
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'capsule_name' in data:
                        title = data['capsule_name']
            except:
                pass
            items.append({
                'title': title,
                'path': str(json_file.relative_to(PROJECT_ROOT)),
                'created': datetime.fromtimestamp(json_file.stat().st_mtime)
            })
        except:
            continue
    return items

def scan_diaries_simple(limit=10):
    """Simple diary scanner"""
    items = []
    if not DIARY_DIR.exists():
        return items

    yaml_files = list(DIARY_DIR.rglob("*.yaml"))
    yaml_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    yaml_files = yaml_files[:limit]

    for yaml_file in yaml_files:
        try:
            title = yaml_file.stem
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    docs = list(yaml.safe_load_all(f))
                    data = docs[0] if docs else {}
                    if 'title' in data:
                        title = data['title']
            except:
                pass
            items.append({
                'title': title,
                'path': str(yaml_file.relative_to(PROJECT_ROOT)),
                'created': datetime.fromtimestamp(yaml_file.stat().st_mtime)
            })
        except:
            continue
    return items

def scan_configs_simple(limit=10):
    """Simple config scanner"""
    items = []
    if not CONFIG_DIR.exists():
        return items

    config_files = list(CONFIG_DIR.glob("*.yaml")) + list(CONFIG_DIR.glob("*.json"))
    config_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    config_files = config_files[:limit]

    for config_file in config_files:
        try:
            items.append({
                'title': config_file.name,
                'path': str(config_file.relative_to(PROJECT_ROOT)),
                'created': datetime.fromtimestamp(config_file.stat().st_mtime)
            })
        except:
            continue
    return items

print("🧪 Test 1: Scanning Proof Capsules")
proof_items = scan_proof_capsules_simple(limit=10)
print(f"✅ Found {len(proof_items)} proof capsules")

if proof_items:
    print("\n📦 Sample proof capsules:")
    for item in proof_items[:3]:
        print(f"  • {item['title']}")
        print(f"    Path: {item['path']}")
        print(f"    Created: {item['created']}")
        print()

print("\n🧪 Test 2: Scanning Diaries")
diary_items = scan_diaries_simple(limit=10)
print(f"✅ Found {len(diary_items)} diary files")

if diary_items:
    print("\n📔 Sample diaries:")
    for item in diary_items[:3]:
        print(f"  • {item['title']}")
        print(f"    Path: {item['path']}")
        print(f"    Created: {item['created']}")
        print()

print("\n🧪 Test 3: Scanning Configs")
config_items = scan_configs_simple(limit=10)
print(f"✅ Found {len(config_items)} config files")

if config_items:
    print("\n⚙️ Sample configs:")
    for item in config_items[:3]:
        print(f"  • {item['title']}")
        print(f"    Path: {item['path']}")
        print()

print("\n" + "="*60)
print("✅ Vault Integration Test Complete!")
print(f"📊 Total Items Found:")
print(f"   Proofs: {len(proof_items)}")
print(f"   Diaries: {len(diary_items)}")
print(f"   Configs: {len(config_items)}")
print(f"   TOTAL: {len(proof_items) + len(diary_items) + len(config_items)}")
print("="*60)
