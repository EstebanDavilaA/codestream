# CODESTREAM

A spec-gated, vertical-slice development framework for AI coding assistants — any of them.

Named for the obvious reason: you go faster because the drag is gone. The drag, in agentic development, is rework — and rework comes from exactly two places. You built the wrong thing because nobody wrote down what "right" meant. Or you believed a broken build passed because the only thing that checked it was the same agent that wrote it. CODESTREAM is the set of gates that make both of those expensive to do by accident.

It is stack-agnostic and tool-agnostic. Nothing in the framework assumes a language, runtime, package manager, or assistant.

---

## What you get

**Two entry speeds.** Ceremony is matched to uncertainty, not applied uniformly. A raw idea goes through `/prototype` — a fast walking skeleton with minimal process — and gets `/promote`d into the structured lifecycle once it has proven worth building. An idea that is already clear goes straight to `/discover`. And a genuinely small change (rule 7's lightweight-task exception) skips the ceremony entirely; the framework is explicit that you should lean on this readily rather than perform process on a one-line fix.

**Vertical-slice milestones.** Every milestone ships something a user can run. Types-only, backend-only, and UI-only slices are rejected by rule, by the roadmapper agent, and by an anti-pattern table in the roadmap template — because horizontal layering is the most common way a plausible-looking roadmap produces nothing demonstrable for weeks.

**Three-layer verification, with the layers separated on purpose.** Layer 1 (tests + typecheck + build + lint, all four, all by exit code) runs inside `/execute`, which then halts. Layer 2 (an independent critic auditing the build against the approved spec) and Layer 3 (cross-milestone regression) run inside `/steer`, in a fresh context. The separation is deliberate: chaining all three off the end of a build compounds an already-large transcript with two more agent-heavy steps before any human has looked at the result. Layer 2's report also carries a **spec reconciliation** (rule 23) — every binding clause labelled `VALIDATED`, `CORRECTED`, `DEFECTIVE`, `UNVERIFIABLE`, `SCOPE CREEP`, or `SILENT DROP` — and `/steer` will not file the spec away without it. **Rule 24** is the same discipline applied to reading: verify each artifact from its bytes on disk, in full, at the moment of verification. Rule 10 already did this for `STATE.json` — re-read it and actually parse it, never trust an earlier read — and rule 24 says do it for everything, because two consecutive dogfood runs were nearly invalidated by a file that was correct when written and wrong when read.

**A shared state directory every assistant reads.** `.codestream/` holds the roadmap, the active spec, the append-only audit logs, and `STATE.json`. Every state transition is logged with the agent id that made it, and a hard-blocking pre-flight check catches the cross-tool desync failures — stale state, duplicate active specs, corrupted JSON — before they compound.

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
| `/reset` | — | Safe rollback of code and `.codestream/` state to a clean checkpoint. |
| `/research` | — | Feasibility and trade-off investigation. |
| `/log` | — | Triages bugs into `BUGS.md` and features into `FEATURES.md`. |
| `/extract-template` | — | Framework maintenance only — see below. |

`/extract-template` is not part of the lifecycle above. It runs entirely outside a project's own `.codestream/` state: it diffs this project's `.claude/`, `.agents/`, and `.codestream/HARD_RULES.md`/`.codestream/templates/` against the upstream template repo, scrubs anything project-identifying, and — after explicit approval — writes the generic improvement back so the *next* project starts from it. It never touches app code, never touches `.codestream/` runtime state, and is exempt from rule 1's `SPEC_APPROVED` gate for the same reason rule 7's lightweight-task exception is: it isn't project output.

---

## Using it on a new project

1. Copy `.claude/`, `.agents/`, `.codestream/`, `CLAUDE.md`, `.github/copilot-instructions.md`, and `.gitignore` into your project root. Merge `.gitignore` rather than overwriting if you already have one. From `.github/`, copy **only** `copilot-instructions.md` — everything else under it (`.github/workflows/`) is template-repo tooling. So are `.codestream-template` and `scripts/`. Copying `.codestream-template` in particular would make `/onboard` refuse to start in your project, because it marks this directory as the framework's own source rather than a project built with it (rule 22).
2. Fill in the **Project-specific context** block at the bottom of every directive you kept — `CLAUDE.md`, `.agents/AGENTS.md`, `.github/copilot-instructions.md`. The Layer 1 command table is the part that matters most — rule 13 requires all four gates, and the agents need to know what to run. Mark any gate that genuinely doesn't apply as `N/A — <reason>` rather than dropping it silently.
3. Open the project and run `/onboard`.

`.codestream/STATE.json` ships at `current_state: 0` with an empty history, so `/onboard` will route you into the discovery or prototype track cleanly.

---

## Using it on an existing codebase

Same setup, but `/onboard` will detect the existing code and route to the codebase-mapper, which audits what is actually there and proposes a vertical-slice roadmap from the real state of the repo rather than from an imagined greenfield.

---

## Session hygiene (recommended, not enforced)

Unlike the hard rules, these aren't things an agent inside the framework can check or self-correct — they're operator habits that keep a long session cheap and the model's context window actually usable. Nothing in `.codestream/` verifies any of this, so it's on you:

- **Start a fresh session (`/clear` or equivalent) between milestones or phases**, not just when the context window forces it. `/execute` and `/steer` are already designed to run in separated contexts for exactly this reason (rule 15) — carrying that discipline into the surrounding session, not just inside the framework's own subagent boundaries, keeps compounding history from becoming the dominant cost.
- **Don't switch models, reasoning-effort levels, or MCP server configuration mid-session.** Each of those invalidates the prompt cache built up so far, so a switch partway through a long `/execute` or `/plan` session quietly multiplies the cost of everything already in context.
- **Watch what's actually landing in context.** Unfiltered CLI output and verbose MCP tool manuals accumulate silently across a session; if a tool's output is large and mostly noise, prefer a form of the command that summarizes or truncates it.

---

## Maintaining this template

This repository is the framework's own source, not a project built with it. Two guards keep those two roles from blurring.

**Rule 22 — the template refuses to run its own lifecycle.** A `.codestream-template` marker at the repo root makes `/onboard`, and the rule 10 pre-flight that gates every session, abort before asking anything. Every runtime file under `.codestream/` is tracked by git, so running even one feature through `/execute` and `/steer` here would write real project content into `STATE.json`, `BUGS.md`, `FEATURES.md`, `DISCOVERY.md`, `ROADMAP.md`, `documents/**`, and the append-only archive logs — content that then ships inside every future project that copies the template. Because rule 12 makes the archive logs append-only, the mistake is also expensive to unwind afterwards. The marker sits at the repo root rather than inside `.codestream/` precisely so that adoption (which copies `.codestream/` wholesale) does not carry it downstream; it is deliberately absent from the copy list above.

**`scripts/check-framework.py` — the integrity check.** No single-file edit can guarantee the invariants this framework depends on, so the script verifies them mechanically:

| Check | Invariant |
|---|---|
| template marker present | rule 22's guard is actually armed |
| protected paths exist | no framework path has gone missing (rule 8) |
| rule mirror agrees | all four directive copies carry the same rule numbers and headed-rule titles (the canonical-source note in `HARD_RULES.md`) |
| headed rule titles match | a renamed rule didn't land in only one copy |
| directive agent ids distinct | each directive declares exactly one agent id, and no two claim the same (rule 11) |
| skill mirror agrees | every `.claude/skills/*/SKILL.md` has its `.agents/skills/*/SKILL.md` counterpart |
| subagent/persona mirror agrees | every `.claude/agents/*.md` has its documented Gemini persona, or is the documented exception |
| STATE.json parses as JSON | valid UTF-8, BOM-free, and a real parse rather than merely a decode (rule 10 point 4 / rule 17) |
| STATE.json still pristine | rule 22's actual invariant: state 0, empty history, no active spec |
| archive logs still pristine | the four append-only logs still contain only their stub sentinel |
| no project residue | no logged bugs/features, no filled-in discovery or roadmap, no `documents/` content |
| no UTF-8 BOM | rule 14 |

```bash
python3 scripts/check-framework.py   # exit 0 = clean, exit 1 = blocker
```

`.github/workflows/framework-integrity.yml` runs the same check on every push and pull request. Neither `scripts/` nor `.github/workflows/` is part of the adoption copy list — downstream projects do not need them. Note that `.github/copilot-instructions.md` **is** adopted; only the workflow directory is not.

Framework changes land on a branch in this repo. Anything that changes agent *behaviour* — a new gate, a new spec section, a reworded skill — should be proven in a throwaway downstream project first, then pushed back here with `/extract-template`, so future projects inherit the version that was actually tested rather than the version that merely looked right.

---

## Layout

```
CLAUDE.md          Claude Code directives — auto-loaded, embeds a full copy of the hard rules
.agents/AGENTS.md  Antigravity/Gemini directives — the same rules, tool-specific names
.github/copilot-instructions.md  VS Code Copilot directives — likewise
                   (every directive declares its own agent id; the rules never enumerate tools)
.codestream-template  marker: this repo is the framework's own source, not a project (rule 22)
scripts/           check-framework.py — template-repo integrity check (not copied downstream)
.github/workflows/ framework-integrity.yml — runs the check on every push and PR
.claude/
  skills/          15 skills: 13 lifecycle commands + /extract-template + /repo-ingest
  agents/          11 subagents, each spawned by exactly one skill above
.agents/
  skills/          25 skills — THE NEUTRAL LAYER. Read by Gemini, by VS Code Copilot,
                    and by Codex alike (the cross-vendor agentskills.io convention):
                    the same lifecycle, plus one persona skill per Claude subagent
.codestream/
  HARD_RULES.md    canonical rules + why each one exists
  STATE.json       live state, provenance-tagged history
  ROADMAP.md       vertical-slice milestone sequence
  DISCOVERY.md     intent questions + answer log
  BUGS.md          defect log
  FEATURES.md      feature & UX backlog
  templates/       blank forms the skills fill in
  documents/       project reference material agents may read
  scratch/         throwaway helper scripts and manifests
  drafts/          ungated spec drafts (never SPEC_APPROVED) — outside the tracked lifecycle
  active/          the single approved spec being built right now
  archive/         append-only audit trail across the project's lifetime
                    (specs/, manual_verification/, pre_reset/, stashed_experiments/,
                     CRITIC_REPORT.md, VERIFICATION_REPORT.md, STEERING_LOG.md, STATE_HISTORY.md)
```

### The 14 Claude Code skills

| Skill | Spawns | Purpose |
|---|---|---|
| `onboard` | `codebase-mapper` (existing-code path) | Entry router — picks prototype, discovery, or codebase-audit track. |
| `prototype` | `prototyper` | Fast walking skeleton from a raw idea; minimal ceremony. |
| `promote` | `codebase-mapper`, `roadmapper` | Formalizes a validated prototype into the structured lifecycle. |
| `discover` | `intent-discoverer` | State 0 — structured discovery document, zero code/architecture. |
| `map` | `codebase-mapper`, `roadmapper` | Audits an existing codebase into a baseline vertical-slice roadmap. |
| `plan` | `planner` | Drafts the feature spec; halts for literal `SPEC_APPROVED`. |
| `execute` | `executor` | Builds the slice, runs Layer 1 (test/typecheck/build/lint), halts. |
| `steer` | `critic`, `verifier` | Runs Layer 2 + 3, presents the mandatory human checkpoint. |
| `verify` | — | Standalone Layer-1-only recheck. |
| `diagnose` | — | Root-cause routing for any verification failure. |
| `reset` | `reset-specialist` | Safe rollback of code and `.codestream/` state to a clean checkpoint. |
| `research` | `researcher`, or `product-strategist` for commercial queries | Feasibility, trade-offs, or market/monetization investigation. |
| `log` | — | Triages bugs into `BUGS.md`, features into `FEATURES.md`. |
| `extract-template` | — | Pushes framework improvements upstream to this template repo. |

### The 11 Claude Code subagents

| Subagent | Model | Spawned by | Does |
|---|---|---|---|
| `intent-discoverer` | sonnet | `/discover` | Converts a project description into a structured discovery doc. Never writes code or proposes architecture. |
| `codebase-mapper` | opus | `/onboard`, `/map`, `/promote` | Audits code that already exists into a vertical-slice roadmap, grounded in what's actually there. |
| `roadmapper` | opus | `/map`, `/promote`, State 1 | Converts discovery answers or a codebase audit into decoupled, vertical-slice milestones. Rejects horizontal layering. |
| `planner` | opus | `/plan` | Drafts the feature spec, including data contracts and the acceptance-criteria matrix `critic` will later audit against. |
| `executor` | sonnet | `/execute` | Builds the approved spec's slice, plus its own smoke-test suite. |
| `critic` | opus | `/steer` (Layer 2) | Independently audits the build against the approved spec's *intent*. Never trusts the executor's own tests as proof. |
| `verifier` | haiku | `/steer` | Compiles the state-of-the-union summary and logs the steering decision. Distinct from `critic`: this one summarizes, it doesn't judge correctness. |
| `reset-specialist` | sonnet | `/reset` | Cleans the working directory, syncs `.codestream/` state, verifies baseline health, documents the rollback. |
| `prototyper` | haiku | `/prototype` | Builds the minimal end-to-end walking skeleton. Optimizes for speed and validation, not completeness. |
| `researcher` | sonnet | `/research` (technical queries) | Inspects codebase state, evaluates feasibility, explores trade-offs — read-only. |
| `product-strategist` | sonnet | `/research` (commercial queries) | Market viability, pricing, positioning, ICP/TAM/SAM, unit economics — a commercial audit, not a technical one. |

The model choice per subagent is deliberate, not a default left unset: `critic`, `planner`, `roadmapper`, and `codebase-mapper` get the strongest model because their entire job is catching what a weaker pass would miss (rule 3's premise — the agent auditing correctness must not be the weak link). `verifier` and `prototyper` get the cheapest model because their jobs are compilation/speed, not judgment. Resist the temptation to downgrade `critic` for cost savings — that's the one subagent where doing so defeats the reason it exists.

### One lifecycle, several agent implementations

The `.codestream/`-gated lifecycle is identical regardless of who runs it. What differs is how each tool models "the substantive work behind a skill". Claude Code has a real subagent-spawning mechanism (the `Agent`/Task tool), so each orchestrating skill hands off to a separate subagent file under `.claude/agents/`. A tool without a spawning primitive represents the same split as a **second skill file** — a "technical process instructions" persona the orchestrating skill invokes as a step, not a tool call. The pairing is 1:1:

| Claude subagent (`.claude/agents/`) | Gemini persona skill (`.agents/skills/`) |
|---|---|
| `intent-discoverer` | `discover_intent` |
| `codebase-mapper` | `map_codebase` |
| `roadmapper` | `roadmap_slices` |
| `planner` | `plan_spec` |
| `executor` | `execute_feature` |
| `critic` | `audit_critic` |
| `verifier` | `verify_steer` |
| `reset-specialist` | `reset_checkpoint` |
| `prototyper` | `prototype_fast` |
| `product-strategist` | `product_strategist` |
| *(none — `researcher`'s job stays inline in `research`)* | *(none)* |

Everything else (`onboard`, `diagnose`, `verify`, `log`, `extract-template`) is self-contained on both sides — no dedicated persona, because the orchestrating skill *is* the whole job. Earlier versions of this framework also shipped `.agents/workflows/*.md` — one-line slash-command stubs that just forwarded `/command $ARGUMENTS` into the matching skill. Antigravity now discovers skills directly, so `workflows/` has been retired; if you're porting an old project forward, deleting its `workflows/` files once the equivalent `.agents/skills/` file exists is a safe, no-op structural cleanup.

**Adding a tool changes no rule.** An agent participates by reading one shared `.codestream/`, declaring its own agent id in the directive file its host auto-loads, and using skills from `.agents/skills/` — the neutral layer. Nothing in the rule text enumerates agents: rule 11's `agent` field is a self-declared alias, and rule 10's pre-flight compares it against **your own** id rather than against a list. So a fourth directive costs two things — the file itself, and one entry in `DIRECTIVES` in `scripts/check-framework.py` so the mirror contract covers it.

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

Sizing is argued, not counted. There is no phases-per-milestone cap, because a number chosen in advance would be arbitrary — the same feature is one phase in a mature codebase and four in a new one. So the roadmap has to *justify* the number against four named split axes: **operation type** (create/read · update/delete · list/search), **complexity** (basic · advanced), **user role** (regular user · admin), and **technical dependency** (core · extension). Those double as the answer to "this slice is too big — split it how?", which the roadmap previously left open: it said only that you may never split by layer, never what to split by instead. `1` on its own is a claim; `1 — one capability, no unmet dependency` is a reason you can disagree with.

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

### Norms and Safeguards: say it, then make it checkable

Two more binding sections exist to close the gap between "we agreed on a standard" and "a different agent can tell whether it was met."

**Norms** name the coding patterns this phase follows, each with a cited precedent. The precedent is the whole point: "follow the existing convention" is unfollowable when the codebase has three conventions. `constructor injection only — precedent: FooService, BarService` gives the executor something to match and the critic something to check. And every norm needs an AC row, because a norm in a binding section with nothing testing it is a claim nobody will ever evaluate.

**Safeguards** apply the same discipline to quality rather than scope — and they have to carry numbers. Compare:

```
- Performance: search should be reasonably fast.
```

with:

```
- Performance: p95 < 200ms for a 1k-row search, measured at the endpoint.
- Error contract: duplicate email returns 409 with {"code":"EMAIL_TAKEN"}.
- Must not change: normalizeQuery() output stays byte-identical — the cache key depends on it.
```

The second set can fail. The first can only be argued about — which means it gets argued about at exactly the worst moment, after the build, when the critic has to decide whether to PASS it.

A Safeguard the spec states but nothing measures is worse than no Safeguard at all, because it looks like coverage. `critic` is instructed to mark such a line PARTIAL rather than assume it holds.

This obligation is not specific to Norms and Safeguards. **Every binding declaration needs an AC row** — Resolved Ambiguities and Out of Scope included — because a binding constraint the AC matrix doesn't test is one the executor can't know it has met.

The failure has a specific shape, and it appeared in this framework's own dogfood run: a spec declared `allowed precision is an integer in range [0, 10]` as binding, then gave AC rows to the negative and non-integer cases but not to the upper bound. The executor implemented exactly what the matrix asked for. `precision = 11` passed silently, and the gap surfaced at Layer 2 as a PARTIAL — after the build — when it would have been a one-line fix at plan time. The constraint was written down. It just wasn't checkable.

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

### A note on running several assistants

If you run more than one assistant against one `.codestream/`, rule 6's strict alternation is the rule that will bite you first, and rule 10's pre-flight is what catches it. The soft division of labor in rule 16 is a starting default, not a law — split by **cost profile**, not by tool name. If you only use one assistant, delete rule 16 and simplify rule 6 rather than leaving instructions that describe a setup you do not have.

---

## The one thing not to do

Do not weaken a hard rule in the moment because it feels like overhead on this particular change. `.codestream/HARD_RULES.md` opens with a section explaining what each rule cost before it existed — silent state corruption that passed every check, verification theater that reported PASS on a build that did not compile, audit trails written retroactively as narrative. Read that section before deciding a rule does not apply to you. If a rule genuinely doesn't fit your project, change it deliberately in `HARD_RULES.md` and mirror it into both directive files in the same sitting — that is a supported edit. Skipping it quietly is not.

---

## License

MIT — see [LICENSE](LICENSE).
