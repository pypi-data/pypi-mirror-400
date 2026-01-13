"""
Dexa runtime guard utilities.

Provides single-shot environment detection and install-command gating so Dexa never
attempts system modifications when running inside a sandbox. Detection happens once
per process (and is persisted to disk) to satisfy the "pre-execution only" rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import platform
from pathlib import Path
from typing import Optional, Sequence, Union

ENV_PATH = Path("dexa_runtime") / "env.json"
INSTALL_BLOCK_MESSAGE = "현재 환경: sandbox / 설치 불가 / 구조 분석만 가능"
_CACHED_INFO: Optional["DexaRuntimeInfo"] = None

_INSTALL_PHRASES = (
    "pip install",
    "pip3 install",
    "npm install",
    "python -m pip install",
)
_INSTALL_SINGLE_WORDS = ("mkdir", "unzip")


@dataclass
class DexaRuntimeInfo:
    """Represents detected runtime state."""

    mode: str
    detected_at: str
    source: str = "probe"

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "detected_at": self.detected_at,
            "source": self.source,
        }


class DexaSandboxInstallError(RuntimeError):
    """Raised when install-like commands are blocked in sandbox mode."""


def _load_cached_info() -> Optional[DexaRuntimeInfo]:
    global _CACHED_INFO
    if _CACHED_INFO is not None:
        return _CACHED_INFO
    if not ENV_PATH.exists():
        return None
    try:
        data = json.loads(ENV_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    mode = data.get("mode")
    if not mode:
        return None
    detected_at = data.get("detected_at") or datetime.now(timezone.utc).isoformat()
    info = DexaRuntimeInfo(mode=mode, detected_at=detected_at, source="persisted")
    _CACHED_INFO = info
    return info


def _persist_info(info: DexaRuntimeInfo) -> None:
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENV_PATH.write_text(json.dumps(info.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def _probe_runtime_mode() -> str:
    forced = os.getenv("DEXA_RUNTIME_MODE")
    if forced:
        return forced
    if os.getenv("WSL_DISTRO_NAME"):
        return "local_wsl"
    try:
        release = platform.release().lower()
        if "microsoft" in release or "wsl" in release:
            return "local_wsl"
    except Exception:
        pass
    try:
        with open("/proc/version", "r", encoding="utf-8") as handle:
            version = handle.read().lower()
            if "microsoft" in version or "wsl" in version:
                return "local_wsl"
    except Exception:
        pass
    return "sandbox"


def get_runtime_info() -> DexaRuntimeInfo:
    """
    Returns cached runtime info, probing only once (and persisting the result).
    """
    global _CACHED_INFO
    info = _load_cached_info()
    if info is not None:
        return info
    detected = DexaRuntimeInfo(
        mode=_probe_runtime_mode(),
        detected_at=datetime.now(timezone.utc).isoformat(),
        source="probe",
    )
    _CACHED_INFO = detected
    _persist_info(detected)
    return detected


def get_runtime_mode() -> str:
    """Convenience wrapper returning the runtime mode string."""
    return get_runtime_info().mode


def is_sandbox_mode() -> bool:
    """True when Dexa is in sandbox-only runtime."""
    return get_runtime_mode() != "local_wsl"


def _command_to_text(command: Union[str, Sequence[str]]) -> str:
    if isinstance(command, str):
        return command.lower()
    return " ".join(str(part) for part in command).lower()


def is_install_command(command: Union[str, Sequence[str]]) -> bool:
    """
    Returns True if the command string/list contains install-like directives.
    """
    text = _command_to_text(command)
    if any(phrase in text for phrase in _INSTALL_PHRASES):
        return True
    tokens = text.replace("\t", " ").split()
    return any(token in _INSTALL_SINGLE_WORDS for token in tokens)


def sandbox_block_message(command: Optional[Union[str, Sequence[str]]] = None) -> str:
    """Builds the standardized sandbox block message with optional command context."""
    if not command:
        return INSTALL_BLOCK_MESSAGE
    cmd_text = _command_to_text(command).strip()
    if not cmd_text:
        return INSTALL_BLOCK_MESSAGE
    return f"{INSTALL_BLOCK_MESSAGE} :: {cmd_text}"


def enforce_install_policy(command: Union[str, Sequence[str]]) -> Optional[str]:
    """
    Returns a block message if the command is install-like and sandboxed; otherwise None.
    """
    if not is_install_command(command):
        return None
    if is_sandbox_mode():
        return sandbox_block_message(command)
    return None


def ensure_install_allowed(command: Union[str, Sequence[str], None] = None) -> None:
    """
    Raises DexaSandboxInstallError if the command is install-like in sandbox mode.

    command may be None (treated as generic install intent) or a command sequence/string.
    """
    if command is None:
        command = "install"
    message = enforce_install_policy(command)
    if message:
        raise DexaSandboxInstallError(message)


def sandbox_monad_response(command: Union[str, Sequence[str], None] = None) -> dict:
    """
    Structured payload describing the sandbox restriction. Helpful for CLI responses.
    """
    return {
        "success": False,
        "environment": get_runtime_mode(),
        "blocked": True,
        "message": sandbox_block_message(command),
    }


def set_runtime_mode(mode: str, source: str = "manual") -> DexaRuntimeInfo:
    """
    Manually override the runtime mode and persist it for subsequent detections.
    """
    global _CACHED_INFO
    info = DexaRuntimeInfo(
        mode=mode,
        detected_at=datetime.now(timezone.utc).isoformat(),
        source=source,
    )
    _CACHED_INFO = info
    _persist_info(info)
    return info
