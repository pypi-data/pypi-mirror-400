"""Responsibility guardrails to keep decision authority human-owned."""

from __future__ import annotations

import logging
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence

logger = logging.getLogger("echo_engine.responsibility_guard")

FORBIDDEN_DECISION_FIELDS = {"final_decision", "approve", "sign_off", "commit_decision"}
HANDOFF_ENV_KEY = "ECHO_HUMAN_HANDOFF_TOKEN"


class HumanHandoffMissingError(RuntimeError):
    """Raised when a human handoff token is missing."""


class ForbiddenAIResponsibilityError(RuntimeError):
    """Raised when the AI attempts to emit a forbidden responsibility marker."""


def resolve_human_handoff_token(
    provided_token: Optional[str], context: str
) -> str:
    """Resolve and validate a human handoff token for the given context."""
    token = (provided_token or os.getenv(HANDOFF_ENV_KEY) or "").strip()
    if not token:
        logger.error(
            "AI_RESPONSIBILITY_BLOCKED: missing human handoff token",
            extra={"context": context},
        )
        raise HumanHandoffMissingError(
            f"Human handoff token required for {context}. "
            f"Set {HANDOFF_ENV_KEY} or supply human_handoff_token explicitly."
        )
    return token


def ensure_no_forbidden_decision_fields(payload: Any, context: str) -> None:
    """
    Raise if payload contains forbidden decision/approval fields.

    Traverses mappings, dataclasses, and iterables (depth-first) to make sure
    no AI-generated structure attempts to sneak in responsibility fields.
    """
    if payload is None:
        return

    if is_dataclass(payload):
        ensure_no_forbidden_decision_fields(asdict(payload), context)
        return

    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if isinstance(key, str) and key.lower() in FORBIDDEN_DECISION_FIELDS:
                _raise_forbidden(context, key)
            ensure_no_forbidden_decision_fields(value, context)
        return

    if isinstance(payload, (list, tuple, set)):
        for item in payload:
            ensure_no_forbidden_decision_fields(item, context)
        return

    # Strings or scalars are ignored—they are only problematic when used as keys.


def _raise_forbidden(context: str, key: str) -> None:
    logger.error(
        "AI_RESPONSIBILITY_BLOCKED: forbidden decision field detected",
        extra={"context": context, "field": key},
    )
    raise ForbiddenAIResponsibilityError(
        f"Field '{key}' is not allowed in AI-generated payload ({context})."
    )


__all__ = [
    "ForbiddenAIResponsibilityError",
    "FORBIDDEN_DECISION_FIELDS",
    "HANDOFF_ENV_KEY",
    "HumanHandoffMissingError",
    "ensure_no_forbidden_decision_fields",
    "resolve_human_handoff_token",
]
