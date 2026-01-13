#!/usr/bin/env python3
"""
Quick test to verify Loop Board integration with registry.yaml
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import yaml
from pydantic import ValidationError

# Test 1: Read registry.yaml
print("🧪 Test 1: Reading loops/registry.yaml")
registry_path = Path(__file__).parent.parent / "loops" / "registry.yaml"

if not registry_path.exists():
    print(f"❌ Registry not found at {registry_path}")
    sys.exit(1)

with open(registry_path, 'r', encoding='utf-8') as f:
    # Registry has comments with --- at the end, use safe_load_all and take first document
    docs = list(yaml.safe_load_all(f))
    registry_data = docs[0] if docs else {}

loops_data = registry_data.get('loops', [])
print(f"✅ Found {len(loops_data)} loops in registry")

# Test 2: Validate with Pydantic model
print("\n🧪 Test 2: Validating with LoopSummary model")
try:
    from models import LoopSummary

    valid_count = 0
    error_count = 0

    for loop in loops_data:
        try:
            loop_summary = LoopSummary(
                id=loop.get('id', ''),
                name=loop.get('name', ''),
                status=loop.get('status', 'unknown'),
                last_run=None,
                mode=None,
                type=loop.get('type'),
                category=loop.get('category'),
                owner=loop.get('owner'),
                trust_score=loop.get('trust_score'),
                description=loop.get('description'),
                manifest=loop.get('manifest'),
                dependencies=loop.get('dependencies', []),
                notes=loop.get('notes')
            )
            valid_count += 1
        except ValidationError as e:
            error_count += 1
            print(f"❌ Validation error for loop {loop.get('id', 'unknown')}: {e}")

    print(f"✅ Successfully validated {valid_count} loops")
    if error_count > 0:
        print(f"⚠️  {error_count} loops had validation errors")

except ImportError as e:
    print(f"❌ Could not import LoopSummary model: {e}")
    sys.exit(1)

# Test 3: Sample loop data
print("\n🧪 Test 3: Sample loop data")
sample_loops = [
    l for l in loops_data
    if l.get('trust_score', 0) >= 0.85  # High trust loops
][:3]

for loop in sample_loops:
    print(f"\n  📦 {loop['name']}")
    print(f"     ID: {loop['id']}")
    print(f"     Trust: {loop.get('trust_score', 0)*100:.0f}%")
    print(f"     Owner: {loop.get('owner', 'Unknown')}")
    print(f"     Category: {loop.get('category', 'N/A')}")
    if loop.get('notes'):
        print(f"     Note: {loop['notes']}")

print("\n" + "="*60)
print("✅ Loop Board Integration Test Complete!")
print(f"📊 Total Loops: {len(loops_data)}")
print(f"📊 Valid: {valid_count}")
print(f"📊 Errors: {error_count}")
print("="*60)
