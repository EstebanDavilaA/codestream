---
name: log
description: Log, track, and structure bug reports into .codestream/BUGS.md and feature requests into .codestream/FEATURES.md via /log. Auto-classifies inputs, tracks lifecycle status, and routes items to /diagnose, /plan, or roadmap sequencing. Ported from the Antigravity/Gemini-side skill so either tool triages logs the same way.
---

# Unified Logger: Log and Categorize Bugs & Features

**Rule:** Every reported issue, broken behavior, feature request, or UX polish idea must be formally logged with structured metadata via `/log`. Defects are written to `.codestream/BUGS.md`, while feature requests/ideas are written to `.codestream/FEATURES.md`.

---

## Process

0. **First action of a session, always**: if `.codestream/STATE.json` already exists, run the pre-flight integrity check (`.codestream/HARD_RULES.md` rule 10) before anything else.

1. **Classification**:
   - **Bug (Implementation Defect / Active Spec Gap)**: Code in a completed/active milestone is broken, miscalculating, or regressing.
     → Log to `.codestream/BUGS.md` as `BUG-xxx`. Initial status: `OPEN`.
   - **Feature (Unbuilt Scope, UX Polish, or Architectural Idea)**: New capability, navigation redesign, layout polish, or future enhancement.
     → Log to `.codestream/FEATURES.md` as `FEAT-xxx`. Initial status: `LOGGED`.

2. **Log Entry Creation (Append-Only)**: Read current target file, generate next sequential ID (`BUG-xxx` or `FEAT-xxx`), and append entry as UTF-8 (`.codestream/HARD_RULES.md` rule 14).

### Entry Templates

**For `.codestream/BUGS.md`**:
```markdown
### [BUG-xxx] <Title>

- **Date Logged:** YYYY-MM-DD
- **Status:** `OPEN`
- **Category:** <Category / Subsystem>
- **Component:** <app or package path> (<Component/File>)
- **Reported Issue:** <Concise problem description>
- **Observed Behavior:** <What actually happens>
- **Expected Behavior:** <What should happen>
- **Triage & Diagnosis:** <Initial root cause or context pointer>
- **Resolution Path:** <Scheduled for Milestone X / Routed to /diagnose / /plan>
```

**For `.codestream/FEATURES.md`**:
```markdown
### FEAT-xxx: <Title>
- **Date Logged**: YYYY-MM-DD
- **Status**: `LOGGED`
- **Category:** <Subsystem / UX / Logic>
- **Summary**: <One-sentence summary of the requested capability or polish>
- **Details**:
  - <Bulleted scope details, constraints, design choices>
```

3. **Status Lifecycle Tracking**:
   - `OPEN` / `LOGGED`: Initial state.
   - `SCHEDULED_MILESTONE (Milestone X)`: Added to `.codestream/ROADMAP.md` during `/roadmap_slices` or `/discover`.
   - `IN_PLANNING`: Included in an active feature spec in `/plan`.
   - `IN_EXECUTION`: Underway in `/execute`.
   - `CLOSED`: Verified complete by the Layer 2 audit and archived during `/steer`.

4. **User Communication**: Present structured summary and routing diagnosis to the user.
