# SLIPSTREAM

A spec-gated, vertical-slice development framework for Claude Code and Antigravity/Gemini.

Named for the obvious reason: you go faster because the drag is gone. The drag, in agentic development, is rework — and rework comes from exactly two places. You built the wrong thing because nobody wrote down what "right" meant. Or you believed a broken build passed because the only thing that checked it was the same agent that wrote it. SLIPSTREAM is the set of gates that make both of those expensive to do by accident.

It is stack-agnostic. Nothing in the framework assumes a language, runtime, or package manager.

---

## What you get

**Two entry speeds.** Ceremony is matched to uncertainty, not applied uniformly. A raw idea goes through `/prototype` — a fast walking skeleton with minimal process — and gets `/promote`d into the structured lifecycle once it has proven worth building. An idea that is already clear goes straight to `/discover`. And a genuinely small change (rule 7's lightweight-task exception) skips the ceremony entirely; the framework is explicit that you should lean on this readily rather than perform process on a one-line fix.

**Vertical-slice milestones.** Every milestone ships something a user can run. Types-only, backend-only, and UI-only slices are rejected by rule, by the roadmapper agent, and by an anti-pattern table in the roadmap template — because horizontal layering is the most common way a plausible-looking roadmap produces nothing demonstrable for weeks.

**Three-layer verification, with the layers separated on purpose.** Layer 1 (tests + typecheck + build + lint, all four, all by exit code) runs inside `/execute`, which then halts. Layer 2 (an independent critic auditing the build against the approved spec) and Layer 3 (cross-milestone regression) run inside `/steer`, in a fresh context. The separation is deliberate: chaining all three off the end of a build compounds an already-large transcript with two more agent-heavy steps before any human has looked at the result.

**A shared state directory both assistants read.** `.gsd/` holds the roadmap, the active spec, the append-only audit logs, and `STATE.json`. Every state transition is logged with which assistant made it, and a hard-blocking pre-flight check catches the cross-tool desync failures — stale state, duplicate active specs, corrupted JSON — before they compound.

**Failures route by cause, not by symptom.** `/diagnose` sits between any verification failure and any fix, because an implementation bug, a spec error, and a misunderstood intent are repaired at three different layers. Patching at the wrong one reproduces the same class of bug a milestone later.

---

## The lifecycle

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

| Command | State | What it does |
|---|---|---|
| `/onboard` | — | Entry router. Reads existing state, picks the track. |
| `/prototype` | fast track | Walking skeleton, minimal ceremony, explicit validation target. |
| `/promote` | fast track → 0 | Converts a validated prototype into structured discovery + roadmap. |
| `/discover` | 0 | Intent discovery. Halts until every open question is answered. |
| `/map` | 0 → 1 | Audits an existing codebase into a baseline roadmap. |
| `/plan` | 2 | Drafts the feature spec. Halts for literal `SPEC_APPROVED`. |
| `/execute` | 3 | Builds the slice, runs Layer 1, halts. |
| `/steer` | 4 | Runs Layer 2 + 3, then presents the mandatory human checkpoint. |
| `/verify` | — | Standalone Layer-1-only recheck. |
| `/diagnose` | — | Root-cause routing for any failure. |
| `/reset` | — | Safe rollback of code and `.gsd/` state to a clean checkpoint. |
| `/research` | — | Feasibility and trade-off investigation. |
| `/log` | — | Triages bugs into `BUGS.md` and features into `FEATURES.md`. |

---

## Using it on a new project

1. Copy `.claude/`, `.agents/`, `.gsd/`, `CLAUDE.md`, and `.gitignore` into your project root. Merge `.gitignore` rather than overwriting if you already have one.
2. Fill in the **Project-specific context** block at the bottom of `CLAUDE.md` and `AGENTS.md`. The Layer 1 command table is the part that matters most — rule 13 requires all four gates, and the agents need to know what to run. Mark any gate that genuinely doesn't apply as `N/A — <reason>` rather than dropping it silently.
3. Open the project and run `/onboard`.

`.gsd/STATE.json` ships at `current_state: 0` with an empty history, so `/onboard` will route you into the discovery or prototype track cleanly.

---

## Using it on an existing codebase

Same setup, but `/onboard` will detect the existing code and route to the codebase-mapper, which audits what is actually there and proposes a vertical-slice roadmap from the real state of the repo rather than from an imagined greenfield.

---

## Layout

```
CLAUDE.md          Claude Code directives — auto-loaded, embeds a full copy of the hard rules
.claude/
  skills/          13 lifecycle commands
  agents/          11 subagents (mapper, planner, executor, critic, verifier, …)
.agents/
  AGENTS.md        Antigravity/Gemini directives — the same rules, tool-specific names
  skills/          the same lifecycle as Gemini personas
  workflows/       slash-command definitions
.gsd/
  HARD_RULES.md    canonical rules + why each one exists
  STATE.json       live state, provenance-tagged history
  ROADMAP.md       vertical-slice milestone sequence
  DISCOVERY.md     intent questions + answer log
  BUGS.md          defect log
  FEATURES.md      feature & UX backlog
  templates/       blank forms the skills fill in
  active/          the single approved spec being built right now
  archive/         append-only audit trail across the project's lifetime
```

---

## Worked examples

These come from a real 37-milestone project built end to end under this framework. The patterns matter more than the domain.

### Name milestones in the user's voice, not the system's

The single highest-leverage habit. Real milestone titles from that project:

```
Milestone 1: Numbers I can trust
Milestone 2: A recipe library that survives a refresh
Milestone 4: Brew this recipe, log the brew day
Milestone 5.5: A shell that scales past six buttons
```

Every one names an outcome a person would recognize. Compare the titles a layer-based roadmap would have produced — "Calculation engine", "Persistence layer", "Routing and navigation shell" — which describe the same code and demo nothing. When a title only makes sense to someone who has read the source, the milestone boundary is drawn along a layer. Redraw it.

Note `Milestone 5.5`. Decimal insertions are normal and healthy: the shell needed rework before Milestone 6 could land, and renumbering 6-through-N to express that would have been churn. Insert, don't renumber.

### Let phases split, and say so in the roadmap

`Estimated phases` is a guess that `/plan` sharpens. In practice a milestone drafted as one phase becomes two often enough that `/steer` reads the field aloud at every checkpoint ("phase 1 of an estimated 2 — at least one more expected"). Milestone 30 ran four phases; Milestone 5.5 ran five. Nothing went wrong — the estimate did its job, which is to tell the user whether to expect another round, not to be right.

Phases follow the vertical-slice rule too. Splitting M30 into "P1: tokens, P2: primitives, P3: consumers" would have been layering at a smaller scale. What actually shipped:

> **M30_P2 — `ui/` is born with its first real consumer.** Introduces the primitive tree (`FormField`, `Input`, `Select`) *and* immediately re-points the calculator cards onto them, so all ten cards inherit consistent control height, corner radius and focus rings in the same slice.
>
> *Why this satisfies vertical-slice constraints (Hard Rule 2):* shipping a primitive layer with zero consumers is an anti-pattern.

That last line was written into the spec itself. Making the slice argument explicit, in the spec, is what stops a plausible-looking layer from getting approved.

### Write the ambiguities down as binding decisions

The most valuable section of a mature spec is the one that records what was decided and closed. From the same spec:

```
### Resolved Ambiguities (Binding)

RA-1 — Class-merging strategy: zero-dependency variant API.
  No class-merging dependency is added. Primitives manage variants via
  deterministic array filtering: [base, size, className].filter(Boolean).join(' ')

RA-2 — Card-component boundary scope in P2.
  The card's two field wrappers are refactored to consume ui/. The card container
  and result row are left structurally functional; their cleanup is scheduled
  for P3 alongside <Button> and <NumberInput>.
```

RA-2 is doing quiet, important work: it names what is *deliberately not* in this slice and where it went instead. Without that line, the critic in Layer 2 flags an incomplete refactor as a defect, and you spend a `/diagnose` cycle rediscovering a decision you already made.

### Use the lightweight-task exception aggressively

Rule 7 exists because process applied uniformly is process that gets abandoned. A tooltip typo, a threshold constant, a mislabeled column — make the edit, confirm it, move on. No spec, no critic, no steering log.

The tell that you have crossed the line: the change starts touching a second file, or you catch yourself writing "and also update…". That is a slice, not a tweak. Stop and route it back through `/plan`.

### Let `/log` be the inbox, and let milestones drain it

Ideas and defects arrive mid-build, when you are not in a position to act on them. `/log` files them as `FEAT-xxx` or `BUG-xxx` and gets you back to work. Later, `roadmapper` reads both files as candidate material — several real milestones were assembled directly from the backlog and cite it in the title:

```
Milestone 19: Batch planning stage architecture & itemized inventory deduction (FEAT-017, FEAT-018)
Milestone 21: Dedicated water chemistry & acid calculator modal (FEAT-012, FEAT-001)
```

A bug can also justify its own slice when the fix is substantial — `BUG-024`, a numerical accuracy problem, became a two-phase milestone with a bounded least-squares solver, because "fix the bug" was genuinely a milestone's worth of work. What never happens is a catch-all "bug fixing milestone"; that is layering wearing a disguise. Bugs in a working feature get fixed inside the milestone that owns that feature.

### What going off the rails actually looks like

The rules in `HARD_RULES.md` are not hypothetical. Over that project's life, these were caught in the wild:

- **A verification PASS on a build that did not compile.** The pass ran the test suite only. The test runner stripped types without checking them, so a type-contract regression was invisible to it. → Rule 13 now requires all four gates, by exit code.
- **`STATE.json` silently unparseable for an unknown number of sessions.** A tool had pasted a second copy of the document raw into the middle of one entry's string field. Every prior session had "verified UTF-8" and passed, because UTF-8 validity and JSON validity are independent properties. Found by accident. → Rule 10 point 4 now demands a real parse; rule 17 forbids the text-splice write that caused it.
- **A verification report citing a critic entry that was never written.** "PASS, 18/18 ACs", with no backing artifact on disk. → Rule 19 requires reading the report back before citing it.
- **An entire build → audit → steer → plan cycle with zero `state_history` entries** until one retroactive summary at the end. → Rule 18 requires logging each step as it completes.
- **Two sessions on the same state, each assuming the other had finished** — stale pointers, a duplicated active spec, append-only logs overwritten. → Rules 10, 11, 12, 20.

Every one of these was cheap to prevent and expensive to find. That asymmetry is the whole argument for the framework.

### A note on the two-assistant split

If you run both Claude Code and Antigravity/Gemini against one `.gsd/`, rule 6's strict alternation is the rule that will bite you first, and the pre-flight check in rule 10 is what catches it. The soft division of labor in rule 16 — Gemini for `/steer`, triage and small repairs; Claude Code for `/plan` and `/execute` — is a starting default, not a law. If you only use one assistant, delete rule 16 and simplify rule 6 rather than leaving instructions that describe a setup you do not have.

---

## The one thing not to do

Do not weaken a hard rule in the moment because it feels like overhead on this particular change. `.gsd/HARD_RULES.md` opens with a section explaining what each rule cost before it existed — silent state corruption that passed every check, verification theater that reported PASS on a build that did not compile, audit trails written retroactively as narrative. Read that section before deciding a rule does not apply to you. If a rule genuinely doesn't fit your project, change it deliberately in `HARD_RULES.md` and mirror it into both directive files in the same sitting — that is a supported edit. Skipping it quietly is not.
