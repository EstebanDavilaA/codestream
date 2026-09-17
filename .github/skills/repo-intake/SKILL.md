---
name: repo-intake
description: Use when the user supplies a repo (GitHub URL or local path) to evaluate for improving the CODESTREAM template. Reads docs/REPO_INTAKE.md and returns what the repo actually does, what to absorb and as which gate or artifact section, what to avoid, and which of the five goals it serves.
---

# Repo intake

The user hands over a repo — a GitHub URL or a local path, one at a time. Invoke as
`/repo-intake <repo>` or `/repo-intake` and paste the repo into the chat.

## What to do

1. Read `docs/REPO_INTAKE.md` (path is repo-root-relative) **in full, from disk** — this is the
   standing brief, and rules 23/24 apply to it as much as to any artifact. It holds the filter
   (§1), what the template already covers, so nothing gets re-absorbed (§2), the gaps actually
   being hunted (§3), the output contract (§5), the rules of the analysis (§6), and the ledger of
   what has already been reviewed (§7).
2. Read the repo. Establish what it *actually does* — its mechanism, not what its README claims.
   Cite file paths for every claim.
3. Return the analysis in §5's shape, obeying §6's rules. In particular: re-verify every claimed
   gap by grepping this template rather than trusting a cached measurement, and label provenance
   for anything that would change agent behaviour (*dogfood-validated* vs *derived-from-evidence*).

## What not to do

Do not modify the template during a review. This is read-only analysis — report findings, then
stop and let the user decide what to act on.

Do not re-litigate §2 or §7. open-spdd has been reviewed; its items are either landed or
deliberately rejected, and both lists are recorded.
