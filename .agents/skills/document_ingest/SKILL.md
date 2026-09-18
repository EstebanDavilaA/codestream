---
name: document_ingest
description: Use when the user supplies a document (a PDF, including an auth-walled link to one) to evaluate against this project — what it actually does, what is worth adopting and as which gate or artifact, what this project already does, and what to avoid. Triggered by /document-ingest, or by a pasted document link alongside "compare this to our project" or "mine this for ideas".
---

# Document Ingest — evaluate an external document against this project

The user hands over a document — usually a PDF, sometimes a link to one — one at a time. Your job
is not to summarise it: it is to decide what, if anything, this project should take from it. This
is `/repo-ingest`'s process applied to a document source.

Scope: PDF documents convert with `opendataloader-pdf`; a document that is already plain text
(Markdown, text) can be read directly. For a format neither path covers, say so and stop — never
promise an analysis you cannot ground in text you actually read.

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

2. **Get the bytes locally.** A public URL can be downloaded directly. An auth-walled link (a
   Google Drive file that redirects to sign-in, for example) must be fetched through a browser
   session that is signed in — open it, trigger the viewer's Download, then locate the saved file
   in the browser's download directory. A local path is used as-is. If none of these yields the
   bytes, ask the user for a local copy — never evaluate a document you could not actually read
   (rule 24).

3. **Convert it to text.** `opendataloader-pdf <file.pdf> -o <scratch-dir> -f markdown,json` —
   Apache-2.0, local, deterministic; needs Java 11+ (`java -version`) and a one-time
   `uv tool install opendataloader-pdf` (pipx or a venv works too). A plain-text document needs no
   conversion. Read the generated `<name>.md` from disk. Scanned/image-only PDFs need the hybrid
   OCR mode instead (`--hybrid`, see `opendataloader-pdf --help`) — near-empty Markdown is the
   signal that a PDF is scanned rather than digital.

4. **Read the document.** Establish what it actually contains — its mechanism, not its blurb.
   Read the full table of contents first, then read in full every section you go on to cite. Cite
   sections and page numbers the way you cite file paths for a repo.

5. **Verify every gap you are about to claim.** Before saying this project lacks something, grep
   for it — in the converted text and in the project. A remembered or stale measurement is how a
   review produces a confident wrong finding.

6. **Classify every candidate** into exactly one of:
   - **Adopt** — and name the gate or artifact section it becomes.
   - **Already covered** — and cite the rule, section, or file that covers it.
   - **Avoid** — and give the reason. Weigh this against rule 7 (don't add ceremony a small
     change does not need) and against rule 15's context-cost reasoning.

7. **Score it against this project's stated goals.** Not every document serves every goal.
   Reporting "irrelevant to three of five" is a normal and useful outcome, not a failure to find
   value.

## Output

1. **What it is** — the mechanism, not the marketing.
2. **Adopt** — each item, with the gate or artifact section it becomes.
3. **Already covered** — each item, with the citation that covers it.
4. **Avoid** — each item, with the reason.
5. **Verdict & actionables** — partial credit where earned, an explicit note of what it does
   *not* help with, and concrete next steps — or plainly state that there are none.

## Rules

- **Evidence, not impressions.** Cite sections/pages for the document's claims and paths for this
  project's. Never claim a gap you have not grepped for.
- **Flag provenance.** Anything that would change agent behaviour is labelled *dogfood-validated*
  (exercised by a run) or *derived-from-evidence* (reasoned from an observed failure). Nothing
  silently reads as tested.
- **Take the idea, not the shape.** If the document's own artifacts are enormous, that is a reason
  to adopt its concept while rejecting its format.
- **Read-only.** Do not modify the project during an ingest. Report, then stop and let the user
  decide what to act on.
- **Do not re-litigate what is already recorded.** If the project keeps a reviewed-sources ledger,
  read it and skip anything already decided there.
