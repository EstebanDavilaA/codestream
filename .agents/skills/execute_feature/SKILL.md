---
name: execute_feature
description: Technical process instructions for feature execution. Spawned during /execute to build the approved spec's vertical slice, including its own test suite. Its tests are treated as a smoke check only — the critic subagent independently audits against the spec afterward.
---

# Feature Execution Process

Build exactly what the approved spec describes — no more, no less.

## Constraints
- Do not add functionality the spec doesn't describe, even if it seems obviously useful — flag it for a future `/plan` phase instead.
- **Architectural Boundary Adherence**: Strictly respect the architectural patterns and port/adapter boundaries specified in the spec's Norms (referencing `.codestream/templates/DESIGN_PATTERNS.md`). Do not bypass interfaces with direct external I/O calls, do not collapse declared strategies into inline conditional ladders, and do not introduce unmanaged mutable global state. Write unit tests that verify domain logic against mocked abstractions.
- **UX Heuristic Adherence**: Where the spec's Norms cite `.codestream/templates/UX_HEURISTICS.md`, build the named interaction/feedback/error-recovery behavior exactly as specified — do not substitute a simplified state (a silent failure instead of a visible error, a blocking action with no loading indicator) even when it's easier to implement.
- **Refactoring Audit Requirement**: When refactoring state containers or data representations (e.g. per-note to per-beat registration), perform a dedicated codebase audit to locate and purge obsolete registration loops, legacy map alias updates, or side-effect functions that were left behind in prior iterations.
- Write tests that genuinely try to break your own implementation, including the edge cases the spec names — but understand these are a smoke check, not the final verdict. The `audit_critic` skill will independently re-derive acceptance criteria from the spec and audit your implementation without trusting your tests — it now runs inside `/steer`, not immediately after you finish (rule 15).
- If the spec is ambiguous or you find yourself guessing at intent, stop and say so rather than picking an interpretation silently — this is exactly the situation `/diagnose` exists to route correctly.
- **Scoped re-entry (rule 28).** When you are re-entering after an amendment whose AC matrix was otherwise green, apply **only what the amendment authorizes** — the amendment's own text is your authorization list, and nothing outside it is in scope. That scoping applies to the *code you touch*, never to the *gates you run*: Layer 1 still runs all four in full (rule 13), because the four gates are the evidence the amendment broke nothing. Do not treat "only one clause changed" as a reason to run a narrower verification.

## Process
1. Build in this order: data types/contracts → pure logic → tests → any UI/wiring the slice needs, end to end for this slice only.
2. Run refactoring audit to purge leftover legacy alias/registration loops.
3. Verify test suite passes, then run typecheck, build, and lint too — all four gates, all reported by actual exit code (Layer 1, rule 13).
4. Report what was built and Layer 1's results, then **halt** — do not hand off to `/verify` or `audit_critic` automatically. Wait for the user to invoke `/steer`, which now runs the critic audit and regression pass itself before presenting the checkpoint (rule 15).
5. Before halting: append this build's completion (with Layer 1 results) to `.codestream/STATE.json`'s `state_history` as its own entry (agent field set, rule 11) — do this now, not later as part of a bundled end-of-session summary (rule 18). If this session already covered multiple lifecycle steps (a prior `/plan` amendment, a `SPEC_APPROVED`, this build), each one gets logged as its own entry, in order — not folded together. Edit `STATE.json` structurally (read, parse, mutate, serialize) and re-parse it after writing to confirm it's still valid JSON (rule 17).

