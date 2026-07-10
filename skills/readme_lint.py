#!/usr/bin/env python3
"""readme_lint — deterministic gate for the README-Writing Discipline.

The mechanical *How* of the Ontological Bond documented in
kb/WHY-0001-readme-writing-discipline.md (Why) and
kb/HOW-0006-readme-writing-discipline.md (When).

Enforces ONLY mechanical invariants (Builder vs Enforcer: register, metaphor,
and emphasis judgments live in the playbook, never here):

  1. YAML frontmatter parses and carries the falsifiable-manifesto schema.
  2. kind == "derived-view" (the README is a lens, never a content-home).
  3. dogma is exactly False (no-dogma is permanent).
  4. belief.status is "hypothesis" or "theory" (a conjecture imports a proof
     that is not coming; settled is forbidden).
  5. updated is an ISO date (YYYY-MM-DD).
  6. Every canonical_home entry ("FILE § Heading") resolves: the file exists
     relative to the README and contains the heading text.
  7. The body contains numbered claims ("**Claim N"), and every claim block
     carries a falsifier marker ("Break it:").

Usage: python3 skills/readme_lint.py [path/to/README.md]
Exit 0 = pass; exit 1 = itemized failures on stdout.
"""

import re
import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = [
    "doc", "kind", "genre", "rule", "belief", "grade", "coverage",
    "dogma", "caution", "cta", "canonical_home", "governed_by", "updated",
]
REQUIRED_BELIEF_FIELDS = ["statement", "foundation", "stance", "status"]
ALLOWED_STATUS = {"hypothesis", "theory"}
FALSIFIER_MARKER = "Break it:"
CLAIM_RE = re.compile(r"\*\*Claim (\d+)")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def split_frontmatter(text):
    """Return (frontmatter_str, body) or (None, text) if no frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:]


def lint_frontmatter(fm_text, readme_dir):
    errors = []
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        return [f"frontmatter does not parse as YAML: {e}"]
    if not isinstance(fm, dict):
        return ["frontmatter is not a YAML mapping"]

    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"missing frontmatter field: {field}")

    if fm.get("kind") != "derived-view":
        errors.append(f"kind must be 'derived-view', got: {fm.get('kind')!r}")

    if fm.get("dogma") is not False:
        errors.append(f"dogma must be exactly false, got: {fm.get('dogma')!r}")

    belief = fm.get("belief")
    if isinstance(belief, dict):
        for field in REQUIRED_BELIEF_FIELDS:
            if field not in belief:
                errors.append(f"missing belief field: belief.{field}")
        status = belief.get("status")
        if status is not None and status not in ALLOWED_STATUS:
            errors.append(
                f"belief.status must be one of {sorted(ALLOWED_STATUS)}, got: {status!r}")
    elif "belief" in fm:
        errors.append("belief must be a mapping")

    updated = fm.get("updated")
    if updated is not None and not DATE_RE.match(str(updated)):
        errors.append(f"updated must be an ISO date (YYYY-MM-DD), got: {updated!r}")

    homes = fm.get("canonical_home")
    if isinstance(homes, list) and homes:
        for entry in homes:
            errors.extend(check_canonical_home(str(entry), readme_dir))
    elif "canonical_home" in fm:
        errors.append("canonical_home must be a non-empty list")

    return errors


def check_canonical_home(entry, readme_dir):
    """Resolve a 'FILE § Heading' pointer against the filesystem."""
    if "§" not in entry:
        return [f"canonical_home entry has no '§ Heading' part: {entry!r}"]
    file_part, heading = (s.strip() for s in entry.split("§", 1))
    target = readme_dir / file_part
    if not target.is_file():
        return [f"canonical_home file not found: {file_part!r}"]
    if heading and heading not in target.read_text(encoding="utf-8"):
        return [f"canonical_home heading {heading!r} not found in {file_part!r}"]
    return []


def lint_claims(body):
    errors = []
    claim_numbers = [int(m.group(1)) for m in CLAIM_RE.finditer(body)]
    if not claim_numbers:
        errors.append("body contains no numbered claims ('**Claim N')")
        return errors
    # Each claim block runs to the next claim (or end of body); each must
    # carry the falsifier marker, except a final standing-invitation claim.
    blocks = re.split(r"(?=\*\*Claim \d+)", body)
    claim_blocks = [b for b in blocks if CLAIM_RE.match(b.strip())]
    last = max(claim_numbers)
    for block in claim_blocks:
        number = int(CLAIM_RE.match(block.strip()).group(1))
        if FALSIFIER_MARKER not in block and number != last:
            errors.append(f"Claim {number} has no falsifier marker ({FALSIFIER_MARKER!r})")
    return errors


def lint(path):
    readme = Path(path)
    if not readme.is_file():
        return [f"file not found: {path}"]
    text = readme.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        return ["no YAML frontmatter block found"]
    errors = lint_frontmatter(fm_text, readme.resolve().parent)
    errors.extend(lint_claims(body))
    return errors


def main(argv):
    path = argv[1] if len(argv) > 1 else "README.md"
    errors = lint(path)
    if errors:
        print(f"[README-LINT] FAIL: {path} — {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"[README-LINT] PASS: {path} conforms to the falsifiable-manifesto form.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
