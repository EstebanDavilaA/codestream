---
name: plan
description: Use to draft a feature spec for the active milestone/phase before any code is written. Runs State 2 — code generation is strictly forbidden until the user replies SPEC_APPROVED. Triggered by /plan, or automatically when a milestone from .codestream/ROADMAP.md is about to start.
---

# State 2: Feature Planning

**Rule:** No implementation code until the user has explicitly approved the spec with the exact phrase `SPEC_APPROVED`.

**Two modes, one halt gate.** *Drafting* produces a new spec for the active phase. *Amending* corrects an already-approved spec. Rules 25 and 28 make amending a first-class mode rather than an improvisation — before them, four different rules sent a spec correction to four different destinations and the two that named a destination (`/plan`, `plan_spec`) had no mode for the task, so every project invented its own "surgical amendment" protocol and re-derived it from the last one.

## Mode A — Draft a new spec
0. **First action of a session, always**: if `.codestream/STATE.json` already exists, run the pre-flight integrity check (`.codestream/HARD_RULES.md` rule 10) before anything else — this is a hard block, not a formality.
1. Run `plan_spec` skill for the active milestone/phase, pulling raw requirements and candidate items from `.codestream/FEATURES.md` and `.codestream/BUGS.md` and setting their status to `IN_PLANNING`.
2. It drafts `.codestream/active/<milestone>_<phase>_feature_spec.md` (e.g. `M4_P3_feature_spec.md` — prior phase files should have been archived at `/steer`) containing: data schema/contracts, pure logic function signatures, and an acceptance-criteria test matrix (each AC must be specific and testable — "works well" is not an acceptance criterion).
3. **Run the plan gate (rule 27) before presenting anything.** `uv run python scripts/check-spec-coverage.py .codestream/active/<milestone>_<phase>_feature_spec.md` must exit 0. It checks two mechanical properties: **coverage** (every addressable binding item — `RA-15`, and `RA-15.a` for sub-items that bind separately — is cited by at least one AC row) and **consistency** (every `AC-N`/`RA-N`/`SG-N`/`N-N` id referenced anywhere resolves, and no two binding items assign different values to the same named quantity). An uncited binding item fails this halt exactly as a failing test fails Layer 1. Report the checker's actual exit code. Do not present a spec it rejects, and do not clear the gate by deleting the binding item — a clause removed to satisfy the checker is the `SILENT DROP` the gate exists to catch.
4. Present the spec and stop with: "Review this feature specification. Reply with SPEC_APPROVED to begin execution."

## Mode B — Amend an approved spec (rule 25)
Use this whenever `/diagnose` returns `spec error`, or Layer 2's Spec Reconciliation returns a clause-level label (`SILENT DROP`, `DEFECTIVE`, `UNVERIFIABLE`, `SCOPE CREEP`). The correction belongs to the **current** phase's spec — the next phase's spec cannot retroactively make this phase's build honest.
1. **Never edit the normative text in place.** Append a numbered entry to the spec's **Amendment Log** below the Approved Baseline: `AM-1`, `AM-2`, … Each entry records the binding-item id it changes (rule 27), the **old text and the new text quoted verbatim**, **why** (the critic finding or `/diagnose` verdict that forced it), and which **AC rows** it adds, re-points, or retires.
2. Leave the baseline untouched — not a typo, not a count, not a clause the build disproved. Superseded text stays readable; a reader resolves the spec by applying the log over the baseline, later entry winning.
3. Re-run the plan gate (rule 27) against the amended document and report its exit code.
4. Present the amendment and stop with: "Review the amendment. Reply with SPEC_APPROVED to begin execution."
5. An amendment takes effect **only** on re-`SPEC_APPROVED` — rule 1 and rule 5 apply to it exactly as they did to the original. If the amendment is clause-level and the AC matrix is otherwise green, the re-entry is **scoped** (rule 28): `/execute` applies only what the amendment authorizes, Layer 1 still runs all four gates in full, and Layer 2 re-audits only the amended clauses plus a regression check on the clauses already labelled `VALIDATED`.

## Halt gate
- Present the spec and stop with: "Review this feature specification. Reply with SPEC_APPROVED to begin execution."
- **MANDATORY TOOL RESTRICTION**: Do NOT invoke any file modification tools (`replace_file_content`, `write_to_file`, `multi_replace_file_content`) on workspace code files. Stop execution immediately and yield the turn to wait for explicit user approval (`SPEC_APPROVED`). Do not proceed to `/execute` under any circumstance until the literal string `SPEC_APPROVED` is received. If the user proposes changes, revise and re-present — do not treat a revision request as approval.
