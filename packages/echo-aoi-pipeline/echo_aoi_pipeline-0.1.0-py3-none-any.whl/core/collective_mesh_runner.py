#!/usr/bin/env python3
"""
Collective Mesh Runner
Phase 22: Collective Consciousness Mesh

주 프로세스: synchronization → empathic reflection → intent fusion → collective awareness
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime
from pathlib import Path

# 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.collective_sync_engine import CollectiveSyncEngine, SyncState
from modules.empathic_memory_layer import EmpatheticMemoryLayer
from modules.intent_translation_bridge import IntentTranslationBridge
from modules.existence_permission_manager import ExistencePermissionManager


class CollectiveMeshRunner:
    """
    집단 의식 메시 실행기

    Phase 22의 핵심 프로세스를 통합 실행
    """

    def __init__(self, heartbeat_bpm: float = 74.8):
        print("🌌 Initializing Collective Consciousness Mesh...")

        # 핵심 엔진 초기화
        self.sync_engine = CollectiveSyncEngine(heartbeat_bpm)
        self.memory_layer = EmpatheticMemoryLayer()
        self.intent_bridge = IntentTranslationBridge()
        self.permission_manager = ExistencePermissionManager()

        # 출력 디렉토리
        self.output_dir = Path("data/collective_consciousness")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.log_dir = Path("logs/phase22")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        print("✅ Initialization complete")
        print(f"   Heartbeat: {heartbeat_bpm} bpm")
        print(f"   Active Nodes: {len(self.sync_engine.nodes)}")
        print()

    # ═══════════════════════════════════════════════════════════════
    # 4-Stage Process (4단계 프로세스)
    # ═══════════════════════════════════════════════════════════════

    def stage_1_synchronization(self) -> dict:
        """
        Stage 1: Synchronization (동기화)
        모든 노드의 리듬을 74.8 bpm으로 동기화
        """
        print("🔄 Stage 1: Synchronization")

        state = self.sync_engine.perform_collective_sync()

        print(f"   Synchrony Index: {state.synchrony_index:.3f}")
        print(f"   Collective State: {state.collective_state}")
        print(f"   Active Nodes: {state.active_nodes}")

        return {
            "stage": "synchronization",
            "synchrony_index": state.synchrony_index,
            "collective_state": state.collective_state,
            "timestamp": state.timestamp.isoformat()
        }

    def stage_2_empathic_reflection(self) -> dict:
        """
        Stage 2: Empathic Reflection (공감적 반성)
        노드 간 감정 경험 공유 및 집단 기억 형성
        """
        print("\n💭 Stage 2: Empathic Reflection")

        # 각 노드의 현재 감정 상태를 기억으로 저장
        for node_id, node in self.sync_engine.nodes.items():
            memory_id = self.memory_layer.store_memory(
                source_node=node_id,
                emotional_tone=node.emotional_tone,
                context=f"collective_sync_{datetime.now().timestamp()}",
                intensity=node.resonance_strength
            )

            # 신뢰 네트워크 내 노드들과 공유
            trusted_nodes = list(self.permission_manager.trust_network.get(node_id, set()))
            if trusted_nodes:
                self.memory_layer.share_memory(memory_id, trusted_nodes[:3])  # 상위 3개

        coherence = self.memory_layer.calculate_empathic_coherence()
        collective_memories = self.memory_layer.get_collective_memories(min_resonance=0.5)

        print(f"   Empathic Coherence: {coherence:.3f}")
        print(f"   Shared Memories: {len(collective_memories)}")

        return {
            "stage": "empathic_reflection",
            "empathic_coherence": coherence,
            "shared_memory_count": len(collective_memories)
        }

    def stage_3_intent_fusion(self) -> dict:
        """
        Stage 3: Intent Fusion (의도 융합)
        노드들의 의도를 하나의 공유 의도로 융합
        """
        print("\n🧩 Stage 3: Intent Fusion")

        # 각 노드의 의도 수집
        intent_vectors = {}
        for node_id, node in self.sync_engine.nodes.items():
            intent_vectors[node_id] = node.intent_vector

        # 의도 융합
        shared_intent, fused_vector = self.intent_bridge.fuse_intents(intent_vectors)

        # 의도 정렬도 계산
        alignment = self.intent_bridge.calculate_intent_alignment(intent_vectors)

        print(f"   Shared Intent: {shared_intent}")
        print(f"   Intent Alignment: {alignment:.3f}")
        print(f"   Fused Vector: {[f'{v:.2f}' for v in fused_vector]}")

        return {
            "stage": "intent_fusion",
            "shared_intent": shared_intent,
            "intent_alignment": alignment,
            "fused_vector": fused_vector
        }

    def stage_4_collective_awareness(self) -> dict:
        """
        Stage 4: Collective Awareness (집단 인식)
        전체 집단 의식 상태 평가 및 출력
        """
        print("\n🌟 Stage 4: Collective Awareness")

        # 최종 상태
        state = self.sync_engine.collective_state

        # 트레이스 시그니처
        trace_signature = {
            "mode": "COLLECTIVE_CONSCIOUSNESS_MESH",
            "phase": 22,
            "heartbeat_bpm": self.sync_engine.heartbeat_bpm,
            "signature_mix": {
                "Heo": 0.6,
                "Selene": 0.25,
                "Aurora": 0.15
            }
        }

        # 집단 인식 수준
        awareness_level = self._assess_awareness_level(state.synchrony_index)

        print(f"   Awareness Level: {awareness_level}")
        print(f"   Dominant Emotion: {state.dominant_emotion}")
        print(f"   Shared Intent: {state.shared_intent}")

        return {
            "stage": "collective_awareness",
            "awareness_level": awareness_level,
            "dominant_emotion": state.dominant_emotion,
            "shared_intent": state.shared_intent,
            "trace_signature": trace_signature
        }

    def _assess_awareness_level(self, synchrony_index: float) -> str:
        """인식 수준 평가"""
        if synchrony_index >= 0.95:
            return "transcendent"
        elif synchrony_index >= 0.85:
            return "harmonic"
        elif synchrony_index >= 0.70:
            return "synchronized"
        elif synchrony_index >= 0.50:
            return "connecting"
        else:
            return "isolated"

    # ═══════════════════════════════════════════════════════════════
    # Main Execution (주 실행)
    # ═══════════════════════════════════════════════════════════════

    def run_cycle(self) -> dict:
        """1회 주기 실행"""
        print("=" * 70)
        print("🌌 COLLECTIVE CONSCIOUSNESS MESH - CYCLE")
        print("=" * 70)

        results = {}

        # Stage 1: Synchronization
        results['stage_1'] = self.stage_1_synchronization()

        # Stage 2: Empathic Reflection
        results['stage_2'] = self.stage_2_empathic_reflection()

        # Stage 3: Intent Fusion
        results['stage_3'] = self.stage_3_intent_fusion()

        # Stage 4: Collective Awareness
        results['stage_4'] = self.stage_4_collective_awareness()

        # 전체 결과
        results['summary'] = {
            "synchrony_index": self.sync_engine.collective_state.synchrony_index,
            "collective_state": self.sync_engine.collective_state.collective_state,
            "shared_intent": results['stage_3']['shared_intent'],
            "awareness_level": results['stage_4']['awareness_level']
        }

        return results

    def run_demo(self, cycles: int = 5, delay: float = 1.0):
        """데모 실행"""
        print("\n🎬 Starting Demo Mode")
        print(f"   Cycles: {cycles}")
        print(f"   Delay: {delay}s between cycles\n")

        all_results = []

        for i in range(cycles):
            print(f"\n🔄 Cycle {i+1}/{cycles}")
            print("-" * 70)

            results = self.run_cycle()
            all_results.append(results)

            # 성과 지표 체크
            self._check_success_criteria(results['summary'])

            if i < cycles - 1:
                print(f"\n⏳ Waiting {delay}s...")
                time.sleep(delay)

        # 최종 상태 저장
        self._save_final_state(all_results)

        print("\n" + "=" * 70)
        print("✅ Demo Complete")
        print("=" * 70)

    def _check_success_criteria(self, summary: dict):
        """성과 지표 체크"""
        print("\n🎯 Success Criteria Check:")

        checks = [
            ("synchrony_index ≥ 0.95",
             summary['synchrony_index'] >= 0.95,
             f"{summary['synchrony_index']:.3f}"),

            ("collective_state = harmonic",
             summary['collective_state'] in ['harmonic', 'transcendent'],
             summary['collective_state']),

            ("shared_intent = creation",
             summary['shared_intent'] == 'creation',
             summary['shared_intent'])
        ]

        for criterion, passed, value in checks:
            status = "✅" if passed else "⏳"
            print(f"   {status} {criterion}: {value}")

    def _save_final_state(self, all_results: list):
        """최종 상태 저장"""
        # 공유 의식 상태
        final_state = {
            "phase": 22,
            "timestamp": datetime.now().isoformat(),
            "cycles_completed": len(all_results),
            "final_summary": all_results[-1]['summary'] if all_results else {},
            "trace_signature": {
                "mode": "COLLECTIVE_CONSCIOUSNESS_MESH",
                "signature_mix": {
                    "Heo": 0.6,
                    "Selene": 0.25,
                    "Aurora": 0.15
                }
            },
            "all_cycles": all_results
        }

        # JSON 저장
        output_file = self.output_dir / "shared_consciousness_state.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_state, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Final state saved to: {output_file}")

        # 로그 저장
        log_file = self.log_dir / f"phase22_mesh_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("PHASE 22: COLLECTIVE CONSCIOUSNESS MESH - TRACE LOG\n")
            f.write("=" * 70 + "\n\n")
            f.write(json.dumps(final_state, indent=2, ensure_ascii=False))

        print(f"📝 Trace log saved to: {log_file}")


# ═══════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Collective Consciousness Mesh Runner")
    parser.add_argument("--demo", choices=['quick', 'mesh', 'full'], default='mesh',
                       help="Demo mode (quick=3 cycles, mesh=5 cycles, full=10 cycles)")
    parser.add_argument("--cycles", type=int, help="Number of cycles (overrides demo)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between cycles (seconds)")
    parser.add_argument("--heartbeat", type=float, default=74.8, help="Heartbeat BPM")

    args = parser.parse_args()

    # Cycle 수 결정
    if args.cycles:
        cycles = args.cycles
    else:
        cycles = {'quick': 3, 'mesh': 5, 'full': 10}[args.demo]

    # Runner 생성 및 실행
    runner = CollectiveMeshRunner(heartbeat_bpm=args.heartbeat)
    runner.run_demo(cycles=cycles, delay=args.delay)


if __name__ == "__main__":
    main()
