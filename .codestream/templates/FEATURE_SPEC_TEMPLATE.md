# FEATURE SPECIFICATION: M{X}_P{Y} - [Feature Name]

## Phase Summary
[Concise summary of phase goals, motivation, and user-visible mechanics]

### Key Behaviors
1. [Key Behavior 1]
2. [Key Behavior 2]

### Binding Declarations — Read This First
The four subsections below — **Resolved Ambiguities**, **Norms**, **Safeguards**, **Out of Scope** — are binding. `critic` (Layer 2) audits against them, treats what they name as authorised non-work, and treats what they omit as unwritten.

**Every binding declaration must map to at least one row in the Acceptance Criteria matrix below.** A constraint that is declared binding but carries no AC is unverifiable: the executor cannot know when it is satisfied, and `critic` will report it as a finding rather than a pass. Where a declaration genuinely cannot be checked mechanically, say so inside the declaration itself — `critic` will then judge it against its stated intent instead of a test.

This applies to **all four** subsections, not only Norms. The failure it prevents, in the shape it actually occurs: a constraint written as binding ("allowed precision is an integer in range `[0, 10]`") that never becomes an AC, so the executor implements only the half the AC matrix happens to test. The omitted half then surfaces at Layer 2 as a PARTIAL, after a build — instead of at plan time, where it was a one-line fix.

### Resolved Ambiguities (Binding)
- **Operator Precision & Boundaries**: [e.g. `>=` vs `>`, exact inclusive/exclusive float bounds e.g. `[-20.0, 0.5]` vs `-20.01` / `0.51`]
- **Gate Interplay**: [e.g. Replaces/augments temporal gate, rendering window vs focus window separation]
- **Fallback Retention**: [e.g. When zero qualifying items match, retain prior state values rather than leaking default placeholders]
- **Transition Mechanics**: [e.g. Animated fast lerp vs same-frame teleport, exact thresholds and lerp factors]

### Norms (Binding)
The coding standards and patterns this phase must follow, resolved to concrete statements rather than a pointer to a generic style guide. Cite the existing code that establishes each norm — "follow the convention" has no referent until you name the file it lives in.

- **[Norm]**: [e.g. "constructor injection only — no field injection. Precedent: `FooService`, `BarService`."]
- **[Norm]**: [e.g. "all DB access goes through the repository layer; services never call the client directly."]
- **[Norm]**: [Naming, error shape, module boundary, or anything else this phase must not improvise.]

**Every norm must have at least one row in the Acceptance Criteria matrix below** (test type `Lint`, `Structure`, or `Convention`). A norm with no AC is decoration, and `critic` (Layer 2) treats an unverifiable norm as a finding in its own right rather than passing it. If a norm genuinely cannot be checked mechanically, say so explicitly here — `critic` will then judge it against its stated intent instead of a test.

Note the trap: reading the codebase to infer "the convention" is unreliable when the codebase is *inconsistent*. Three call sites using three different patterns is not a convention, it's an unmade decision. If that's what you find, name the pattern this phase standardises on and say plainly that the others are legacy — do not treat the majority as authoritative.

### Safeguards (Binding, Quantified)
Hard constraints on **quality**, distinct from Out of Scope below, which governs **scope**. Quantify wherever possible — an unquantified safeguard is an invitation to interpret.

- **Performance**: [Measurable budget — e.g. "p95 < 200ms for the list endpoint at 1k rows", "at most one DB round-trip per render."]
- **Error contracts**: [Exact messages, codes, and shapes a caller can rely on — e.g. `409` + `{"code":"EMAIL_TAKEN"}`.]
- **Data integrity**: [Invariants that must hold — e.g. "the import is one transaction; no partial writes."]
- **Security / privacy**: [e.g. "never log the raw session token."]
- **Behaviour that must not change**: [e.g. "`formatLegacyDate()` output stays byte-identical — existing callers depend on it."]
- **Refactoring limits**: [e.g. "extend `UserRepository`; do not restructure it in this phase."]

Where a number genuinely isn't knowable yet, state the *direction and bound* ("must not regress against the current baseline") rather than leaving the line blank. An empty Safeguards section is the same signal an empty Out of Scope section sends: the boundary wasn't thought through, not that nothing needed excluding.

Each safeguard also needs an AC row — test type `Measured` for a numeric budget, `Unit Test` for an error contract or data invariant. A quantified budget that no test asserts will be reported PARTIAL by `critic`, and correctly so: measuring it once by hand is not the same as verifying it, and an unasserted number is a number nobody notices regressing.

### Out of Scope (Explicit Exclusions, Binding)
- [Something a reader might reasonably expect this phase to cover, named explicitly as deferred — and to which milestone/phase, if known. e.g. "Retry/backoff on failed writes — deferred to M6_P1, this phase assumes writes succeed."]
- [A component or file adjacent to this work that stays untouched on purpose. e.g. "The legacy `formatLegacyDate()` path is not migrated in this phase — new call sites only."]

This section exists to shrink the implementation's "creative area" as much as the Resolved Ambiguities above do — everything decided in scope by inclusion, everything decided out of scope by name. An empty section is a signal the phase's boundary wasn't actually thought through, not evidence there's nothing to exclude. `critic` (Layer 2) treats an item listed here as authorized non-work, not a gap — and treats material scope creep *beyond* what's listed here as its own finding.

---

## 1. Data Schema & Contracts
- **Exported Constants & Types**: [e.g., `CAMERA_JUMP_THRESHOLD: 3.0`, interfaces, exported types]
- **Symbol Inventory**: [Explicit list of modified symbols and existing untouched symbols]

---

## 2. Transformations & Pure Logic
- **Pure Function Contracts**: [Signatures, default arguments, deterministic inputs -> outputs]
- **No-Match / Fallback Contracts**: [Explicit return values on empty/zero match, caller branching rules]
- **Stateful Integration Contract**: [Step-by-step logic integration in render/frame loop, lerp selection, lockstep component updates]
- **Refactoring & Legacy Cleanup**: [Explicitly identify obsolete registration paths, legacy alias loops, or side effects to be purged]

---

## 3. Acceptance Criteria & Test Matrix
| ID | Requirement | Test Type | Expected Outcome |
|----|-------------|-----------|-------------------|
| AC-1 | Constant Exports | Unit Test | `CONSTANT === value`, imported cleanly |
| AC-2 | Basic Logic Below Threshold | Unit Test | Deterministic boolean / value outcome |
| AC-3 | Basic Logic Above Threshold | Unit Test | Deterministic boolean / value outcome |
| AC-4 | Exact Boundary Edge Case | Unit Test | Inclusive/exclusive exact float boundary assertion |
| AC-5 | Multi-Element & Spans | Unit Test | Span calculations, padding, bounds |
| AC-6 | Degenerate & Empty Inputs | Unit Test | Zero items / empty array handling |
| AC-7 | Stateful Frame Integration | Integration Test | Integration behaviour in stateful container |
| AC-8 | Fallback Preservation | Integration Test | Prior state retained across zero-match frames |
| AC-9 | Lockstep Sync | Integration Test | Dual component sync (e.g. camera and spotlight) |
| AC-10 | Invariant Preservation | Integration Test | Unrelated features/windows remain unaffected |
| AC-11 | Scope Guardrail | Verification | `git diff --name-only` confirms specified files are untouched |

Allowed `Test Type` values: `Unit Test`, `Integration Test`, `Lint`, `Structure`, `Convention`, `Measured`, `Verification`. `Verification` means a manual but reproducible check — reading a diff, a screenshot, a `git diff --name-only` — rather than an automated assertion.

---
> **HALT GATE (STATE 2):** Present this spec to the user. Prompt: *"Review this feature specification. Reply with **SPEC_APPROVED** to begin execution, or provide feedback/adjustments."* DO NOT WRITE A SINGLE LINE OF CODE UNTIL "SPEC_APPROVED" IS RECEIVED.

