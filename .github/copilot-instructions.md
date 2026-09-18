# CODESTREAM — GitHub Copilot (VS Code) Directives

> **Your agent id is `github-copilot`.** Write it to the `agent` field of every `state_history` entry you append (rule 11). The framework never enumerates agents — an id is an alias, so adding a tool changes no rule.

CODESTREAM is a spec-gated, vertical-slice development framework designed to remove the two most expensive kinds of rework: building the wrong thing, and believing a broken build passed. It runs against one shared `.codestream/` state directory, from any assistant that can read these files and write JSON. This file is the Copilot-side copy of the directives; the other shipped copies are `CLAUDE.md` and `.agents/AGENTS.md`.

Two things distinguish it from a plain checklist:
1. **A two-speed entry point** — prototype-first when the idea is still raw, spec-first when it isn't. Ceremony is matched to uncertainty, not applied uniformly.
2. **Vertical-slice milestones with independent verification** — every milestone ships something a user can run, and no build is trusted on the strength of its own author's tests.

**Where Copilot's skills live.** VS Code discovers `SKILL.md` bundles under `.github/skills/`, `.agents/skills/`, and `.claude/skills/`. CODESTREAM's **neutral** layer is `.agents/skills/` — it is read by VS Code Copilot, by Antigravity, and by Codex alike (the cross-vendor `agentskills.io` convention). Use that layer. `.claude/skills/` and `.claude/agents/` are the Claude-specific implementations of the same lifecycle; read them if useful, but do not treat them as the canonical location.

## Protected paths — never delete or overwrite
`CLAUDE.md`, `.claude/`, `.agents/`, `.github/copilot-instructions.md` (this file), and `.codestream/` are the framework itself, not project output. No skill, subagent, or scaffolding step — including `/prototype` and its `prototype_fast` persona — may delete, move, mass-overwrite, or `rm -rf` these paths under any circumstance, including "clean slate" project scaffolding, template initializers (`npm create`, `create-vite`, `cargo new`, `django-admin startproject`, etc.), or full-repo resets. If a scaffolding tool would normally wipe the target directory, run it in a temp directory and copy only the app files in, or scaffold in place file-by-file instead. If these paths ever go missing, stop and tell the user immediately rather than proceeding — do not silently continue.

**Historical exception**: on 2026-09-08 this directory was renamed from `.gsd/` to `.slipstream/` via a deliberate, explicit, user-directed `git mv` (run by the user themselves, outside any automated scaffolding step), immediately followed by a full reference rewrite across every framework file. On 2026-09-17 the project was renamed from SLIPSTREAM to CODESTREAM, renaming `.slipstream/` to `.codestream/` via explicit user instruction, immediately followed by a full reference rewrite across every framework file. This is not a precedent for automated renames — the rule above still blocks any skill, subagent, or scaffolding step from doing this on its own.

## Entry point
Start with `/onboard`. It routes to:
- **`/prototype`** — raw, unvalidated idea. Minimal ceremony, fast walking skeleton.
- **`/discover`** — idea is already validated/clear enough to spec directly.
- **Existing codebase audit** — formalizes what's already there via `map_codebase`.

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

## Hard rules (non-negotiable regardless of track or tool)

1. No implementation code before either a prototype's validation target is explicit, or a spec is approved with the literal string `SPEC_APPROVED`.
2. Milestones must be **vertical slices** — a user-visible outcome — never a horizontal layer (types-only, backend-only, UI-only).
3. Neither `/execute` nor `/steer` trusts the executor's own tests as proof of correctness. `/execute` runs Layer 1 (executor's tests, plus typecheck/build/lint — rule 13) and then halts; `/steer` runs Layer 2 (an independent critic audit against the approved spec) and Layer 3 (a regression pass across all prior milestones) before presenting the steering checkpoint. See rule 15 for why Layer 2/3 moved out of an auto-chain and into `/steer`.
4. Any verification failure routes through `/diagnose` before any fix is attempted — implementation bug, spec error, and misunderstood intent are fixed at different layers (`/execute`, `/plan`, `/discover` respectively), and patching at the wrong layer tends to reproduce the same class of bug later.
5. `/steer` is a mandatory halt. Never auto-advance *past* it, even when the next step seems obvious — but see rule 15: the halt happens *at* the checkpoint, not before reaching it.
6. **Strict alternation rule**: `.codestream/` state is shared between assistants. Only one operates on the active phase at a time; check `.codestream/STATE.json` before starting a session — see rule 10 for what "check" concretely means.
7. **Lightweight-task exception**: a small, self-contained edit (numeric/config tweaks, single-file fixes, doc/log corrections) that introduces no new user-visible capability skips the spec/execute/verify/steer ceremony entirely — no spec, no critic, no steering log update. Just make the edit and confirm it with the user. If a "small" change turns out to touch multiple files, cross a milestone boundary, or introduce new behavior, stop and route it back into the normal lifecycle instead. **Lean on this exception readily** — don't default to full ceremony for a genuinely small change just because heavier process is available.
8. Framework paths are protected (`CLAUDE.md`, `.claude/`, `.agents/`, `.github/copilot-instructions.md`, `.codestream/`) — never deleted, moved, or mass-overwritten by any skill or scaffolding step under any circumstance. If these paths ever go missing, stop and tell the user immediately rather than proceeding. **Historical exception**: on 2026-09-08 this directory was renamed from `.gsd/` to `.slipstream/` via a deliberate, explicit, user-directed `git mv` (run by the user themselves, outside any automated scaffolding step), immediately followed by a full reference rewrite across every framework file. On 2026-09-17 the project was renamed from SLIPSTREAM to CODESTREAM, renaming `.slipstream/` to `.codestream/` via explicit user instruction, immediately followed by a full reference rewrite across every framework file. This is not a precedent for automated renames — the rule above still blocks any skill, subagent, or scaffolding step from doing this on its own.
9. Milestones must be **vertical slices** (restated from rule 2 for emphasis, since horizontal-layer proposals are the single most common roadmap mistake): every milestone produces something a user can run and use, never a types-only/API-only/UI-only slice.

### 10. Cross-tool pre-flight integrity check — mandatory, hard-blocking

**Run rule 22's template-repo guard before this check.** If it trips, stop here — the four steps below assume this is a real project.

Before taking **any** action in a project where `.codestream/STATE.json` already exists — not only at literal `/onboard`, but at the start of *every* session regardless of which skill is invoked first — check, in order:

1. **Read `.codestream/STATE.json` in full.**
2. **Check the most recent `state_history` entry's `agent` field** (rule 11) and its `state` value. If it names an agent **other than your own** and does not look like a natural halt point (`state: 4` / a `/steer` checkpoint, or an explicit "AWAITING SPEC_APPROVED" / "AWAITING re-SPEC_APPROVED" halt) — **stop and tell the user plainly** before doing anything else, including read-only work. Do not guess whether the other session is "probably done."
3. **Verify `.codestream/active/` contains at most one spec file, and that it matches `artifacts.active_spec`.** If more than one spec file exists, or the pointer doesn't match what's on disk, **stop and flag the discrepancy** rather than silently picking one or archiving the "old" one yourself.
4. **Verify that spec file, and `STATE.json`, are valid UTF-8 text with no encoding corruption, AND that `STATE.json` parses as valid JSON** — an actual `JSON.parse` / `json.load`, not merely a successful text decode. These are independent properties: a file can be perfectly valid UTF-8 while still being structurally broken JSON, and that exact combination has shipped undetected before. Either failure is a cross-tool corruption signal and stops you.

This check is **hard-blocking**: if any of the four steps fails, do not proceed — surface the specific failure to the user and wait for their direction. This is deliberately stricter than a warning, because a warning is easy to skim past under time pressure.

### 11. State provenance

Every `state_history` entry appended to `.codestream/STATE.json` must include an `"agent"` field holding **your own agent id**: a short, stable, lowercase slug you use for yourself, declared in the header of the directive file your tool auto-loads.

The framework deliberately does **not** enumerate agents. The field is a self-declared alias, so a tool the framework has never heard of participates simply by writing its own id — no rule change, no registry, no coordination. Two obligations follow from that. Use **one** id consistently, so a reader can attribute history. And never write an id that is not the one you are: a false id is worse than a vague one, because rule 10's pre-flight trusts this field to decide whether another session may still be mid-task, and an entry claiming to be someone it is not silently disables that check.

An entry without this field is itself a rule violation — add it retroactively if you find one missing (don't rewrite the entry's other content, just add the field).

### 12. Archive files are append-only

`.codestream/archive/CRITIC_REPORT.md`, `.codestream/archive/VERIFICATION_REPORT.md`, and `.codestream/archive/STEERING_LOG.md` are cumulative logs across the **entire project's lifetime**, not per-milestone scratch files. Before writing to any of them: read the current file first (if it exists), and **append** a new dated section — never truncate, replace, or overwrite existing content. A tool call that would write the whole file (rather than insert/append) needs the full prior content re-included, not discarded.

### 13. Layer 1 (run by `/execute`) is four gates, not one

"Run the executor's tests" means: the project's test suite **and** typecheck **and** build **and** lint — all four, all reported with their actual exit codes — not just whichever of these the spec's own AC matrix happened to enumerate. A green test suite with a broken build is not a Layer 1 pass.

Substitute the project's real commands for each gate — this framework is stack-agnostic, and a stack without a meaningful "typecheck" or "build" step should say so explicitly in the run rather than silently collapsing four gates into two. Where a gate genuinely does not apply, record "N/A — no build step in this project", not silence.

Note the specific trap: test runners that strip types without checking them (esbuild-based runners and their equivalents in other ecosystems) are *structurally incapable* of catching a type-contract regression. A passing suite under such a runner is not evidence the code typechecks. Layer 1 runs inside `/execute` itself (rule 15) — it is not deferred to a separate `/verify` invocation.

### 14. UTF-8, no BOM, for every framework file

Every file this framework writes or edits — feature specs, `STATE.json`, archive logs, `.codestream/BUGS.md`, `.codestream/FEATURES.md` — must be UTF-8 text (BOM-free preferred, but a BOM is recoverable; UTF-16 or other encodings are not acceptable). If a tool's default file-write path produces something else on a given platform, that is a bug in that session to route around (e.g. explicit encoding on write), not an acceptable variance to leave for the next reader to discover.

### 15. `/execute` halts after Layer 1; Layer 2/3 (critic + regression) run inside `/steer`, not auto-chained from `/execute`

`/execute` does not hand off into `/verify` automatically. After building the slice, it runs Layer 1 itself (tests + typecheck + build + lint, rule 13), reports the result, and **halts** — waiting for the user to explicitly invoke `/steer` when ready to proceed. There is no "reflexive" critic pass after every build.

`/steer`, before presenting the checkpoint, runs Layer 2 (independent critic audit against the approved spec) and Layer 3 (cross-milestone regression) itself, in a fresh context rather than one still carrying the executor's full build transcript. Once Layer 2/3 clear, `/steer` presents the checkpoint in that same turn — do not stop and wait for a second explicit trigger between "Layer 2/3 passed" and the options block; that half of rule 5's halt-at-the-checkpoint (not before it) still applies. If Layer 2 FAILs or Layer 3 finds a regression, route to `/diagnose` instead of presenting the checkpoint.

`/verify` still exists as a standalone, user-invoked Layer-1-only recheck (e.g. re-running tests/typecheck/build/lint after an unrelated environment change) — it is no longer the place Layer 2/3 live.

### 16. Suggested division of labor (soft preference, not enforced)

A documented default, not a restriction — any agent can run any step, and rules 1–15 apply identically regardless of who is doing the work.

Where more than one agent is available, split by **cost profile** rather than by tool name:
- Give the cheap, fast agent `/steer`, state-reading and roadmap/bug triage (`/log`), and lightweight-task-exception repairs (rule 7). Fast turnaround suits this class of work.
- Give the strongest available model `/plan`, `/execute`, and `/steer`'s critic layer for larger multi-file work. The critic especially belongs on the strongest model the project can afford — its entire job is catching what a weaker pass would miss, so cheaping out on it defeats rule 3's premise.

This is a default lean for deciding which agent to open, not a hard boundary, and it never relaxes rules 1–15. Name the agents filling each role per project, or delete this rule entirely if only one agent is in play.

### 17. `STATE.json` is edited structurally, never by raw text paste

Any change to `STATE.json` (or any other framework JSON file) is made by reading the file, parsing it as JSON into an in-memory structure, mutating that structure, and serializing it back out — never by pasting, concatenating, or string-inserting raw text into the file, and never by writing a new document's content into the middle of an existing string field. Immediately after the write, re-read the file and run an actual JSON parse against it before treating the write as complete. If that parse fails, this is a blocking corruption event: stop immediately and report it, rather than leaving a broken file for a future session's rule-10 pre-flight to discover later.

### 18. Log every lifecycle step to `state_history` as it happens, not in a retroactive batch

Every `/plan` draft, every `SPEC_APPROVED` (or re-`SPEC_APPROVED`), every `/execute` completion, every individual `/verify` layer result, and every `/steer` decision gets its own `state_history` entry appended **before moving on to the next step** — including multiple steps completed within one continuous session. Do not defer logging until the session's end, and do not compress several distinct lifecycle steps into a single summary entry written after the fact. An entry written after the work is unverifiable narrative; an entry written as each step completes is the actual audit trail rule 10's pre-flight check depends on.

### 19. A critic-report citation must point at an entry that already exists

Before `VERIFICATION_REPORT.md`'s Layer 2 section cites a dated `CRITIC_REPORT.md` entry (by date, milestone/phase, or verdict), that exact entry must already be written and saved on disk — confirm this by reading `CRITIC_REPORT.md` back, not by assuming the critic step happened because it was supposed to. If Layer 2 was skipped, deferred, or the critic subagent/skill was unavailable in that pass, `VERIFICATION_REPORT.md` must say so plainly ("Layer 2: not run this pass") rather than write a verdict that implies an audit occurred.

### 20. Archiving a spec removes the `active/` copy in the same action

When `/steer` (or the verifier subagent/persona) archives a spec into `.codestream/archive/specs/` at milestone/phase closure, the corresponding copy in `.codestream/active/` is removed as part of that same action — verified afterward by re-listing `.codestream/active/`, not assumed to have succeeded. A byte-identical duplicate left behind in `active/` is exactly the ambiguity rule 10 point 3 exists to catch in whichever session opens next — don't create the ambiguity you already have a rule to detect.

### 21. `state_history` is archived by milestone boundary, not left to grow unbounded

When `/steer` closes out a milestone (not a phase — phases within an open milestone stay inline), move every `state_history` entry belonging to milestones older than the current milestone and the one immediately before it out of `.codestream/STATE.json` and append them to `.codestream/archive/STATE_HISTORY.md`, in the same append-only style as rule 12's other archive files (read the existing archive first, append a new dated section, never truncate). `STATE.json` itself keeps only the current milestone's and the immediately-prior milestone's entries inline. This is a `STATE.json` edit like any other — it goes through rule 17's read-parse-mutate-serialize-reparse discipline, not a text splice.

Rule 10's pre-flight check is unaffected: it only ever needed the *most recent* entry and the top-level `current_state`/`active_milestone`/`active_phase` fields, all of which stay inline. Rule 19's critic-report citation check is unaffected too — citations are verified against `CRITIC_REPORT.md`, not `state_history`.

### 22. The template repo refuses to run its own lifecycle

A `.codestream-template` marker file at the repo root declares "this directory is the framework's own source, not a project built with it." `/onboard` — and the rule 10 pre-flight that gates every session — must abort when that marker is present, before any routing question is asked. Run this check **first**, ahead of rule 10's four integrity steps: it is a single-path existence check, and it gates everything else.

The failure it prevents is a one-command trap, not slow drift. Every runtime file under `.codestream/` is tracked by git — `STATE.json`, `BUGS.md`, `FEATURES.md`, `DISCOVERY.md`, `ROADMAP.md`, `documents/**`, and the append-only archive logs. Run a single feature through `/execute` and `/steer` in the template repo and those files accumulate real project content, which then ships inside every future project that copies the template. Rule 12 makes the archive logs append-only, so the mistake is also expensive to unwind later — you would be manually undoing your own rule.

The marker lives at the repo root rather than inside `.codestream/` deliberately: adoption copies `.codestream/` wholesale, so a flag inside it would travel downstream and block real projects instead of this one. The marker is **not** part of `README.md`'s adoption copy list, and must never be added to it.

Overriding is possible but must be deliberate and session-scoped: the user states explicitly that they intend to dogfood the framework in the template repo. If a downstream project ever shows this marker, it was copied in by mistake — delete the marker there; do not weaken the check here.

### 23. A spec is reconciled against the build before it is archived

Layer 2 audits the build against the spec. Nothing audits the spec against what the build actually proved — and rule 20 then files the spec away byte-identical. The result is that a clause the phase *disproved* is archived indistinguishably from a clause the phase validated: the next project reads both as equally established precedent.

At `/steer`, once Layer 2 and Layer 3 are clear and **before** rule 20's archive step, produce a **Spec Reconciliation** labelling every clause in the closing spec's binding sections (Key Behaviors, Resolved Ambiguities, Norms, Safeguards, Scope Guardrail):

| Label | Meaning | Routes to |
|---|---|---|
| `VALIDATED` | An AC row exists and passed; the clause is unchanged | — |
| `CORRECTED` | The clause had to be amended for the AC to pass — cite both texts | — |
| `DEFECTIVE` | The AC row failed, or the clause was disproved | `/plan` |
| `UNVERIFIABLE` | A binding clause with no AC row | `/plan` |
| `SCOPE CREEP` | Built behaviour that no clause authorises | `/log` |
| `SILENT DROP` | A clause with no built artifact | `/diagnose` |

Two constraints keep this a reconciliation rather than a rewrite:

- **The archived spec's normative text is never edited.** Code does not get to redefine what was asked for. A `DEFECTIVE` or `CORRECTED` clause is fixed in the *next* phase's spec, through `/plan` — never patched in place in the archived copy.
- **A `DEFECTIVE` clause must not become precedent.** It is an open item handed to `/plan` or `/log`, not a closed annotation. Recording the defect and then leaving it in the archive unaddressed is the failure this rule exists to prevent.

The reconciliation is a required section of the critic's report, and rule 19's citation discipline applies to it. That is what makes it enforced rather than advisory: `/steer` cannot assemble `VERIFICATION_REPORT.md` without it.

### 24. Verify from disk, in full — context is not evidence

Rule 10 already applies this discipline to exactly one file: `STATE.json` is re-read and actually parsed, never trusted from an earlier read. Rule 24 generalises it to every artifact. **An artifact is verified from its bytes on disk, read in full, at the moment of verification.**

A file that was correct when written is not evidence it is correct when read. This is not hypothetical — a file edited through an IDE can be silently reverted by a stale editor buffer, leaving it right when written and wrong when read. No check inside `.codestream/` can catch that, because that state does not know what the source tree is supposed to look like. It has already invalidated a run that would otherwise have *looked like a pass*: `/execute` rebuilt a feature that was already committed, the critic audited a pre-built artifact, and every gate reported green.

Partial reading is the same failure one step earlier. A referenced file that was skimmed, summarised, or never opened has not been read — and a binding clause inside it cannot honestly be called honoured or verified. The critic persona's step 2c-ii is this rule applied to a claim's input domain: an AC that spot-checks ordinary values has not established an absolute claim about the whole domain.

This is conduct, not state — no checker can confirm it. Its enforcement is that every verification step in this framework opens by reading its inputs from disk, which rule 10 already demonstrates for one file.

---

**Copilot-specific addendum — not a canonical rule number; it has no counterpart in `.codestream/HARD_RULES.md`.** At any halt gate (`/discover`, `/plan`, `/steer`, `/map`, `/promote`), do not apply edits to workspace source files and do not auto-advance. Present the artifact, state plainly what you are waiting for (usually the literal `SPEC_APPROVED`), and yield the turn to the user. VS Code will happily let you keep editing after presenting a plan; rule 1 and rule 5 are what make that wrong. This is the same constraint the other directives carry under their own tool-specific addenda.

**A note on critic independence (rule 3).** What makes the audit independent is the **context**, not the label: spawn the `critic` subagent, or invoke `audit_critic` in a fresh session — never audit in the context that wrote the code.

---

## Directory reference

```
.codestream/                            ← runtime state; identical for every agent
├── HARD_RULES.md                ← canonical rules, mirrored into every directive
├── STATE.json                   ← every state_history entry carries an "agent" field (rule 11)
├── DISCOVERY.md · ROADMAP.md · BUGS.md · FEATURES.md
├── templates/                   ← blank forms the skills fill in
├── documents/ · scratch/ · drafts/
├── active/                      ← the single approved spec being built right now
└── archive/                     ← append-only audit trail across the project's lifetime

.agents/skills/                  ← THE NEUTRAL SKILL LAYER. VS Code reads this.
├── onboard · diagnose · discover · plan · execute · steer · verify · reset · log
├── research · prototype · promote · extract_template
└── <persona>/SKILL.md           ← the work behind one orchestrator step
                                   (plan_spec, audit_critic, roadmap_slices, …)

.claude/skills/  .claude/agents/ ← the Claude-specific implementation of the same lifecycle
.github/copilot-instructions.md  ← this file
scripts/check-framework.py       ← verifies every directive copy agrees (not copied downstream)
```

## Project-specific context

<!--
FILL THIS IN when you adopt CODESTREAM into a real project. Everything above this
line is framework and should stay stack-agnostic; everything below is yours.
Keep it short — this file is auto-loaded every session.

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
