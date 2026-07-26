#!/usr/bin/env python3
"""pgm_lint — schema gate for program definitions (the ``pgm-`` four-slot model).

Mechanical validator for the program abstraction (ADR-0010;
``dialectic/design/daily-reflection-spec.md`` § 6). Enforces ONLY machine-checkable
invariants — Builder vs Enforcer: quality/altitude judgments live in the discipline,
never here. In particular the **`pgm-operating-invariant`**: a program initializes
with a minimum of two slots — ``program`` and ``program_telos``.
``program_value``/``program_invariant`` are optional (unset → inherit the parent
dyad's slots — never an error).

Runs on program-definition files (``dialectic/design/programs/*.md``). Program
definitions are **PII-clear and public**, so they lint here directly — no
dual-checkout (contrast the private ``d-re`` records under ADR-0006).

Checks:
  1. YAML frontmatter parses as a mapping.
  2. ``program_id`` present, a non-empty string (the discriminator + identity), and
     equals the filename stem.
  3. ``program`` present, a non-empty string        (``pgm-operating-invariant``).
  4. ``program_telos`` present, a non-empty string  (``pgm-operating-invariant``).
  5. ``program_value`` / ``program_invariant`` — optional; non-empty strings when
     set (unset = inherit milo's parent slots — never flagged).
  6. ``enrollment`` — optional operational field; an ISO date (YYYY-MM-DD) when present.
  7. body (below the frontmatter) is non-empty (a definition must elaborate; length
     is never gated).

Extra keys are allowed (open-extensible; a method-override is a behavioral pointer,
not a linted slot — ADR-0002 proportionality).

Usage: python3 skills/pgm_lint.py PROGRAM.md [PROGRAM.md ...]
Exit 0 = all pass; exit 1 = itemized failures on stdout; exit 2 = usage.
"""

import datetime as dt
import re
import sys
from pathlib import Path

import yaml

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED_SLOTS = ("program", "program_telos")   # the pgm-operating-invariant
OPTIONAL_SLOTS = ("program_value", "program_invariant")  # unset → inherit parent


def split_frontmatter(text):
    """Return (frontmatter_str, body) or (None, text) if no frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:]


def _nonempty_str(v):
    return isinstance(v, str) and bool(v.strip())


def _is_iso_date(v):
    if isinstance(v, dt.datetime):
        return False  # an instant, not a calendar day
    if isinstance(v, dt.date):
        return True
    return isinstance(v, str) and bool(DATE_RE.match(v))


def lint(path):
    rec = Path(path)
    if not rec.is_file():
        return [f"file not found: {path}"]
    text = rec.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        return ["no YAML frontmatter block found"]
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        return [f"frontmatter does not parse as YAML: {exc}"]
    if not isinstance(fm, dict):
        return ["frontmatter is not a YAML mapping"]

    errors = []

    # program_id — discriminator + identity + filename agreement
    program_id = fm.get("program_id")
    if not _nonempty_str(program_id):
        errors.append(
            "program_id is required and must be a non-empty string (the program discriminator)")
    elif program_id.strip() != rec.stem:
        errors.append(
            f"program_id {program_id.strip()!r} does not match the filename stem {rec.stem!r}")

    # the pgm-operating-invariant — the two required slots
    for slot in REQUIRED_SLOTS:
        if slot not in fm:
            errors.append(
                f"{slot} is required — the pgm-operating-invariant mandates a minimum of two "
                f"slots (program + program_telos); the rest are earned")
        elif not _nonempty_str(fm.get(slot)):
            errors.append(f"{slot} must be a non-empty string")

    # optional slots — inherit-when-unset; shape-if-present only
    for slot in OPTIONAL_SLOTS:
        val = fm.get(slot)
        if val is not None and not _nonempty_str(val):
            errors.append(
                f"{slot} must be a non-empty string when set (unset = inherit the parent dyad's slot)")

    # enrollment — optional operational field; a valid date when present
    enrollment = fm.get("enrollment")
    if enrollment is not None and not _is_iso_date(enrollment):
        errors.append(
            f"enrollment must be an ISO date (YYYY-MM-DD) when present, got: {enrollment!r}")

    if not body.strip():
        errors.append(
            "body is empty — a program definition must elaborate (presence); length is never gated")
    return errors


def main(argv):
    paths = argv[1:]
    if not paths:
        print("usage: pgm_lint.py PROGRAM.md [PROGRAM.md ...]")
        return 2
    total = 0
    for path in paths:
        errors = lint(path)
        if errors:
            total += len(errors)
            print(f"[PGM-LINT] FAIL: {path} — {len(errors)} violation(s):")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"[PGM-LINT] PASS: {path}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
