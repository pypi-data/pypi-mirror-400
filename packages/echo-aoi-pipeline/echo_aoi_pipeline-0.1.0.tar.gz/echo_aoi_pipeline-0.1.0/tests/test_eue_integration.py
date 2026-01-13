#!/usr/bin/env python3
"""
EUE v1.0 Integration Test

Tests all EUE subsystems to ensure proper integration.
"""

import asyncio
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    """Restrict AnyIO backend to asyncio for this module."""
    return "asyncio"


# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ops.eue import get_eue, EUEConfig, EUEMode

LOCAL_BROWSERS = ["chromium", "firefox"]
REMOTE_ENDPOINT = "ws://mock-playwright"


class DummyVideo:
    async def path(self):
        return "/tmp/mock-video.webm"


class DummyMouse:
    async def move(self, *_args, **_kwargs):
        return None


class DummyKeyboard:
    async def press(self, *_args, **_kwargs):
        return None


class DummyPage:
    def __init__(self):
        self.video = DummyVideo()
        self.mouse = DummyMouse()
        self.keyboard = DummyKeyboard()

    async def goto(self, *_args, **_kwargs):
        return None

    async def add_init_script(self, *_args, **_kwargs):
        return None

    async def evaluate(self, *_args, **_kwargs):
        return None

    async def screenshot(self, *_, **__):
        return "/tmp/mock.png"


class DummyContext:
    async def new_page(self):
        return DummyPage()

    async def close(self):
        return None


class DummyBrowser:
    async def new_context(self, *_, **__):
        return DummyContext()

    async def close(self):
        return None


class DummyBrowserType:
    async def launch(self, *_args, **_kwargs):
        return DummyBrowser()

    async def connect_over_cdp(self, *_args, **_kwargs):
        return DummyBrowser()


class DummyPlaywright:
    def __init__(self):
        self.chromium = DummyBrowserType()
        self.firefox = DummyBrowserType()
        self.webkit = DummyBrowserType()

    async def stop(self):
        return None

    async def close(self):
        return None

    async def connect_over_ws(self, *_args, **_kwargs):
        return self


class DummyAsyncPlaywrightManager:
    async def start(self):
        return DummyPlaywright()

    async def connect_over_ws(self, *_args, **_kwargs):
        return DummyPlaywright()


def mock_async_playwright():
    return DummyAsyncPlaywrightManager()


class SimpleMonkeyPatch:
    """Fallback monkeypatch for standalone execution."""

    def setattr(self, target: str, value):
        module_name, attr = target.rsplit(".", 1)
        module = __import__(module_name, fromlist=[attr])
        setattr(module, attr, value)


async def test_health_check():
    """Test health check subsystem."""
    print("\n🏥 Testing Health Check...")

    for browser in LOCAL_BROWSERS:
        config = EUEConfig(mode=EUEMode.VERIFY, browser=browser)
        eue = get_eue(config)

        try:
            result = await eue.health_check()
            assert result.success, f"Health check should succeed for {browser}"
            assert result.subsystem == "health"
            print(f"  ✅ Health check passed ({browser})")
        except Exception as e:
            print(f"  ❌ Health check failed for {browser}: {e}")
            raise
        finally:
            await eue.cleanup()
    return True


async def test_reset():
    """Test reset subsystem."""
    print("\n🔄 Testing Reset...")

    for browser in LOCAL_BROWSERS:
        config = EUEConfig(mode=EUEMode.DIRECT, browser=browser)
        eue = get_eue(config)

        try:
            result = await eue.reset()
            assert result.success, f"Reset should succeed for {browser}"
            assert result.subsystem == "reset"
            print(f"  ✅ Reset passed ({browser})")
        except Exception as e:
            print(f"  ❌ Reset failed for {browser}: {e}")
            raise
        finally:
            await eue.cleanup()
    return True


async def test_mock():
    """Test mock subsystem."""
    print("\n🎭 Testing Mock...")

    for browser in LOCAL_BROWSERS:
        config = EUEConfig(mode=EUEMode.DIRECT, browser=browser)
        eue = get_eue(config)

        try:
            result = await eue.load_mock()
            assert result.success, f"Mock loading should succeed for {browser}"
            assert result.subsystem == "mock"
            print(f"  ✅ Mock passed ({browser})")
        except Exception as e:
            print(f"  ❌ Mock failed for {browser}: {e}")
            raise
        finally:
            await eue.cleanup()
    return True


async def test_config():
    """Test configuration."""
    print("\n⚙️  Testing Configuration...")

    for browser in LOCAL_BROWSERS:
        config = EUEConfig(
            scenario="test_scenario",
            mode=EUEMode.SELF_HEAL,
            enable_cursor=True,
            enable_timecapsule=True,
            max_attempts=5,
            browser=browser,
        )

        eue = get_eue(config)

        try:
            assert eue.config.scenario == "test_scenario"
            assert eue.config.mode == EUEMode.SELF_HEAL
            assert eue.config.enable_cursor is True
            assert eue.config.enable_timecapsule is True
            assert eue.config.max_attempts == 5
            assert eue.config.browser == browser

            print(f"  ✅ Configuration passed ({browser})")
            print(f"  Scenario: {eue.config.scenario}")
            print(f"  Mode: {eue.config.mode.value}")
            print(f"  Max Attempts: {eue.config.max_attempts}")
        except Exception as e:
            print(f"  ❌ Configuration failed for {browser}: {e}")
            raise
        finally:
            await eue.cleanup()
    return True


async def test_remote_health(monkeypatch):
    """Ensure remote execution path initializes via mocked endpoint."""
    print("\n🌐 Testing Remote Health...")
    monkeypatch.setattr("ops.mcp.playwright.mcp_bridge.async_playwright", mock_async_playwright)

    config = EUEConfig(
        mode=EUEMode.VERIFY,
        browser="chromium",
        location="remote",
        endpoint=REMOTE_ENDPOINT,
    )
    eue = get_eue(config)

    try:
        result = await eue.health_check()
        assert result.success, "Remote health should succeed"
        assert result.data["location"] == "remote"
        assert result.data["endpoint"] == REMOTE_ENDPOINT
        print("  ✅ Remote health passed (mock endpoint)")
    except Exception as e:
        print(f"  ❌ Remote health failed: {e}")
        raise
    finally:
        await eue.cleanup()
    return True


async def test_remote_validation():
    """Ensure remote without endpoint fails with clear error."""
    print("\n🚫 Testing Remote Validation...")

    # Test 1: Remote without endpoint should fail at config creation
    try:
        config = EUEConfig(
            mode=EUEMode.VERIFY,
            browser="chromium",
            location="remote",
            endpoint=None,  # Missing endpoint
        )
        print("  ❌ Should have raised ValueError for missing endpoint")
        return False
    except ValueError as e:
        assert "endpoint" in str(e).lower(), "Error message should mention endpoint"
        print(f"  ✅ Correctly rejected remote without endpoint: {e}")

    # Test 2: Verify browser/location/endpoint lockstep in results
    for browser in LOCAL_BROWSERS:
        config = EUEConfig(
            mode=EUEMode.DIRECT,
            browser=browser,
            location="local",
        )
        eue = get_eue(config)

        try:
            result = await eue.reset()
            assert result.data["browser"] == browser, f"Browser mismatch in result"
            assert result.data["location"] == "local", f"Location mismatch in result"
            print(f"  ✅ Browser/location/endpoint lockstep verified ({browser})")
        except Exception as e:
            print(f"  ❌ Lockstep validation failed for {browser}: {e}")
            raise
        finally:
            await eue.cleanup()

    return True


async def main():
    """Run all integration tests."""
    print("=" * 80)
    print("EUE v1.0 Integration Tests")
    print("=" * 80)

    results = []

    # Run tests
    results.append(await test_health_check())
    results.append(await test_reset())
    results.append(await test_mock())
    results.append(await test_config())
    results.append(await test_remote_validation())
    results.append(await test_remote_health(SimpleMonkeyPatch()))

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total:  {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
