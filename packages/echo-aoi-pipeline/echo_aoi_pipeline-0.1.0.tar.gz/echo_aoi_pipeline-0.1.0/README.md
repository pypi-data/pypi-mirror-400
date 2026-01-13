# Echo Judgment System

## 🧭 Human-Visible Output Principle

This system does **not** define success by logs, tests, or internal metrics.

**If a human can see a failure in the final output,  
the system considers it a failure.**

All deliverables must pass the **Human-Visible Output Gate**  
before they can be released.

> **This system is not designed to decide safely.
> It is designed so that decision cannot happen unsafely.**

---

## Judgmentless Systems

Echo’s UX constitution, flow, and runtime stack define the new **Judgmentless Systems** category—apps where 사용자가 판단하지 않아도 결과가 조용히 도착한다.  
See `docs/JUDGMENTLESS_SYSTEMS_POSITIONING.md` for the three-sentence explainer, role-based definitions, and pitch line, plus links to the UX 헌법과 첫 도메인 이식 청사진.

**Human-Visible Output Judgment Constitution**: `docs/HUMAN_VISIBLE_OUTPUT_JUDGMENT_CONSTITUTION.md` lays out the universal rule that 시스템 성공은 사용자가 받아들일 수 있는 결과에 의해 결정된다는 점을 명문화하며, 체크리스트·FinalOutputGate 코드 스펙·원페이지 요약·Judgment Layer 통합 규칙을 포함한다.

**HVPC + Phase 4.4 Boundary Doctrine**: `docs/HVPC_PHASE4_BOUNDARY_DOCTRINE.md` describes the Gate → Repairable State → Negotiated Override pipeline so 규칙은 시스템이 지키고, 선택/책임은 인간에게 귀속된다는 경계 선언이 고정된다.

**Control Profiles**: `docs/CONTROL_PROFILES.md` enumerates the 4 reusable control structures (Full Lockdown / Guarded Flow / Soft Guard / Open Assist) so 각 파이프라인이 어느 프로파일을 따르는지 한 문장으로 설명할 수 있다.

---

## Core Judgment Stack (STOP → Boundary → Judgment → AJT)

| Icon | Pillar | One-Line Definition |
|------|--------|---------------------|
| 🛑 | **STOP** | Execution brake that makes “do not run” a first-class, normal outcome. |
| 🧱 | **Boundary** | Operating rules that state who may decide, on what scope, and where STOP must trigger. |
| ✋ | **Judgment Interface (HJTL)** | Human-before-execution loop that asks the structured questions, seals the answer, and only then allows Resume. |
| 📜 | **AJT (Atomic Judgment Trace)** | Append-only proof that records who judged, under which boundary, and why the action was allowed, modified, or denied. AJT assumes a separate Observation Layer has already fixed the raw facts; it does not record reality itself, only the decisions made *about* observed reality. AJT is the same judgment core that governs STOP/Branch logic, now applied inside the RAG pipeline: RAG supplies evidence, AJT decides whether answering is permissible. |

These four surfaces always operate in this order—STOP → Boundary → Judgment-before-Execution → AJT—before any model token is generated.

---

## What Echo Is (and Is Not)


**Echo is not AI.**

Echo does not control AI.

Echo does not make AI smarter, safer, or more aligned.

**What Echo does**:

Echo fixes where judgment lives.

Every AI output passes through a boundary called **STOP**.

At STOP, the system asks: "Where is the human decision for this action?"

- If missing → Execution blocked
- If present → Human owner logged, then execution proceeds

**Result**: When auditors ask "who decided?"—there is always a timestamped human owner, created before the action, not reconstructed from logs afterward.

**Quick entry**: See [ECHO_BOUNDARY_KIT_OVERVIEW.md](ECHO_BOUNDARY_KIT_OVERVIEW.md) for 1-page explanation.

**Detailed design**: See Core Documents below (Constitutional, Architectural, Operational layers).

---


**Mode**: Judgment-Sovereign Mode (Non-Coercive Gate Architecture)

## What This System Is NOT

- ❌ An automation framework
- ❌ An AI agent platform
- ❌ A safety guardrail library
- ❌ A decision-making system

**This system does not generate judgment. It structures where judgment must reside.**

---

## 4-Layer Boundary Architecture

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: Gate (echo_runtime)                       │
│ - Blocks execution without judgment file           │
│ - Default: STOP (human approval required)          │
│ - Never generates approval                         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 2: Authority (INVARIANT_JUDGMENT)            │
│ - Classifies judgment type (8 categories)          │
│ - Routes per delegation config                     │
│ - Never makes decisions                            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 3: Execution (ops/eui + ops/eue)             │
│ - Human approval workflows (Excel UI)              │
│ - Offline-first distributed execution              │
│ - Never auto-advances workflow stages              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Layer 4: Intelligence (echo_engine + ops/tools)    │
│ - Two-stage judgment pipeline                      │
│ - Counterfactual simulation                        │
│ - Stage 2 narrates, never judges                   │
└─────────────────────────────────────────────────────┘
```

**Full specification**: [ARCHITECTURE_BOUNDARY_MAP.md](ARCHITECTURE_BOUNDARY_MAP.md)

---

## 6 Entry Points (Fixed)

All system access goes through exactly six entry points:

1. **run_gate** — Enforce judgment boundaries before skill execution
2. **author_judgment** — Human-authored authority specification (YAML)
3. **approve_in_excel** — Human approval workflow via Excel UI
4. **execute_offline** — Distributed offline-first agent execution
5. **analyze_pipeline** — Two-stage observation → judgment → narration
6. **govern_ci** — Automated governance at PR merge time

**Full specification**: [ENTRYPOINTS.md](ENTRYPOINTS.md)

---

## Phase 3: Human-as-Final-Authority

**Core Principle**: Authority shifts must be declared. Responsibility must be previewed.

**Enforcement Mechanisms**:
- Judgment files specify human owner (never inferred)
- Approval states logged before execution (never after)
- ARAL governance enforced at PR merge ([world/docs/cognitive_infrastructure/ARAL_OVERVIEW.md](world/docs/cognitive_infrastructure/ARAL_OVERVIEW.md))

**What This Prevents**:
- Automated decisions on employment, clinical, safety, content moderation
- Authority persistence without human awareness (login creep, delegation drift)
- Responsibility assignment after incidents (no retroactive authority claims)

---

## Trust Surface

**What We Publish** (append-only, immutable):
- Evidence of execution stops: [execution-stop-ledger](https://github.com/Nick-heo-eg/execution-stop-ledger)
- Timestamps and stop reasons
- Human ownership declarations

**What We Do NOT Publish**:
- Internal enforcement mechanisms
- Approval schema details
- Bypass prevention architecture

**Trust Package**: [TRUST_PACKAGE.md](TRUST_PACKAGE.md)

---

## Proof & Governance

**Proof Surfaces**:
- `echo_runtime/trace/run_log.jsonl` — Machine-readable audit log
- `echo_runtime/trace/proof_log.md` — Human-readable proof trail
- `echo_runtime/product/PRODUCT_LOG.md` — Prevented unsafe actions

**Governance Automation**:
- `.github/workflows/aral_gate_check.yml` — Authority-Responsibility validation at PR merge
- `.github/workflows/eue-rbac-gate.yml` — Role-based access control enforcement
- [world/docs/cognitive_infrastructure/](world/docs/cognitive_infrastructure/) — 14-document ARAL specification

## Codex CLI (STOP Guardrail Surface)

- **Purpose:** Provide a CI-enforced guardrail that refuses to run or merge when a `judgment.yaml` STOP policy is violated.
- **Mechanics:** `.github/workflows/stop_policy_ci.yml` invokes `ci/check_stop_policy.py`, which loads the repo’s STOP rules and fails the pipeline on any `PolicyViolationError`.
- **Evidence:** CI logs show the exact STOP condition, the offending command, and remediation link; no approval UI or runtime override exists.
- **Integrator usage:** Add/modify STOP clauses in `judgment.yaml`, run the checker locally (`python ci/check_stop_policy.py`), and rely on the GitHub Action to block non-compliant pull requests automatically.

---

## Quick Start

**For Auditors**: Read [ARCHITECTURE_BOUNDARY_MAP.md](ARCHITECTURE_BOUNDARY_MAP.md) → [GUARANTEES in execution-stop-ledger](https://github.com/Nick-heo-eg/execution-stop-ledger/blob/master/GUARANTEES.md)

**For Integrators**: Read [ENTRYPOINTS.md](ENTRYPOINTS.md) → [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

**For Developers**: Read [OPERATING_CHARTER.md](OPERATING_CHARTER.md) → [WHY_STOP.md](WHY_STOP.md)

---

## Maps and Their Roles

Three types of maps govern this system:

### Constitutional Maps (What Must Never Be Crossed)
- **[ARCHITECTURE_BOUNDARY_MAP.md](ARCHITECTURE_BOUNDARY_MAP.md)** — Defines boundaries, prohibitions, responsibilities
  - 4-layer enforcement architecture
  - What each layer must NOT do
  - Authority and responsibility assignment

- **[ENTRYPOINTS.md](ENTRYPOINTS.md)** — Operational access points
  - 6 fixed entry points (no others)
  - What each entry point can/cannot trigger
  - Layer boundaries crossed

- **[BOUNDARY_INDEX.md](BOUNDARY_INDEX.md)** — Directory classification
  - Judgment authority by directory
  - Execution capability mapping
  - Phase 3 enforcement scope

### Descriptive Maps (What Exists, Not What Is Allowed)
- **[WORLD_MAP.md](WORLD_MAP.md)** — System components and conceptual structure
  - Modules, tools, agents, pipelines
  - How components relate
  - Current system state

**Rule**: Boundary → World (links allowed). World → Boundary (reference only, never claims authority).

---

## Core Documents (Sealed)

### Constitutional Layer (Why This Exists)
- **[CONSTITUTIONAL_FOUNDATION.md](world/docs/CONSTITUTIONAL_FOUNDATION.md)** — Foundational truths
  - Why judgment sovereignty is structural, not technical
  - Three proofs: STOP layering, Model independence, Post-Model system
  - The line that cannot be crossed
- **[STOP_AJT_BOUNDARY_IDENTITY_MANIFEST.md](world/docs/STOP_AJT_BOUNDARY_IDENTITY_MANIFEST.md)** — Identity-level declaration that execution is a privilege, with STOP/AJT/Boundary as constitutional duties
- **[JUDGMENT_FIRST_SYSTEMS.md](world/docs/JUDGMENT_FIRST_SYSTEMS.md)** — Pre-execution doctrine outlining STOP, AJT, and non-bypassable boundaries as the system’s reason for existing

### Architectural Layer (What Must Never Be Crossed)
- **[ARCHITECTURE_BOUNDARY_MAP.md](ARCHITECTURE_BOUNDARY_MAP.md)** — 4-layer enforcement architecture
- **[LocalEcho_Model_Independence_Anchor.md](world/docs/LocalEcho_Model_Independence_Anchor.md)** — Model independence proof
- **[LocalEcho_Reference_JEPA_LLM_Layer_Decomposition.md](world/docs/LocalEcho_Reference_JEPA_LLM_Layer_Decomposition.md)** — JEPA/LLM layer distinction
- **[ENTRYPOINTS.md](ENTRYPOINTS.md)** — 6 fixed entry points
- **[BOUNDARY_INDEX.md](BOUNDARY_INDEX.md)** — Directory classification

### Operational Layer (How This Operates)
- **[OPERATING_CHARTER.md](OPERATING_CHARTER.md)** — Asset boundaries, role constraints
- **[WHY_STOP.md](WHY_STOP.md)** — STOP semantics, evidence contract
- **[SEALING_RULES.md](world/docs/SEALING_RULES.md)** — Document governance protocol

---

## What This System Enforces

1. **No execution without judgment file** — Layer 1 (Gate)
2. **No judgment generation** — All layers
3. **No judgment movement** — Authority stays with human owner
4. **No judgment outsourcing** — LLMs narrate, never decide
5. **Default STOP** — Irreversible actions blocked until approval

---

## System Phases

**Sealed Phases** (Complete):
- Phase 0: Offline judgment
- Phase B: ARAL enforcement
- Phase A': Decision attribution
- Phase 2-α: Approval Constitution

**Ready** (Not Yet Executed):
- Phase C: Observation testing

**Planning** (Not Active):
- Phase D: See [PHASE_D_PREPARATION.md](PHASE_D_PREPARATION.md)

---

**This system is not designed to decide safely. It is designed so that decision cannot happen unsafely.**
