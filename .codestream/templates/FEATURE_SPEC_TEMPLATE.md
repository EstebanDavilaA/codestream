# FEATURE SPECIFICATION: M{X}_P{Y} - [Feature Name]

> **This file has two parts, and only one of them is ever written to after approval (rule 25).**
>
> **1. The Approved Baseline** — everything from `## Phase Summary` down to the end of Section 3. This is the normative text exactly as approved. Once the spec is `SPEC_APPROVED` its normative text is **never edited**: not to fix a typo, not to correct a stale count, not to narrow a clause the build disproved. Code does not get to redefine what was asked for.
>
> **2. The Amendment Log** — appended at the bottom. Every correction after approval is a numbered entry (`AM-1`, `AM-2`, …) recording the binding item it changes, the old and new text quoted verbatim, why it was forced, and which AC rows it adds, re-points, or retires. A reader resolves the spec by applying the log over the baseline, later entry winning. Nothing is deleted; superseded text stays readable so the reasoning that changed remains auditable. An amendment takes effect only on re-`SPEC_APPROVED` (rule 1).

## Phase Summary
[Concise summary of phase goals, motivation, and user-visible mechanics]

### Key Behaviors
1. [Key Behavior 1]
2. [Key Behavior 2]

### Binding Declarations — Read This First
The four subsections below — **Resolved Ambiguities**, **Norms**, **Safeguards**, **Out of Scope** — are binding. `critic` (Layer 2) audits against them, treats what they name as authorized non-work, and treats what they omit as unwritten.

**Every binding *constraint* must map to at least one row in the Acceptance Criteria matrix below** — that is Resolved Ambiguities, Norms, and Safeguards. A constraint declared binding but carrying no AC is unverifiable: the executor cannot know when it is satisfied, and `critic` will report it as a finding rather than a pass. Where a constraint genuinely cannot be checked mechanically, say so inside it — `critic` will then judge it against its stated intent instead of a test.

**Out of Scope is the deliberate exception.** An exclusion is authorized *non-work*, and it is earned by the single **Scope Guardrail AC** — the row asserting the named files and behaviours are untouched — rather than by one AC per exclusion. A per-exclusion AC would have to assert the *absence* of something, which is busywork and easy to write in a way that passes vacuously. Keep the exclusions list complete and specific; let the one guardrail row carry the verification.

The constraint rule applies to all three constraint subsections, not only Norms. The failure it prevents, in the shape it actually occurs: a constraint written as binding ("allowed precision is an integer in range `[0, 10]`") that never becomes an AC, so the executor implements only the half the AC matrix happens to test. The omitted half then surfaces at Layer 2 as a PARTIAL, after a build — instead of at plan time, where it was a one-line fix.

**Absolute wording needs a stated domain.** A constraint phrased as "never", "no X", or "always" is a claim about *every* input, and it is only checkable if the spec also names the inputs it ranges over. "Scaled amounts are never `Infinity`" is not satisfied by a test whose inputs happen not to overflow — it needs the domain written down ("for amounts in `[0, 1e12]`") or else the guard that makes the absolute claim true. Without a declared domain the AC passes on whatever inputs the author happened to try, and the claim reads as verified when it has only been spot-checked. Watch for this most on numeric contracts, where the author's test values tend to cluster in a comfortable middle and never approach the bounds.

**Binding items must be addressable (rule 27).** Every item in a binding section carries an id — `RA-15`, `SG-3`, `N-2` — and where an item has sub-items that bind separately, each sub-item carries its own (`RA-15.a`, `RA-15.b`, …). Every AC row then names the ids it verifies (the `Verifies` column in Section 3). This is what makes coverage a mechanical check instead of a judgement call: an item that cannot be identified individually cannot be shown to be covered, and `"Mapped to AC-19 through AC-24"` on a five-part clause is exactly how a sub-item escapes review — a documented `label` bound of 128 once shipped with no AC row and no artifact anywhere in the codebase, under precisely that phrasing. `scripts/check-spec-coverage.py` fails the plan halt (`.codestream/HARD_RULES.md` rule 27) on any binding item no AC row cites.

**No derived literals (rule 26).** A binding clause must not assert a value it does not itself define. Do not write a prose count of files, paths, clauses, edits or phases; an enumeration restated from another clause instead of cited from it; a hand-computed date, duration or arithmetic result; or a permission list duplicating one that already exists elsewhere in the spec. Cite the AC row that derives it, or have the AC compute it from source or a declared list at run time. The reason is mechanical: `critic` audits quantified constraints **literally** (its step 2c) while prose is checked by nobody but `critic`, so every hand-maintained literal is a defect with a fuse on it — and the literals are coupled, so changing one makes every clause that restated the old number wrong. One clause amendment once required 13 coordinated count corrections; a single AC row asserting a date-window edge as the calendar date `2016-09-25` passed for a whole phase because the test derived the true boundary (`2016-09-24`) and never read the literal.

### Resolved Ambiguities (Binding)
- **RA-1 (Operator Precision & Boundaries)**: [e.g. `>=` vs `>`, exact inclusive/exclusive float bounds e.g. `[-20.0, 0.5]` vs `-20.01` / `0.51`]
- **RA-2 (Gate Interplay)**: [e.g. Replaces/augments temporal gate, rendering window vs focus window separation]
- **RA-3 (Fallback Retention)**: [e.g. When zero qualifying items match, retain prior state values rather than leaking default placeholders]
- **RA-4 (Transition Mechanics)**: [e.g. Animated fast lerp vs same-frame teleport, exact thresholds and lerp factors]

Sub-id where a single item binds more than one thing separately — `RA-4.a` for the threshold, `RA-4.b` for the lerp factor — because a sub-item folded under one id is a sub-item no AC row can be shown to cover (rule 27).

### Norms (Binding)
The coding standards and patterns this phase must follow, resolved to concrete statements rather than a pointer to a generic style guide. Cite the existing code or pattern archetype that establishes each norm — "follow the convention" has no referent until you name the file it lives in. For architectural abstractions (Strategy, Port/Adapter, State Machine, Factory, Pub-Sub, Middleware, Composite), evaluate fit against `.codestream/templates/DESIGN_PATTERNS.md` and declare the interface contract and prohibited anti-pattern. For phases that render or update user-facing UI, evaluate fit against `.codestream/templates/UX_HEURISTICS.md` and declare the load-bearing heuristics, not all of them by default.

- **N-1**: [e.g. "constructor injection only — no field injection. Precedent: `FooService`, `BarService`."]
- **N-2**: [e.g. "all DB access goes through the repository layer; services never call the client directly."]
- **N-3 (Pattern)**: [e.g. "Strategy pattern for pricing rules; concrete variants must not access DB or HTTP context directly. Precedent: `.codestream/templates/DESIGN_PATTERNS.md#strategy` and `FooService`."]
- **N-4 (Port)**: [e.g. "Port/Adapter: all external API / DB access goes through a domain-owned interface; services never instantiate client drivers directly. Precedent: `.codestream/templates/DESIGN_PATTERNS.md#port-adapter`."]
- **N-5 (UX)**: [e.g. "Async mutations show a loading state within 100ms and a success/error confirmation on completion; trigger control disabled while pending. Precedent: `.codestream/templates/UX_HEURISTICS.md#1-visibility-of-system-status`."]
- **N-6**: [Naming, error shape, module boundary, or anything else this phase must not improvise.]

**Every norm must have at least one row in the Acceptance Criteria matrix below** (test type `Lint`, `Structure`, or `Convention`). A norm with no AC is decoration, and `critic` (Layer 2) treats an unverifiable norm as a finding in its own right rather than passing it. If a norm genuinely cannot be checked mechanically, say so explicitly here — `critic` will then judge it against its stated intent instead of a test.

Note the trap: reading the codebase to infer "the convention" is unreliable when the codebase is *inconsistent*. Three call sites using three different patterns is not a convention, it's an unmade decision. If that's what you find, name the pattern this phase standardises on and say plainly that the others are legacy — do not treat the majority as authoritative.

### Safeguards (Binding, Quantified)
Hard constraints on **quality**, distinct from Out of Scope below, which governs **scope**. Quantify wherever possible — an unquantified safeguard is an invitation to interpret.

- **SG-1 (Performance)**: [Measurable budget — e.g. "p95 < 200ms for the list endpoint at 1k rows", "at most one DB round-trip per render."]
- **SG-2 (Error contracts)**: [Exact messages, codes, and shapes a caller can rely on — e.g. `409` + `{"code":"EMAIL_TAKEN"}`.]
- **SG-3 (Data integrity)**: [Invariants that must hold — e.g. "the import is one transaction; no partial writes."]
- **SG-4 (Security / privacy)**: [e.g. "never log the raw session token."]
- **SG-5 (Behaviour that must not change)**: [e.g. "`formatLegacyDate()` output stays byte-identical — existing callers depend on it."]
- **SG-6 (Refactoring limits)**: [e.g. "extend `UserRepository`; do not restructure it in this phase."]

Where a number genuinely isn't knowable yet, state the *direction and bound* ("must not regress against the current baseline") rather than leaving the line blank. An empty Safeguards section is the same signal an empty Out of Scope section sends: the boundary wasn't thought through, not that nothing needed excluding.

Each safeguard also needs an AC row — test type `Measured` for a numeric budget, `Unit Test` for an error contract or data invariant. A quantified budget that no test asserts will be reported PARTIAL by `critic`, and correctly so: measuring it once by hand is not the same as verifying it, and an unasserted number is a number nobody notices regressing.

### Out of Scope (Explicit Exclusions, Binding)
- **OOS-1**: [Something a reader might reasonably expect this phase to cover, named explicitly as deferred — and to which milestone/phase, if known.]
- **OOS-2**: [A component or file adjacent to this work that stays untouched on purpose. e.g. "The legacy `formatLegacyDate()` path is not migrated in this phase — new call sites only."]

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
| ID | Verifies | Requirement | Test Type | Expected Outcome |
|----|----------|-------------|-----------|-------------------|
| AC-1 | N-1 | Constant Exports | Unit Test | `CONSTANT === value`, imported cleanly |
| AC-2 | RA-2 | Basic Logic Below Threshold | Unit Test | Deterministic boolean / value outcome |
| AC-3 | RA-2 | Basic Logic Above Threshold | Unit Test | Deterministic boolean / value outcome |
| AC-4 | RA-1, SG-1 | Exact Boundary Edge Case | Unit Test | Inclusive/exclusive exact float boundary assertion |
| AC-5 | RA-3 | Multi-Element & Spans | Unit Test | Span calculations, padding, bounds |
| AC-6 | RA-3 | Degenerate & Empty Inputs | Unit Test | Zero items / empty array handling |
| AC-7 | N-2, N-3, N-4 | Stateful Frame Integration | Integration Test | Integration behaviour in stateful container |
| AC-8 | RA-4, SG-2 | Fallback Preservation | Integration Test | Prior state retained across zero-match frames |
| AC-9 | N-5, N-6 | Lockstep Sync | Integration Test | Dual component sync (e.g. camera and spotlight) |
| AC-10 | SG-3, SG-4, SG-5, SG-6 | Invariant Preservation | Integration Test | Unrelated features/windows remain unaffected |
| AC-11 | OOS-1, OOS-2 | Scope Guardrail | Verification | `git diff --name-only` confirms specified files are untouched |

**The `Verifies` column is what makes rule 27's coverage gate work.** Name every addressable binding item this row establishes — `RA-15.a`, `SG-3`, `N-2`, `OOS-1` — or `—` for a row that verifies only ordinary behaviour. Cross-check before halting: every id defined in the binding sections and Section 1's symbol inventory should appear in at least one row here. `scripts/check-spec-coverage.py` checks exactly that, plus that no `Verifies` cell cites an id that doesn't exist, and exits non-zero if either fails — so a spec presented without a passing checker run is presented with an unenforced Coverage claim.

Allowed `Test Type` values: `Unit Test`, `Integration Test`, `Lint`, `Structure`, `Convention`, `Measured`, `Verification`. `Structure` tests verify architectural isolation and pattern contracts (e.g. mocking an adapter/port without I/O, verifying domain imports zero infrastructure, or ensuring Open-Closed strategy extensibility). `Verification` means a manual but reproducible check — reading a diff, a screenshot, a `git diff --name-only`, or exercising a UX heuristic Norm's flow by hand — rather than an automated assertion. A `Verification` or `Measured` row counts for coverage like any other; what rule 27 rejects is a binding item no row cites at all.

---

## Amendment Log (append-only — rule 25)

**Empty on a newly approved spec. Never edit the baseline above; append here instead.** One numbered entry per correction, oldest first. The old and new text are both quoted verbatim, so a reader can see exactly what changed and why without trusting anyone's summary of it.

<!--
### AM-1 — YYYY-MM-DD — corrects RA-15.c
- **Changes**: RA-15.c (the `label` bound)
- **Old text**: "Applied as `description` (max **512**), `notes` (max **2000**), `label` (max **128**)."
- **New text**: "Applied as `description` (max **512**), `notes` (max **2000**)."
- **Why**: Layer 2 critic audit found the `label` bound was cited by no AC row and implemented nowhere — the constant declaring it was referenced by no source file, and the validator was never called with a label (critic Finding 1). `/diagnose` verdict: spec error.
- **AC rows**: retires the implied label coverage; no row added.
- **Effect**: takes effect on re-`SPEC_APPROVED`; re-entry is scoped per rule 28.
-->

---
> **HALT GATE (STATE 2):** Present this spec to the user. Prompt: *"Review this feature specification. Reply with **SPEC_APPROVED** to begin execution, or provide feedback/adjustments."* DO NOT WRITE A SINGLE LINE OF CODE UNTIL "SPEC_APPROVED" IS RECEIVED.

