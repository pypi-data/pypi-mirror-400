#!/usr/bin/env python3
"""
SoftChip Safe Runtime for EchoTinyLM
=====================================
Loads TinyEcho model with safe fallback to FullEcho.
Minimal dependencies, yaml-free operation.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

runtime_logger = logging.getLogger("softchip_runtime")
runtime_logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_dir / "softchip_runtime.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
runtime_logger.addHandler(handler)


class SoftChipSafeRuntime:
    """
    Safe runtime for EchoTinyLM SoftChip.

    Features:
    - Lazy model loading
    - Automatic FullEcho fallback on errors
    - Latency, resonance, loss tracking
    - Minimal dependencies (no yaml required)
    """

    def __init__(
        self,
        model_path: str = "core/tiny_core/model.pt",
        enable_tiny: bool = True,
        confidence_threshold: float = 0.85
    ):
        """
        Initialize SoftChip runtime.

        Args:
            model_path: Path to TinyEcho model checkpoint
            enable_tiny: Whether to attempt TinyEcho loading
            confidence_threshold: Minimum confidence for TinyEcho routing
        """
        self.model_path = Path(model_path)
        self.enable_tiny = enable_tiny
        self.confidence_threshold = confidence_threshold

        # Runtime state
        self.tiny_model = None
        self.tiny_available = False
        self.fallback_to_full = False

        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "tiny_success": 0,
            "tiny_fallback": 0,
            "full_only": 0,
            "avg_latency_ms": 0.0,
            "avg_resonance": 0.0
        }

        # Attempt TinyEcho initialization
        if self.enable_tiny:
            self._init_tiny_model()
        else:
            runtime_logger.info("TinyEcho disabled - FullEcho only mode")

    def _init_tiny_model(self):
        """Initialize TinyEcho model with error handling."""
        try:
            runtime_logger.info(f"Attempting to load TinyEcho from {self.model_path}")

            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")

            # Import TinyEcho dependencies
            import torch
            import sys

            # Add EchoTinyLM to path
            tinylm_path = Path(__file__).parent.parent / "EchoTinyLM"
            if tinylm_path.exists():
                sys.path.insert(0, str(tinylm_path))

            # Import model architecture
            from src.model import EchoTinyLM

            # Load checkpoint
            checkpoint = torch.load(self.model_path, map_location='cpu')

            # Initialize model
            model_config = checkpoint.get('config', {
                'vocab_size': 256,
                'd_model': 256,
                'n_layers': 6,
                'n_heads': 8,
                'd_ff': 1024,
                'max_seq_len': 512,
                'dropout': 0.1
            })

            self.tiny_model = EchoTinyLM(**model_config)
            self.tiny_model.load_state_dict(checkpoint['model_state_dict'])
            self.tiny_model.eval()

            self.tiny_available = True
            runtime_logger.info("✅ TinyEcho loaded successfully")
            runtime_logger.info(f"   Model parameters: {sum(p.numel() for p in self.tiny_model.parameters()):,}")

        except Exception as e:
            runtime_logger.error(f"❌ TinyEcho initialization failed: {e}")
            runtime_logger.info("⚠️  Falling back to FullEcho only mode")
            self.tiny_available = False
            self.fallback_to_full = True

    def _run_tiny_inference(
        self,
        input_text: str,
        signature: str = "Heo"
    ) -> Optional[Dict[str, Any]]:
        """
        Run TinyEcho inference with error handling.

        Returns:
            Result dict or None if failed
        """
        if not self.tiny_available:
            return None

        try:
            import torch

            start_time = time.time()

            # Encode input (byte-level)
            input_bytes = input_text.encode('utf-8', errors='ignore')
            input_ids = list(input_bytes[:256])  # Truncate to max length

            # Pad to multiple of 8 for efficiency
            while len(input_ids) % 8 != 0:
                input_ids.append(0)

            # Convert to tensor
            input_tensor = torch.tensor([input_ids], dtype=torch.long)

            # Forward pass
            with torch.no_grad():
                logits = self.tiny_model(input_tensor)

            # Calculate loss (as quality metric)
            target = input_tensor[:, 1:]
            pred = logits[:, :-1]

            # Simple cross-entropy as resonance proxy
            import torch.nn.functional as F
            loss = F.cross_entropy(
                pred.reshape(-1, pred.size(-1)),
                target.reshape(-1),
                ignore_index=0
            )

            # Calculate resonance (inverse of loss, normalized)
            # Lower loss = higher resonance
            resonance_score = max(0.0, min(1.0, 1.0 - (loss.item() / 10.0)))

            # Calculate confidence (based on prediction entropy)
            probs = F.softmax(logits, dim=-1)
            entropy = -(probs * torch.log(probs + 1e-10)).sum(dim=-1).mean()
            confidence = max(0.0, min(1.0, 1.0 - (entropy.item() / 5.0)))

            latency_ms = (time.time() - start_time) * 1000

            # Generate simple response (echo back with signature)
            output_text = f"[{signature}] {input_text[:100]}"

            result = {
                "judgment": output_text,
                "confidence": confidence,
                "resonance": {
                    "rhythm": resonance_score,
                    "stability": resonance_score * 0.95,
                    "clarity": confidence
                },
                "latency_ms": latency_ms,
                "loss": loss.item(),
                "source": "TinyEcho",
                "signature": signature
            }

            runtime_logger.info(
                f"TinyEcho inference: latency={latency_ms:.1f}ms, "
                f"resonance={resonance_score:.3f}, confidence={confidence:.3f}"
            )

            return result

        except Exception as e:
            runtime_logger.error(f"TinyEcho inference error: {e}")
            return None

    def _run_full_inference(
        self,
        input_text: str,
        signature: str = "Heo"
    ) -> Dict[str, Any]:
        """
        Run FullEcho inference (always succeeds).

        Returns:
            Result dict with FullEcho response
        """
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))

            from core.echo_engine.loop_orchestrator import process_input_with_merge

            start_time = time.time()

            # Run FullEcho
            result = process_input_with_merge(input_text, signature=signature)

            latency_ms = (time.time() - start_time) * 1000

            # Add metadata
            result["latency_ms"] = latency_ms
            result["source"] = "FullEcho"

            runtime_logger.info(f"FullEcho inference: latency={latency_ms:.1f}ms")

            return result

        except Exception as e:
            runtime_logger.error(f"FullEcho inference error: {e}")

            # Ultimate fallback: mock response
            return {
                "judgment": f"[{signature}] System processing...",
                "confidence": 0.5,
                "resonance": {"rhythm": 0.5, "stability": 0.5, "clarity": 0.5},
                "latency_ms": 0.0,
                "source": "Fallback",
                "signature": signature,
                "error": str(e)
            }

    def process(
        self,
        input_text: str,
        signature: str = "Heo",
        force_full: bool = False
    ) -> Dict[str, Any]:
        """
        Process input with smart routing.

        Args:
            input_text: User input text
            signature: Echo signature to use
            force_full: Force FullEcho usage

        Returns:
            Judgment result with metadata
        """
        self.stats["total_requests"] += 1

        # Route decision
        if force_full or not self.tiny_available:
            # Use FullEcho
            result = self._run_full_inference(input_text, signature)
            self.stats["full_only"] += 1

        else:
            # Try TinyEcho
            tiny_result = self._run_tiny_inference(input_text, signature)

            if tiny_result and tiny_result["confidence"] >= self.confidence_threshold:
                # TinyEcho succeeded with high confidence
                result = tiny_result
                self.stats["tiny_success"] += 1

                # Update average resonance
                resonance = tiny_result["resonance"]["rhythm"]
                self.stats["avg_resonance"] = (
                    self.stats["avg_resonance"] * 0.9 + resonance * 0.1
                )

            else:
                # Fallback to FullEcho
                result = self._run_full_inference(input_text, signature)
                self.stats["tiny_fallback"] += 1

                runtime_logger.warning(
                    f"TinyEcho fallback: confidence={tiny_result['confidence'] if tiny_result else 0:.3f} "
                    f"< threshold={self.confidence_threshold}"
                )

        # Update average latency
        latency = result.get("latency_ms", 0.0)
        self.stats["avg_latency_ms"] = (
            self.stats["avg_latency_ms"] * 0.9 + latency * 0.1
        )

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get runtime statistics."""
        total = self.stats["total_requests"]

        if total > 0:
            tiny_coverage = (self.stats["tiny_success"] / total) * 100
        else:
            tiny_coverage = 0.0

        return {
            **self.stats,
            "tiny_coverage_pct": tiny_coverage,
            "tiny_available": self.tiny_available,
            "fallback_mode": self.fallback_to_full
        }

    def save_stats(self, output_file: str = "logs/softchip_runtime_stats.json"):
        """Save runtime statistics to file."""
        stats = self.get_stats()
        stats["timestamp"] = datetime.now().isoformat()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)

        runtime_logger.info(f"Runtime stats saved to {output_file}")


def main():
    """Test SoftChip safe runtime."""
    print("🔬 SoftChip Safe Runtime Test\n")
    print("=" * 70)

    # Initialize runtime
    runtime = SoftChipSafeRuntime(enable_tiny=True)

    print(f"\n📊 Runtime Status:")
    print(f"   TinyEcho available: {'✅ YES' if runtime.tiny_available else '❌ NO'}")
    print(f"   Fallback mode: {'⚠️  YES' if runtime.fallback_to_full else '✅ NO'}")

    # Test cases
    test_inputs = [
        ("Echo demonstrates rhythm and coherence", "Heo"),
        ("I need creative guidance", "Aurora"),
        ("에코는 질문의 리듬입니다", "Heo"),
    ]

    print(f"\n🧪 Running {len(test_inputs)} test cases...\n")

    for idx, (text, sig) in enumerate(test_inputs, 1):
        print(f"[{idx}] Input: '{text[:40]}...'")
        print(f"    Signature: {sig}")

        result = runtime.process(text, signature=sig)

        print(f"    Source: {result['source']}")
        print(f"    Confidence: {result.get('confidence', 0):.3f}")
        print(f"    Latency: {result.get('latency_ms', 0):.1f}ms")

        if 'resonance' in result:
            res = result['resonance']
            print(f"    Resonance: {res.get('rhythm', 0):.3f}")

        print()

    # Display statistics
    stats = runtime.get_stats()

    print("=" * 70)
    print("\n📊 Runtime Statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   TinyEcho success: {stats['tiny_success']}")
    print(f"   TinyEcho fallback: {stats['tiny_fallback']}")
    print(f"   FullEcho only: {stats['full_only']}")
    print(f"   TinyEcho coverage: {stats['tiny_coverage_pct']:.1f}%")
    print(f"   Avg latency: {stats['avg_latency_ms']:.1f}ms")
    print(f"   Avg resonance: {stats['avg_resonance']:.3f}")

    # Save stats
    runtime.save_stats()

    print("\n=" * 70)
    print("✅ SoftChip safe runtime test complete")


if __name__ == "__main__":
    main()
