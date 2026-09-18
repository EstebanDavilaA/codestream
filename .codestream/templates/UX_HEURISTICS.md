# CODESTREAM UX Heuristic Audit Reference

This reference guides planners (`plan_spec` / `planner`) and executors (`execute_feature` / `executor`) in applying proven usability heuristics to any feature spec that produces user-facing UI, and gives critics (`audit_critic` / `critic`) a checkable audit surface for it.

In CODESTREAM, a UX concern is **not advisory narrative** and **not a subjective taste call**. Under the framework's adoption rule:
> **A UX concern only exists in a slice if it becomes a binding Norm mapped to an Acceptance Criteria row that can fail or that a critic can audit.**

---

## The Heuristic-to-Gate Rule

Whenever a feature renders, updates, or reacts to user-facing UI:

1. **Planner scans the quick-reference table** below and selects the heuristics actually load-bearing for what's being built — not all ten, every time.
2. **Planner declares each in `Norms (Binding)`**, naming the concrete interaction/feedback/error-recovery behavior and the prohibited anti-pattern.
3. **Planner adds at least one AC row** (Test Type: `Verification` for a walkthrough/screenshot, `Structure` for a code-level check like an ARIA attribute or a disabled-state guard) per declared heuristic.
4. **Executor builds to the contract** without taking shortcuts (e.g. no silent failure in place of a visible error, no blocking action with no loading indicator).
5. **Critic (`audit_critic`) audits by exercising the actual behavior** during Layer 2 verification before `/steer` — not by reading the code and inferring compliance — and grades any deviation on the severity scale below.

---

## Severity Scale

Distinct from `critic`'s PASS / PARTIAL / NO verdict on an individual AC row, this grades *how bad* a UX finding is, for prioritizing what `/diagnose` or `/log` picks up first:

- **Critical** — blocks core task completion: no error recovery, no feedback on a destructive/irreversible action, no undo, a WCAG failure that blocks access entirely.
- **Major** — significant friction or confusion: inconsistent patterns across the same flow, an error message that doesn't say what to do next.
- **Minor** — inconvenience with a workaround: missing tooltip, suboptimal tab order, a slightly late loading indicator.
- **Advisory** — enhancement opportunity that doesn't impede task completion.

A `Critical` or `Major` finding routes through `/diagnose` like any other verification failure (rule 4). A `Minor` or `Advisory` finding routes to `/log` as a `FEATURE` entry rather than blocking the checkpoint — see the YAGNI guardrail below for why this project doesn't gate on cosmetic polish.

---

## Quick-Reference: Nielsen's 10 Heuristics + Accessibility Floor

| # | Heuristic | Anti-Pattern to Catch | Typical AC Test Type |
|:--|:---|:---|:---|
| 1 | Visibility of System Status | Async action with no loading/progress indicator; state change with no visible confirmation | `Verification` |
| 2 | Match Between System and the Real World | Jargon, error codes, or internal terminology surfaced directly to the user | `Verification` |
| 3 | User Control and Freedom | No cancel/undo/escape from a multi-step or destructive flow | `Verification` |
| 4 | Consistency and Standards | The same action (e.g. "delete") behaves or is labeled differently across screens | `Structure` |
| 5 | Error Prevention | A destructive action has no confirmation step; a form allows an invalid submission the backend will reject anyway | `Verification` |
| 6 | Recognition Rather Than Recall | User must remember a value shown on a prior screen instead of it staying visible/selectable | `Verification` |
| 7 | Flexibility and Efficiency of Use | No keyboard path or shortcut for a frequent action a mouse-only flow forces | `Verification` |
| 8 | Aesthetic and Minimalist Design | Irrelevant or redundant information competing with the task at hand | `Verification` |
| 9 | Help Users Recognize, Diagnose, and Recover from Errors | Generic error message ("Something went wrong") with no specific cause or next step | `Structure` |
| 10 | Help and Documentation | A non-obvious feature has no in-context help where one is needed to complete the task | `Verification` |
| A11y | Accessibility Floor | Missing ARIA label on an interactive element; focus state not visible; color contrast below WCAG AA; keyboard trap | `Structure` / `Lint` |

---

## Worked Examples

### 1. Visibility of System Status

- **Target Smell:** A button triggers a network request with no visual change until the response resolves; the user clicks again, assuming nothing happened.
- **Spec Norm Declaration Example:**
  > `Norm: All async mutations show a loading state within 100ms of trigger and a success/error confirmation on completion. The trigger control is disabled for the duration of the request. Precedent: .codestream/templates/UX_HEURISTICS.md#1-visibility-of-system-status`
- **Acceptance Criteria Archetype:**
  | ID | Requirement | Test Type | Expected Outcome |
  |:---|:---|:---|:---|
  | AC-UX-1 | Loading Feedback | `Verification` | Triggering [action] shows a spinner/skeleton before the response resolves, and the trigger is disabled while pending |
- **Critic Audit Gate:** Trigger the action (or read the recorded screenshot sequence); confirm a visible state transition occurs before resolution, not just after.

### 2. Help Users Recognize, Diagnose, and Recover from Errors

- **Target Smell:** A failed request surfaces "An error occurred" with no indication of what failed or what the user should do.
- **Spec Norm Declaration Example:**
  > `Norm: Every user-triggered error state names the specific cause and offers a concrete next action (retry, edit the invalid field, contact support), never a bare generic message. Precedent: .codestream/templates/UX_HEURISTICS.md#9-help-users-recognize-diagnose-and-recover-from-errors`
- **Acceptance Criteria Archetype:**
  | ID | Requirement | Test Type | Expected Outcome |
  |:---|:---|:---|:---|
  | AC-UX-2 | Actionable Error Copy | `Structure` | Error-rendering code path references the specific failure reason and a recovery action, not a single hardcoded generic string |
- **Critic Audit Gate:** Force each declared failure mode; confirm the rendered message differs by cause and each names a recovery step.

### 3. Consistency and Standards

- **Target Smell:** Three screens implement "delete" as three different confirmation flows (one inline, one modal, one instant with no confirmation).
- **Spec Norm Declaration Example:**
  > `Norm: Destructive actions across this phase's screens use the shared confirmation-modal component; no screen implements its own inline or instant-delete variant. Precedent: .codestream/templates/UX_HEURISTICS.md#4-consistency-and-standards`
- **Acceptance Criteria Archetype:**
  | ID | Requirement | Test Type | Expected Outcome |
  |:---|:---|:---|:---|
  | AC-UX-3 | Shared Confirmation Pattern | `Structure` | Every destructive-action call site in this phase's diff imports the shared confirmation component; zero bespoke confirmation implementations |
- **Critic Audit Gate:** Grep the diff's destructive-action call sites; reject any that don't route through the shared component.

---

## The YAGNI Guardrail (Rule 7 Alignment)

> [!WARNING]
> **Do not gate on UX polish that has no bearing on task completion.**
> This file exists to catch friction that blocks or confuses users, not to enforce aesthetic taste.
> - A phase with no user-facing UI surface (a CLI tool, a backend-only utility script, a data migration) cites nothing here — there is no interaction to audit.
> - A `Minor` or `Advisory`-grade concern (spacing, tooltip wording, tab order) belongs in `/log` as a `FEATURE` entry, not a blocking Norm — don't force a `SPEC_APPROVED` halt over cosmetic polish.
> - When applying the **lightweight-task exception** ([`.codestream/HARD_RULES.md`](file:///home/eda/Dev/Workspaces/Templates/codestream/.codestream/HARD_RULES.md) Rule 7), skip heuristic extraction and keep changes minimal.
