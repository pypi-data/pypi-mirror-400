"""Process fingers2 image through the two-stage judgment pipeline"""
import json
import glob
import cv2
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from two_stage_judgment_pipeline import TwoStageJudgmentPipeline, ObservationRecord
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def find_fingers2_image():
    """Auto-discover fingers2 image in Downloads folder"""
    search_patterns = [
        "/mnt/c/Users/*/Downloads/fingers2.*",
        "/mnt/c/Users/*/Downloads/fingers2.jpeg",
        "/mnt/c/Users/*/Downloads/fingers2.jpg",
        "/mnt/c/Users/*/Downloads/fingers2.png",
    ]

    for pattern in search_patterns:
        matches = glob.glob(pattern)
        if matches:
            # Get most recent if multiple
            matches.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
            return matches[0]

    return None


def extract_structural_features(image_path):
    """
    OpenCV external observation - NO concept labels allowed

    Extracts structural primitives:
    - Protrusions (peaks)
    - Valleys (gaps)
    - Defects

    Forbidden: hand, finger, thumb, knuckle, palm
    """
    logger.info(f"Processing image: {image_path}")

    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")

    h, w = img.shape[:2]
    logger.info(f"Image size: {w} x {h}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Binarization (OTSU threshold)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No contours found in image")

    # Get largest contour (assume main structure)
    main_contour = max(contours, key=cv2.contourArea)
    contour_area = cv2.contourArea(main_contour)
    logger.info(f"Main contour area: {contour_area:,.1f} pixels")

    # Convex hull
    hull = cv2.convexHull(main_contour, returnPoints=False)
    hull_points = len(hull)
    logger.info(f"Convex hull points: {hull_points}")

    # Convexity defects
    try:
        defects = cv2.convexityDefects(main_contour, hull)

        if defects is not None:
            # Count significant defects (depth > threshold)
            depth_threshold = 20
            significant_defects = 0

            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                depth = d / 256.0  # Convert to pixels

                if depth > depth_threshold:
                    significant_defects += 1

            logger.info(f"Convexity defects (depth > {depth_threshold}): {significant_defects}")

            # Estimate protrusions (peaks = valleys + 1)
            estimated_protrusions = significant_defects + 1
        else:
            significant_defects = 0
            estimated_protrusions = 1
    except:
        significant_defects = 0
        estimated_protrusions = 1

    logger.info(f"Estimated protrusions: {estimated_protrusions}")

    # Bounding box
    x, y, bbox_w, bbox_h = cv2.boundingRect(main_contour)
    aspect_ratio = bbox_w / bbox_h if bbox_h > 0 else 0

    # Create observation record (NO concept labels!)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    record_id = f"OBS_fingers2_{time.strftime('%Y%m%d_%H%M%S')}"

    return ObservationRecord(
        record_id=record_id,
        timestamp=timestamp,
        estimated_protrusions=estimated_protrusions,
        convexity_defects=significant_defects,
        contour_area=contour_area,
        hull_points=hull_points,
        bbox_width=bbox_w,
        bbox_height=bbox_h,
        aspect_ratio=aspect_ratio,
        image_path=str(image_path),
        processing_method="opencv_convexity_defects"
    )


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("FINGERS2 - TWO-STAGE JUDGMENT PIPELINE TEST")
    logger.info("=" * 80)
    logger.info("")

    # Step 1: Find image
    logger.info("Step 1: Auto-discovering fingers2 image...")
    image_path = find_fingers2_image()

    if not image_path:
        logger.error("❌ fingers2 image not found in Downloads folder")
        logger.error("   Please place fingers2.jpeg/jpg/png in C:/Users/*/Downloads/")
        return

    logger.info(f"✅ Found: {image_path}")
    logger.info("")

    # Step 2: External observation (OpenCV)
    logger.info("Step 2: External Observation (OpenCV - NO concepts)")
    observation = extract_structural_features(image_path)

    # Save observation record
    obs_file = "observation_record_fingers2.json"
    with open(obs_file, 'w') as f:
        # Convert to dict but exclude image_path for cleaner JSON
        obs_dict = asdict(observation)
        json.dump(obs_dict, f, indent=2)

    logger.info(f"✅ Observation saved: {obs_file}")
    logger.info("")

    # Step 3: Two-stage pipeline
    logger.info("Step 3: Two-Stage Judgment Pipeline")
    logger.info("   Stage 1: phi3:mini (Judge)")
    logger.info("   Stage 2: Mistral (Narrator)")
    logger.info("")

    pipeline = TwoStageJudgmentPipeline()
    result = pipeline.execute(observation)

    # Save result
    result_file = "two_stage_result_fingers2.json"
    with open(result_file, 'w') as f:
        # Manually create dict to handle dataclass serialization
        result_dict = {
            "record_id": result.record_id,
            "timestamp": result.timestamp,
            "stage1_result": asdict(result.stage1_result),
            "stage2_result": asdict(result.stage2_result) if result.stage2_result else None,
            "final_state": result.final_state,
            "final_value": result.final_value,
            "pipeline_stopped_early": result.pipeline_stopped_early,
            "prior_intrusion_detected": result.prior_intrusion_detected,
        }
        json.dump(result_dict, f, indent=2)

    logger.info(f"✅ Result saved: {result_file}")
    logger.info("")

    # Display summary
    logger.info("=" * 80)
    logger.info("FINAL RESULT")
    logger.info("=" * 80)
    logger.info(f"Image: {Path(image_path).name}")
    logger.info(f"Observation ID: {observation.record_id}")
    logger.info(f"Detected Protrusions: {observation.estimated_protrusions}")
    logger.info("")
    logger.info(f"Stage 1 (phi3 Judge):")
    logger.info(f"  State: {result.stage1_result.state}")
    logger.info(f"  Value: {result.stage1_result.value}")
    logger.info(f"  Latency: {result.stage1_result.latency_s:.2f}s")
    logger.info("")

    if result.stage2_result:
        logger.info(f"Stage 2 (Mistral Narrator):")
        logger.info(f"  Prior Intrusion: {result.stage2_result.prior_intrusion_detected}")
        logger.info(f"  Latency: {result.stage2_result.latency_s:.2f}s")
    else:
        logger.info(f"Stage 2: Skipped (early termination)")

    logger.info("")
    logger.info(f"Final Decision: {result.final_state} = {result.final_value}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
