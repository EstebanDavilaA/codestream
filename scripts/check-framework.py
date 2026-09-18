#!/usr/bin/env python3
"""CODESTREAM framework integrity check.

Verifies the invariants that no single-file edit can guarantee on its own:

  1. protected framework paths exist
  2. the three rule mirrors agree (HARD_RULES.md is canonical, rule 13's
     "if the three ever disagree, this file wins" invariant)
  3. every Claude skill has a Gemini counterpart
  4. every Claude subagent has its documented persona counterpart
  5. STATE.json is valid UTF-8, BOM-free, and parses as real JSON
     (rule 10 point 4 / rule 17)
  6. this repo's own runtime state is still pristine (rule 22)
  7. no framework file carries a UTF-8 BOM (rule 14)

Template-repo tooling: this script is NOT part of the adoption copy list and
should not be copied into downstream projects.

Exit code 0 = every gate passed. Exit code 1 = at least one FAIL.
WARNs do not fail the run.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CANONICAL = Path(".codestream/HARD_RULES.md")
# Every directive file that embeds a full copy of the rules. Adding a tool to the
# framework means adding its directive here and declaring its own agent id in it —
# the rules themselves never enumerate agents (rule 11).
DIRECTIVES = [
    Path("CLAUDE.md"),
    Path(".agents/AGENTS.md"),
    Path(".github/copilot-instructions.md"),
]
RULE_FILES = [CANONICAL, *DIRECTIVES]

PROTECTED = [
    "CLAUDE.md",
    ".agents/AGENTS.md",
    ".github/copilot-instructions.md",
    ".claude",
    ".agents",
    ".codestream",
    ".codestream/HARD_RULES.md",
    ".codestream/templates/FEATURE_SPEC_TEMPLATE.md",
]

CLAUDE_SKILLS = Path(".claude/skills")
AGENTS_SKILLS = Path(".agents/skills")
CLAUDE_AGENTS = Path(".claude/agents")

STATE_JSON = Path(".codestream/STATE.json")

# Claude subagent -> Gemini persona skill (README "Two implementations, one
# lifecycle"). researcher is the documented exception: it has no persona file
# because its job stays inline in /research.
PERSONA_PAIRS = {
    "codebase-mapper": "map_codebase",
    "intent-discoverer": "discover_intent",
    "prototyper": "prototype_fast",
    "roadmapper": "roadmap_slices",
    "planner": "plan_spec",
    "executor": "execute_feature",
    "critic": "audit_critic",
    "verifier": "verify_steer",
    "reset-specialist": "reset_checkpoint",
    "product-strategist": "product_strategist",
}
PERSONA_EXEMPT_AGENTS = {"researcher"}

# Runtime files that must be pristine in the template repo (rule 22).
ARCHIVE_STUBS = [
    ".codestream/archive/CRITIC_REPORT.md",
    ".codestream/archive/VERIFICATION_REPORT.md",
    ".codestream/archive/STEERING_LOG.md",
    ".codestream/archive/STATE_HISTORY.md",
]
ARCHIVE_SENTINEL = "_No entries yet._"

results: list[tuple[str, str, str]] = []  # (level, check, detail)


def record(level: str, check: str, detail: str = "") -> None:
    results.append((level, check, detail))


def normalize(text: str) -> str:
    text = re.sub(r"[`*_\[\]()]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


# ---------------------------------------------------------------- 1. paths
def check_protected_paths() -> None:
    missing = [p for p in PROTECTED if not (REPO / p).exists()]
    if missing:
        record("FAIL", "protected paths exist", "missing: " + ", ".join(missing))
    else:
        record("PASS", "protected paths exist", f"{len(PROTECTED)} paths")


# ------------------------------------------------- 2b. agent ids (rule 11)
AGENT_ID = re.compile(r"Your agent id is `([a-z0-9][a-z0-9-]*)`")


def check_agent_ids() -> None:
    """Every directive declares its own agent id, and no two declare the same one.

    Rule 11 deliberately does not enumerate agents — the id is a self-declared
    alias. So what can be checked is not "is this a known tool" but "does each
    directive claim exactly one identity, and are they distinct". Two directives
    claiming the same id would make rule 10's pre-flight unable to tell them
    apart, which is the failure the field exists to prevent.
    """
    ids: dict[str, str] = {}
    problems: list[str] = []

    for directive in DIRECTIVES:
        path = REPO / directive
        if not path.is_file():
            problems.append(f"{directive} missing")
            continue
        found = AGENT_ID.findall(path.read_text(encoding="utf-8"))
        if len(found) != 1:
            problems.append(
                f"{directive} declares {len(found)} agent id(s), expected exactly 1"
            )
            continue
        ids[str(directive)] = found[0]

    for directive, agent_id in ids.items():
        for other, other_id in ids.items():
            if other != directive and other_id == agent_id:
                problems.append(
                    f"{directive} and {other} both claim agent id '{agent_id}'"
                )

    if problems:
        record("FAIL", "directive agent ids distinct", "; ".join(sorted(set(problems))))
    else:
        record(
            "PASS",
            "directive agent ids distinct",
            ", ".join(f"{p}={i}" for p, i in ids.items()),
        )


# ------------------------------------------------------------ 2. rule mirror
RULE_HEAD = re.compile(r"^#{2,3}\s+(\d+)\.\s*(.*)$")
RULE_ITEM = re.compile(r"^(\d+)\.\s+(.*)$")
HARD_RULES_HEADING = re.compile(r"^##\s+.*hard rules", re.IGNORECASE)
SECTION_HEADING = re.compile(r"^##\s+")


def parse_rules(path: Path) -> tuple[dict[int, str], dict[int, str]]:
    """Return (headings, bodies) keyed by rule number.

    Scoped to the file's "Hard rules" section: the directive files carry other
    numbered lists (e.g. AGENTS.md's "Team Personas") that would otherwise be
    mistaken for rules.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    headings: dict[int, str] = {}
    bodies: dict[int, list[str]] = {}
    in_rules = False
    current: int | None = None
    for line in lines:
        if HARD_RULES_HEADING.match(line):
            in_rules = True
            current = None
            continue
        if in_rules and SECTION_HEADING.match(line):
            break
        if not in_rules:
            continue
        if 24 in headings and line.strip() == "---":
            # End of the shared rules section: a tool-specific addendum follows,
            # and it is directive-local, not shared rule text. Without this break
            # the parser absorbs the addendum into rule 24 and reports drift that
            # isn't there.
            break
        head = RULE_HEAD.match(line)
        if head:
            current = int(head.group(1))
            headings[current] = head.group(2).strip()
            bodies[current] = []
            continue
        item = RULE_ITEM.match(line)
        if item and (current is None or int(item.group(1)) == len(bodies) + 1):
            current = int(item.group(1))
            headings.setdefault(current, "")
            bodies[current] = [item.group(2)]
            continue
        if current is not None:
            bodies[current].append(line)
    return headings, {k: "\n".join(v) for k, v in bodies.items()}


def check_rule_mirror() -> None:
    parsed = {p: parse_rules(REPO / p) for p in RULE_FILES}
    canonical_numbers = set(parsed[CANONICAL][1])

    problems: list[str] = []
    for mirror in DIRECTIVES:
        numbers = set(parsed[mirror][1])
        missing = sorted(canonical_numbers - numbers)
        extra = sorted(numbers - canonical_numbers)
        if missing:
            problems.append(f"{mirror} missing rule(s) {missing}")
        if extra:
            problems.append(f"{mirror} has extra rule(s) {extra}")

    if problems:
        record("FAIL", "rule mirror agrees", "; ".join(problems))
    else:
        record(
            "PASS",
            "rule mirror agrees",
            f"{len(canonical_numbers)} rules across {len(RULE_FILES)} files",
        )

    # Headed-rule titles must match exactly across the three copies.
    title_mismatch: list[str] = []
    for number in sorted(canonical_numbers):
        titles = {
            p: parsed[p][0].get(number, "")
            for p in RULE_FILES
            if parsed[p][0].get(number)
        }
        normalized = {p: normalize(t) for p, t in titles.items()}
        if len(set(normalized.values())) > 1:
            title_mismatch.append(f"rule {number}: " + " | ".join(
                f"{p.name}={titles[p]!r}" for p in sorted(titles)
            ))
    if title_mismatch:
        record("FAIL", "headed rule titles match", "; ".join(title_mismatch))
    else:
        record("PASS", "headed rule titles match")

    # Body drift is a FAILURE, not a note. The rules section is meant to be
    # byte-identical across the canonical file and all three directive copies;
    # tool-specific material belongs in each directive's addendum, outside the
    # rules section. Keeping the copies equal by hand is exactly what failed
    # before — 19 of 24 bodies had diverged, invisibly, over an unknown number
    # of sessions — so this check is what actually keeps them equal.
    drift = []
    for number in sorted(canonical_numbers):
        bodies = {
            p: normalize(parsed[p][1].get(number, "")) for p in RULE_FILES
        }
        if len(set(bodies.values())) > 1:
            drift.append(number)
    if drift:
        shown = drift[:6]
        more = "" if len(drift) == len(shown) else f" (+{len(drift) - len(shown)} more)"
        record(
            "FAIL",
            "rule body text identical",
            f"{len(drift)}/{len(canonical_numbers)} rule(s) differ in wording —"
            f" the copies must match `.codestream/HARD_RULES.md` exactly, with"
            f" tool-specific material in each directive's addendum:"
            f" {shown}{more}",
        )
    else:
        record("PASS", "rule body text identical")


# ---------------------------------------------------------- 3/4. skill mirror
def dirs_with_file(root: Path, filename: str) -> set[str]:
    if not root.is_dir():
        return set()
    return {p.parent.name for p in root.glob(f"*/{filename}")}


def check_skill_mirror() -> None:
    claude = dirs_with_file(REPO / CLAUDE_SKILLS, "SKILL.md")
    agents = dirs_with_file(REPO / AGENTS_SKILLS, "SKILL.md")

    def norm(name: str) -> str:
        return name.replace("-", "_")

    normalized_agents = {norm(n) for n in agents}
    # Persona skills pair with a .claude/agents entry, not a .claude/skills one
    # (see check_persona_mirror) — they are not orphans.
    personas = set(PERSONA_PAIRS.values())
    missing = sorted(n for n in claude if norm(n) not in normalized_agents)
    orphan = sorted(
        n for n in agents if n not in {norm(c) for c in claude} and n not in personas
    )
    if missing or orphan:
        detail = []
        if missing:
            detail.append(f"no Gemini counterpart for: {missing}")
        if orphan:
            detail.append(f"Gemini-only skill: {orphan}")
        record("FAIL", "skill mirror agrees", "; ".join(detail))
    else:
        record("PASS", "skill mirror agrees", f"{len(claude)} skills paired")


def check_persona_mirror() -> None:
    agents = {p.stem for p in (REPO / CLAUDE_AGENTS).glob("*.md")}
    skills = dirs_with_file(REPO / AGENTS_SKILLS, "SKILL.md")

    problems = []
    documented_agents = set(PERSONA_PAIRS) | PERSONA_EXEMPT_AGENTS
    if agents - documented_agents:
        problems.append(
            f"subagent(s) with no documented persona pairing: "
            f"{sorted(agents - documented_agents)}"
        )
    for agent, persona in sorted(PERSONA_PAIRS.items()):
        if agent not in agents:
            problems.append(f"missing subagent file: {agent}.md")
        if persona not in skills:
            problems.append(f"missing persona skill: {persona}")
    if problems:
        record("FAIL", "subagent/persona mirror agrees", "; ".join(problems))
    else:
        record(
            "PASS",
            "subagent/persona mirror agrees",
            f"{len(PERSONA_PAIRS)} pairs + {len(PERSONA_EXEMPT_AGENTS)} "
            f"documented exception",
        )


# ------------------------------------------------------------- 5. STATE.json
def check_state_json() -> dict | None:
    path = REPO / STATE_JSON
    if not path.is_file():
        record("FAIL", "STATE.json parses as JSON", "file missing")
        return None
    raw = path.read_bytes()
    problems = []
    if raw.startswith(b"\xef\xbb\xbf"):
        problems.append("has a UTF-8 BOM")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        record("FAIL", "STATE.json parses as JSON", f"not valid UTF-8: {exc}")
        return None
    data = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        problems.append(f"invalid JSON: {exc}")
    if problems:
        record("FAIL", "STATE.json parses as JSON", "; ".join(problems))
        return None
    record("PASS", "STATE.json parses as JSON", "valid UTF-8, BOM-free, parsed")
    return data


# ------------------------------------------------- 6. template state pristine
def check_template_pristine(data: dict | None) -> None:
    if data is not None:
        problems = []
        if data.get("current_state") != 0:
            problems.append(f"current_state is {data.get('current_state')}, expected 0")
        if data.get("state_history"):
            problems.append(
                f"state_history has {len(data['state_history'])} entr(ies)"
            )
        if data.get("active_milestone") is not None:
            problems.append(f"active_milestone is {data['active_milestone']!r}")
        if data.get("active_phase") is not None:
            problems.append(f"active_phase is {data['active_phase']!r}")
        artifact = (data.get("artifacts") or {}).get("active_spec")
        if artifact is not None:
            problems.append(f"artifacts.active_spec points at {artifact!r}")
        if problems:
            record("FAIL", "STATE.json still pristine", "; ".join(problems))
        else:
            record("PASS", "STATE.json still pristine", "state 0, empty history")

    # active/ holds no spec files
    active = REPO / ".codestream/active"
    specs = [p.name for p in active.glob("*.md")] if active.is_dir() else []
    if specs:
        record("FAIL", "active/ holds no spec", f"found {specs}")
    else:
        record("PASS", "active/ holds no spec")

    # append-only archives still contain only their stub sentinel
    polluted = []
    for rel in ARCHIVE_STUBS:
        path = REPO / rel
        if not path.is_file():
            polluted.append(f"{rel} missing")
        elif ARCHIVE_SENTINEL not in path.read_text(encoding="utf-8"):
            polluted.append(f"{rel} has been appended to")
    if polluted:
        record("FAIL", "archive logs still pristine", "; ".join(polluted))
    else:
        record("PASS", "archive logs still pristine", f"{len(ARCHIVE_STUBS)} stubs")

    # logs and docs carry no project content — matched against the same
    # sentinel discipline as the archive stubs, not an ID regex (the stub text
    # itself mentions "BUG-001" as an example)
    residue = []
    for rel, sentinel in [
        (".codestream/BUGS.md", "_No bugs logged yet."),
        (".codestream/FEATURES.md", "_No features logged yet."),
    ]:
        path = REPO / rel
        if not path.is_file():
            residue.append(f"{rel} missing")
        elif sentinel not in path.read_text(encoding="utf-8"):
            residue.append(f"{rel} has logged items")
    for rel in [".codestream/DISCOVERY.md", ".codestream/ROADMAP.md"]:
        path = REPO / rel
        if not path.is_file():
            residue.append(f"{rel} missing")
        elif "[PROJECT NAME]" not in path.read_text(encoding="utf-8"):
            residue.append(f"{rel} has been filled in")
    docs = REPO / ".codestream/documents"
    if docs.is_dir():
        extra = [p.name for p in docs.iterdir() if p.name != ".gitkeep"]
        if extra:
            residue.append(f"documents/ has content: {extra}")
    if residue:
        record("FAIL", "no project residue in template", "; ".join(residue))
    else:
        record("PASS", "no project residue in template")


def check_template_marker() -> None:
    marker = REPO / ".codestream-template"
    if marker.is_file():
        record("PASS", "template marker present", ".codestream-template")
    else:
        record(
            "FAIL",
            "template marker present",
            ".codestream-template is missing — rule 22's guard is inert "
            "without it",
        )


# ------------------------------------------------------------------- 7. BOM
def check_bom() -> None:
    scanned = 0
    offenders = []
    for pattern in ("*.md", "*.json"):
        for path in REPO.rglob(pattern):
            if ".git/" in str(path) or "node_modules" in str(path):
                continue
            scanned += 1
            if path.read_bytes().startswith(b"\xef\xbb\xbf"):
                offenders.append(str(path.relative_to(REPO)))
    if offenders:
        record("FAIL", "no UTF-8 BOM in framework files", ", ".join(offenders))
    else:
        record("PASS", "no UTF-8 BOM in framework files", f"{scanned} files scanned")


def main() -> int:
    print("CODESTREAM framework integrity check")
    print(f"  repo: {REPO}\n")

    check_template_marker()
    check_protected_paths()
    check_agent_ids()
    check_rule_mirror()
    check_skill_mirror()
    check_persona_mirror()
    data = check_state_json()
    check_template_pristine(data)
    check_bom()

    width = max(len(c) for _, c, _ in results)
    for level, check, detail in results:
        print(f"  [{level}] {check.ljust(width)}  {detail}")

    failed = [r for r in results if r[0] == "FAIL"]
    warned = [r for r in results if r[0] == "WARN"]
    print(
        f"\n  {len(results) - len(failed) - len(warned)} passed, "
        f"{len(warned)} warned, {len(failed)} failed"
    )
    if failed:
        print("\n  Rule 22 / rule 13 / rule 14 blockers — fix before merging.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
