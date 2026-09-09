---
name: map
description: Use to audit code that already exists — including a validated prototype — and produce a vertical-slice roadmap grounded in what's actually there. Triggered by /map, or automatically as the next step after /onboard's "existing codebase" path or after /promote.
---

# Map: Audit Existing Code → Vertical-Slice Roadmap

**Rule:** Treat existing code as ground truth, not as scaffolding to discard. Never propose a rebuild without a specific, named reason (a security issue, a proven scalability wall) — "it wasn't built with a framework" is not a valid reason on its own.

## What to do

0. **Pre-flight.** If `.slipstream/STATE.json` already exists, run the rule 10 integrity check before anything else. `/map` is often invoked mid-project to re-baseline a roadmap, not only at first onboarding — do not assume you are on a clean slate.

1. Spawn the `codebase-mapper` subagent to audit the repo.

2. `codebase-mapper` runs a stability check first (the project's actual build/test commands, from the Project-specific context block in `CLAUDE.md`), then inventories files, types, tests, and working entry points:
   - If the project doesn't build/run at all, it stops short of feature milestones and proposes **Milestone 0: Stabilization** instead.
   - If it builds/runs with isolated known-broken features, it proceeds to a normal inventory and folds bug fixes into the milestone that owns that feature — never into a catch-all "bug fixing" milestone.

3. Hand the findings to `roadmapper` to produce `.slipstream/ROADMAP.md`. The canonical milestone shape is `.slipstream/templates/ROADMAP_DECOUPLED_TEMPLATE.md` — including its anti-pattern table, which `roadmapper` must self-check against before presenting. Milestone 1 is typically the stabilization slice or "formalize what already works," not a rewrite. Every milestone carries an `Estimated phases` line; `/steer` depends on it to tell the user whether more phases are expected, so it is never left blank.

4. **Write `.slipstream/STATE.json`** through the rule 17 read-parse-mutate-serialize-reparse discipline (never a text splice):
   - `current_state: 1` — a roadmap exists, planning has not begun. Same as `/promote`, and for the same reason: `/map` establishes intent from real code, so State 0 discovery is already effectively satisfied.
   - `gate_approvals.roadmap_approved: false` — the roadmap is drafted, not yet authorized. Step 5's halt is what flips it.
   - `artifacts.roadmap: ".slipstream/ROADMAP.md"`.
   - Append one `state_history` entry for this `/map` completion **now**, before presenting (rule 18), carrying an `"agent"` field (rule 11).
   - Re-read and `JSON.parse` the file before treating the write as complete (rule 17).

## Halt gate

Present the resulting roadmap and **halt** for the user's explicit approval — this is the STATE 1 halt gate, the same one `.slipstream/templates/ROADMAP_DECOUPLED_TEMPLATE.md` carries. Ask plainly: *"Does this milestone sequence capture your vision, and are these boundaries sufficiently flexible?"*

Do not route to `/steer` to obtain this approval. `/steer` opens by spawning `critic` against the approved spec for the active milestone (rule 15 / Layer 2), and at roadmap time no spec and no build exist yet — there is nothing for it to audit. `/steer` is the checkpoint for *completed work*; this is the checkpoint for a *plan*.

On approval: set `gate_approvals.roadmap_approved: true`, append a second `state_history` entry recording the authorization, and only then may `/plan` begin on Milestone 1. Do not auto-advance into `/plan`.
