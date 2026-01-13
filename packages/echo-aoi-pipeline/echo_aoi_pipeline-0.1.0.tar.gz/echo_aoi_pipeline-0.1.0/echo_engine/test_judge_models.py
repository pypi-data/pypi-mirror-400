"""Test different models for Stage 1 judgment"""
import json
import sys
from two_stage_judgment_pipeline import TinyLlamaJudge, ObservationRecord

# Load observation
with open('observation_record_real.json') as f:
    data = json.load(f)

obs = ObservationRecord(
    record_id=data['record_id'],
    timestamp=data['timestamp'],
    estimated_protrusions=data['estimated_protrusions'],
    convexity_defects=data['convexity_defects'],
    contour_area=data['contour_area'],
    hull_points=data['hull_points'],
    bbox_width=data['bbox_width'],
    bbox_height=data['bbox_height'],
    aspect_ratio=data['aspect_ratio'],
    image_path=data['image_path'],
    processing_method=data['processing_method'],
)

# Model to test (can pass as argument)
model = sys.argv[1] if len(sys.argv) > 1 else 'tinyllama:latest'

print('=' * 80)
print(f'TESTING MODEL: {model}')
print('=' * 80)
print(f'Observation ID: {obs.record_id}')
print(f'Expected protrusions (ground truth): {obs.estimated_protrusions}')
print()

# Create judge with specified model
judge = TinyLlamaJudge(model=model)

# Run judgment
result = judge.judge(obs)

print()
print('=' * 80)
print('RESULT')
print('=' * 80)
print(f'Model: {model}')
print(f'Raw Response: |{result.raw_response}|')
print(f'Parsed State: {result.state}')
print(f'Parsed Value: {result.value}')
print(f'Latency: {result.latency_s:.2f}s')
print()

# Evaluation
if result.state == 'VALUE':
    if result.value == obs.estimated_protrusions:
        print('✅ SUCCESS: Correct value extracted!')
        print(f'   Model correctly output {result.value}')
    else:
        print(f'⚠️  PARTIAL: Value extracted but incorrect')
        print(f'   Got: {result.value}, Expected: {obs.estimated_protrusions}')
elif result.state == 'INDETERMINATE':
    print('❌ INDETERMINATE: Model couldn\'t determine value')
    print('   This may be philosophically correct (epistemic uncertainty)')
    print('   Or it may indicate instruction-following failure')
elif result.state == 'STOP':
    print('⛔ STOP: Model detected untraceable evidence source')
    print('   This is a valid epistemic response')
else:
    print(f'❓ UNKNOWN STATE: {result.state}')

print()
print('=' * 80)
