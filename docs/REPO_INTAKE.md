# CODESTREAM Repo-Intake Brief

> **Purpose.** A standing brief for the research sweep that improves this template. Feed the
> agent a repo (GitHub URL or local path) one at a time; it returns the analysis in the shape
> defined in §5, filtered by §1's rule.
>
> **How to invoke.** Type `/repo-intake <repo>` in chat — that skill (`.github/skills/repo-intake/`)
> reads this file and follows it. This document is the content; the skill is only the trigger, so
> never maintain the two in parallel.
>
> **Not framework.** This file is a working document for improving the template. It is
> deliberately outside `.codestream/` — rule 22's integrity check verifies that directory stays
> pristine so its contents do not ship into every future project, and a research brief would.
> It is also outside the adoption copy list (`.claude/`, `.agents/`, `.codestream/`, `CLAUDE.md`,
> `.github/copilot-instructions.md`, `.gitignore`), so it does not travel downstream.

## 1. What is being improved, and the one filter that matters

**CODESTREAM** is a spec-gated, vertical-slice development framework for AI coding assistants.
24 hard rules in `.codestream/HARD_RULES.md`, mirrored into four directive files
(`CLAUDE.md`, `.agents/AGENTS.md`, `.github/copilot-instructions.md`, plus the canonical file).
Lifecycle: `/onboard → /prototype → /promote`, or `/onboard → /discover → /map → /plan →
[SPEC_APPROVED] → /execute → /steer`; plus `/verify`, `/diagnose`, `/reset`, `/log`, `/research`.

**The filter.** CODESTREAM is a *state machine*, not a knowledge base — a set of gates that block
progress plus artifacts that must be filled in. So an idea from a repo only transfers if it can
become **a gate** (something that can fail) or **a checkable artifact section** (something a critic
can audit).

This is why open-spdd's Norms and Safeguards landed — they became binding spec sections with an
AC-mapping obligation — while its 7-dimension canvas did not. Advice that cannot fail is advice
the framework already has too much of.

## 2. Already covered — do not re-absorb

Process gates · vertical-slice milestone enforcement · state integrity and cross-tool provenance ·
append-only audit archives · Layer 1 four-gate verification (test/typecheck/build/lint, by exit
code) · independent critic audit against spec intent · root-cause routing via `/diagnose` ·
rollback · bug and feature triage (`/log`) · **coding standards and design patterns** (Norms, each
citing an in-repo precedent, each owing an AC row) · **quantified quality constraints**
(Safeguards — perf budgets, exact error contracts, data-integrity invariants, refactor limits) ·
spec reconciliation at archive time (rule 23) · verification against disk rather than context
(rule 24) · milestone sizing by argued phase count against four split axes.

## 3. The gaps being hunted

Measured by grep, still zero hits across the whole framework:

- **Visual experience** — accessibility/WCAG, color, typography, spacing and scale, design systems,
  component patterns. `design` appears ~10× but only as the English verb ("designed to").
- **Product design** — user journeys, information architecture, interaction patterns,
  empty/loading/error states, onboarding.
- **Marketing** — copywriting, positioning, launch. `product_strategist` exists but only as a
  read-only audit at `/research` time; it is wired into nothing.
- **Market research** — competitor analysis, ICP/TAM/SAM. Likewise reachable only through that one
  read-only skill.

**The asymmetry worth exploiting:** visual quality already has a place to *land evidence* —
`.codestream/active/manual_verification/` captures screenshots and archives them — but it has **no
standard to verify against**. A repo that supplies that standard is a strong hit.

## 4. Input

A repo — GitHub URL or local path. One at a time. No other context needed; the reading is the
agent's job.

## 5. Output contract

1. **What it is** — the mechanism, not the marketing. What actually ships.
2. **Absorb** — specific ideas, each named with *which gate or artifact section* it becomes. If an
   idea cannot become one, say so plainly instead of describing it glowingly.
3. **Avoid** — what not to take, and why. Especially anything contradicting rule 7
   (lightweight-task exception) or rule 15's context-cost reasoning.
4. **Relevance against the five goals** — coding standards, design patterns, visual experience,
   product design, marketing and market research. Name which it hits and which it is irrelevant to.
   A strong repo for two goals and useless for three is a normal result, not a failure.
5. **Honest verdict** — partial credit where earned. open-spdd scored 2 of 5 and that was recorded.

## 6. Rules of the analysis

- **Evidence, not impressions.** Cite files and paths. Re-verify a claim rather than reusing a
  cached measurement — a stale grep has already produced one wrong finding in this sweep.
- **Verify the gap still exists** before claiming the template lacks something. Grep first.
- **Flag provenance.** Anything that changes agent behaviour is labelled *dogfood-validated* or
  *derived-from-evidence*. Nothing silently reads as tested.
- **Do not propose speculatively.** If an idea needs a scoping decision first, name the decision.
- **No bloat.** open-spdd ships 58–77KB single-file artifacts; the whole of `HARD_RULES.md` is
  ~9KB. That is a deliberate constraint, not an accident.

## 7. Reviewed so far

### `gszhangwei/open-spdd` — done

7 of 8 absorbable items landed:

| Item | Landed as |
|---|---|
| `/spdd-sync` reverse flow | Rule 23 — spec reconciled against the build before archiving |
| Context-integrity guardrails | Rule 24 — verify from disk, in full |
| Norms as a spec section | Binding section, each owing an AC row |
| Quantified Safeguards | Binding section, verified literally by the critic |
| Sync-priority table | Folded into rule 23 |
| INVEST sizing method | Four split axes; phase count must be argued |
| dry-run / print-plan | `verify_steer` + `verifier` (half — `/reset` still open) |
| File naming with action type | Skipped — assessed marginal |

Deliberately rejected: the full 7-dimension canvas (rule 7), artifact sizes (rule 15), prose-only
enforcement, self-review without authority separation (rule 3), `/spdd-reverse` as a routine
direction (lossy), and six drifting template copies (solved instead via the tool-agnostic agent
alias).

### Not yet reviewed

Every other repo. The sweep is 1 of N.
