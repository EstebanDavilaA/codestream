---
name: verify
description: Standalone, user-invoked Layer-1-only recheck (tests, typecheck, build, lint). Use to re-confirm a build is still green after an unrelated environment or dependency change. The critic audit and regression pass no longer run here — they run inside /steer, right before the steering checkpoint (.codestream/HARD_RULES.md rule 15).
---

# Layer 1 Recheck

**Rule:** This skill is Layer 1 only. `/execute` already runs Layer 1 once as part of building the slice and halts on completion — you normally don't need to invoke `/verify` separately. Use it standalone when something outside the build itself might have changed (dependency bump, environment change, a fix applied by hand) and you want to re-confirm the four gates are still green before running `/steer`.

## What to do
Run the test suite, typecheck, build, and lint — all four, every time, each reported by actual exit code (`.codestream/HARD_RULES.md` rule 13). Do not stop at "tests pass."

## Verdict logic
- All four clear → tell the user Layer 1 is green and that `/steer` is next (it runs the critic audit and regression pass itself before presenting the checkpoint).
- Any gate fails → do not proceed to `/steer`. Route through `/diagnose` before any fix (rule 4) — the cause decides whether it returns to `executor`/`/execute` or goes up to `planner`/`/plan`.

## Note
Layer 2 (independent critic audit) and Layer 3 (cross-milestone regression) are no longer part of this skill — they run inside `/steer`, in a fresh context, right before the steering checkpoint is presented. This keeps the expensive critic pass decoupled from the executor's context and under explicit user control (rule 15).
