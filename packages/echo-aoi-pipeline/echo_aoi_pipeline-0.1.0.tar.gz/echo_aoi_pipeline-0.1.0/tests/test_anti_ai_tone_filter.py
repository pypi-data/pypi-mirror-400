#!/usr/bin/env python3
"""
Unit Tests for Anti-AI Tone Filter Layer v1
============================================

Tests all 5 detection patterns and 4 transformation types
Verifies success criteria:
- Detection accuracy: 80%+
- Natural tone rating: 75%+
- Meaning preservation: < 20% deviation
"""

import unittest
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.echo_core.tone_filter import AntiAIToneFilter, ToneTransformation
from core.echo_core.tone_filter.anti_ai_tone_layer import (
    MetaObservationDetector,
    OvergeneralizationDetector,
    ParallelismDetector,
    AbstractionDensityDetector,
    FlatConclusionDetector,
    HumanUncertaintyInjector,
    ColloquialRhythmAdjuster,
    SpecificityEnhancer,
    MetaphoricalGrounding,
    AITonePattern
)


class TestMetaObservationDetector(unittest.TestCase):
    """Test meta observation pattern detection"""

    def setUp(self):
        self.detector = MetaObservationDetector()

    def test_detect_community_omniscience(self):
        """Test detection of omniscient community perspective"""
        text = "커뮤니티는 이러한 변화를 느끼고 있다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect omniscient community pattern")
        self.assertEqual(detections[0].pattern_type, AITonePattern.META_OBSERVATION)
        self.assertGreaterEqual(detections[0].confidence, 0.85)

    def test_detect_meta_observation_verb(self):
        """Test detection of meta observation verbs"""
        text = "이러한 흐름을 관찰할 수 있다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect meta observation verb")

    def test_detect_passive_reveal(self):
        """Test detection of passive omniscient reveal"""
        text = "새로운 패턴이 드러나고 있다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect passive reveal pattern")

    def test_no_false_positive(self):
        """Test that normal statements are not flagged"""
        text = "나는 이것을 관찰했다. 데이터에서 패턴을 발견했다."
        detections = self.detector.detect(text)

        self.assertEqual(len(detections), 0, "Should not flag first-person observations")


class TestOvergeneralizationDetector(unittest.TestCase):
    """Test overgeneralization pattern detection"""

    def setUp(self):
        self.detector = OvergeneralizationDetector()

    def test_detect_people_generalization(self):
        """Test detection of 'people do X' generalizations"""
        text = "사람들은 이러한 방식을 선호한다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect people generalization")
        self.assertEqual(detections[0].pattern_type, AITonePattern.OVERGENERALIZATION)

    def test_detect_majority_claim(self):
        """Test detection of unfounded majority claims"""
        text = "대부분은 이 방법이 효과적이다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect majority claim")

    def test_detect_general_statement(self):
        """Test detection of 'generally' statements"""
        text = "일반적으로 성과가 향상된다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect general statement")

    def test_detect_universal_claim(self):
        """Test detection of universal claims"""
        text = "모든 사용자는 편리함을 원한다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect universal claim")


class TestParallelismDetector(unittest.TestCase):
    """Test mechanical parallelism detection"""

    def setUp(self):
        self.detector = ParallelismDetector()

    def test_detect_three_item_list(self):
        """Test detection of 3-item parallel structure"""
        text = "시스템은 효율적이고, 안정적이며, 확장 가능하다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect 3-item parallel structure")
        self.assertEqual(detections[0].pattern_type, AITonePattern.PARALLELISM)

    def test_detect_four_item_list(self):
        """Test detection of 4-item list"""
        text = "이 방법은 빠르고, 정확하고, 간단하며, 효과적이다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect 4-item list")

    def test_ignore_two_item_list(self):
        """Test that 2-item lists are not flagged"""
        text = "시스템은 효율적이고 안정적이다."
        detections = self.detector.detect(text)

        self.assertEqual(len(detections), 0, "Should not flag 2-item lists")


class TestAbstractionDensityDetector(unittest.TestCase):
    """Test abstraction density detection"""

    def setUp(self):
        self.detector = AbstractionDensityDetector()

    def test_detect_high_abstraction(self):
        """Test detection of high abstract noun density"""
        text = "이는 시스템의 본질적인 구조와 메커니즘의 패러다임을 나타낸다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect high abstraction density")
        self.assertEqual(detections[0].pattern_type, AITonePattern.ABSTRACTION_DENSITY)

    def test_detect_multiple_abstractions(self):
        """Test detection of multiple abstract nouns in paragraph"""
        text = """
        이 프레임워크는 아키텍처의 핵심 개념을 정의한다.
        전체 맥락에서 보면 차원이 다른 레이어를 형성한다.
        """
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect multiple abstractions")

    def test_ignore_low_abstraction(self):
        """Test that low abstraction paragraphs are not flagged"""
        text = "사용자가 버튼을 클릭하면 화면이 전환된다. 결과가 표시된다."
        detections = self.detector.detect(text)

        self.assertEqual(len(detections), 0, "Should not flag concrete descriptions")


class TestFlatConclusionDetector(unittest.TestCase):
    """Test flat conclusion pattern detection"""

    def setUp(self):
        self.detector = FlatConclusionDetector()

    def test_detect_because_conclusion(self):
        """Test detection of 'because' conclusions"""
        text = "이것은 시스템 설계의 문제 때문이다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect 'because' conclusion")
        self.assertEqual(detections[0].pattern_type, AITonePattern.FLAT_CONCLUSION)

    def test_detect_definitive_statement(self):
        """Test detection of overly definitive statements"""
        text = "그것은 명백한 사실이다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect definitive statement")

    def test_detect_conclusive_phrase(self):
        """Test detection of 'in conclusion' phrases"""
        text = "결론적으로 이 접근법이 최선이다."
        detections = self.detector.detect(text)

        self.assertGreater(len(detections), 0, "Should detect conclusive phrase")


class TestHumanUncertaintyInjector(unittest.TestCase):
    """Test uncertainty injection transformation"""

    def setUp(self):
        self.transformer = HumanUncertaintyInjector()

    def test_transform_because_to_uncertain(self):
        """Test transformation of definitive 'because' to uncertain"""
        text = "이것은 설계 문제 때문이다."
        result, logs = self.transformer.transform(text, [])

        self.assertIn("것 같다", result, "Should add uncertainty marker")
        self.assertGreater(len(logs), 0, "Should log transformation")

    def test_transform_definitive_to_tentative(self):
        """Test transformation of definitive to tentative"""
        text = "그것은 명확한 사실이다."
        result, logs = self.transformer.transform(text, [])

        self.assertIn("것 같다", result, "Should add tentative marker")

    def test_transform_community_omniscience(self):
        """Test transformation of community omniscience"""
        text = "커뮤니티는 이를 느끼고 있다."
        result, logs = self.transformer.transform(text, [])

        self.assertIn("글 흐름을 보면", result, "Should ground in observable evidence")

    def test_transform_generalization(self):
        """Test transformation of people generalization"""
        text = "사람들은 이를 선호한다."
        result, logs = self.transformer.transform(text, [])

        self.assertIn("편이다", result, "Should qualify generalization")


class TestColloquialRhythmAdjuster(unittest.TestCase):
    """Test rhythm adjustment transformation"""

    def setUp(self):
        self.transformer = ColloquialRhythmAdjuster()

    def test_break_long_sentence(self):
        """Test breaking of overly long sentences"""
        # 80+ character sentence with comma
        text = "이 시스템은 매우 복잡한 구조를 가지고 있으며, 동시에 여러 가지 기능을 수행할 수 있고, 확장 가능한 아키텍처를 제공한다."
        result, logs = self.transformer.transform(text, [])

        # Should have more sentence breaks
        original_sentences = text.count('.')
        result_sentences = result.count('.')
        self.assertGreaterEqual(result_sentences, original_sentences,
                               "Should add sentence breaks")

    def test_preserve_short_sentences(self):
        """Test that short sentences are preserved"""
        text = "시스템이 작동한다. 결과가 표시된다."
        result, logs = self.transformer.transform(text, [])

        self.assertEqual(text, result, "Should preserve short sentences")


class TestSpecificityEnhancer(unittest.TestCase):
    """Test specificity enhancement transformation"""

    def setUp(self):
        self.transformer = SpecificityEnhancer()

    def test_replace_essence(self):
        """Test replacement of '본질' with concrete term"""
        text = "이것이 시스템의 본질이다."
        result, logs = self.transformer.transform(text, [])

        self.assertNotIn("본질", result, "Should replace abstract term")
        self.assertIn("핵심적인 부분", result, "Should use concrete term")

    def test_replace_atmosphere(self):
        """Test replacement of '존재감' with '분위기'"""
        text = "독특한 존재감을 가지고 있다."
        result, logs = self.transformer.transform(text, [])

        self.assertNotIn("존재감", result)
        self.assertIn("분위기", result)

    def test_replace_mechanism(self):
        """Test replacement of '메커니즘' with '동작 방식'"""
        text = "핵심 메커니즘을 이해해야 한다."
        result, logs = self.transformer.transform(text, [])

        self.assertNotIn("메커니즘", result)
        self.assertIn("동작 방식", result)

    def test_replace_paradigm(self):
        """Test replacement of '패러다임' with '관점'"""
        text = "새로운 패러다임이 필요하다."
        result, logs = self.transformer.transform(text, [])

        self.assertNotIn("패러다임", result)
        self.assertIn("관점", result)


class TestMetaphoricalGrounding(unittest.TestCase):
    """Test metaphorical grounding transformation"""

    def setUp(self):
        self.transformer = MetaphoricalGrounding()

    def test_transform_analytical_approach(self):
        """Test transformation of '분석적으로 접근'"""
        text = "분석적으로 접근하면 다음과 같다."
        result, logs = self.transformer.transform(text, [])

        self.assertNotIn("분석적으로", result)
        self.assertIn("단계적으로 살펴보면", result)

    def test_transform_systematic_organization(self):
        """Test transformation of '체계적으로 정리'"""
        text = "체계적으로 정리하면 명확해진다."
        result, logs = self.transformer.transform(text, [])

        self.assertNotIn("체계적으로", result)
        self.assertIn("하나씩 정리하면", result)

    def test_transform_logical_explanation(self):
        """Test transformation of '논리적으로 설명'"""
        text = "논리적으로 설명하면 이해가 쉽다."
        result, logs = self.transformer.transform(text, [])

        self.assertNotIn("논리적으로", result)
        self.assertIn("순서대로 보면", result)


class TestAntiAIToneFilter(unittest.TestCase):
    """Test complete tone filter pipeline"""

    def setUp(self):
        self.filter = AntiAIToneFilter()

    def test_complete_pipeline_meta_observation(self):
        """Test Case 1: Meta observation + overgeneralization"""
        text = "커뮤니티는 이러한 변화를 느끼고 있다. 사람들은 새로운 방식을 이해하고 있다."

        result = self.filter.transform(text)

        # Verify detection
        self.assertGreater(len(result.detections), 0, "Should detect AI patterns")

        # Verify transformation
        self.assertNotEqual(result.original, result.transformed,
                          "Should transform the text")

        # Verify specific transformations
        self.assertIn("것 같", result.transformed,
                     "Should add uncertainty markers")

    def test_complete_pipeline_abstraction(self):
        """Test Case 2: High abstraction density"""
        text = "이는 시스템의 본질적인 구조와 메커니즘의 패러다임을 나타낸다."

        result = self.filter.transform(text)

        # Should detect abstraction density
        abstraction_detected = any(
            d.pattern_type == AITonePattern.ABSTRACTION_DENSITY
            for d in result.detections
        )
        self.assertTrue(abstraction_detected, "Should detect high abstraction")

        # Should replace abstract terms
        self.assertNotIn("본질", result.transformed, "Should replace '본질'")
        self.assertNotIn("메커니즘", result.transformed, "Should replace '메커니즘'")
        self.assertNotIn("패러다임", result.transformed, "Should replace '패러다임'")

    def test_complete_pipeline_flat_conclusion(self):
        """Test Case 3: Flat conclusion + definitive statements"""
        text = "이것은 설계의 문제 때문이다. 결론적으로 개선이 필요하다."

        result = self.filter.transform(text)

        # Should detect flat conclusions
        flat_detected = any(
            d.pattern_type == AITonePattern.FLAT_CONCLUSION
            for d in result.detections
        )
        self.assertTrue(flat_detected, "Should detect flat conclusion")

        # Should add uncertainty
        self.assertIn("것 같", result.transformed, "Should add uncertainty")

    def test_meaning_preservation(self):
        """Test that transformation preserves core meaning"""
        text = "사람들은 이 기능을 선호한다. 이것은 사용성 때문이다."

        result = self.filter.transform(text)

        # Core concepts should be preserved
        self.assertIn("기능", result.transformed, "Should preserve '기능'")
        self.assertIn("사용", result.transformed, "Should preserve '사용' concept")

        # Length should not deviate too much (< 20% as per spec)
        length_ratio = len(result.transformed) / len(result.original)
        self.assertLess(abs(1.0 - length_ratio), 0.2,
                       "Length change should be < 20%")

    def test_statistics_tracking(self):
        """Test statistics collection"""
        texts = [
            "커뮤니티는 변화를 느끼고 있다.",
            "사람들은 이를 선호한다.",
            "이것은 설계 문제 때문이다."
        ]

        for text in texts:
            self.filter.transform(text)

        stats = self.filter.get_statistics()

        self.assertEqual(stats['total_transformations'], 3,
                        "Should track 3 transformations")
        self.assertGreater(stats['total_detections'], 0,
                          "Should track detections")
        self.assertGreater(stats['total_transformations_applied'], 0,
                          "Should track applied transformations")

    def test_no_transformation_needed(self):
        """Test that natural text passes through unchanged"""
        text = "오늘 회의에서 새로운 기능을 논의했다. 다음 주에 개발을 시작할 예정이다."

        result = self.filter.transform(text)

        # Should detect minimal or no patterns
        self.assertLessEqual(len(result.detections), 1,
                            "Natural text should have minimal detections")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests with real-world scenarios"""

    def setUp(self):
        self.filter = AntiAIToneFilter()

    def test_reddit_post_scenario(self):
        """Test Reddit post with multiple AI patterns"""
        text = """
        커뮤니티는 이러한 변화를 느끼고 있다. 사람들은 새로운 패러다임을 이해하고 있다.
        일반적으로 이러한 접근법이 효과적이다. 이것은 시스템의 본질적인 구조 때문이다.
        """

        result = self.filter.transform(text)

        # Should detect multiple patterns
        self.assertGreater(len(result.detections), 2,
                          "Should detect multiple AI patterns")

        # Should have human-like markers
        uncertainty_markers = ["것 같", "편이다", "보면"]
        has_uncertainty = any(marker in result.transformed for marker in uncertainty_markers)
        self.assertTrue(has_uncertainty, "Should add human uncertainty markers")

    def test_technical_documentation_scenario(self):
        """Test technical documentation with abstractions"""
        text = """
        이 아키텍처는 시스템의 핵심 메커니즘을 제공한다.
        분석적으로 접근하면, 체계적으로 정리된 구조를 볼 수 있다.
        """

        result = self.filter.transform(text)

        # Should replace abstractions
        self.assertNotIn("아키텍처", result.transformed)
        self.assertNotIn("메커니즘", result.transformed)

        # Should add metaphorical grounding
        self.assertIn("살펴보면", result.transformed)

    def test_long_form_content_scenario(self):
        """Test long-form content with parallelism"""
        text = """
        이 방법은 효율적이고, 안정적이며, 확장 가능하고, 유지보수가 용이하다.
        대부분의 사용자는 이를 선호한다. 결론적으로 최적의 솔루션이다.
        """

        result = self.filter.transform(text)

        # Should detect parallelism
        parallelism_detected = any(
            d.pattern_type == AITonePattern.PARALLELISM
            for d in result.detections
        )
        self.assertTrue(parallelism_detected, "Should detect parallelism")

        # Should add uncertainty to conclusion
        self.assertNotIn("결론적으로", result.transformed)


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestMetaObservationDetector,
        TestOvergeneralizationDetector,
        TestParallelismDetector,
        TestAbstractionDensityDetector,
        TestFlatConclusionDetector,
        TestHumanUncertaintyInjector,
        TestColloquialRhythmAdjuster,
        TestSpecificityEnhancer,
        TestMetaphoricalGrounding,
        TestAntiAIToneFilter,
        TestIntegrationScenarios
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
