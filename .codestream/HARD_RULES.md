# CODESTREAM Hard Rules — Canonical, Tool-Agnostic

This file is the single source of truth for the framework's non-negotiable rules. Every tool-specific directive file embeds a copy of these rules, because each directive must be self-contained and auto-loaded by its own tool — a pointer alone is not reliably read. The directive files currently shipped are `CLAUDE.md`, `.agents/AGENTS.md`, and `.github/copilot-instructions.md`. **When these rules change, edit this file first, then run `scripts/render-directives.py` to regenerate every directive copy in the same sitting.** If any copy disagrees, this file wins, and the disagreement itself is a bug to fix immediately, not a judgment call to make in the moment.

The mirror is enforced mechanically by `scripts/check-framework.py`: every directive must carry the same rule *numbers* and the same headed-rule *titles*, and each directive's rule section must be byte-identical to what `scripts/render-directives.py` renders **from this file**. A drift that misses a copy therefore fails CI rather than surfacing in a project — and so does a hand-edit inside a directive's `<!-- GENERATED:rules -->` region, because that region is a generated artifact, not a source.

This file is the single authored copy of the rules. The `## Hard rules` section below is rendered verbatim into every directive between those markers, with exactly one per-tool value injected (rule 11's agent id). Everything *above* that heading — this note and the failure table — is deliberately **not** embedded: it is addressed to whoever is maintaining or weakening a rule, not to an agent mid-task, so it stays here rather than paying context rent in every session.

**Adding a new tool does not change these rules.** An agent participates by declaring its own agent id (rule 11) and reading one shared `.codestream/` — there is nothing to add to the rule text itself.

## Why these rules exist

Every rule below was written after a specific failure cost real time. None is a style preference, and none is tool-specific — each closes a gap that was latent in the shared design. **This is the section to read before weakening one.**

| Failure class | What actually happened | Rules |
|---|---|---|
| Cross-tool desync | Two assistants shared one `.codestream/`; `STATE.json` went stale, cumulative audit logs were overwritten instead of appended, specs were written in the wrong encoding, and two "active" specs coexisted with no way to tell which was real | 10, 11, 12, 14, 20 |
| Verification theater | `PASS` reported from the test suite alone, on a build that did not compile — the runner stripped types, so a type-contract regression was invisible to it | 13 |
| Silent state corruption | A raw text paste put a second copy of the document inside one entry's string field. It passed every UTF-8 check, because UTF-8 validity and JSON validity are independent properties. Found by accident, sessions later | 10 (pt 4), 17 |
| Retroactive audit trails | A full build → audit → steer → plan → execute cycle with zero `state_history` entries, plus a verification report citing a critic entry that was never written | 18, 19 |
| Unbounded context cost | `state_history` grew to hundreds of entries, so every pre-flight check paid to load the project's whole lifetime just to read one line | 21 |
| Runaway auto-chaining | A build auto-chained into audit and regression in one continuous context, compounding an already-large transcript with two more agent-heavy steps before any human looked | 15 |
| Spec drift at archive time | A clause the phase *disproved* was archived indistinguishably from one it validated, to be read as precedent by the next project. Same family: a file correct when written and wrong when read, which no check inside `.codestream/` can see | 23, 24 |

Each one was cheaper to prevent than to find. That asymmetry is the whole argument for the rules below.

## Hard rules (non-negotiable regardless of track or tool)

1. No implementation code before either a prototype's validation target is explicit, or a spec is approved with the literal string `SPEC_APPROVED`.
2. Milestones must be **vertical slices** — a user-visible outcome — never a horizontal layer (types-only, backend-only, UI-only).
3. Neither `/execute` nor `/steer` trusts the executor's own tests as proof of correctness. `/execute` runs Layer 1, reports, and halts; `/steer` runs Layer 2 (an independent critic audit against the approved spec) and Layer 3 (a regression pass across all prior milestones) before presenting the checkpoint. Rule 13 defines Layer 1; rule 15 says why Layer 2/3 run where they do.
4. Any verification failure routes through `/diagnose` before any fix is attempted — implementation bug, spec error, and misunderstood intent are fixed at different layers (`/execute`, `/plan`, `/discover` respectively), and patching at the wrong layer tends to reproduce the same class of bug later.
5. `/steer` is a mandatory halt, and the halt is *at* the checkpoint, not before it: never auto-advance *past* `/steer` even when the next step seems obvious, and never stop short of reaching it either.
6. **Strict alternation rule**: `.codestream/` state is shared between assistants. Only one operates on the active phase at a time; check `.codestream/STATE.json` before starting a session — see rule 10 for what "check" concretely means.
7. **Lightweight-task exception**: a small, self-contained edit (numeric/config tweaks, single-file fixes, doc/log corrections) that introduces no new user-visible capability skips the spec/execute/verify/steer ceremony entirely — no spec, no critic, no steering log update. Just make the edit and confirm it with the user. If a "small" change turns out to touch multiple files, cross a milestone boundary, or introduce new behavior, stop and route it back into the normal lifecycle instead. **Lean on this exception readily** — don't default to full ceremony for a genuinely small change just because heavier process is available.
8. Framework paths are protected (`CLAUDE.md`, `.claude/`, `.agents/`, `.github/copilot-instructions.md`, `.codestream/`) — never deleted, moved, or mass-overwritten by any skill, subagent, or scaffolding step under any circumstance, including "clean slate" project scaffolding and full-repo resets. If these paths ever go missing, stop and tell the user immediately rather than proceeding. Renaming one is a deliberate, explicit, user-directed act performed outside any automated step; the two historical renames (`.gsd/` → `.slipstream/` → `.codestream/`) were exactly that, and are not a precedent for a skill to do it on its own.
9. Rule 2 restated, deliberately, because horizontal layering is the most common roadmap mistake. The anti-pattern table and the four axes to split a slice by live in `.codestream/templates/ROADMAP_DECOUPLED_TEMPLATE.md`; a roadmap containing any of its layer-shaped rows is a rule 2 violation.

### 10. Cross-tool pre-flight integrity check — mandatory, hard-blocking

**Run rule 22's template-repo guard before this check.** If it trips, stop here — the four steps below assume this is a real project.

Before taking **any** action in a project where `.codestream/STATE.json` already exists — not only at literal `/onboard`, but at the start of *every* session regardless of which skill is invoked first — check, in order:

1. **Read `.codestream/STATE.json` in full.**
2. **Check the most recent `state_history` entry's `agent` field** (rule 11) and its `state` value. If it names an agent **other than your own** and does not look like a natural halt point (`state: 4` / a `/steer` checkpoint, or an explicit "AWAITING SPEC_APPROVED" / "AWAITING re-SPEC_APPROVED" halt) — **stop and tell the user plainly** before doing anything else, including read-only work. Do not guess whether the other session is "probably done."
3. **Verify `.codestream/active/` contains at most one spec file, and that it matches `artifacts.active_spec`.** If more than one spec file exists, or the pointer doesn't match what's on disk, **stop and flag the discrepancy** rather than silently picking one or archiving the "old" one yourself.
4. **Verify that spec file, and `STATE.json`, are valid UTF-8 text with no encoding corruption, AND that `STATE.json` parses as valid JSON** — an actual `JSON.parse` / `json.load`, not merely a successful text decode. These are independent properties: a file can be perfectly valid UTF-8 while still being structurally broken JSON, and that exact combination has shipped undetected before. Either failure is a cross-tool corruption signal and stops you.

This check is **hard-blocking**: if any of the four steps fails, do not proceed — surface the specific failure to the user and wait for their direction. This is deliberately stricter than a warning, because a warning is easy to skim past under time pressure.

### 11. State provenance

Every `state_history` entry appended to `.codestream/STATE.json` must include an `"agent"` field holding **your own agent id**: a short, stable, lowercase slug you use for yourself, declared in the directive file your tool auto-loads (for the shipped directives: `claude-code`, `antigravity-gemini`, `github-copilot` — examples, not a list).

The framework deliberately does **not** enumerate agents. The field is a self-declared alias, so a tool the framework has never heard of participates simply by writing its own id — no rule change, no registry, no coordination. Two obligations follow from that. Use **one** id consistently, so a reader can attribute history. And never write an id that is not the one you are: a false id is worse than a vague one, because rule 10's pre-flight trusts this field to decide whether another session may still be mid-task, and an entry claiming to be someone it is not silently disables that check.

An entry without this field is itself a rule violation — add it retroactively if you find one missing (don't rewrite the entry's other content, just add the field).

### 12. Archive files are append-only

`.codestream/archive/CRITIC_REPORT.md`, `.codestream/archive/VERIFICATION_REPORT.md`, and `.codestream/archive/STEERING_LOG.md` are cumulative logs across the **entire project's lifetime**, not per-milestone scratch files. Before writing to any of them: read the current file first (if it exists), and **append** a new dated section — never truncate, replace, or overwrite existing content. A tool call that would write the whole file (rather than insert/append) needs the full prior content re-included, not discarded.

### 13. Layer 1 (run by `/execute`) is four gates, not one

"Run the executor's tests" means: the project's test suite **and** typecheck **and** build **and** lint — all four, all reported with their actual exit codes — not just whichever of these the spec's own AC matrix happened to enumerate. A green test suite with a broken build is not a Layer 1 pass.

Substitute the project's real commands for each gate — this framework is stack-agnostic, and a stack without a meaningful "typecheck" or "build" step should say so explicitly in the run rather than silently collapsing four gates into two. Where a gate genuinely does not apply, record "N/A — no build step in this project", not silence.

Note the specific trap: test runners that strip types without checking them (esbuild-based runners and their equivalents in other ecosystems) are *structurally incapable* of catching a type-contract regression. A passing suite under such a runner is not evidence the code typechecks. Layer 1 runs inside `/execute` itself — it is never deferred to a separate step.

### 14. UTF-8, no BOM, for every framework file

Every file this framework writes or edits — feature specs, `STATE.json`, archive logs, `.codestream/BUGS.md`, `.codestream/FEATURES.md` — must be UTF-8 text (BOM-free preferred, but a BOM is recoverable; UTF-16 or other encodings are not acceptable). If a tool's default file-write path produces something else on a given platform, that is a bug in that session to route around (e.g. explicit encoding on write), not an acceptable variance to leave for the next reader to discover.

### 15. `/execute` halts after Layer 1; Layer 2/3 (critic + regression) run inside `/steer`, not auto-chained from `/execute`

Auto-chaining a build straight into audit and regression burns tokens at a high rate: both are agent-heavy, and both would otherwise fire in the same continuous context as the build transcript, before any human has looked at the result.

So `/execute` does not hand off into `/verify` automatically. It reports its Layer 1 result and **halts**, waiting for the user to invoke `/steer`. There is no reflexive critic pass after every build.

`/steer`, before presenting the checkpoint, runs Layer 2 and Layer 3 itself — in a fresh context, not one still carrying the executor's build transcript — and presents the checkpoint in that same turn. If Layer 2 FAILs or Layer 3 finds a regression, route to `/diagnose` instead of presenting the checkpoint.

`/verify` still exists as a standalone, user-invoked Layer-1-only recheck (e.g. re-running tests/typecheck/build/lint after an unrelated environment change) — it is no longer where Layer 2/3 live.

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

The failure it prevents is a one-command trap, not slow drift. Every runtime file under `.codestream/` is git-tracked, so running one feature through `/execute` and `/steer` here accumulates real project content in `STATE.json`, `BUGS.md`, `FEATURES.md`, `DISCOVERY.md`, `ROADMAP.md`, `documents/**`, and the append-only archive logs — content that then ships inside every future project that copies the template. Rule 12 makes the archive logs append-only, so the mistake is also expensive to unwind later. `README.md` explains the mechanism in full; it is not repeated here.

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
