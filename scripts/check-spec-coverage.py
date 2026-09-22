#!/usr/bin/env python3
"""CODESTREAM spec coverage & consistency gate (rule 27).

`/plan` may not present a spec for SPEC_APPROVED until this exits 0. It enforces
the two properties that a spec's own prose cannot enforce on itself:

  COVERAGE     every addressable binding item is cited by at least one AC row.
               An uncited binding item is a SILENT DROP (rule 23) found at plan
               time instead of after a full build.

  CONSISTENCY  every `AC-N` / `RA-N` / `SG-N` / `N-N` / `OOS-N` id referenced
               anywhere resolves to something that exists, no id is defined
               twice, and no two binding clauses assert different values for the
               same enumerated quantity.

Rules 26/27 also make a third class visible: a binding clause asserting a
hand-maintained derived literal (a count of files, edits, clauses...) is reported
as a WARN, because it is a defect with a fuse on it rather than a hard failure —
the clause may legitimately be citing an AC row that derives it.

Exit code 0 = clean. Exit code 1 = at least one FAIL. WARNs do not fail the run.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Sections whose prose is binding, and therefore scanned for derived-literal and
# conflicting-count defects. "Binding Declarations" is the template's preamble —
# it is not one of rule 23's five labelable sections, but it carries binding
# prose (it is where the spec states that the subsections below are binding), so
# a count asserted there is as load-bearing as one asserted inside a clause.
BINDING_SECTIONS = (
    "Key Behaviors",
    "Binding Declarations",
    "Resolved Ambiguities",
    "Norms",
    "Safeguards",
    "Out of Scope",
)

# Nouns that make a numeral a *derived* quantity when asserted in binding prose.
COUNTABLE_NOUNS = (
    "files?",
    "paths?",
    "clauses?",
    "edits?",
    "rows?",
    "tables?",
    "tests?",
    "functions?",
    "entries?",
    "migrations?",
    "tools?",
    "phases?",
    "sections?",
    "rows?",
    "sites?",
    "call sites?",
    "columns?",
)

NUM_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

ID_RE = re.compile(r"\b(AC|RA|SG|N|OOS|KB|AM)-(\d+)(?:\.([a-z]))?\b")
AC_ROW_RE = re.compile(r"^\|\s*\*{0,2}(AC-\d+)\*{0,2}\s*\|(.*)$", re.M)
# An id'd binding item: **RA-15 (...)**, **SG-3**, **N-2**, **RA-15.a**
DEFINED_RE = re.compile(r"\*\*((?:RA|SG|N|OOS|KB|AM)-\d+(?:\.\w)?)\b")


def strip_fences(text: str) -> str:
    """Drop fenced code blocks so example text can't be parsed as real content."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def split_sections(text: str) -> dict[str, str]:
    """Map each binding-section name to its body text."""
    out: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^#{2,4}\s+(.*?)\s*$", line)
        if m:
            title = m.group(1)
            hit = next((k for k in BINDING_SECTIONS if title.startswith(k)), None)
            if hit:
                current = hit
                out.setdefault(current, "")
                continue
            current = None  # any other heading ends the current binding section
        if current:
            out[current] += line + "\n"
    return out


def expand_ids(text: str) -> set[str]:
    """Every id mentioned in `text`, expanding 'AC-19 through AC-24' ranges."""
    found: set[str] = set()
    for m in re.finditer(
        r"\b(AC|RA|SG|N|OOS|AM)-(\d+)\s+(?:through|to|-)\s+\1?-?(\d+)\b", text
    ):
        pre, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        lo, hi = sorted((a, b))
        for n in range(lo, hi + 1):
            found.add(f"{pre}-{n}")
    for m in ID_RE.finditer(text):
        pre, num, sub = m.group(1), m.group(2), m.group(3)
        found.add(f"{pre}-{num}")
        if sub:
            found.add(f"{pre}-{num}.{sub}")
    return found


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        spec = Path(argv[1])
    else:
        cands = sorted(p for p in Path(".codestream/active").glob("*feature_spec.md"))
        if len(cands) != 1:
            print(
                f"FAIL: expected exactly one spec in .codestream/active/, found {len(cands)}"
            )
            return 1
        spec = cands[0]

    if not spec.is_file():
        print(f"FAIL: no spec at {spec}")
        return 1

    raw = spec.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"FAIL: {spec} is not valid UTF-8: {e}")
        return 1
    if raw[:3] == b"\xef\xbb\xbf":
        print("WARN: spec carries a UTF-8 BOM (rule 14 prefers BOM-free)")

    body = strip_fences(text)
    sections = split_sections(body)

    print(f"CODESTREAM spec coverage & consistency check (rule 27)\n  spec: {spec}")
    print(f"  {len(raw)} bytes, {text.count(chr(10)) + 1} lines, valid UTF-8")

    fails: list[str] = []
    warns: list[str] = []

    # ---- collect AC rows -------------------------------------------------
    ac_rows: dict[str, str] = {}
    for m in AC_ROW_RE.finditer(body):
        ac_id, rest = m.group(1), m.group(2)
        if ac_id in ac_rows:
            fails.append(f"AC id {ac_id} is defined more than once")
        ac_rows[ac_id] = rest

    # ---- binding items ---------------------------------------------------
    defined: dict[str, str] = {}  # id -> the binding section it lives in
    for name, text_ in sections.items():
        for m in DEFINED_RE.finditer(text_):
            defined.setdefault(m.group(1), name)

    # ---- coverage --------------------------------------------------------
    # A `Verifies` column is authoritative: an item is covered only if some AC
    # row names it. A spec without one predates rule 27, so the best available
    # evidence is a clause-level `Mapped to AC-...` — checked, but reported as
    # the coarse approximation it is rather than implying precision we lack.
    has_verifies = bool(re.search(r"\|\s*Verifies\s*\|", body))
    uncovered: list[str] = []
    if has_verifies:
        cited: set[str] = set()
        for rest in ac_rows.values():
            cited |= expand_ids(rest)
        uncovered = sorted(i for i in defined if i not in cited)
        for item in uncovered:
            fails.append(
                f"coverage: binding item {item} ({defined[item]}) is cited by no AC row — a "
                f"SILENT DROP (rule 23). Add an AC row naming it in `Verifies`, or delete the "
                f"clause — deleting one only to clear this gate is the failure the gate exists to catch."
            )
    else:
        for name in sections:
            ids_here = [i for i, sec in defined.items() if sec == name]
            if ids_here and not (expand_ids(sections[name]) & set(ac_rows)):
                uncovered.extend(ids_here)
        if defined:
            warns.append(
                "no `Verifies` column — this spec predates rule 27's addressable-id requirement, "
                "so coverage is checked only at section granularity and a sub-item with no AC row "
                "of its own cannot be detected here. New specs must give each binding item its own "
                "id (`RA-15.a`) and name it in each AC row's `Verifies` cell."
            )
        for item in sorted(uncovered):
            fails.append(
                f"coverage: no clause in '{defined[item]}' cites any AC row, so {item} is "
                f"unverified — a SILENT DROP (rule 23)"
            )

    # ---- consistency: an id defined twice --------------------------------
    for name, text_ in sections.items():
        seen: dict[str, int] = {}
        for m in DEFINED_RE.finditer(text_):
            seen[m.group(1)] = seen.get(m.group(1), 0) + 1
        for ident, n in seen.items():
            if n > 1:
                fails.append(
                    f"consistency: binding item {ident} is defined {n} times in {name}"
                )

    # ---- consistency: conflicting counts for the same quantity -----------
    # The noun phrase is capped at two words on purpose: a greedy capture swallows
    # trailing prose ("constraint subsections are bind" vs "constraint
    # subsections"), which silently stops two restatements of the SAME quantity
    # from ever comparing equal — the exact defect this check exists to find.
    claims: dict[str, set[int]] = {}
    for name, text_ in sections.items():
        for m in re.finditer(
            r"\b(?:exactly|only|all|the|both)\s+(\d{1,4}|"
            + "|".join(NUM_WORDS)
            + r")\s+"
            r"([a-z]+(?:[\s/\-]+[a-z]+){0,1})",
            text_,
            re.I,
        ):
            word, noun = m.group(1).lower(), re.sub(
                r"\s+", " ", m.group(2).strip().lower()
            )
            val = NUM_WORDS.get(word)
            if val is None and word.isdigit():
                val = int(word)
            if val is None:
                continue
            claims.setdefault(noun, set()).add(val)
    for noun, vals in sorted(claims.items()):
        if len(vals) > 1:
            fails.append(
                f"consistency: '{noun}' is asserted with conflicting counts {sorted(vals)} across "
                f"binding clauses — only one can be true, and per rule 26 neither belongs in prose"
            )

    # ---- rule 26: derived literals in binding prose ----------------------
    seen_warn: set[str] = set()
    for name, text_ in sections.items():
        for m in re.finditer(
            r"\b(?:exactly|only)\s+(\d{1,4}|"
            + "|".join(NUM_WORDS)
            + r")\s+("
            + "|".join(COUNTABLE_NOUNS)
            + r")\b",
            text_,
            re.I,
        ):
            key = f"{name}:{m.group(0).lower()}"
            if key in seen_warn:
                continue
            seen_warn.add(key)
            warns.append(
                f"rule 26: {name} asserts a derived count ('{m.group(0).strip()}') — cite the AC "
                f"row that derives it, or derive it in the AC instead of writing a literal"
            )

    # ---- report ----------------------------------------------------------
    print(f"  binding sections: {', '.join(sections) or 'NONE FOUND'}")
    print(
        f"  AC rows: {len(ac_rows)}   Verifies column: {'yes' if has_verifies else 'no (legacy)'}"
    )
    print(
        f"  binding items with ids: {len(defined)}   covered: {len(defined) - len(uncovered)}"
    )
    if not defined:
        warns.append(
            "no id'd binding items found — each binding item needs its own id (`RA-15`, "
            "`SG-3`, `N-2`) for coverage to be checkable at all (rule 27)"
        )
    if not ac_rows:
        warns.append("no AC rows found — is this actually a feature spec?")

    for w in warns:
        print(f"  [WARN] {w}")
    for f in fails:
        print(f"  [FAIL] {f}")

    if fails:
        print(
            f"\n{len(fails)} FAILED, {len(warns)} warned — do not present for SPEC_APPROVED (rule 27)"
        )
        return 1
    print(f"\nPASS — 0 failed, {len(warns)} warned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
