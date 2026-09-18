#!/usr/bin/env python3
"""Render the embedded rule section of every directive copy from one file.

Single source:    .codestream/HARD_RULES.md   (its `## Hard rules` section)
Generated copies: CLAUDE.md
                  .agents/AGENTS.md
                  .github/copilot-instructions.md

Why this exists
---------------
The rules used to be hand-mirrored into three directive files. That meant four
places to edit for one rule change, and the parity check in
`check-framework.py` could only compare rule *numbers* and headed *titles* —
bodies were free to drift, and they did: 19 of 24 rule bodies differed between
the canonical file and the directive copies, invisibly, for an unknown number
of sessions.

The directive copies are generated artifacts now, rendered verbatim from the
canonical file between `RULES` markers. `check-framework.py` fails the build if
any directive drifts from what this script would render, so a hand-edit inside
those markers — or a canonical change nobody re-rendered — cannot ship to one
tool and not the others.

What is *not* embedded
----------------------
Only the `## Hard rules` section is rendered. Everything above it in the
canonical file — the canonical-source note and the "Why these rules exist"
failure table — stays there. That material is addressed to whoever is
maintaining or weakening a rule, not to an agent mid-task, so shipping it into
every auto-loaded directive would pay context rent on every session for
reasoning the agent does not need in order to comply.

The one per-tool value
----------------------
Rule 11 requires each directive to declare its own agent id. The rules
themselves never enumerate tools, so the id is injected here rather than
written into the canonical text.

Usage
-----
    python3 scripts/render-directives.py           # write the directive copies
    python3 scripts/render-directives.py --check   # verify only; exit 1 if stale

Template-repo tooling: NOT part of the adoption copy list. Downstream projects
receive the rendered directive copies and never run this script.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CANONICAL = REPO / ".codestream/HARD_RULES.md"

START_MARKER = "<!-- GENERATED:rules"
END_MARKER = "<!-- /GENERATED:rules -->"

RULES_HEADING = re.compile(r"^##\s+.*hard rules", re.IGNORECASE)
RULE_11_HEADING = re.compile(r"^###\s+11\.\s")
RULE_12_HEADING = re.compile(r"^###\s+12\.\s")

PROLOGUE = (
    "> **Generated from `.codestream/HARD_RULES.md` — do not hand-edit this "
    "section.** In the template repo, edit the canonical file and re-run "
    "`scripts/render-directives.py`; `scripts/check-framework.py` fails the "
    "build if a directive drifts from the rendered output. Downstream projects "
    "receive this section as source — the rendering tooling does not ship with "
    "them."
)

# The only per-tool value in the whole render. Adding a tool to the framework
# means adding its directive here (plus its entry in check-framework.py's
# DIRECTIVES) — the rule text itself changes no more than it does for any other
# tool, per rule 11's "the framework never enumerates agents".
AGENT_IDS: dict[str, str] = {
    "CLAUDE.md": "claude-code",
    ".agents/AGENTS.md": "antigravity-gemini",
    ".github/copilot-instructions.md": "github-copilot",
}


def canonical_rules() -> list[str]:
    """Return the canonical file's `## Hard rules` section, trailing blanks stripped."""
    if not CANONICAL.is_file():
        raise SystemExit(f"canonical rules file missing: {CANONICAL.relative_to(REPO)}")

    lines = CANONICAL.read_text(encoding="utf-8").splitlines()
    start = next((n for n, line in enumerate(lines) if RULES_HEADING.match(line)), None)
    if start is None:
        raise SystemExit(
            f"{CANONICAL.relative_to(REPO)}: no '## Hard rules' section found — "
            f"this is the section that gets rendered into every directive."
        )

    section = lines[start:]
    while section and not section[-1].strip():
        section.pop()
    return section


def with_agent_id(section: list[str], agent_id: str) -> list[str]:
    """Append the per-tool agent id to rule 11's body.

    Inserted structurally — located by the `### 11.` / `### 12.` headings, not
    by matching prose — so a wording change in rule 11 cannot silently drop it.
    """
    start = next((n for n, line in enumerate(section) if RULE_11_HEADING.match(line)), None)
    end = next((n for n, line in enumerate(section) if RULE_12_HEADING.match(line)), None)
    if start is None or end is None or end < start:
        raise SystemExit(
            "canonical rules section is missing a well-ordered '### 11.' / "
            "'### 12.' heading pair — rule 11 is where the agent id is injected."
        )

    body = section[:end]
    while body and not body[-1].strip():
        body.pop()

    return [
        *body,
        "",
        f"**Your own agent id is `{agent_id}`** — write exactly that string in the "
        f"`agent` field.",
        "",
        *section[end:],
    ]


def render_block(agent_id: str) -> str:
    """Return the full marked block for one directive, markers included."""
    block = "\n".join(
        [
            f"{START_MARKER} -->",
            "",
            PROLOGUE,
            "",
            *with_agent_id(canonical_rules(), agent_id),
            "",
            END_MARKER,
        ]
    )
    if "{{" in block:
        raise SystemExit(
            "rendered output contains an unreplaced '{{' — the canonical rules "
            "section is meant to be verbatim, not templated."
        )
    return block


def splice(path: Path, block: str) -> str:
    """Replace everything between the markers in `path` with `block`."""
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()

    starts = [n for n, line in enumerate(lines) if line.startswith(START_MARKER)]
    ends = [n for n, line in enumerate(lines) if line.startswith(END_MARKER)]
    if len(starts) != 1 or len(ends) != 1:
        raise SystemExit(
            f"{path.relative_to(REPO)}: expected exactly one pair of RULES markers, "
            f"found {len(starts)} start(s) and {len(ends)} end(s). "
            f"The generated region is delimited by '{START_MARKER} ...' and "
            f"'{END_MARKER}'."
        )
    start, end = starts[0], ends[0]
    if end < start:
        raise SystemExit(f"{path.relative_to(REPO)}: END marker precedes START marker.")

    rebuilt = [*lines[:start], *block.splitlines(), *lines[end + 1 :]]
    trailing_newline = "\n" if original.endswith("\n") else ""
    return "\n".join(rebuilt) + trailing_newline


def render_all(check: bool) -> list[str]:
    """Render every directive. Returns the paths whose content differed.

    In check mode nothing is written — the caller decides what a difference
    means. In write mode each differing path is rewritten. Returning the same
    list in both modes is what lets the CLI report honestly instead of claiming
    "up to date" straight after writing three files.
    """
    changed: list[str] = []
    for rel, agent_id in AGENT_IDS.items():
        path = REPO / rel
        if not path.is_file():
            raise SystemExit(f"directive missing: {rel}")
        desired = splice(path, render_block(agent_id))
        if desired == path.read_text(encoding="utf-8"):
            continue
        changed.append(rel)
        if not check:
            path.write_text(desired, encoding="utf-8")
    return changed


def main() -> int:
    check = "--check" in sys.argv[1:]
    unknown = [a for a in sys.argv[1:] if a not in {"--check"}]
    if unknown:
        raise SystemExit(f"unknown argument(s): {unknown}. Use --check or nothing.")

    changed = render_all(check=check)

    if check:
        # Detail only — check-framework.py owns the PASS/FAIL formatting so the
        # gate reads like every other row in that report.
        if changed:
            print("stale: " + ", ".join(changed))
            return 1
        print(f"{len(AGENT_IDS)} copies match")
        return 0

    if changed:
        for rel in changed:
            print(f"rendered {rel}")
    else:
        print(f"{len(AGENT_IDS)} copies already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
