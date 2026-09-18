---
name: document_ingest
description: Use when a document — a PDF, including an auth-walled link to one — should be acquired, converted to readable text, and filed under .codestream/documents/ as project reference material for future agents to consult. Triggered by /document-ingest, or by a pasted document link alongside "add this to the project" / "ingest this document".
---

# Document Ingest — acquire a document, make it readable, file it as reference material

The user hands over a document — usually a PDF, sometimes a link to one. Your job is not to
summarise it away: it is to make it readable, file it where future agents can consult it, and
report what you actually stored.

Scope: PDF documents. `opendataloader-pdf` converts PDFs; other formats need a different
converter — say so and stop rather than promising output you cannot produce.

## Process

1. **Check the project.** If `.codestream/` does not exist, this project has not been onboarded —
   say so and stop. List `.codestream/documents/` first: if the document is already filed there,
   say so instead of filing it twice.

2. **Get the bytes locally.** A public URL can be downloaded directly. An auth-walled link (a
   Google Drive file that redirects to sign-in, for example) must be fetched through a browser
   session that is signed in — open it, trigger the viewer's Download, then locate the saved file
   in the browser's download directory. A local path is used as-is. If none of these yields the
   bytes, ask the user for a local copy — never proceed on a document you could not actually read
   (rule 24).

3. **Convert it to text.** `opendataloader-pdf <file.pdf> -o <scratch-dir> -f markdown,json` —
   Apache-2.0, local, deterministic; needs Java 11+ (`java -version`) and a one-time
   `uv tool install opendataloader-pdf` (pipx or a venv works too). Read the generated
   `<name>.md` from disk. Scanned/image-only PDFs need the hybrid OCR mode instead (`--hybrid`,
   see `opendataloader-pdf --help`) — near-empty Markdown is the signal that a PDF is scanned
   rather than digital.

4. **Read before filing.** Read the full table of contents, then enough of the body to describe
   the document accurately. Read in full every section you make claims about.

5. **File it** under `.codestream/documents/<slug>/` (a short kebab-case slug):
   - `<name>.md` — the converted Markdown, exactly as generated. Never edit it to "fix"
     extraction; note extraction noise in `PROVENANCE.md` instead.
   - `PROVENANCE.md` — source (URL or path), date, your agent id, the conversion command and
     tool version, a one-paragraph description of what the document is, a structure map
     (parts/table of contents, with page numbers where the conversion carries them), and the
     document's copyright/license status as stated in it. If the source says "all rights
     reserved", flag the redistribution question to the user in your report.
   The `<name>.json` output (page numbers, bounding boxes, element types) is large and only
   needed for element-level citation — keep it out of the repo unless the user wants it.

6. **Report.** State what was ingested, the path it now lives at, and what it is useful for.
   Point at the filed path instead of pasting large excerpts; future agents can read
   `.codestream/documents/<slug>/` for context.

## Rules

- **Evidence, not impressions.** Describe the document from the converted text you read from
  disk — cite sections and pages the way you cite file paths (rule 24).
- **Byte fidelity.** The filed `.md` is the converter's output, untouched.
- **Filing, not evaluation.** "What should this project take from it" — gates, artifact
  sections — is `/repo-ingest`'s judgment, not this skill's. File first; evaluate there.
- **One document per directory.** Keep slugs and filenames recognizable.
