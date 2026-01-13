#!/usr/bin/env python3
"""
Production Router with Hardening (Phase 10)
============================================
Adds rate limiting and circuit breaker to production router.

Rate Limits:
- Per-client: 60 rpm
- Global: 5,000 rpm

Circuit Breaker:
- Window: 5 seconds
- Error rate threshold: 8%
- Action: Force Tiny→Full fallback
"""

import time
from collections import defaultdict, deque
from typing import Dict, Any


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate_per_minute: int):
        self.rate = rate_per_minute
        self.tokens = defaultdict(lambda: rate_per_minute)
        self.last_refill = defaultdict(lambda: time.time())

    def allow(self, client_id: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        last = self.last_refill[client_id]

        # Refill tokens
        elapsed = now - last
        if elapsed > 60:
            self.tokens[client_id] = self.rate
            self.last_refill[client_id] = now

        # Check tokens
        if self.tokens[client_id] > 0:
            self.tokens[client_id] -= 1
            return True

        return False


class CircuitBreaker:
    """Circuit breaker for error rate monitoring."""

    def __init__(self, window_seconds: int = 5, error_threshold: float = 0.08):
        self.window_seconds = window_seconds
        self.error_threshold = error_threshold
        self.requests = deque()
        self.state = "closed"  # closed, open, half-open

    def record_request(self, success: bool):
        """Record request result."""
        now = time.time()
        self.requests.append((now, success))

        # Remove old requests outside window
        cutoff = now - self.window_seconds
        while self.requests and self.requests[0][0] < cutoff:
            self.requests.popleft()

        # Check error rate
        if len(self.requests) >= 10:
            errors = sum(1 for _, success in self.requests if not success)
            error_rate = errors / len(self.requests)

            if error_rate > self.error_threshold:
                self.state = "open"
            else:
                self.state = "closed"

    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self.state == "open"


class ProductionRouterHardened:
    """
    Production router with rate limiting and circuit breaker.
    """

    def __init__(self, enable_tiny: bool = False):
        self.enable_tiny = enable_tiny

        # Rate limiters
        self.client_limiter = RateLimiter(60)  # 60 rpm per client
        self.global_limiter = RateLimiter(5000)  # 5k rpm global

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(window_seconds=5, error_threshold=0.08)

        # Stats
        self.stats = {
            "total_requests": 0,
            "rate_limited": 0,
            "circuit_open": 0,
            "tiny_used": 0,
            "full_used": 0
        }

    def route(self, input_text: str, signature: str = "Heo", client_id: str = "default") -> Dict[str, Any]:
        """
        Route request with rate limiting and circuit breaker.
        """
        self.stats["total_requests"] += 1

        # Check global rate limit
        if not self.global_limiter.allow("global"):
            self.stats["rate_limited"] += 1
            return {
                "error": "Global rate limit exceeded (5,000 rpm)",
                "status": 429,
                "source": "RateLimiter"
            }

        # Check client rate limit
        if not self.client_limiter.allow(client_id):
            self.stats["rate_limited"] += 1
            return {
                "error": f"Client rate limit exceeded (60 rpm)",
                "status": 429,
                "client_id": client_id,
                "source": "RateLimiter"
            }

        # Check circuit breaker
        if self.circuit_breaker.is_open():
            self.stats["circuit_open"] += 1
            # Force FullEcho when circuit is open
            return self._use_full_echo(input_text, signature, "Circuit breaker open (error rate > 8%)")

        # Try routing logic
        try:
            if self.enable_tiny:
                # Attempt TinyEcho (placeholder - would call actual TinyEcho)
                result = self._try_tiny_echo(input_text, signature)
                success = "error" not in result
                self.circuit_breaker.record_request(success)

                if success:
                    self.stats["tiny_used"] += 1
                    return result
                else:
                    # Fallback to FullEcho
                    return self._use_full_echo(input_text, signature, "TinyEcho error")
            else:
                # Use FullEcho directly
                result = self._use_full_echo(input_text, signature, "TinyEcho disabled")
                self.circuit_breaker.record_request(True)
                return result

        except Exception as e:
            self.circuit_breaker.record_request(False)
            return {
                "error": str(e),
                "source": "RouterException"
            }

    def _try_tiny_echo(self, input_text: str, signature: str) -> Dict[str, Any]:
        """Try TinyEcho (placeholder)."""
        # Placeholder - would call actual TinyEcho runtime
        return {
            "judgment": f"[{signature}] {input_text[:50]}",
            "confidence": 0.87,
            "source": "TinyEcho",
            "latency_ms": 180
        }

    def _use_full_echo(self, input_text: str, signature: str, reason: str) -> Dict[str, Any]:
        """Use FullEcho (safe fallback)."""
        self.stats["full_used"] += 1

        # Placeholder - would call actual FullEcho
        return {
            "judgment": f"[{signature}] Full judgment: {input_text[:100]}",
            "confidence": 0.92,
            "source": "FullEcho",
            "route_reason": reason,
            "latency_ms": 2400
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            **self.stats,
            "circuit_state": self.circuit_breaker.state,
            "rate_limit_efficiency": 1 - (self.stats["rate_limited"] / max(1, self.stats["total_requests"]))
        }


def main():
    """Test hardened router."""
    print("🛡️  Production Router with Hardening\n")

    router = ProductionRouterHardened(enable_tiny=False)

    # Test normal requests
    for i in range(10):
        result = router.route(f"Test input {i}", "Heo", client_id="client1")
        print(f"[{i+1}] Source: {result.get('source', 'N/A')}, Status: {result.get('status', 200)}")

    # Test rate limiting
    print("\n🚦 Testing rate limiting (70 requests from same client)...")
    limited_count = 0
    for i in range(70):
        result = router.route(f"Burst {i}", "Heo", client_id="client2")
        if result.get("status") == 429:
            limited_count += 1

    print(f"   Rate limited: {limited_count}/70 requests")

    # Print stats
    stats = router.get_stats()
    print(f"\n📊 Router Statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Rate limited: {stats['rate_limited']}")
    print(f"   Circuit state: {stats['circuit_state']}")
    print(f"   Tiny used: {stats['tiny_used']}")
    print(f"   Full used: {stats['full_used']}")

    print("\n✅ Hardened router test complete")


if __name__ == "__main__":
    main()
