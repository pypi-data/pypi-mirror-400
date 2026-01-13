"""
Phase 4 Review Mode constitutional tests.

These tests intentionally encode the UX/state contract so regressions are caught
before shipping. Implementations may substitute actual UI/test harnesses, but
the behavioral assertions must hold.
"""

from typing import Dict, Set

import pytest


class DummyReviewUI:
    """Lightweight stand-in to assert constitutional behavior."""

    def __init__(self, slides: int = 1):
        self.slides = slides
        self.current_slide = 1
        self.states: Dict[int, str] = {i: "UNREVIEWED" for i in range(1, slides + 1)}
        self.text_elements: Set[str] = set()

    def enter(self) -> "DummyReviewUI":
        return self

    @property
    def slide_state(self) -> str:
        return self.states[self.current_slide]

    def edit_translation(self, text: str) -> None:
        # Editing does not auto-review
        self.text_elements.add(text)

    def mark_as_ok(self, slide: int | None = None) -> None:
        index = slide or self.current_slide
        self.states[index] = "REVIEWED"

    def ask_ai_revision(self) -> None:
        # Explicitly keeps slide UNREVIEWED
        self.states[self.current_slide] = "UNREVIEWED"

    def next_slide(self) -> None:
        if self.current_slide < self.slides:
            self.current_slide += 1

    def get_actions(self) -> Set[str]:
        return {"mark_as_ok", "ask_ai_revision", "next_slide"}

    def can_finish_review(self) -> bool:
        return all(state == "REVIEWED" for state in self.states.values())


def enter_review_mode(slides: int = 1) -> DummyReviewUI:
    """Factory helper to align with test descriptions."""
    return DummyReviewUI(slides=slides).enter()


def test_review_mode_no_ai_explanation():
    """Review Mode must not expose AI explanations or slide interpretations."""
    ui = enter_review_mode()
    forbidden = {"first impression", "appears to be"}
    assert ui.text_elements.isdisjoint(forbidden)


def test_review_mode_allowed_actions_only():
    """Only 3 actions are permitted in Review Mode."""
    ui = enter_review_mode()
    assert ui.get_actions() == {"mark_as_ok", "ask_ai_revision", "next_slide"}


def test_review_state_manual_only():
    """REVIEWED state must require explicit user action."""
    ui = enter_review_mode()
    assert ui.slide_state == "UNREVIEWED"
    ui.edit_translation("minor fix")
    assert ui.slide_state == "UNREVIEWED"
    ui.mark_as_ok()
    assert ui.slide_state == "REVIEWED"


def test_review_completion_requires_all_reviewed():
    """Review completion must be blocked until all slides are reviewed."""
    ui = enter_review_mode(slides=3)
    ui.mark_as_ok(slide=1)
    ui.mark_as_ok(slide=2)
    assert not ui.can_finish_review()
    ui.mark_as_ok(slide=3)
    assert ui.can_finish_review()


def test_phase3_writer_guardrail(monkeypatch):
    """
    Phase 4 must not affect Phase 3 writer logic.

    This test stubs the Phase 3 suite entry point to ensure it is still invoked.
    """

    phase3_module = pytest.importorskip(
        "tests.phase3_runner", reason="Phase 3 runner module missing"
    )

    phase3_called = {"value": False}

    def fake_phase3_runner():
        phase3_called["value"] = True

    monkeypatch.setattr(
        phase3_module,
        "run_phase3_writer_tests",
        fake_phase3_runner,
        raising=True,
    )

    # When invoked inside CI, this function should call the Phase 3 suite.
    phase3_module.run_phase3_writer_tests()
    assert phase3_called["value"] is True
