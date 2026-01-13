#!/usr/bin/env python3
"""
Level 3 QA: Documentation Examples Test
Based on Echo OS Quality Foundation v1.0

Tests documentation examples with:
1. 경계인지력 (Boundary Awareness)
2. 드리프트감도 (Drift Sensitivity)
3. 시나리오다양성 (Scenario Diversity)
4. 판단일관성 (Judgment Consistency)
5. 리듬 중심 (Rhythm-based)
6. 원인 중심 (Cause-based)
7. 루프 기반 (Loop-based)
8. 멀티브레인 (Multi-brain perspective)
"""

import asyncio
import time
import sys
from pathlib import Path
import statistics
from typing import List, Dict, Any

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ops.eue import get_eue, EUEConfig, EUEMode


class EchoOSQualityTester:
    """Echo OS 품질 철학 기반 테스터"""

    def __init__(self):
        self.test_results = []
        self.rhythm_data = []
        self.judgment_consistency = []

    async def test_with_echo_philosophy(self, test_name: str, test_func, iterations: int = 10):
        """
        Echo OS 철학 기반 테스트 실행

        - 루프 기반: iterations 회 반복
        - 리듬 중심: 실행 시간 변동성 측정
        - 판단일관성: 결과 일관성 검증
        """
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print(f"Philosophy: Echo OS Quality Foundation v1.0")
        print(f"Iterations: {iterations} (Loop-based)")
        print(f"{'='*60}\n")

        results = []
        timings = []
        errors = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")

            start_time = time.time()
            try:
                result = await test_func()
                elapsed = time.time() - start_time

                results.append(result)
                timings.append(elapsed)

                # 리듬 체크: 실행 시간 변동
                if len(timings) >= 2:
                    rhythm_variance = statistics.variance(timings)
                    rhythm_mean = statistics.mean(timings)
                    if rhythm_variance > rhythm_mean * 0.5:  # 변동 > 50%
                        print(f"⚠️  Rhythm unstable (variance={rhythm_variance:.3f})")

                print(f"✅ {elapsed:.3f}s")

            except Exception as e:
                elapsed = time.time() - start_time
                errors.append({"iteration": i+1, "error": str(e), "cause": type(e).__name__})
                print(f"❌ {e}")

        # 멀티브레인 분석
        analysis = self.multi_brain_analysis(test_name, results, timings, errors)

        return analysis

    def multi_brain_analysis(self, test_name: str, results: List, timings: List, errors: List) -> Dict:
        """
        멀티브레인 관점 분석

        1. 기능 브레인: 동작하는가?
        2. 성능 브레인: 얼마나 빠른가?
        3. 안정성 브레인: 일관적인가?
        4. UX 브레인: 명확한가?
        """
        total = len(results) + len(errors)

        # 1. 기능 브레인
        functional_score = len(results) / total if total > 0 else 0

        # 2. 성능 브레인
        if timings:
            avg_time = statistics.mean(timings)
            time_variance = statistics.variance(timings) if len(timings) > 1 else 0
            performance_score = 1.0 - min(time_variance / (avg_time * avg_time), 1.0)
        else:
            avg_time = 0
            time_variance = 0
            performance_score = 0

        # 3. 안정성 브레인 (판단일관성) - Semantic Comparison
        if len(results) >= 2:
            # 결과 일관성 체크 (핵심 필드만 비교)
            # str() 비교는 타임스탬프/비디오 경로 포함 → false positive
            # semantic comparison: success, subsystem 등 핵심만
            def get_core_signature(result):
                """Extract core judgment fields only"""
                if hasattr(result, 'success') and hasattr(result, 'subsystem'):
                    return (result.success, result.subsystem)
                elif isinstance(result, dict):
                    return (result.get('success'), result.get('subsystem'))
                else:
                    return str(result)

            first_signature = get_core_signature(results[0])
            consistency_count = sum(1 for r in results if get_core_signature(r) == first_signature)
            stability_score = consistency_count / len(results)
        else:
            stability_score = 1.0 if len(results) == 1 else 0

        # 4. UX 브레인 (에러 메시지 명확성)
        if errors:
            # 에러 원인이 명확한가?
            clear_errors = sum(1 for e in errors if e.get("cause"))
            ux_score = clear_errors / len(errors)
        else:
            ux_score = 1.0

        # 종합 점수
        overall_score = (
            functional_score * 0.4 +
            performance_score * 0.2 +
            stability_score * 0.3 +
            ux_score * 0.1
        )

        analysis = {
            "test_name": test_name,
            "iterations": total,
            "successes": len(results),
            "failures": len(errors),
            "multi_brain_scores": {
                "functional": functional_score,
                "performance": performance_score,
                "stability": stability_score,
                "ux": ux_score,
                "overall": overall_score
            },
            "rhythm_metrics": {
                "avg_time": avg_time,
                "time_variance": time_variance,
                "timings": timings
            },
            "errors": errors,
            "passed": overall_score >= 0.7
        }

        self.print_analysis(analysis)
        return analysis

    def print_analysis(self, analysis: Dict):
        """분석 결과 출력"""
        print(f"\n{'─'*60}")
        print("Multi-Brain Analysis Results")
        print(f"{'─'*60}")

        scores = analysis["multi_brain_scores"]
        print(f"  🧠 Functional Brain:  {scores['functional']:.2%} {'✅' if scores['functional'] >= 0.9 else '⚠️'}")
        print(f"  ⚡ Performance Brain: {scores['performance']:.2%} {'✅' if scores['performance'] >= 0.7 else '⚠️'}")
        print(f"  🎯 Stability Brain:   {scores['stability']:.2%} {'✅' if scores['stability'] >= 0.9 else '⚠️'}")
        print(f"  💡 UX Brain:          {scores['ux']:.2%} {'✅' if scores['ux'] >= 0.8 else '⚠️'}")
        print(f"  {'─'*60}")
        print(f"  📊 Overall Score:     {scores['overall']:.2%} {'✅ PASS' if analysis['passed'] else '❌ FAIL'}")

        rhythm = analysis["rhythm_metrics"]
        if rhythm["timings"]:
            print(f"\n  Rhythm Metrics:")
            print(f"    Average: {rhythm['avg_time']:.3f}s")
            print(f"    Variance: {rhythm['time_variance']:.4f}")

        if analysis["errors"]:
            print(f"\n  Errors ({len(analysis['errors'])}):")
            for err in analysis["errors"][:3]:  # Show first 3
                print(f"    - Iteration {err['iteration']}: {err['cause']} - {err['error'][:60]}")

        print(f"{'─'*60}\n")


async def test_simple_usage():
    """Test: Simple Usage Example (README line 166-169)"""

    async def simple_test():
        eue = get_eue()
        result = await eue.navigate("https://example.com", with_cursor=True)
        await eue.cleanup()
        return result

    tester = EchoOSQualityTester()
    return await tester.test_with_echo_philosophy(
        "Simple Usage (README Example 1)",
        simple_test,
        iterations=10
    )


async def test_advanced_usage():
    """Test: Advanced Usage with Self-Heal (README line 172-188)"""

    async def advanced_test():
        config = EUEConfig(
            scenario="level3_advanced_test",
            mode=EUEMode.SELF_HEAL,
            max_attempts=3,
            enable_proof=True,
            enable_video=True
        )

        eue = get_eue(config)

        async def my_async_function():
            return await eue.navigate("https://example.com")

        result = await eue.execute_with_self_heal(
            step_name="complex_task",
            executor=my_async_function,
            url="https://example.com"
        )

        await eue.cleanup()
        return result

    tester = EchoOSQualityTester()
    return await tester.test_with_echo_philosophy(
        "Advanced Usage with Self-Heal (README Example 2)",
        advanced_test,
        iterations=5  # Self-heal takes longer
    )


async def test_boundary_awareness():
    """
    경계인지력 테스트

    시스템이 잘못된 입력에 대해 명확한 에러를 제공하는가?
    """
    print(f"\n{'='*60}")
    print("Boundary Awareness Test (경계인지력)")
    print(f"{'='*60}\n")

    test_cases = [
        {
            "name": "Invalid URL",
            "url": "not-a-url",
            "expected": "명확한 URL 에러"
        },
        {
            "name": "Empty URL",
            "url": "",
            "expected": "빈 URL 에러"
        },
        {
            "name": "None URL",
            "url": None,
            "expected": "None 에러"
        }
    ]

    results = []
    for case in test_cases:
        print(f"  Testing: {case['name']}...", end=" ")
        try:
            eue = get_eue()
            result = await eue.navigate(case["url"])
            await eue.cleanup()
            print(f"⚠️  No error raised (unexpected)")
            results.append({"case": case["name"], "error_raised": False, "clear": False})
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            is_clear = len(error_msg) > 0 and error_type != "Exception"
            print(f"✅ {error_type}: {error_msg[:50]}")
            results.append({"case": case["name"], "error_raised": True, "clear": is_clear, "error": error_msg})

    # 분석
    boundary_score = sum(1 for r in results if r.get("error_raised") and r.get("clear")) / len(results)
    print(f"\n  Boundary Awareness Score: {boundary_score:.2%} {'✅' if boundary_score >= 0.7 else '⚠️'}\n")

    return {"boundary_awareness_score": boundary_score, "results": results}


async def test_judgment_consistency():
    """
    판단일관성 테스트

    같은 입력에 대해 일관된 판단을 유지하는가?
    """
    print(f"\n{'='*60}")
    print("Judgment Consistency Test (판단일관성)")
    print(f"{'='*60}\n")

    # 같은 URL을 20번 호출
    url = "https://example.com"
    results = []

    for i in range(20):
        eue = get_eue(EUEConfig(scenario=f"consistency_test_{i}"))
        result = await eue.navigate(url)
        await eue.cleanup()

        # 결과 해시
        result_signature = f"{result.success}_{result.subsystem}"
        results.append(result_signature)

    # 일관성 분석
    most_common = max(set(results), key=results.count)
    consistency_rate = results.count(most_common) / len(results)

    print(f"  Total iterations: {len(results)}")
    print(f"  Most common result: {most_common}")
    print(f"  Consistency rate: {consistency_rate:.2%}")
    print(f"  {'✅ PASS' if consistency_rate >= 0.95 else '⚠️ REVIEW'}\n")

    return {"consistency_rate": consistency_rate, "iterations": len(results)}


async def main():
    """Main test suite with Echo OS Quality Philosophy"""

    print(f"\n{'█'*60}")
    print("  EUE v1.0 - Level 3 QA")
    print("  Based on: Echo OS Quality Foundation v1.0")
    print(f"{'█'*60}")

    all_results = {}

    # 1. Simple Usage (루프 기반, 리듬 중심)
    print("\n[Test 1/5] Simple Usage Example")
    all_results["simple"] = await test_simple_usage()

    # 2. Advanced Usage (루프 기반, 멀티브레인)
    print("\n[Test 2/5] Advanced Usage Example")
    all_results["advanced"] = await test_advanced_usage()

    # 3. Boundary Awareness (경계인지력)
    print("\n[Test 3/5] Boundary Awareness")
    all_results["boundary"] = await test_boundary_awareness()

    # 4. Judgment Consistency (판단일관성)
    print("\n[Test 4/5] Judgment Consistency")
    all_results["consistency"] = await test_judgment_consistency()

    # Final Summary
    print(f"\n{'█'*60}")
    print("  Final Summary")
    print(f"{'█'*60}\n")

    # Overall Pass/Fail
    tests_passed = sum([
        all_results["simple"]["passed"],
        all_results["advanced"]["passed"],
        all_results["boundary"]["boundary_awareness_score"] >= 0.7,
        all_results["consistency"]["consistency_rate"] >= 0.95
    ])

    print(f"  Tests Passed: {tests_passed}/4")
    print(f"  {'✅ ALL TESTS PASSED' if tests_passed == 4 else '⚠️ SOME TESTS FAILED'}")

    # Echo OS Quality Dimensions
    print(f"\n  Echo OS Quality Dimensions:")
    print(f"    경계인지력 (Boundary):     {all_results['boundary']['boundary_awareness_score']:.2%}")
    print(f"    판단일관성 (Consistency):  {all_results['consistency']['consistency_rate']:.2%}")
    print(f"    리듬안정성 (Rhythm):       {all_results['simple']['multi_brain_scores']['performance']:.2%}")
    print(f"    기능완성도 (Functional):   {all_results['simple']['multi_brain_scores']['functional']:.2%}")

    overall_quality = (
        all_results['boundary']['boundary_awareness_score'] +
        all_results['consistency']['consistency_rate'] +
        all_results['simple']['multi_brain_scores']['performance'] +
        all_results['simple']['multi_brain_scores']['functional']
    ) / 4

    print(f"\n  Overall Quality Score: {overall_quality:.2%}")
    print(f"  {'✅ PRODUCTION READY' if overall_quality >= 0.85 else '⚠️ NEEDS IMPROVEMENT'}")

    print(f"\n{'█'*60}\n")

    return all_results


if __name__ == "__main__":
    asyncio.run(main())
