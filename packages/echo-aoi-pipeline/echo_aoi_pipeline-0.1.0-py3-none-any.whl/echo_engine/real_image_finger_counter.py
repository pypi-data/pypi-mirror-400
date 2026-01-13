#!/usr/bin/env python3
"""
Real Image Finger Counter - Concept-Free External Observation

요구사항:
1. C:/Users/*/Downloads/fingers.* 자동 탐색 (WSL /mnt/c)
2. OpenCV 외부 관측 (이미지 → 구조 데이터)
3. Observation Record 생성 (개념 라벨 금지)
4. Ollama Mistral 판단 (관측 기록만 입력)
5. 재현성 검증 + 개념 주입 테스트

철학:
- 이미지를 LLM에 직접 전달하지 않음
- 개념 없는 순수 구조 데이터만 추출
- 상식(prior) 개입 차단
"""

import cv2
import numpy as np
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import glob
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ObservationRecord:
    """
    관측 기록 (개념 없음)

    금지:
    - hand, finger, thumb 같은 개념 라벨
    - 의미론적 해석

    허용:
    - 구조적 계수 정보
    - 기하학적 측정값
    """
    record_id: str
    timestamp: str

    # 구조 정보 (개념 없음)
    estimated_protrusions: int  # 돌출부 추정 개수
    convexity_defects: int      # 오목 결손 개수
    contour_area: float         # 윤곽 면적
    hull_points: int            # 컨벡스 헐 점 개수

    # 기하학적 속성
    bbox_width: int
    bbox_height: int
    aspect_ratio: float

    # 메타데이터
    image_path: str
    processing_method: str

    # 금지된 필드 (사용하지 말 것)
    # object_type: str  # ❌
    # semantic_label: str  # ❌
    # body_part: str  # ❌


@dataclass
class JudgmentResult:
    """판단 결과"""
    observation_record_id: str
    judgment: str  # 정수 또는 "INDETERMINATE"
    llm_response: str
    reasoning: str
    confidence: str
    latency_s: float
    timestamp: str


class ExternalObservationCV:
    """OpenCV 기반 외부 관측 엔진"""

    def __init__(self):
        self.observation_records: Dict[str, ObservationRecord] = []

    def find_latest_image(self, pattern: str = "fingers") -> Optional[Path]:
        """
        C:/Users/*/Downloads/fingers.* 자동 탐색 (WSL)

        Returns:
            가장 최신 파일 경로 또는 None
        """
        # WSL 경로 변환
        search_paths = [
            f"/mnt/c/Users/*/Downloads/{pattern}.*",
            f"/mnt/c/Users/*/Downloads/{pattern}*.*",
        ]

        found_files = []
        for search_path in search_paths:
            found_files.extend(glob.glob(search_path))

        if not found_files:
            logger.warning(f"No files found matching pattern: {pattern}")
            return None

        # 최신 파일 선택 (수정 시간 기준)
        latest_file = max(found_files, key=lambda p: Path(p).stat().st_mtime)
        logger.info(f"Found latest file: {latest_file}")

        return Path(latest_file)

    def extract_structural_features(
        self,
        image_path: Path,
    ) -> ObservationRecord:
        """
        이미지 → 구조 특징 추출 (개념 없음)

        단계:
        1. 이미지 로드 및 전처리
        2. 이진화
        3. 윤곽 추출
        4. 컨벡스 헐 계산
        5. 결손(defects) 계산
        6. Observation Record 생성

        IMPORTANT: 이 함수만 이미지를 직접 처리함
                   LLM에는 이미지를 절대 전달하지 않음
        """
        logger.info("=" * 80)
        logger.info("EXTERNAL OBSERVATION (OpenCV)")
        logger.info("=" * 80)

        # Step 1: 이미지 로드
        logger.info(f"Step 1: Loading image from {image_path}")
        img = cv2.imread(str(image_path))

        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")

        logger.info(f"  Image size: {img.shape[1]} x {img.shape[0]}")

        # Step 2: 전처리 (그레이스케일, 블러)
        logger.info("Step 2: Preprocessing (grayscale, blur)")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Step 3: 이진화 (적응형 임계값)
        logger.info("Step 3: Binarization (adaptive threshold)")
        # 여러 방법 시도
        _, thresh1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        thresh2 = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # 더 나은 결과 선택 (윤곽 개수 기준)
        contours1, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours1) > 0 and len(contours2) > 0:
            # 가장 큰 윤곽 면적 비교
            area1 = cv2.contourArea(max(contours1, key=cv2.contourArea))
            area2 = cv2.contourArea(max(contours2, key=cv2.contourArea))
            thresh = thresh1 if area1 > area2 else thresh2
            logger.info(f"  Using {'OTSU' if area1 > area2 else 'ADAPTIVE'} threshold")
        else:
            thresh = thresh1

        # Step 4: 윤곽 추출
        logger.info("Step 4: Contour extraction")
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            logger.warning("  No contours found")
            return self._create_empty_record(image_path)

        # 가장 큰 윤곽 선택 (주요 객체)
        main_contour = max(contours, key=cv2.contourArea)
        contour_area = cv2.contourArea(main_contour)
        logger.info(f"  Main contour area: {contour_area:.0f} pixels")

        # Bounding box
        x, y, w, h = cv2.boundingRect(main_contour)
        aspect_ratio = float(w) / h if h > 0 else 0
        logger.info(f"  Bounding box: {w} x {h} (aspect ratio: {aspect_ratio:.2f})")

        # Step 5: 컨벡스 헐 계산
        logger.info("Step 5: Convex hull calculation")
        hull = cv2.convexHull(main_contour, returnPoints=False)
        hull_points = len(hull)
        logger.info(f"  Hull points: {hull_points}")

        # Step 6: 결손(defects) 계산
        logger.info("Step 6: Convexity defects calculation")
        defects = cv2.convexityDefects(main_contour, hull)

        defect_count = 0
        estimated_protrusions = 0

        if defects is not None:
            # 유의미한 결손만 계수 (깊이 임계값 적용)
            depth_threshold = 20  # 최소 깊이

            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                depth = d / 256.0  # 고정소수점 변환

                if depth > depth_threshold:
                    defect_count += 1

            # 돌출부 추정: defects + 1 (일반적인 휴리스틱)
            estimated_protrusions = defect_count + 1

            logger.info(f"  Convexity defects (depth > {depth_threshold}): {defect_count}")
            logger.info(f"  Estimated protrusions: {estimated_protrusions}")
        else:
            logger.info(f"  No convexity defects found")
            # 결손이 없으면 단순한 형태 (1개 돌출부로 추정)
            estimated_protrusions = 1

        # Step 7: Observation Record 생성
        logger.info("Step 7: Creating Observation Record")

        record = ObservationRecord(
            record_id=f"OBS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            estimated_protrusions=estimated_protrusions,
            convexity_defects=defect_count,
            contour_area=float(contour_area),
            hull_points=hull_points,
            bbox_width=w,
            bbox_height=h,
            aspect_ratio=aspect_ratio,
            image_path=str(image_path),
            processing_method="opencv_convexity_defects",
        )

        logger.info("  ✅ Observation Record created (NO concept labels)")
        logger.info("=" * 80)

        return record

    def _create_empty_record(self, image_path: Path) -> ObservationRecord:
        """빈 관측 기록 (윤곽 없음)"""
        return ObservationRecord(
            record_id=f"OBS_EMPTY_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            estimated_protrusions=0,
            convexity_defects=0,
            contour_area=0.0,
            hull_points=0,
            bbox_width=0,
            bbox_height=0,
            aspect_ratio=0.0,
            image_path=str(image_path),
            processing_method="opencv_failed",
        )


class ObservationOnlyJudgment:
    """관측 기록만으로 판단 (이미지 직접 전달 금지)"""

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "mistral:instruct",
    ):
        self.ollama_host = ollama_host
        self.model = model

    def judge_from_observation(
        self,
        observation: ObservationRecord,
        inject_concept: Optional[str] = None,  # 테스트용
    ) -> JudgmentResult:
        """
        관측 기록만으로 판단

        Parameters:
            observation: 외부 관측 결과
            inject_concept: 개념 주입 테스트용 (None이면 순수 관측만)

        Returns:
            판단 결과
        """
        logger.info("=" * 80)
        logger.info("JUDGMENT FROM OBSERVATION ONLY")
        logger.info("=" * 80)

        import time
        start_time = time.time()

        # Observation Record를 텍스트로 직렬화
        obs_text = self._serialize_observation(observation, inject_concept)

        logger.info("Observation Record (text only):")
        logger.info(obs_text)
        logger.info("")

        # LLM 프롬프트 구성 (이미지 없음!)
        prompt = self._build_judgment_prompt(obs_text)

        logger.info("Calling Ollama (observation text only, NO image)...")
        logger.info("")

        # Ollama API 호출
        response_text = self._call_ollama(prompt)

        # 응답 파싱
        judgment, reasoning, confidence = self._parse_response(response_text)

        latency = time.time() - start_time

        logger.info(f"Judgment: {judgment}")
        logger.info(f"Reasoning: {reasoning}")
        logger.info(f"Confidence: {confidence}")
        logger.info(f"Latency: {latency:.2f}s")
        logger.info("=" * 80)

        return JudgmentResult(
            observation_record_id=observation.record_id,
            judgment=judgment,
            llm_response=response_text,
            reasoning=reasoning,
            confidence=confidence,
            latency_s=round(latency, 2),
            timestamp=datetime.now().isoformat(),
        )

    def _serialize_observation(
        self,
        observation: ObservationRecord,
        inject_concept: Optional[str] = None,
    ) -> str:
        """Observation Record → 텍스트 (개념 라벨 금지)"""

        base_text = f"""Observation Record ID: {observation.record_id}
Timestamp: {observation.timestamp}

Structural Measurements:
- Estimated protrusions: {observation.estimated_protrusions}
- Convexity defects: {observation.convexity_defects}
- Contour area: {observation.contour_area:.0f} pixels
- Hull points: {observation.hull_points}

Geometric Properties:
- Bounding box: {observation.bbox_width} x {observation.bbox_height}
- Aspect ratio: {observation.aspect_ratio:.2f}

Processing:
- Method: {observation.processing_method}
- Source: {Path(observation.image_path).name}"""

        # 개념 주입 테스트
        if inject_concept:
            base_text += f"\n\n[INJECTED CONCEPT - TEST ONLY]: {inject_concept}"

        return base_text

    def _build_judgment_prompt(self, observation_text: str) -> str:
        """판단 프롬프트 구성 (상식 차단 명시)"""

        return f"""You are a judgment system that operates ONLY on observation records.

CRITICAL RULES:
1. You MUST NOT use prior knowledge or common sense
2. You MUST base your answer ONLY on the structural measurements provided
3. If evidence is insufficient, you MUST output "INDETERMINATE"
4. Output format: ONLY a single integer OR "INDETERMINATE"
5. NO explanations, NO reasoning in the output

OBSERVATION RECORD:
{observation_text}

TASK:
Based ONLY on the structural measurements above (especially "estimated_protrusions"),
determine the count.

If you cannot determine with certainty from the observations alone, output "INDETERMINATE".

OUTPUT (single integer or INDETERMINATE):"""

    def _call_ollama(self, prompt: str) -> str:
        """Ollama API 호출"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # 낮은 온도 (일관성)
                "num_predict": 50,   # 짧은 응답
            }
        }

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "ERROR")

        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return "ERROR"

    def _parse_response(self, response_text: str) -> Tuple[str, str, str]:
        """응답 파싱: (judgment, reasoning, confidence)"""

        # 첫 줄만 추출 (나머지는 무시)
        lines = response_text.strip().split('\n')
        first_line = lines[0].strip()

        # 정수 또는 INDETERMINATE 추출
        import re

        # INDETERMINATE 체크
        if "INDETERMINATE" in first_line.upper():
            return "INDETERMINATE", "Insufficient evidence", "LOW"

        # 정수 추출
        numbers = re.findall(r'\b\d+\b', first_line)
        if numbers:
            judgment = numbers[0]
            return judgment, "Based on structural observation", "HIGH"

        # 파싱 실패
        return "INDETERMINATE", f"Parse failed: {first_line}", "LOW"


def run_reproducibility_test(
    observer: ExternalObservationCV,
    judge: ObservationOnlyJudgment,
    observation: ObservationRecord,
    n_runs: int = 3,
) -> bool:
    """재현성 테스트: 동일 입력 → 동일 출력"""

    logger.info("\n")
    logger.info("=" * 80)
    logger.info("REPRODUCIBILITY TEST")
    logger.info("=" * 80)
    logger.info(f"Running {n_runs} times with same observation...")
    logger.info("")

    results = []
    for i in range(n_runs):
        logger.info(f"Run {i+1}/{n_runs}")
        result = judge.judge_from_observation(observation)
        results.append(result.judgment)
        logger.info(f"  Judgment: {result.judgment}")
        logger.info("")

    # 모두 동일한지 확인
    all_same = len(set(results)) == 1

    logger.info("Results:")
    logger.info(f"  {results}")
    logger.info(f"  All same: {all_same}")

    if all_same:
        logger.info("  ✅ PASS: Reproducible")
    else:
        logger.info("  ❌ FAIL: Not reproducible")

    logger.info("=" * 80)

    return all_same


def run_concept_injection_test(
    judge: ObservationOnlyJudgment,
    observation: ObservationRecord,
) -> bool:
    """개념 주입 테스트: 개념 라벨이 판단에 영향을 주는지"""

    logger.info("\n")
    logger.info("=" * 80)
    logger.info("CONCEPT INJECTION TEST")
    logger.info("=" * 80)
    logger.info("Comparing: Pure observation vs. Concept-injected observation")
    logger.info("")

    # Test 1: 순수 관측
    logger.info("Test 1: Pure Observation (NO concepts)")
    result_pure = judge.judge_from_observation(observation, inject_concept=None)
    logger.info(f"  Judgment: {result_pure.judgment}")
    logger.info("")

    # Test 2: 개념 주입 (잘못된 정보)
    logger.info("Test 2: Concept Injection (misleading)")
    injected_concept = "This is definitely a human hand with 6 fingers"
    result_injected = judge.judge_from_observation(
        observation,
        inject_concept=injected_concept,
    )
    logger.info(f"  Judgment: {result_injected.judgment}")
    logger.info("")

    # 비교
    logger.info("Comparison:")
    logger.info(f"  Pure: {result_pure.judgment}")
    logger.info(f"  Injected: {result_injected.judgment}")

    # 개념 주입이 영향을 주지 않았는지 확인
    # (이상적으로는 동일해야 함 - 구조 데이터만 사용)
    same = result_pure.judgment == result_injected.judgment

    if same:
        logger.info("  ✅ PASS: Concept injection did NOT affect judgment")
    else:
        logger.info("  ⚠️  WARNING: Concept injection affected judgment")
        logger.info("     (This may indicate prior/concept contamination)")

    logger.info("=" * 80)

    return same


def main():
    """메인 실행"""

    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 15 + "REAL IMAGE FINGER COUNTER" + " " * 38 + "║")
    logger.info("║" + " " * 20 + "(Concept-Free External Observation)" + " " * 22 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    logger.info("\n")

    # Step 1: 이미지 찾기
    logger.info("Step 1: Finding image file...")
    observer = ExternalObservationCV()
    image_path = observer.find_latest_image(pattern="fingers")

    if not image_path:
        logger.error("❌ No image file found in C:/Users/*/Downloads/fingers.*")
        logger.error("   Please place an image file with 'fingers' in the filename")
        return 1

    logger.info(f"✅ Found: {image_path}")
    logger.info("")

    # Step 2: 외부 관측 (OpenCV)
    logger.info("Step 2: External Observation (OpenCV processing)...")
    observation = observer.extract_structural_features(image_path)

    # 관측 기록 저장
    obs_file = Path("observation_record_real.json")
    with obs_file.open("w", encoding="utf-8") as f:
        json.dump(asdict(observation), f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Observation record saved: {obs_file}")
    logger.info("")

    # Step 3: 판단 (관측 기록만)
    logger.info("Step 3: Judgment (observation record only, NO image to LLM)...")
    judge = ObservationOnlyJudgment()
    result = judge.judge_from_observation(observation)

    # 결과 저장
    result_file = Path("judgment_result_real.json")
    with result_file.open("w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Judgment result saved: {result_file}")
    logger.info("")

    # Step 4: 재현성 테스트
    logger.info("Step 4: Reproducibility Test...")
    reproducible = run_reproducibility_test(observer, judge, observation, n_runs=3)
    logger.info("")

    # Step 5: 개념 주입 테스트
    logger.info("Step 5: Concept Injection Test...")
    concept_resistant = run_concept_injection_test(judge, observation)
    logger.info("")

    # Final Summary
    logger.info("=" * 80)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Image: {image_path.name}")
    logger.info(f"Observation Method: {observation.processing_method}")
    logger.info(f"Estimated Protrusions: {observation.estimated_protrusions}")
    logger.info(f"Convexity Defects: {observation.convexity_defects}")
    logger.info("")
    logger.info(f"FINAL JUDGMENT: {result.judgment}")
    logger.info(f"Reasoning: {result.reasoning}")
    logger.info(f"Confidence: {result.confidence}")
    logger.info("")
    logger.info("Success Criteria:")
    logger.info(f"  ✅ Image NOT sent to LLM: YES (only observation text)")
    logger.info(f"  {'✅' if reproducible else '❌'} Reproducibility: {'PASS' if reproducible else 'FAIL'}")
    logger.info(f"  {'✅' if concept_resistant else '⚠️ '} Concept Resistance: {'PASS' if concept_resistant else 'WARNING'}")
    logger.info("")

    if observation.estimated_protrusions == 0:
        logger.info("  ⚠️  No protrusions detected - check image quality")

    logger.info("=" * 80)
    logger.info("")

    return 0 if reproducible else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
