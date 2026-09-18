---
name: repo_ingest
description: Use when the user supplies an external repo (GitHub URL or local path), or a document to mine for ideas (a PDF, including an auth-walled link to one), to evaluate against this project — what it actually does, what is worth adopting and as which gate or artifact, what this project already does, and what to avoid. Triggered by /repo-ingest, or by a pasted repo/document URL alongside "compare this to our template".
---

# Repo Ingest — evaluate an external repo or document against this project

The user hands over external material — usually a repo, sometimes a document (a PDF) — one at a
time. Your job is not to summarise it. It is to decide what, if anything, this project should take
from it.

## The filter that decides everything

**An idea only transfers if it becomes a gate — something that can fail — or a checkable artifact
section — something a critic can audit.** This framework is a state machine, not a knowledge base.
Advice that cannot fail is advice the project already has too much of.

That filter is the whole reason some imports work and most do not. Whenever you propose an
absorption, name the gate or artifact section it becomes. If you cannot name one, say so plainly
rather than describing the idea glowingly.

## Process

1. **Read this project's own rules and conventions first** — `.codestream/HARD_RULES.md`, the
   relevant `.codestream/templates/`, the **Project-specific context** block in whichever directive
   file your tool auto-loads, and anything in `.codestream/documents/`. You cannot judge what is
   "already covered" without knowing what is there. Read from disk, in full (rule 24).
   If `.codestream/` does not exist, this project has not been onboarded — say so and stop.

2. **Read the source.** Establish what it actually does — its mechanism, not what its README claims.
   Cite file paths for every claim you make about it.
   If the source is a document (PDF) rather than a repo: it must first be made readable —
   `/document-ingest` owns acquiring and converting documents (and files the ones that are kept).
   Read the converted Markdown from disk — cite sections and page numbers the way file paths are
   cited — then apply this skill's process to what you read. Never evaluate a document you could
   not actually read (rule 24).

3. **Verify every gap you are about to claim.** Before saying this project lacks something, grep
   for it. A remembered or stale measurement is how a review produces a confident wrong finding.

4. **Classify every candidate** into exactly one of:
   - **Adopt** — and name the gate or artifact section it becomes.
   - **Already covered** — and cite the rule, section, or file that covers it.
   - **Avoid** — and give the reason. Weigh this against rule 7 (don't add ceremony a small
     change does not need) and against rule 15's context-cost reasoning.

5. **Score it against this project's stated goals.** Not every repo serves every goal. Reporting
   "irrelevant to three of five" is a normal and useful outcome, not a failure to find value.

## Output

1. **What it is** — the mechanism, not the marketing.
2. **Adopt** — each item, with the gate or artifact section it becomes.
3. **Already covered** — each item, with the citation that covers it.
4. **Avoid** — each item, with the reason.
5. **Verdict** — partial credit where earned, and an explicit note of what it does *not* help with.

## Rules

- **Evidence, not impressions.** Cite paths for a repo, sections/pages for a document — for the
  source's claims and for this project's alike. Never claim a gap you have not grepped for.
- **Flag provenance.** Anything that would change agent behaviour is labelled *dogfood-validated*
  (exercised by a run) or *derived-from-evidence* (reasoned from an observed failure). Nothing
  silently reads as tested.
- **Take the idea, not the shape.** If the repo's own artifacts are enormous, that is a reason to
  adopt its concept while rejecting its format.
- **Read-only.** Do not modify the project during an ingest. Report, then stop and let the user
  decide what to act on.
- **Do not re-litigate what is already recorded.** If the project keeps a reviewed-repos ledger,
  read it and skip anything already decided there.
