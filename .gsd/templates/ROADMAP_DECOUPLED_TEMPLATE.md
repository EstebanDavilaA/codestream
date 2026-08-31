# ROADMAP: [PROJECT NAME]

## Executive Summary & Product Vision
[Summary of product vision derived from resolved State 0 Discovery]

## Slicing Principles

1. **Vertical slices only (HARD_RULES 2 & 9).** Every milestone delivers a user-visible outcome — something a person can run and use end to end. A milestone that produces only types, only business logic, only UI, or only a persistence driver is not a milestone; it is a layer, and layers are the single most common roadmap mistake. Each slice cuts through *every* layer it needs, thinly.

   > **The test:** can you finish this milestone and demo it to a non-technical user who would recognize that something new works? If no, it is not a slice. "The schema is defined" fails. "You can create a record and see it in the list" passes.

2. **Thin over complete.** A slice's first pass may hardcode, stub, or ignore cases the next slice will handle. Narrow the *scope* of a slice, never its *depth* through the stack.

3. **Reversibility.** Later milestones must not force refactoring of earlier ones. Where a slice needs a decision it cannot yet make well, name the seam explicitly rather than guessing at an abstraction.

4. **Ordered by risk and learning.** Sequence so the slices that would most change the plan if they went badly come early. Cheap, well-understood work goes late.

---

## Decoupled Milestones

> Replace the examples below. They show the *shape* of a vertical slice, not a prescribed sequence — a real roadmap's milestones are specific to the product. Phases (`P1`, `P2`, …) subdivide a milestone when one slice is still too large to build in a single `/execute`; they follow the same vertical-slice rule.
>
> These five fields are the canonical milestone form. `roadmapper` (Claude Code) and `roadmap_slices` (Gemini) both emit exactly this shape, and `/steer` reads `Estimated phases` back out of it — so none of the five may be dropped or renamed.

```
### Milestone N: <short name>
- User-visible outcome: what a person can actually do after this milestone, in one sentence, in their words.
- Builds on: which prior milestone's slice this extends (or "none — first slice").
- Estimated phases: 1  (or "1–2, TBD at /plan" if the slice looks large enough it might split)
- Hardening scope: what gets made production-grade here — types, error handling, tests. Be specific; "polish" is not a scope.
- Verification threshold: a concrete, testable condition — not "works well."
```

**`Estimated phases` is load-bearing, not decorative.** `/steer` reads it at every checkpoint to tell the user whether more phases are still expected in the active milestone ("phase 1 of an estimated 2"). Leaving it blank breaks that readout. It is a first guess, not a promise — `planner` / `plan_spec` sharpen it as scoping clarifies, and milestones drafted as one phase routinely turn out to need two. `/steer` treats it as advisory: Option B (next phase) stays available past the estimate, Option D (complete) stays available before it.

**Two self-checks before you write a milestone down** — these are not fields, they are the questions the fields have to survive:
- *Slice depth:* which layers does this cut through — input → logic → storage → display? If the honest answer is one layer, it is not a slice. Redraw the boundary.
- *Deliberately excluded:* what is hardcoded, stubbed, or deferred in this pass, and to which milestone? A slice with nothing excluded is usually a slice that is too fat to build.

## Anti-patterns — reject these at review

| Proposed milestone | Why it fails | Reslice as |
|---|---|---|
| "Define all data models and schemas" | Types-only. Nothing runs. | Fold the models into the first slice that actually uses them. |
| "Build the core logic engine, zero UI coupling" | Logic-only. Nothing a user can reach. | One user action, driven all the way through the logic to a visible result. |
| "Implement the UI components" | UI-only. Nothing behind it. | One screen wired to real behavior, even if the data is narrow. |
| "Wire up persistence and external services" | Integration-only, deferred to the end — the riskiest work lands last. | Push one real write through the real store in Milestone 1; broaden later. |
| "Testing and polish milestone" | Verification is not a milestone; it is rule 13's Layer 1 inside every `/execute`. | Distribute into the slices whose quality it belongs to. |

---

> **HALT GATE (STATE 1):** Present `.gsd/ROADMAP.md` to the user. Ask: *"Does this milestone sequence capture your vision, and are these boundaries sufficiently flexible?"* Before presenting, self-check every milestone against the anti-pattern table above — a horizontal layer that reaches the user is a rule-2 violation that will cost a reslice later. Wait for explicit user authorization before proceeding to State 2.
