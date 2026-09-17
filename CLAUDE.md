# CODESTREAM — Claude Code Directives

> **Your agent id is `claude-code`.** Write it to the `agent` field of every `state_history` entry you append (rule 11). The framework never enumerates agents — an id is an alias, so adding a tool changes no rule.

CODESTREAM is a spec-gated, vertical-slice development framework designed to remove the two most expensive kinds of rework: building the wrong thing, and believing a broken build passed. It runs against one shared `.codestream/` state directory, from any assistant that can read these files and write JSON.

Two things distinguish it from a plain checklist:
1. **A two-speed entry point** — prototype-first when the idea is still raw, spec-first when it isn't. Ceremony is matched to uncertainty, not applied uniformly.
2. **Vertical-slice milestones with independent verification** — every milestone ships something a user can run, and no build is trusted on the strength of its own author's tests.

## Protected paths — never delete or overwrite
`CLAUDE.md`, `.claude/` (this directory), `.agents/`, `.github/copilot-instructions.md`, and `.codestream/` are the framework itself, not project output. No skill, subagent, or scaffolding step — including `/prototype` and its `prototyper` subagent — may delete, move, mass-overwrite, or `rm -rf` these paths under any circumstance, including "clean slate" project scaffolding, template initializers (`npm create`, `create-vite`, `cargo new`, `django-admin startproject`, etc.), or full-repo resets. If a scaffolding tool would normally wipe the target directory, run it in a temp directory and copy only the app files in, or scaffold in place file-by-file instead. If these paths ever go missing, stop and tell the user immediately rather than proceeding — do not silently continue.

**Historical exception**: on 2026-09-08 this directory was renamed from `.gsd/` to `.slipstream/` via a deliberate, explicit, user-directed `git mv` (run by the user themselves, outside any automated scaffolding step), immediately followed by a full reference rewrite across every framework file. On 2026-09-17 the project was renamed from SLIPSTREAM to CODESTREAM, renaming `.slipstream/` to `.codestream/` via explicit user instruction, immediately followed by a full reference rewrite across every framework file. This is not a precedent for automated renames — the rule above still blocks any skill, subagent, or scaffolding step from doing this on its own.

## Entry point
Start with `/onboard`. It routes to:
- **`/prototype`** — raw, unvalidated idea. Minimal ceremony, fast walking skeleton.
- **`/discover`** — idea is already validated/clear enough to spec directly.
- **Existing codebase audit** — formalizes what's already there via `codebase-mapper`.

## The full lifecycle
```
/onboard → /prototype → (user validates) → /promote ─┐
                                                      │
/onboard → /discover ─────────────────────────────────┼─→ /map → /plan →
                                                                 [SPEC_APPROVED] →
                                       /execute (Layer 1, halts) → user runs /steer ───┐
                                       (Layer 2/3 pass) → checkpoint presented          │
                                       (fail - local) → /diagnose → back to /execute, /plan, or /discover
                                       (fail - widespread) → /reset → clean checkpoint → /plan or /discover
```

## Hard rules (non-negotiable regardless of track)

> **Canonical source: `.codestream/HARD_RULES.md`.** This section is a full copy for auto-load reliability, kept identical (modulo tool-specific names) with every other directive — currently `.agents/AGENTS.md` and `.github/copilot-instructions.md`. If you edit a rule, edit `.codestream/HARD_RULES.md` first, then mirror the change into **all** directive copies in the same sitting. `.codestream/HARD_RULES.md` also documents *why* each rule exists — read that before weakening one. `scripts/check-framework.py` verifies the copies agree on rule numbers and headed-rule titles, so a missed mirror fails CI instead of surfacing in a project.

1. No implementation code before either a prototype's validation target is explicit, or a spec is approved with the literal string `SPEC_APPROVED`.
2. Milestones must be **vertical slices** — a user-visible outcome — never a horizontal layer (types-only, backend-only, UI-only). See `.claude/agents/roadmapper.md`.
3. Neither `/execute` nor `/steer` trusts the executor's own tests as proof of correctness. `/execute` runs Layer 1 (executor's tests, plus typecheck/build/lint — rule 13) and then halts; `/steer` runs Layer 2 (an independent `critic` audit against the approved spec) and Layer 3 (a regression pass across all prior milestones) before presenting the steering checkpoint. See rule 15 for why Layer 2/3 moved out of an auto-chain and into `/steer`.
4. Any verification failure routes through `/diagnose` before any fix is attempted — implementation bug, spec error, and misunderstood intent are fixed at different layers (`/execute`, `/plan`, `/discover` respectively), and patching at the wrong layer tends to reproduce the same class of bug later.
5. `/steer` is a mandatory halt. Never auto-advance *past* it, even when the next step seems obvious — but see rule 15: the halt happens *at* the checkpoint, not before reaching it.
6. **Strict alternation rule**: `.codestream/` state is shared between assistants. Only one operates on the active phase at a time; check `.codestream/STATE.json` before starting a session — see rule 10 for what "check" concretely means.
7. **Lightweight-task exception**: a small, self-contained edit (numeric/config tweaks, single-file fixes, doc/log corrections) that introduces no new user-visible capability skips the spec/execute/verify/steer ceremony entirely — no spec, no critic, no steering log update. Just make the edit and confirm it with the user. If a "small" change turns out to touch multiple files, cross a milestone boundary, or introduce new behavior, stop and route it back into the normal lifecycle instead. **Lean on this exception readily** — don't default to full ceremony for a genuinely small change just because heavier process is available.
8. **Framework paths are protected** (see "Protected paths" above). This overrides any instinct to regenerate/reset the project directory during prototyping or scaffolding.
9. Milestones must be **vertical slices** (restated from rule 2 for emphasis, since horizontal-layer proposals are the single most common roadmap mistake): every milestone produces something a user can run and use, never a types-only/API-only/UI-only slice.

### 10. Cross-tool pre-flight integrity check — mandatory, hard-blocking
**Run rule 22's template-repo guard before this check.** If it trips, stop here — the four steps below assume this is a real project.

Before taking **any** action in a project where `.codestream/STATE.json` already exists — not only at literal `/onboard`, but at the start of *every* session regardless of which skill is invoked first — check, in order: (1) read `.codestream/STATE.json` in full; (2) check the most recent `state_history` entry's `agent` field (rule 11) and `state` value — if it names an agent **other than your own** and doesn't look like a natural halt point (`state: 4`, or an "AWAITING SPEC_APPROVED"/"AWAITING re-SPEC_APPROVED" halt), **stop and tell the user plainly** before doing anything else, including read-only work; (3) verify `.codestream/active/` holds at most one spec file matching `artifacts.active_spec` — if not, **stop and flag it** rather than silently picking one; (4) verify that spec file and `STATE.json` are valid UTF-8 AND that `STATE.json` parses as valid JSON — an actual parse, not merely a UTF-8 decode; these are independent failure modes, and a file can pass one while failing the other. This is **hard-blocking**: a warning is easy to skim past under time pressure, and this exact failure mode has cost real time before (see `.codestream/HARD_RULES.md`, "Why these rules exist").

### 11. State provenance
Every `state_history` entry appended to `.codestream/STATE.json` must include an `"agent"` field holding **your own agent id** — here, `claude-code`. The framework does not enumerate agents: the value is a self-declared alias, so any tool participates by writing its own. Use one id consistently, and never write an id that is not the one you are — rule 10 reads this field to decide whether another session may still be mid-task, so a false id silently disables that check. Add it retroactively if you find an entry missing it.

### 12. Archive files are append-only
`.codestream/archive/CRITIC_REPORT.md`, `VERIFICATION_REPORT.md`, and `STEERING_LOG.md` are cumulative logs across the entire project's lifetime. Read the current file first, then **append** a new dated section — never truncate or overwrite existing content.

### 13. Layer 1 (run by `/execute`) is four gates, not one
"Run the executor's tests" means the test suite **and** typecheck **and** build **and** lint — all four, all reported by exit code — not just whichever the spec's own AC matrix happened to enumerate. A green test suite with a broken build is not a Layer 1 pass. Substitute this project's real commands for each gate; where a gate genuinely doesn't apply to the stack, record "N/A — no build step in this project" rather than silently dropping it. Note the specific trap: test runners that strip types without checking them (esbuild-based runners and their equivalents in other ecosystems) are structurally incapable of catching a type-contract regression. Layer 1 runs inside `/execute` itself (rule 15) — it is not deferred to a separate `/verify` invocation.

### 14. UTF-8, no BOM, for every framework file
Specs, `STATE.json`, archive logs, `.codestream/BUGS.md`, `.codestream/FEATURES.md` — all UTF-8 text. If a tool's file-write path defaults to something else on a given platform, that's a bug in that session to route around, not a variance to leave for the next reader to discover.

### 15. `/execute` halts after Layer 1; Layer 2/3 (critic + regression) run inside `/steer`, not auto-chained from `/execute`
Auto-chaining `/execute` straight into `/verify` (which immediately spawned `critic`) burns tokens at a high rate: the critic audit and the regression pass fire in the same continuous context as the entire build, compounding an already-large transcript with two more agent-heavy steps before any human has looked at the result.

So `/execute` does not hand off into `/verify` automatically. After building the slice, it runs Layer 1 itself (tests + typecheck + build + lint, rule 13), reports the result, and **halts** — waiting for the user to explicitly invoke `/steer` when ready to proceed. There is no reflexive critic pass after every build.

`/steer`, before presenting the checkpoint, runs Layer 2 (independent `critic` audit against the approved spec) and Layer 3 (cross-milestone regression) itself, in a fresh context rather than one still carrying the executor's full build transcript. Once Layer 2/3 clear, `/steer` presents the checkpoint in that same turn — do not stop and wait for a second explicit trigger between "Layer 2/3 passed" and the options block; that half of rule 5's halt-at-the-checkpoint (not before it) still applies. If Layer 2 FAILs or Layer 3 finds a regression, route to `/diagnose` instead of presenting the checkpoint.

`/verify` still exists as a standalone, user-invoked Layer-1-only recheck — it is no longer the place Layer 2/3 live.

### 16. Suggested division of labor (soft preference, not enforced)
A documented default, not a restriction — any agent can run any step, and it never relaxes rules 1–15. Where more than one agent is available, split by **cost profile** rather than by tool name: give the cheap, fast agent `/steer`, state-reading and roadmap/bug triage (`/log`), and lightweight-task-exception repairs (rule 7); give the strongest available model `/plan`, `/execute`, and `/steer`'s critic layer. The critic especially belongs on the strongest model the project can afford — its entire job is catching what a weaker pass would miss, so cheaping out on it defeats rule 3's premise. Name the agents filling each role per project, or delete this rule entirely if only one agent is in play.

### 17. `STATE.json` is edited structurally, never by raw text paste
Any change to `STATE.json` (or any other framework JSON file) is made by reading the file, parsing it as JSON, mutating the in-memory structure, and serializing it back out — never by pasting, concatenating, or string-inserting raw text into the file, and never by writing a new document's content into the middle of an existing string field. Immediately after the write, re-read the file and run an actual JSON parse against it before treating the write as complete. If that parse fails, this is a blocking corruption event: stop immediately and report it, rather than leaving a broken file for a future session's rule-10 pre-flight to discover later.

### 18. Log every lifecycle step to `state_history` as it happens, not in a retroactive batch
Every `/plan` draft, every `SPEC_APPROVED` (or re-`SPEC_APPROVED`), every `/execute` completion, every individual `/verify` layer result, and every `/steer` decision gets its own `state_history` entry appended **before moving on to the next step** — including multiple steps completed within one continuous session. Do not defer logging until the session's end, and do not compress several distinct lifecycle steps into a single summary entry written after the fact. An entry written after the work is unverifiable narrative; an entry written as each step completes is the actual audit trail rule 10's pre-flight check depends on.

### 19. A critic-report citation must point at an entry that already exists
Before `VERIFICATION_REPORT.md`'s Layer 2 section cites a dated `CRITIC_REPORT.md` entry (by date, milestone/phase, or verdict), that exact entry must already be written and saved on disk — confirm by reading `CRITIC_REPORT.md` back, not by assuming the critic step happened because it was supposed to. If Layer 2 was skipped, deferred, or the `critic` subagent was unavailable in that pass, `VERIFICATION_REPORT.md` must say so plainly ("Layer 2: not run this pass") rather than write a verdict that implies an audit occurred.

### 20. Archiving a spec removes the `active/` copy in the same action
When `/steer` (or the `verifier` subagent) archives a spec into `.codestream/archive/specs/` at milestone/phase closure, the corresponding copy in `.codestream/active/` is removed as part of that same action — verified afterward by re-listing `.codestream/active/`, not assumed to have succeeded. A byte-identical duplicate left behind in `active/` is exactly the ambiguity rule 10 point 3 exists to catch in whichever session opens next.

### 21. `state_history` is archived by milestone boundary, not left to grow unbounded
When `/steer` closes out a milestone (not a phase — phases within an open milestone stay inline), move every `state_history` entry belonging to milestones older than the current milestone and the one immediately before it out of `.codestream/STATE.json` and append them to `.codestream/archive/STATE_HISTORY.md`, in the same append-only style as rule 12's other archive files. `STATE.json` keeps only the current and immediately-prior milestone's entries inline. This is a `STATE.json` edit like any other — it goes through rule 17's read-parse-mutate-serialize-reparse discipline, not a text splice. Rule 10's pre-flight only ever needed the most recent entry plus the top-level state fields, both of which stay inline, so this doesn't weaken it.

### 22. The template repo refuses to run its own lifecycle

A `.codestream-template` marker file at the repo root declares "this directory is the framework's own source, not a project built with it." `/onboard` — and the rule 10 pre-flight that gates every session — must abort when that marker is present, before any routing question is asked. Run this check **first**, ahead of rule 10's four integrity steps: it is a single-path existence check, and it gates everything else.

The failure it prevents is a one-command trap, not slow drift. Every runtime file under `.codestream/` is tracked by git — `STATE.json`, `BUGS.md`, `FEATURES.md`, `DISCOVERY.md`, `ROADMAP.md`, `documents/**`, and the append-only archive logs. Run a single feature through `/execute` and `/steer` in the template repo and those files accumulate real project content, which then ships inside every future project that copies the template. Rule 12 makes the archive logs append-only, so the mistake is also expensive to unwind later — you would be manually undoing your own rule.

The marker lives at the repo root rather than inside `.codestream/` deliberately: adoption copies `.codestream/` wholesale, so a flag inside it would travel downstream and block real projects instead of this one. The marker is **not** part of `README.md`'s adoption copy list, and must never be added to it.

Overriding is possible but must be deliberate and session-scoped: the user states explicitly that they intend to dogfood the framework in the template repo. If a downstream project ever shows this marker, it was copied in by mistake — delete the marker there; do not weaken the check here.

### 23. A spec is reconciled against the build before it is archived

Layer 2 audits the build against the spec; nothing audits the spec against what the build *proved*, and rule 20 then files the spec away byte-identical — so a clause the phase disproved is archived indistinguishably from one it validated.

At `/steer`, once Layer 2 and Layer 3 are clear and **before** rule 20's archive step, label every clause in the closing spec's binding sections (Key Behaviors, Resolved Ambiguities, Norms, Safeguards, Scope Guardrail): `VALIDATED` (AC passed, clause unchanged) · `CORRECTED` (clause amended for the AC to pass — cite both texts) · `DEFECTIVE` (AC failed, or clause disproved → `/plan`) · `UNVERIFIABLE` (binding clause with no AC row → `/plan`) · `SCOPE CREEP` (built behaviour no clause authorises → `/log`) · `SILENT DROP` (clause with no built artifact → `/diagnose`).

The archived spec's normative text is never edited — code does not get to redefine what was asked for. A `DEFECTIVE` clause is fixed in the *next* phase's spec via `/plan`, and must not be left in the archive as precedent. The reconciliation is a required section of the `critic` subagent's report (rule 19's citation discipline applies), which is what makes it enforced rather than advisory: `/steer` cannot assemble `VERIFICATION_REPORT.md` without it.

### 24. Verify from disk, in full — context is not evidence

Rule 10 applies this to exactly one file (`STATE.json` is re-read and actually parsed, never trusted from an earlier read). Rule 24 applies it to every artifact: **verify from the bytes on disk, read in full, at the moment of verification.**

A file correct when written is not evidence it is correct when read — an IDE can silently revert it via a stale editor buffer. That has already invalidated a run that would otherwise have *looked like a pass*: `/execute` rebuilt a feature that was already committed, the `critic` subagent audited a pre-built artifact, and every gate reported green. Partial reading is the same failure one step earlier: a referenced file that was skimmed, summarised, or never opened has not been read, and a binding clause inside it cannot honestly be called verified. Step 2c-ii is this rule applied to a claim's input domain.

Conduct, not state — no checker can confirm it. Its enforcement is that every verification step opens by reading its inputs from disk; rule 10 is the worked example.

## Directory reference

```
.claude/
├── skills/
│   ├── onboard/SKILL.md
│   ├── prototype/SKILL.md      ← fast track
│   ├── promote/SKILL.md        ← prototype → structured handoff
│   ├── discover/SKILL.md       ← State 0
│   ├── map/SKILL.md            ← existing-codebase audit → roadmap
│   ├── plan/SKILL.md           ← State 2
│   ├── execute/SKILL.md        ← State 3
│   ├── verify/SKILL.md         ← Layer 1 standalone recheck
│   ├── diagnose/SKILL.md       ← root-cause routing
│   ├── steer/SKILL.md          ← State 4 (runs Layer 2/3)
│   ├── research/SKILL.md       ← feasibility & trade-offs
│   ├── reset/SKILL.md          ← state & code rollback
│   └── log/SKILL.md            ← .codestream/BUGS.md & .codestream/FEATURES.md triage
└── agents/
    ├── codebase-mapper.md
    ├── intent-discoverer.md
    ├── prototyper.md
    ├── product-strategist.md    ← positioning & scope pressure-testing
    ├── roadmapper.md            ← vertical-slice enforcement
    ├── planner.md
    ├── executor.md
    ├── critic.md                ← independent correctness audit
    ├── verifier.md              ← steering-log summarizer
    ├── researcher.md            ← feasibility & prompt refinement
    └── reset-specialist.md      ← safe rollback & state alignment
```

```
.codestream/                            ← runtime state, unchanged across IDEs
├── HARD_RULES.md                ← canonical rules, mirrored into CLAUDE.md/AGENTS.md
├── STATE.json                   ← every state_history entry carries an "agent" field (rule 11)
├── DISCOVERY.md
├── ROADMAP.md
├── BUGS.md                      ← defect log (either tool)
├── FEATURES.md                  ← feature & UX backlog (either tool)
├── templates/                   ← blank forms the skills fill in
├── documents/                   ← project reference material agents may read
├── scratch/                     ← throwaway helper scripts and manifests
├── drafts/                      ← ungated spec drafts (never SPEC_APPROVED) — not part of the tracked lifecycle
├── active/                      ← only what's needed to build the NEXT thing — the only place agents read from
│   ├── <milestone>_<phase>_feature_spec.md  ← current phase's approved spec (name tracked in STATE.json's artifacts.active_spec)
│   └── manual_verification/     ← current milestone's in-progress screenshot evidence
└── archive/                     ← historical record, kept on disk, not auto-read by agents
    ├── specs/                   ← completed milestones' specs
    ├── manual_verification/<milestone>_<phase>/
    ├── CRITIC_REPORT.md         ← cumulative log across all milestones
    ├── VERIFICATION_REPORT.md   ← cumulative log across all milestones
    ├── STEERING_LOG.md          ← cumulative log across all milestones
    └── STATE_HISTORY.md         ← state_history entries retired per rule 21
```

`critic` reads only the single spec file in `.codestream/active/` (never a glob over historical specs). `verifier` moves the outgoing spec and manual-verification evidence into `archive/` at `/steer`, once a milestone/phase genuinely closes.

## Project-specific context

<!--
FILL THIS IN when you adopt CODESTREAM into a real project. Everything above this
line is framework and should stay stack-agnostic; everything below is yours.

Suggested contents — keep it short, this file is auto-loaded every session:

  ### What this project is
  One or two sentences. What it does, who for.

  ### Stack & layout
  Language, framework, package manager, monorepo shape, where the app code lives.

  ### Layer 1 commands (rule 13 — all four gates)
  - test:      <command>
  - typecheck: <command>
  - build:     <command>
  - lint:      <command>
  Mark any gate that genuinely doesn't apply as "N/A — <reason>".

  ### Domain vocabulary
  Terms an agent would otherwise guess wrong.

  ### Known constraints
  Things that must stay true — deployment targets, data shapes, external contracts.
-->
