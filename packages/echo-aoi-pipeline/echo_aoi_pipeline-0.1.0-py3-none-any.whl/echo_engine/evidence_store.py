"""
Judgment Evidence Store - EU AI Act Art. 12 Compliant

This is NOT optional logging.
This is NOT debug tracing.
This is MANDATORY evidence generation.

Without evidence, Echo does not execute.
"""

import sqlite3
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import uuid


@dataclass
class JudgmentEvidence:
    """
    Single judgment evidence record.

    Complies with EU AI Act Art. 12 (Record-keeping) and Art. 14 (Transparency).
    Designed for litigation, audit, and regulatory submission.
    """

    # Core identification (immutable)
    run_id: str                     # UUID v4 - unique execution identifier
    timestamp: str                  # ISO-8601 UTC - when judgment occurred

    # Request context (PII-free, per GDPR Art. 25)
    input_hash: str                 # SHA-256 of input (content verification without storage)
    input_summary: str              # Sanitized summary (no PII, max 500 chars)

    # EU AI Act classification (Art. 6 high-risk, Art. 5 prohibited)
    risk_level: str                 # "high-risk" | "limited-risk" | "minimal-risk"
    prohibited_practice_check: bool # Art. 5 screening performed

    # Stage 1: Deterministic judgment (pre-LLM)
    stage1_decision: str            # ALLOW | STOP | PAUSE_HUMAN
    stage1_reason_code: str         # EXTERNAL_DATA_TRANSMISSION | UNSAFE_EXECUTION | etc.
    stage1_eu_reqs: str             # JSON list of triggered REQ-* (e.g., ["REQ-HR-003", "REQ-RK-001"])

    # Stage 2: LLM-based judgment (if executed)
    stage2_used: bool               # Whether LLM was called
    stage2_model_version: Optional[str]  # Model identifier (for traceability)

    # Human oversight (Art. 14)
    human_gate_triggered: bool      # Was human approval required?
    human_reviewer_id: Optional[str]     # Who approved (if applicable)
    human_approval_timestamp: Optional[str]  # When approved (ISO-8601 UTC)
    human_justification: Optional[str]   # Why approved (max 1000 chars)

    # Final outcome
    execution_allowed: bool         # Was execution ultimately permitted?

    # Evidence artifacts (file paths for detailed records)
    decision_trace_path: Optional[str]  # decision_trace.json location
    stop_or_gate_path: Optional[str]    # stop_or_gate.json location
    human_gate_path: Optional[str]      # human_gate.json location

    # System metadata (tamper detection)
    system_version: str             # Echo version (git hash or semver)
    policy_hash: str                # SHA-256 of current policy configuration

    # Compliance status
    eu_act_compliant: bool          # Did this execution comply with all requirements?
    violations: str                 # JSON list of violation descriptions

    # Immutability marker
    created_at: str                 # Database insertion timestamp (UTC)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JudgmentEvidence':
        """Reconstruct from dictionary."""
        return cls(**data)


class EvidenceStore:
    """
    Append-only evidence database.

    Design principles:
    - No UPDATE operations (only INSERT)
    - No DELETE operations (immutable record)
    - Every judgment creates exactly one record
    - Failure to log blocks execution
    """

    def __init__(self, db_path: Path):
        """
        Initialize evidence store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Create evidence table with EU AI Act-compliant schema."""
        conn = sqlite3.connect(self.db_path)

        # Single table: judgment_evidence (append-only)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS judgment_evidence (
                -- Primary key
                run_id TEXT PRIMARY KEY,

                -- Temporal
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                -- Request context
                input_hash TEXT NOT NULL,
                input_summary TEXT NOT NULL,

                -- EU AI Act classification
                risk_level TEXT NOT NULL,
                prohibited_practice_check INTEGER NOT NULL,

                -- Stage 1 judgment
                stage1_decision TEXT NOT NULL,
                stage1_reason_code TEXT NOT NULL,
                stage1_eu_reqs TEXT NOT NULL,

                -- Stage 2 judgment
                stage2_used INTEGER NOT NULL,
                stage2_model_version TEXT,

                -- Human oversight
                human_gate_triggered INTEGER NOT NULL,
                human_reviewer_id TEXT,
                human_approval_timestamp TEXT,
                human_justification TEXT,

                -- Outcome
                execution_allowed INTEGER NOT NULL,

                -- Evidence artifacts
                decision_trace_path TEXT,
                stop_or_gate_path TEXT,
                human_gate_path TEXT,

                -- System metadata
                system_version TEXT NOT NULL,
                policy_hash TEXT NOT NULL,

                -- Compliance
                eu_act_compliant INTEGER NOT NULL,
                violations TEXT NOT NULL
            )
        """)

        # Index for temporal queries (audit, litigation)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON judgment_evidence(timestamp)
        """)

        # Index for compliance queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_compliance
            ON judgment_evidence(eu_act_compliant, execution_allowed)
        """)

        # Index for human oversight queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_human_gate
            ON judgment_evidence(human_gate_triggered, human_reviewer_id)
        """)

        conn.commit()
        conn.close()

    def append(self, evidence: JudgmentEvidence) -> None:
        """
        Append evidence record (no updates allowed).

        Args:
            evidence: Evidence record to append

        Raises:
            sqlite3.IntegrityError: If run_id already exists (duplicate)
            sqlite3.Error: If database write fails
        """
        conn = sqlite3.connect(self.db_path)

        try:
            # Set created_at if not already set
            if not evidence.created_at:
                evidence.created_at = datetime.now(timezone.utc).isoformat()

            # Convert boolean fields to integers (SQLite compatibility)
            data = evidence.to_dict()
            for bool_field in ['prohibited_practice_check', 'stage2_used',
                               'human_gate_triggered', 'execution_allowed',
                               'eu_act_compliant']:
                if data.get(bool_field) is not None:
                    data[bool_field] = 1 if data[bool_field] else 0

            # INSERT only (no UPDATE)
            conn.execute("""
                INSERT INTO judgment_evidence (
                    run_id, timestamp, input_hash, input_summary,
                    risk_level, prohibited_practice_check,
                    stage1_decision, stage1_reason_code, stage1_eu_reqs,
                    stage2_used, stage2_model_version,
                    human_gate_triggered, human_reviewer_id,
                    human_approval_timestamp, human_justification,
                    execution_allowed,
                    decision_trace_path, stop_or_gate_path, human_gate_path,
                    system_version, policy_hash,
                    eu_act_compliant, violations,
                    created_at
                ) VALUES (
                    :run_id, :timestamp, :input_hash, :input_summary,
                    :risk_level, :prohibited_practice_check,
                    :stage1_decision, :stage1_reason_code, :stage1_eu_reqs,
                    :stage2_used, :stage2_model_version,
                    :human_gate_triggered, :human_reviewer_id,
                    :human_approval_timestamp, :human_justification,
                    :execution_allowed,
                    :decision_trace_path, :stop_or_gate_path, :human_gate_path,
                    :system_version, :policy_hash,
                    :eu_act_compliant, :violations,
                    :created_at
                )
            """, data)

            conn.commit()

        finally:
            conn.close()

    def query_range(self, start: datetime, end: datetime) -> List[JudgmentEvidence]:
        """
        Query evidence records within time range.

        Used for:
        - Audit requests
        - Litigation discovery
        - Regulatory submissions

        Args:
            start: Start of time range (inclusive)
            end: End of time range (exclusive)

        Returns:
            List of evidence records in chronological order
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.execute("""
                SELECT * FROM judgment_evidence
                WHERE timestamp >= ? AND timestamp < ?
                ORDER BY timestamp ASC
            """, (start.isoformat(), end.isoformat()))

            records = []
            for row in cursor:
                data = dict(row)

                # Convert integers back to booleans
                for bool_field in ['prohibited_practice_check', 'stage2_used',
                                   'human_gate_triggered', 'execution_allowed',
                                   'eu_act_compliant']:
                    if data.get(bool_field) is not None:
                        data[bool_field] = bool(data[bool_field])

                records.append(JudgmentEvidence.from_dict(data))

            return records

        finally:
            conn.close()

    def query_violations(self, limit: int = 100) -> List[JudgmentEvidence]:
        """
        Query evidence records with compliance violations.

        Critical for:
        - Post-market monitoring (Art. 72)
        - Serious incident reporting (Art. 73)

        Args:
            limit: Maximum number of records to return

        Returns:
            List of evidence records with violations (most recent first)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.execute("""
                SELECT * FROM judgment_evidence
                WHERE eu_act_compliant = 0
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            records = []
            for row in cursor:
                data = dict(row)

                # Convert integers back to booleans
                for bool_field in ['prohibited_practice_check', 'stage2_used',
                                   'human_gate_triggered', 'execution_allowed',
                                   'eu_act_compliant']:
                    if data.get(bool_field) is not None:
                        data[bool_field] = bool(data[bool_field])

                records.append(JudgmentEvidence.from_dict(data))

            return records

        finally:
            conn.close()

    def count_total(self) -> int:
        """Count total evidence records."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM judgment_evidence")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def count_violations(self) -> int:
        """Count evidence records with violations."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM judgment_evidence
                WHERE eu_act_compliant = 0
            """)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_latest(self, n: int = 10) -> List[JudgmentEvidence]:
        """Get n most recent evidence records."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.execute("""
                SELECT * FROM judgment_evidence
                ORDER BY timestamp DESC
                LIMIT ?
            """, (n,))

            records = []
            for row in cursor:
                data = dict(row)

                # Convert integers back to booleans
                for bool_field in ['prohibited_practice_check', 'stage2_used',
                                   'human_gate_triggered', 'execution_allowed',
                                   'eu_act_compliant']:
                    if data.get(bool_field) is not None:
                        data[bool_field] = bool(data[bool_field])

                records.append(JudgmentEvidence.from_dict(data))

            return records

        finally:
            conn.close()


# Global evidence store instance
_evidence_store: Optional[EvidenceStore] = None


def get_evidence_store() -> EvidenceStore:
    """
    Get global evidence store instance.

    Lazily initializes if not already created.
    Database location: runtime/judgment_evidence_store.db
    """
    global _evidence_store

    if _evidence_store is None:
        db_path = Path("runtime/judgment_evidence_store.db")
        _evidence_store = EvidenceStore(db_path)

    return _evidence_store


def generate_run_id() -> str:
    """Generate unique run ID (UUID v4)."""
    return str(uuid.uuid4())


def compute_input_hash(input_text: str) -> str:
    """Compute SHA-256 hash of input (for content verification without storage)."""
    return hashlib.sha256(input_text.encode('utf-8')).hexdigest()


def compute_policy_hash(policy_config: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of policy configuration (for change detection)."""
    policy_json = json.dumps(policy_config, sort_keys=True)
    return hashlib.sha256(policy_json.encode('utf-8')).hexdigest()


@contextmanager
def evidence_transaction(input_text: str, system_version: str, policy_config: Dict[str, Any]):
    """
    Context manager for evidence generation.

    Usage:
        with evidence_transaction(input_text, version, policy) as evidence:
            # Perform judgment
            decision = stage1_judgment(input_text)
            evidence.stage1_decision = decision

            # On exception, evidence still logged
            raise SomeError()

    Evidence is ALWAYS logged, even on exception.
    This ensures audit trail completeness.
    """
    # Initialize evidence record
    evidence = JudgmentEvidence(
        run_id=generate_run_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_hash=compute_input_hash(input_text),
        input_summary="",  # To be filled by caller
        risk_level="minimal-risk",  # Default, to be updated
        prohibited_practice_check=False,
        stage1_decision="UNKNOWN",
        stage1_reason_code="",
        stage1_eu_reqs="[]",
        stage2_used=False,
        stage2_model_version=None,
        human_gate_triggered=False,
        human_reviewer_id=None,
        human_approval_timestamp=None,
        human_justification=None,
        execution_allowed=False,
        decision_trace_path=None,
        stop_or_gate_path=None,
        human_gate_path=None,
        system_version=system_version,
        policy_hash=compute_policy_hash(policy_config),
        eu_act_compliant=True,
        violations="[]",
        created_at=""
    )

    try:
        yield evidence
    except Exception as e:
        # Log exception as violation
        evidence.eu_act_compliant = False
        evidence.violations = json.dumps([f"Exception during execution: {str(e)}"])
        raise
    finally:
        # ALWAYS append evidence, success or failure
        store = get_evidence_store()
        store.append(evidence)


if __name__ == "__main__":
    # Test evidence store
    print("Testing Evidence Store...")

    # Initialize
    store = get_evidence_store()
    print(f"Evidence store initialized: {store.db_path}")

    # Create test evidence
    test_evidence = JudgmentEvidence(
        run_id=generate_run_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_hash=compute_input_hash("test input"),
        input_summary="Test judgment execution",
        risk_level="minimal-risk",
        prohibited_practice_check=True,
        stage1_decision="ALLOW",
        stage1_reason_code="SAFE",
        stage1_eu_reqs=json.dumps(["REQ-RK-001"]),
        stage2_used=False,
        stage2_model_version=None,
        human_gate_triggered=False,
        human_reviewer_id=None,
        human_approval_timestamp=None,
        human_justification=None,
        execution_allowed=True,
        decision_trace_path=None,
        stop_or_gate_path=None,
        human_gate_path=None,
        system_version="test-v1.0",
        policy_hash=compute_policy_hash({"test": "config"}),
        eu_act_compliant=True,
        violations="[]",
        created_at=""
    )

    # Append
    store.append(test_evidence)
    print(f"✅ Evidence appended: {test_evidence.run_id}")

    # Query
    total = store.count_total()
    print(f"Total evidence records: {total}")

    latest = store.get_latest(1)
    if latest:
        print(f"Latest record: {latest[0].run_id} ({latest[0].stage1_decision})")

    print("✅ Evidence Store test complete!")
