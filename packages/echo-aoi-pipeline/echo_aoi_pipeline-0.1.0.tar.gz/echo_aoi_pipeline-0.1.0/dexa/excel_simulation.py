"""
Dexa helper to generate SimulationIntent payloads and invoke the Excel MC runner.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from echo_engine.excel_ai.simulation_wiring import (
    SimulationIntentPayload,
    run_simulation_from_dict,
    build_context_snippet,
)


def build_intent(
    goal: str,
    file_path: Path,
    *,
    sheet: Optional[str] = None,
    target_range: Optional[str] = None,
    user_style: str = "human_like",
    mode: str = "excel_mc",
) -> Dict[str, Any]:
    payload = SimulationIntentPayload(
        mode=mode,
        goal=goal,
        file_path=file_path,
        sheet=sheet,
        target_range=target_range,
        user_style=user_style,
    )
    return payload.to_dict()


def run_excel_mc_session(intent_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Excel MC and return both the raw simulation output and an LLM-ready snippet.
    """
    simulation = run_simulation_from_dict(intent_payload)
    snippet = build_context_snippet(simulation)
    return {
        "intent": intent_payload,
        "simulation": simulation,
        "llm_context": snippet,
    }
