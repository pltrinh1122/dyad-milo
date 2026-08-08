#!/usr/bin/env python3
"""dre_create — construct a daily-reflection (``d-re``) record.

**Construction over validation.** A record built here cannot carry the defect
classes ``dre_lint`` exists to catch, because the values never pass through
hand-written YAML text: a serializer quotes what YAML would otherwise truncate.
Issue #26 — an unquoted plain scalar containing ` #` silently losing its tail —
is not *gated* here, it is **impossible** (ADR-0012 remains the gate for records
that arrive by any other path, including hand edits).

Five of ``dre_lint``'s checks stop being failable for constructed records: the
envelope types, the ``practice_day`` bucket and the filename are **computed**
rather than checked, and capture-fidelity has no hand-serialization to fail.

**This module does not lint its own output.** A capture-time self-lint is an
explicit non-goal (ADR-0007): capture is un-gated, validation gates the *land*,
and the adversarial-validate re-lints before anything reaches ``main``. The
refusals below are *parameter* requirements — you cannot construct a record
without a trigger — not a validation pass.

**Generate/Validate do not collapse.** ``dre_lint`` stays the independent
validator; a correct constructor is no reason to retire it. Records are still
edited by hand after creation, and the disposer must never be the generator.

Usage:
  python3 skills/dre_create.py --primary TEXT [--proximate TEXT] [--boundary TEXT]
      [--setting TEXT] [--zone IANA] [--created ISO8601] [--program NAME ...]
      [--observation JSON ...] [--reference JSON ...]
      [--body TEXT | --body-file PATH | --body-stdin] [--dir DIR] [--print]

Writes ``DIR/YYYY-MM-DD-NN.md`` and prints the path; ``--print`` writes nothing
and emits the record on stdout instead.
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml

DEFAULT_ZONE = "America/Los_Angeles"
FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d+)$")
BP0_ALIASES = {"bp#0", "bp0", "behavioral-program #0", "behavioral-program-0",
               "behavioral-program#0"}
# dre-schema.md order. Stable key order is what keeps a record's diff readable —
# the review path (d-rub-with-land, Operator-disposes-at-merge) runs on diffs.
KEY_ORDER = ("record", "created", "practice_day", "zone", "trigger",
             "references", "programs", "observations")


def practice_day_for(created, zone):
    """The ``zone`` calendar day of ``created`` — the DST-correct adherence bucket.

    Computed, never asked for: the agreement ``dre_lint`` checks cannot fail
    when the value is derived rather than supplied.
    """
    return created.astimezone(ZoneInfo(zone)).date()


def next_filename(directory, day):
    """``YYYY-MM-DD-NN.md``, sequencing after any records already on that day."""
    used = set()
    directory = Path(directory)
    if directory.is_dir():
        for path in directory.glob("*.md"):
            match = FILENAME_RE.match(path.stem)
            if match and match.group(1) == day.isoformat():
                used.add(int(match.group(2)))
    seq = 1
    while seq in used:
        seq += 1
    return f"{day.isoformat()}-{seq:02d}.md"


def _require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required and must be a non-empty string")
    return value


def build_record(primary, proximate=None, boundary=None, setting=None,
                 programs=None, observations=None, references=None,
                 created=None, zone=DEFAULT_ZONE):
    """Build the frontmatter mapping. Raises ValueError on an unbuildable record."""
    _require_text(primary, "trigger.primary")
    if primary.strip().lower() == "none":
        raise ValueError(
            "trigger.primary must never be 'none' — a spontaneous trigger is a "
            "state-capture, not none")

    try:
        tz = ZoneInfo(str(zone))
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(f"zone is not a valid IANA zone: {zone!r}")

    created = created or dt.datetime.now(tz)
    if not isinstance(created, dt.datetime) or created.tzinfo is None:
        raise ValueError("created must carry a UTC offset (timezone-aware ISO-8601)")

    programs = list(programs or [])
    for prog in programs:
        _require_text(prog, "programs entry")
        if prog.strip().lower() in BP0_ALIASES:
            raise ValueError(
                "programs must not list BP#0 — it is implicit (every entry feeds it)")

    observations = [dict(obs) for obs in (observations or [])]
    for i, obs in enumerate(observations):
        for prog in obs.get("programs", []) or []:
            if prog.strip().lower() in BP0_ALIASES:
                raise ValueError(f"observations[{i}].programs must not list BP#0")
            if prog not in programs:
                raise ValueError(
                    f"observations[{i}].programs lists {prog!r}, which the record's "
                    f"programs[] does not serve")

    trigger = {"primary": primary}
    for name, value in (("proximate", proximate), ("boundary", boundary),
                        ("setting", setting)):
        if value is not None:
            trigger[name] = _require_text(value, f"trigger.{name}")

    record = {
        "record": "d-re",
        # Emitted as a string so the ISO-8601 'T' survives: PyYAML re-emits a
        # datetime as 'YYYY-MM-DD HH:MM:SS±HH:MM', which parses but no longer
        # matches the form dre-schema.md documents.
        "created": created.isoformat(),
        "practice_day": practice_day_for(created, zone).isoformat(),
        "zone": str(zone),
        "trigger": trigger,
        "programs": programs,
    }
    if references:
        record["references"] = [dict(ref) for ref in references]
    if observations:
        record["observations"] = observations
    return record


def serialize(record, body):
    """Frontmatter + verbatim body.

    The body is written **literally** — it is the Operator's own words
    (three-layer capture model: body ⟶ verbatim ⟶ fidelity). It is never parsed,
    reflowed, or re-serialized, so a literal ``---`` inside it survives.
    """
    ordered = {k: record[k] for k in KEY_ORDER if k in record}
    ordered.update({k: v for k, v in record.items() if k not in KEY_ORDER})
    fm = yaml.dump(ordered, sort_keys=False, allow_unicode=True,
                   default_flow_style=False, width=100)
    return f"---\n{fm}---\n{body}"


def _json_arg(raw, label):
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--{label} must be valid JSON: {exc}")
    if not isinstance(value, dict):
        raise ValueError(f"--{label} must be a JSON object")
    return value


def main(argv):
    parser = argparse.ArgumentParser(
        prog="dre_create.py", description="Construct a d-re record.")
    parser.add_argument("--primary", required=True, help="trigger.primary (required)")
    parser.add_argument("--proximate")
    parser.add_argument("--boundary")
    parser.add_argument("--setting")
    parser.add_argument("--zone", default=DEFAULT_ZONE)
    parser.add_argument("--created", help="ISO-8601 instant with offset; default now")
    parser.add_argument("--program", action="append", default=[], dest="programs")
    parser.add_argument("--observation", action="append", default=[],
                        dest="observations", help="JSON object; repeatable")
    parser.add_argument("--reference", action="append", default=[],
                        dest="references", help="JSON object; repeatable")
    body_src = parser.add_mutually_exclusive_group()
    body_src.add_argument("--body")
    body_src.add_argument("--body-file")
    body_src.add_argument("--body-stdin", action="store_true")
    parser.add_argument("--dir", default="reflections")
    parser.add_argument("--print", action="store_true", dest="to_stdout",
                        help="emit to stdout instead of writing a file")
    args = parser.parse_args(argv[1:])

    try:
        created = dt.datetime.fromisoformat(args.created) if args.created else None
        record = build_record(
            primary=args.primary, proximate=args.proximate, boundary=args.boundary,
            setting=args.setting, programs=args.programs,
            observations=[_json_arg(o, "observation") for o in args.observations],
            references=[_json_arg(r, "reference") for r in args.references],
            created=created, zone=args.zone)
    except ValueError as exc:
        print(f"[DRE-CREATE] refused: {exc}")
        return 2

    if args.body_stdin:
        body = sys.stdin.read()
    elif args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    else:
        body = args.body if args.body is not None else ""
    if not body.strip():
        print("[DRE-CREATE] refused: a record must say something — body is empty")
        return 2
    if not body.endswith("\n"):
        body += "\n"

    text = serialize(record, body)
    if args.to_stdout:
        sys.stdout.write(text)
        return 0

    directory = Path(args.dir)
    directory.mkdir(parents=True, exist_ok=True)
    day = dt.date.fromisoformat(record["practice_day"])
    path = directory / next_filename(directory, day)
    path.write_text(text, encoding="utf-8")
    print(f"[DRE-CREATE] wrote: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
