---
name: reset_checkpoint
description: Technical process instructions for safe reset & state alignment. Spawned during /reset to clean working directory, sync .codestream runtime state, verify baseline health, and document the rollback in state history.
---

# Reset Checkpoint Process

Safely restore codebase and `.codestream/` state to a verified clean point when implementation breaks features or corrupts project health.

## Constraints
- Never execute a hard reset without first logging affected files or confirming uncommitted work is stashed/backed up.
- Ensure `.codestream/STATE.json`, `.codestream/ROADMAP.md`, and active specs in `.codestream/active/` match the restored point (no orphaned active specs pointing to rolled-back code).
- Never report completion until post-reset build & test suite commands are executed and confirmed clean.

## Process

1. **Log Pre-Reset Audit:**
   - Record modified, untracked, and deleted files (`git status --short`).
   - Identify the exact target commit SHA or milestone/phase tag to restore.

2. **Execute Git Restoration:**
   - Execute git reset (`git reset --hard <target_commit>`).
   - Remove untracked build artifacts or transient files if necessary (`git clean -fd` with care, excluding `.codestream/`).

3. **Synchronize `.codestream/` Runtime State:**
   - Append a `RESET` entry to `state_history` in `.codestream/STATE.json` detailing:
     - Timestamp
     - Target commit or milestone/phase restored
     - Reason for reset
     - Restored state gate (`verified`, `steered`, or `reset`)
   - Clean up or archive any obsolete spec files in `.codestream/active/` into `.codestream/archive/pre_reset/` if rolling back before that spec was created.

4. **Verify Baseline Stability:**
   - Run the project's test suite using the command recorded in the project-specific section of `CLAUDE.md` / `AGENTS.md` (rule 13).
   - Ensure 0 test failures and zero build/typecheck errors.

5. **Report & Hand Off:**
   - Present a concise summary of restored files, test suite status, and current state pointer.
   - Hand off to the appropriate lifecycle phase (`/plan`, `/discover`, or `/steer`).
