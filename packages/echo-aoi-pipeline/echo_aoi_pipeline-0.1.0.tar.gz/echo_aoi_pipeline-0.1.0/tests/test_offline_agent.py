"""
Unit tests for Offline Agent.

Tests decision logic WITHOUT requiring Playwright.
Uses mock PageSnapshots to test pure judgment logic.
"""

import pytest
from ops.eue.offline_agent import (
    Goal,
    Playbook,
    PageSnapshot,
    PageType,
    Action,
    DOMStateAnalyzer,
    RuleBasedDecisionMaker,
    FailureRecoveryEngine,
    OfflineAgent,
)


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def simple_goal():
    """Simple test goal."""
    return Goal(
        name="test_login",
        start_url="https://test.com/login",
        targets=["Login", "Dashboard"],
        success_conditions=["url:dashboard"]
    )


@pytest.fixture
def simple_playbook():
    """Simple test playbook."""
    return Playbook(
        name="test_playbook",
        credentials={"username": "testuser", "password": "testpass"},
        selectors={
            "username_input": "#username",
            "password_input": "#password",
            "login_button": "#login-btn"
        },
        fallback_urls={
            "Dashboard": "https://test.com/dashboard"
        }
    )


@pytest.fixture
def login_page_snapshot():
    """Mock login page snapshot."""
    return PageSnapshot(
        url="https://test.com/login",
        title="Login Page",
        page_type=PageType.LOGIN,
        page_text="Please login with your credentials",
        inputs={
            "username": "#username",
            "password": "#password"
        },
        buttons={
            "Login": "#login-btn"
        },
        all_elements=["#username", "#password", "#login-btn"]
    )


@pytest.fixture
def dashboard_page_snapshot():
    """Mock dashboard page snapshot."""
    return PageSnapshot(
        url="https://test.com/dashboard",
        title="Dashboard",
        page_type=PageType.DASHBOARD,
        page_text="Welcome to Dashboard",
        links={
            "Inventory": "/inventory",
            "Reports": "/reports",
            "Settings": "/settings"
        },
        all_elements=[],
    )


@pytest.fixture
def error_page_snapshot():
    """Mock error page snapshot."""
    return PageSnapshot(
        url="https://test.com/error",
        title="Error",
        page_type=PageType.ERROR,
        page_text="An error occurred",
        errors=["Invalid credentials"],
        all_elements=[]
    )


# ============================================================================
# Goal Tests
# ============================================================================

def test_goal_is_achieved_url_condition():
    """Test goal achievement detection by URL."""
    goal = Goal(
        name="test",
        start_url="https://test.com",
        targets=[],
        success_conditions=["url:dashboard"]
    )

    # Not achieved
    snapshot = PageSnapshot(
        url="https://test.com/login",
        title="Login",
        page_type=PageType.LOGIN
    )
    assert not goal.is_achieved(snapshot)

    # Achieved
    snapshot = PageSnapshot(
        url="https://test.com/dashboard",
        title="Dashboard",
        page_type=PageType.DASHBOARD
    )
    assert goal.is_achieved(snapshot)


def test_goal_is_achieved_element_condition():
    """Test goal achievement detection by element."""
    goal = Goal(
        name="test",
        start_url="https://test.com",
        targets=[],
        success_conditions=["element:#success-message"]
    )

    # Not achieved
    snapshot = PageSnapshot(
        url="https://test.com",
        title="Page",
        page_type=PageType.UNKNOWN,
        all_elements=["#other-element"]
    )
    assert not goal.is_achieved(snapshot)

    # Achieved
    snapshot = PageSnapshot(
        url="https://test.com",
        title="Page",
        page_type=PageType.SUCCESS,
        all_elements=["#success-message"]
    )
    assert goal.is_achieved(snapshot)


def test_goal_get_next_target():
    """Test getting next uncompleted target."""
    goal = Goal(
        name="test",
        start_url="https://test.com",
        targets=["Login", "Dashboard", "Inventory"]
    )

    assert goal.get_next_target([]) == "Login"
    assert goal.get_next_target(["Login"]) == "Dashboard"
    assert goal.get_next_target(["Login", "Dashboard"]) == "Inventory"
    assert goal.get_next_target(["Login", "Dashboard", "Inventory"]) is None


# ============================================================================
# Playbook Tests
# ============================================================================

def test_playbook_has_credentials():
    """Test credential availability check."""
    # Has credentials
    playbook = Playbook(credentials={"username": "user", "password": "pass"})
    assert playbook.has_credentials()

    # Missing password
    playbook = Playbook(credentials={"username": "user"})
    assert not playbook.has_credentials()

    # Empty
    playbook = Playbook(credentials={})
    assert not playbook.has_credentials()


def test_playbook_get_credential():
    """Test getting credential values."""
    playbook = Playbook(credentials={"username": "testuser", "password": "testpass"})

    assert playbook.get_credential("username") == "testuser"
    assert playbook.get_credential("password") == "testpass"
    assert playbook.get_credential("nonexistent") == ""


# ============================================================================
# PageSnapshot Tests
# ============================================================================

def test_page_snapshot_has_element():
    """Test element existence check."""
    snapshot = PageSnapshot(
        url="https://test.com",
        title="Test",
        page_type=PageType.UNKNOWN,
        all_elements=["#element1", ".element2", "button.submit"]
    )

    assert snapshot.has_element("#element1")
    assert snapshot.has_element(".element2")
    assert not snapshot.has_element("#nonexistent")


def test_page_snapshot_find_button():
    """Test finding button by text pattern."""
    snapshot = PageSnapshot(
        url="https://test.com",
        title="Test",
        page_type=PageType.UNKNOWN,
        buttons={
            "Login": "#login-btn",
            "Sign Up": "#signup-btn",
            "Submit Form": "#submit-btn"
        }
    )

    assert snapshot.find_button("login") == "#login-btn"
    assert snapshot.find_button("LOGIN") == "#login-btn"  # Case-insensitive
    assert snapshot.find_button("sign") == "#signup-btn"
    assert snapshot.find_button("submit") == "#submit-btn"
    assert snapshot.find_button("nonexistent") is None


def test_page_snapshot_find_link():
    """Test finding link by text pattern."""
    snapshot = PageSnapshot(
        url="https://test.com",
        title="Test",
        page_type=PageType.UNKNOWN,
        links={
            "Dashboard": "/dashboard",
            "Inventory Management": "/inventory",
            "User Settings": "/settings"
        }
    )

    assert snapshot.find_link("dashboard") == "/dashboard"
    assert snapshot.find_link("inventory") == "/inventory"
    assert snapshot.find_link("INVENTORY") == "/inventory"  # Case-insensitive
    assert snapshot.find_link("user") == "/settings"
    assert snapshot.find_link("nonexistent") is None


# ============================================================================
# RuleBasedDecisionMaker Tests
# ============================================================================

def test_decision_maker_login_page_fill_username(simple_goal, simple_playbook, login_page_snapshot):
    """Test decision on login page - should fill username."""
    decider = RuleBasedDecisionMaker()

    action = decider.decide(simple_goal, simple_playbook, login_page_snapshot, [login_page_snapshot])

    # Should decide to fill username or password (order may vary)
    assert action.kind == "fill"
    assert action.target in ["#username", "#password"]
    assert action.payload in ["testuser", "testpass"]


def test_decision_maker_login_page_no_credentials(simple_goal, login_page_snapshot):
    """Test decision on login page without credentials."""
    playbook = Playbook()  # No credentials
    decider = RuleBasedDecisionMaker()

    action = decider.decide(simple_goal, playbook, login_page_snapshot, [login_page_snapshot])

    assert action.kind == "abort"
    assert "credentials" in action.reason.lower()


def test_decision_maker_error_page_abort(simple_goal, simple_playbook, error_page_snapshot):
    """Test decision on error page - should abort."""
    decider = RuleBasedDecisionMaker()

    action = decider.decide(simple_goal, simple_playbook, error_page_snapshot, [error_page_snapshot])

    # Should try fallback or abort
    assert action.kind in ["abort", "navigate"]


def test_decision_maker_dashboard_page_navigate(simple_goal, simple_playbook, dashboard_page_snapshot):
    """Test decision on dashboard page - should navigate to next target."""
    decider = RuleBasedDecisionMaker()

    action = decider.decide(simple_goal, simple_playbook, dashboard_page_snapshot, [dashboard_page_snapshot])

    # Could be navigate/click (if targets remain) or complete (if goal achieved)
    # Dashboard URL matches success_conditions, so it's correctly completing
    assert action.kind in ["navigate", "click", "complete"]


def test_decision_maker_goal_achieved(simple_goal, simple_playbook):
    """Test decision when goal is achieved."""
    decider = RuleBasedDecisionMaker()

    # Create snapshot that meets success condition
    snapshot = PageSnapshot(
        url="https://test.com/dashboard",
        title="Dashboard",
        page_type=PageType.DASHBOARD,
        all_elements=[]
    )

    action = decider.decide(simple_goal, simple_playbook, snapshot, [snapshot])

    # Should complete
    assert action.kind == "complete"


# ============================================================================
# FailureRecoveryEngine Tests
# ============================================================================

def test_recovery_engine_detect_stuck_same_url():
    """Test stuck state detection by same URL."""
    engine = FailureRecoveryEngine(max_stuck_count=5)

    # Create history with same URL
    history = [
        PageSnapshot(
            url="https://test.com/page",
            title="Page",
            page_type=PageType.UNKNOWN
        )
        for _ in range(5)
    ]

    assert engine.detect_stuck_state(history)


def test_recovery_engine_detect_stuck_same_error_page():
    """Test stuck state detection by repeated error pages."""
    engine = FailureRecoveryEngine(max_stuck_count=5)

    # Create history with same error page
    history = [
        PageSnapshot(
            url=f"https://test.com/page{i}",
            title="Error",
            page_type=PageType.ERROR
        )
        for i in range(5)
    ]

    assert engine.detect_stuck_state(history)


def test_recovery_engine_not_stuck_different_urls():
    """Test that different URLs don't trigger stuck detection."""
    engine = FailureRecoveryEngine(max_stuck_count=5)

    # Create history with different URLs AND different page types
    # (same page_type can still trigger stuck detection)
    page_types = [PageType.LOGIN, PageType.DASHBOARD, PageType.FORM, PageType.LIST, PageType.DASHBOARD]
    history = [
        PageSnapshot(
            url=f"https://test.com/page{i}",
            title="Page",
            page_type=page_types[i]
        )
        for i in range(5)
    ]

    assert not engine.detect_stuck_state(history)


def test_recovery_engine_should_retry():
    """Test action retry logic."""
    engine = FailureRecoveryEngine(max_retries_per_action=3)

    action = Action(kind="click", target="#button")

    # First 3 should succeed
    assert engine.should_retry(action)
    assert engine.should_retry(action)
    assert engine.should_retry(action)

    # 4th should fail
    assert not engine.should_retry(action)


def test_recovery_engine_get_recovery_action(simple_goal, simple_playbook):
    """Test recovery action generation."""
    engine = FailureRecoveryEngine()

    # Create stuck history
    history = [
        PageSnapshot(
            url="https://test.com/stuck",
            title="Stuck",
            page_type=PageType.ERROR
        )
        for _ in range(5)
    ]

    action = engine.get_recovery_action(simple_goal, simple_playbook, history)

    # Should try to navigate back to start
    assert action.kind in ["navigate", "refresh"]


# ============================================================================
# Integration Tests (with mock page)
# ============================================================================

class MockPage:
    """Mock Playwright Page for testing."""

    def __init__(self, snapshots: list):
        self.snapshots = snapshots
        self.current_index = 0
        self.actions_executed = []

    async def goto(self, url: str):
        self.actions_executed.append(("goto", url))

    async def wait_for_load_state(self, state: str):
        pass

    async def title(self) -> str:
        if self.current_index < len(self.snapshots):
            return self.snapshots[self.current_index].title
        return "Page"

    @property
    def url(self) -> str:
        if self.current_index < len(self.snapshots):
            return self.snapshots[self.current_index].url
        return "https://test.com"

    async def inner_text(self, selector: str) -> str:
        if self.current_index < len(self.snapshots):
            return self.snapshots[self.current_index].page_text
        return ""

    async def query_selector(self, selector: str):
        # Return mock element if it exists
        if self.current_index < len(self.snapshots):
            snapshot = self.snapshots[self.current_index]
            if selector in snapshot.all_elements:
                return MockElement()
        return None

    async def query_selector_all(self, selector: str):
        return []

    async def click(self, selector: str):
        self.actions_executed.append(("click", selector))
        self.current_index = min(self.current_index + 1, len(self.snapshots) - 1)

    async def fill(self, selector: str, value: str):
        self.actions_executed.append(("fill", selector, value))

    async def wait_for_timeout(self, timeout: int):
        pass

    async def reload(self):
        self.actions_executed.append(("reload",))


class MockElement:
    """Mock Playwright Element."""

    async def get_attribute(self, name: str):
        return None

    async def inner_text(self) -> str:
        return ""

    async def evaluate(self, expression: str):
        return True


@pytest.mark.asyncio
async def test_offline_agent_simple_flow():
    """Test offline agent with simple success flow."""
    goal = Goal(
        name="test",
        start_url="https://test.com",
        targets=["Page1"],
        success_conditions=["url:success"]
    )

    playbook = Playbook(max_steps=10)

    # Create snapshots for: initial -> success
    snapshots = [
        PageSnapshot(
            url="https://test.com",
            title="Start",
            page_type=PageType.UNKNOWN,
            all_elements=[]
        ),
        PageSnapshot(
            url="https://test.com/success",
            title="Success",
            page_type=PageType.SUCCESS,
            all_elements=[]
        )
    ]

    mock_page = MockPage(snapshots)
    agent = OfflineAgent(goal, playbook)

    # Note: Full integration requires real Playwright
    # This test just verifies the agent can be instantiated and structure is correct
    assert agent.goal == goal
    assert agent.playbook == playbook
    assert isinstance(agent.analyzer, DOMStateAnalyzer)
    assert isinstance(agent.decider, RuleBasedDecisionMaker)
    assert isinstance(agent.recovery, FailureRecoveryEngine)


def test_action_string_representation():
    """Test Action string conversion."""
    action = Action(kind="navigate", target="https://test.com")
    assert "Navigate" in str(action)

    action = Action(kind="click", target="#button")
    assert "Click" in str(action)

    action = Action(kind="fill", target="#input", payload="value")
    assert "Fill" in str(action)
    assert "value" in str(action)


def test_agent_result_summary():
    """Test AgentResult summary generation."""
    from ops.eue.offline_agent import AgentResult

    result = AgentResult(
        success=True,
        goal_achieved=True,
        step_count=5
    )

    summary = result.summary()
    assert "SUCCESS" in summary
    assert "ACHIEVED" in summary
    assert "5" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
