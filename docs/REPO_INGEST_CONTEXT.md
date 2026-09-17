# Repo-Ingest Context — this repository

> **Purpose.** The project-specific half of `/repo-ingest`. The skill holds the *method*; this
> file holds *this repository's data* — what CODESTREAM already covers, the gaps still open, and
> the ledger of repos already reviewed. The skill reads it when it exists and skips it when it
> does not, which is what lets the skill ship downstream while this file stays here.
>
> **Not framework, and not shipped.** It sits outside `.codestream/` deliberately: rule 22's
> integrity check exists to keep that directory pristine so its contents never travel into a
> future project, and a research ledger would. It is also outside the adoption copy list, so it
> does not leave this repo.

## Already covered — do not re-absorb

Process gates · vertical-slice milestone enforcement · state integrity and cross-tool provenance ·
append-only audit archives · Layer 1 four-gate verification (test/typecheck/build/lint, by exit
code) · independent critic audit against spec intent · root-cause routing via `/diagnose` ·
rollback · bug and feature triage (`/log`) · **coding standards and design patterns** (Norms, each
citing an in-repo precedent, each owing an AC row) · **quantified quality constraints**
(Safeguards — perf budgets, exact error contracts, data-integrity invariants, refactor limits) ·
spec reconciliation at archive time (rule 23) · verification against disk rather than context
(rule 24) · milestone sizing by argued phase count against four split axes.

## The gaps still open

Measured by grep; re-verify before trusting these, since a stale measurement has already produced
one wrong finding in this sweep.

Zero hits across the whole framework:

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

## Reviewed so far

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
