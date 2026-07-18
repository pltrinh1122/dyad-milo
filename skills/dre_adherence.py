#!/usr/bin/env python3
"""dre_adherence — program-agnostic, fail-closed adherence for ``d-re`` records.

Computes the base meter (spec § 9): covered-days / eligible-days since enrollment,
plus rolling 7 / 30 / 90-day windows, bucketing by the ``practice_day`` (PT
calendar day) already stamped on each record.

- **Program-agnostic:** ``--program`` filters to records whose ``programs[]``
  lists it; no program (or BP#0, which is implicit) counts every record.
- **Fail-closed:** a record that does not parse or lacks a ``practice_day`` is
  **skipped and reported**, never counted and never crashes the run. This tool
  only ever prints/returns a report — it never writes anywhere. Surfacing a
  number publicly is a separate manual step, by design.

Usage: python3 skills/dre_adherence.py RECORDS_DIR [--program P]
       [--enrollment YYYY-MM-DD] [--as-of YYYY-MM-DD]
"""

import argparse
import datetime as dt
import sys
from pathlib import Path

import yaml

from skills.dre_lint import _as_date, split_frontmatter

DEFAULT_ENROLLMENT = dt.date(2026, 7, 18)
BP0_ALIASES = {"bp#0", "bp0", "behavioral-program #0", "behavioral-program-0",
               "behavioral-program#0"}


def load_records(records_dir):
    """Return (records, skipped). Fail-closed: unparseable records are skipped."""
    root = Path(records_dir)
    records, skipped = [], []
    for path in sorted(root.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            skipped.append((str(path), f"unreadable: {exc}"))
            continue
        fm_text, _ = split_frontmatter(text)
        if fm_text is None:
            skipped.append((str(path), "no frontmatter"))
            continue
        try:
            fm = yaml.safe_load(fm_text)
        except yaml.YAMLError as exc:
            skipped.append((str(path), f"frontmatter parse error: {exc}"))
            continue
        if not isinstance(fm, dict) or fm.get("record") != "d-re":
            skipped.append((str(path), "not a d-re record"))
            continue
        day = _as_date(fm.get("practice_day"))
        if day is None:
            skipped.append((str(path), "missing/invalid practice_day"))
            continue
        programs = fm.get("programs") or []
        if not isinstance(programs, list):
            skipped.append((str(path), "programs is not a list"))
            continue
        records.append({"path": str(path), "practice_day": day,
                        "programs": [str(p) for p in programs]})
    return records, skipped


def _matches(record, program):
    if program is None or program.strip().lower() in BP0_ALIASES:
        return True  # base / BP#0 (implicit) counts every record
    return program in record["programs"]


def _window(covered_days, start, end):
    if end < start:
        return {"covered": 0, "eligible": 0, "rate": None, "lapses": 0}
    eligible = (end - start).days + 1
    covered = sum(1 for d in covered_days if start <= d <= end)
    return {"covered": covered, "eligible": eligible,
            "rate": (covered / eligible) if eligible else None,
            "lapses": eligible - covered}


def adherence(records, program=None, enrollment=DEFAULT_ENROLLMENT, as_of=None):
    if as_of is None:
        as_of = dt.date.today()
    covered = {r["practice_day"] for r in records if _matches(r, program)}
    rolling = {}
    for n in (7, 30, 90):
        start = max(enrollment, as_of - dt.timedelta(days=n - 1))
        rolling[n] = _window(covered, start, as_of)
    return {
        "program": program or "(base / BP#0)",
        "enrollment": enrollment.isoformat(),
        "as_of": as_of.isoformat(),
        "since_start": _window(covered, enrollment, as_of),
        "rolling": rolling,
        "covered_days": sorted(
            d.isoformat() for d in covered if enrollment <= d <= as_of),
    }


def format_report(report, skipped):
    def pct(window):
        return "n/a" if window["rate"] is None else f"{window['rate'] * 100:.0f}%"

    lines = [
        f"adherence — program: {report['program']}",
        f"  window: enrollment {report['enrollment']} → as-of {report['as_of']}",
    ]
    s = report["since_start"]
    lines.append(
        f"  since start: {s['covered']}/{s['eligible']} = {pct(s)}  (lapses: {s['lapses']})")
    for n in (7, 30, 90):
        w = report["rolling"][n]
        lines.append(f"  rolling {n:>2}d: {w['covered']}/{w['eligible']} = {pct(w)}")
    if skipped:
        lines.append(f"  fail-closed: {len(skipped)} record(s) skipped, not counted:")
        for path, reason in skipped:
            lines.append(f"    - {path}: {reason}")
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="d-re adherence (fail-closed)")
    parser.add_argument("records_dir")
    parser.add_argument("--program", default=None)
    parser.add_argument("--enrollment", default=DEFAULT_ENROLLMENT.isoformat())
    parser.add_argument("--as-of", default=None, dest="as_of")
    args = parser.parse_args(argv[1:])
    enrollment = dt.date.fromisoformat(args.enrollment)
    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    records, skipped = load_records(args.records_dir)
    report = adherence(records, program=args.program, enrollment=enrollment, as_of=as_of)
    print(format_report(report, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
