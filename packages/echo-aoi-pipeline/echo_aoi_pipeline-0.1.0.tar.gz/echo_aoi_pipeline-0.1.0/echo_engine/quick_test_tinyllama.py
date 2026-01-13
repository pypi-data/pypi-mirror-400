"""Quick test of optimized TinyLlama prompt"""
import json
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

judge = TinyLlamaJudge()

print('=' * 80)
print('QUICK TEST: Optimized TinyLlama Prompt')
print('=' * 80)
print(f'Observation ID: {obs.record_id}')
print(f'Estimated protrusions (ground truth): {obs.estimated_protrusions}')
print()

result = judge.judge(obs)

print()
print('=' * 80)
print('RESULT')
print('=' * 80)
print(f'Raw Response: |{result.raw_response}|')
print(f'Parsed State: {result.state}')
print(f'Parsed Value: {result.value}')
print(f'Latency: {result.latency_s:.2f}s')
print()

if result.state == 'VALUE' and result.value == obs.estimated_protrusions:
    print('✅ SUCCESS: TinyLlama correctly extracted the value!')
elif result.state == 'VALUE':
    print(f'⚠️  PARTIAL: Got VALUE={result.value}, expected {obs.estimated_protrusions}')
else:
    print(f'❌ FAIL: Got {result.state} instead of VALUE')
