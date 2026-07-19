#!/usr/bin/env python3
"""dre_lint — schema gate for daily-reflection (``d-re``) records.

The mechanical validator for the base-class telemetry schema
(``dialectic/design/daily-reflection-spec.md`` §§ 3-6). Enforces ONLY
machine-checkable invariants — Builder vs Enforcer: quality/altitude judgments
live in the discipline, never here. In particular **presence-not-quality**: the
body must exist, but its length is never gated.

Checks:
  1. YAML frontmatter parses as a mapping; ``record == "d-re"``.
  2. ``practice_day`` is an ISO date; ``zone`` is a valid IANA zone;
     ``created`` is a timezone-aware ISO-8601 instant (carries an offset).
  3. ``practice_day`` equals the ``zone`` calendar day of ``created`` (the
     DST-correct adherence bucket).
  4. filename ``YYYY-MM-DD[-NN]`` (when it matches) agrees with ``practice_day``.
  5. ``trigger`` is a mapping with a non-empty ``primary`` that is never "none"
     (a spontaneous trigger is a state-capture, not none); optional
     ``proximate``/``boundary``/``setting`` are non-empty strings when present.
  6. ``programs`` is a list and never lists BP#0 (implicit, § 6).
  7. ``references`` (optional) — each has a non-empty ``links`` list; each
     ``essence`` fragment has a non-empty ``facet`` (open-extensible) and
     ``text``, and ``partition`` (if present) is trigger-time|confirmed-after.
  8. ``observations`` (optional, shared sub-class telemetry, § 6) — a list of
     mappings at the record level (NOT keyed by program), so one datum can serve
     several programs without duplication. Each observation may tag the
     program(s) it feeds via ``programs`` (⊆ the record's ``programs`` and never
     BP#0). Every field is optional and open-extensible; observations are NEVER
     required and never gated on quantity (presence-not-quality extends here — a
     program may ride the base free-flow with no observation).
  9. body (below the frontmatter) is non-empty.

Usage: python3 skills/dre_lint.py RECORD.md [RECORD.md ...]
Exit 0 = all pass; exit 1 = itemized failures on stdout.
"""

import datetime as dt
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-\d+)?$")
PARTITIONS = {"trigger-time", "confirmed-after"}
BP0_ALIASES = {"bp#0", "bp0", "behavioral-program #0", "behavioral-program-0",
               "behavioral-program#0"}


def split_frontmatter(text):
    """Return (frontmatter_str, body) or (None, text) if no frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:]


def _as_date(v):
    """Coerce a YAML value to a datetime.date, or None if it isn't one."""
    if isinstance(v, dt.datetime):
        return None  # a datetime is an instant, not a calendar day
    if isinstance(v, dt.date):
        return v
    if isinstance(v, str) and DATE_RE.match(v):
        try:
            return dt.date.fromisoformat(v)
        except ValueError:
            return None
    return None


def _as_aware_datetime(v):
    """Coerce a YAML value to a timezone-aware datetime, or None."""
    if isinstance(v, dt.datetime):
        return v if v.tzinfo is not None else None
    if isinstance(v, str):
        try:
            parsed = dt.datetime.fromisoformat(v)
        except ValueError:
            return None
        return parsed if parsed.tzinfo is not None else None
    return None


def _check_envelope(fm, rec):
    errors = []
    if fm.get("record") != "d-re":
        errors.append(f"record must be 'd-re', got: {fm.get('record')!r}")

    practice_day = _as_date(fm.get("practice_day"))
    if practice_day is None:
        errors.append(
            f"practice_day must be an ISO date (YYYY-MM-DD), got: {fm.get('practice_day')!r}")

    zone = fm.get("zone")
    tz = None
    if not zone:
        errors.append("zone is required (IANA, e.g. America/Los_Angeles)")
    else:
        try:
            tz = ZoneInfo(str(zone))
        except (ZoneInfoNotFoundError, ValueError):
            errors.append(f"zone is not a valid IANA zone: {zone!r}")

    created_raw = fm.get("created")
    created = _as_aware_datetime(created_raw)
    if created is None:
        naive = (isinstance(created_raw, dt.datetime) and created_raw.tzinfo is None)
        if isinstance(created_raw, str):
            try:
                naive = dt.datetime.fromisoformat(created_raw).tzinfo is None
            except ValueError:
                naive = False
        if naive:
            errors.append("created must carry a UTC offset (timezone-aware ISO-8601)")
        else:
            errors.append(
                f"created must be an ISO-8601 instant with offset, got: {created_raw!r}")

    if created is not None and tz is not None and practice_day is not None:
        pt_day = created.astimezone(tz).date()
        if pt_day != practice_day:
            errors.append(
                f"practice_day {practice_day.isoformat()} does not match the {zone} "
                f"calendar day (bucket) of created, which is {pt_day.isoformat()}")

    match = FILENAME_DATE_RE.match(rec.stem)
    if match and practice_day is not None and match.group(1) != practice_day.isoformat():
        errors.append(
            f"filename date {match.group(1)} does not match practice_day "
            f"{practice_day.isoformat()}")

    return errors


def _check_trigger(trigger):
    errors = []
    if not isinstance(trigger, dict):
        errors.append("trigger must be a mapping with a 'primary' field")
        return errors
    primary = trigger.get("primary")
    if primary is None:
        errors.append("trigger.primary is required and must never be empty or 'none'")
    elif not isinstance(primary, str) or not primary.strip():
        errors.append("trigger.primary must be a non-empty string")
    elif primary.strip().lower() == "none":
        errors.append(
            "trigger.primary must never be 'none' — a spontaneous trigger is a "
            "state-capture, not none")
    for opt in ("proximate", "boundary", "setting"):
        val = trigger.get(opt)
        if val is not None and (not isinstance(val, str) or not val.strip()):
            errors.append(f"trigger.{opt} must be a non-empty string when present")
    return errors


def _check_programs(programs):
    errors = []
    if programs is None:
        errors.append("programs is required (a list; default empty [])")
        return errors
    if not isinstance(programs, list):
        errors.append(f"programs must be a list, got: {type(programs).__name__}")
        return errors
    for prog in programs:
        if not isinstance(prog, str) or not prog.strip():
            errors.append(f"programs entries must be non-empty strings, got: {prog!r}")
        elif prog.strip().lower() in BP0_ALIASES:
            errors.append(
                "programs must not list BP#0 — it is implicit (every entry feeds it), "
                "never listed")
    return errors


# Optional observation fields, open-extensible (a record may add its own). The
# listed set is the vocabulary the practice reaches for; extras are allowed.
OBSERVATION_STR_FIELDS = ("intensity", "somatic", "situation", "antecedent",
                          "thought", "behavior", "relief", "note")


def _check_observations(observations, programs):
    """Shared, record-level sub-class telemetry (§ 6). Optional; never gated.

    A list of observation mappings (NOT keyed by program), so one datum can feed
    several programs. Invariants: a list of mappings; each field open-extensible
    and non-empty when a string is given; ``at`` is a timestamp or non-empty
    string; an observation's own ``programs`` (which program(s) it feeds) is a
    list ⊆ the record's ``programs`` and never BP#0. Observations are NEVER
    required and quantity is NEVER gated (presence-not-quality).
    """
    errors = []
    if observations is None:
        return errors  # optional
    if not isinstance(observations, list):
        errors.append("observations must be a list when present")
        return errors
    listed = {p for p in programs if isinstance(p, str)} if isinstance(programs, list) else set()
    for i, obs in enumerate(observations):
        tag = f"observations[{i}]"
        if not isinstance(obs, dict):
            errors.append(f"{tag} must be a mapping")
            continue
        for field in OBSERVATION_STR_FIELDS:
            val = obs.get(field)
            if val is not None and (not isinstance(val, str) or not val.strip()):
                errors.append(f"{tag}.{field} must be a non-empty string when present")
        at = obs.get("at")
        if at is not None and not isinstance(at, (str, dt.datetime, dt.date)):
            errors.append(f"{tag}.at must be a timestamp or non-empty string when present")
        elif isinstance(at, str) and not at.strip():
            errors.append(f"{tag}.at must be a timestamp or non-empty string when present")
        obs_programs = obs.get("programs")
        if obs_programs is not None:
            if not isinstance(obs_programs, list):
                errors.append(f"{tag}.programs must be a list of program-ids when present")
                continue
            for prog in obs_programs:
                if not isinstance(prog, str) or not prog.strip():
                    errors.append(f"{tag}.programs entries must be non-empty program-ids, got: {prog!r}")
                elif prog.strip().lower() in BP0_ALIASES:
                    errors.append(
                        f"{tag}.programs must not list BP#0 — it is implicit (the base)")
                elif prog not in listed:
                    errors.append(
                        f"{tag}.programs lists {prog!r}, which the record's programs[] does not "
                        f"serve — an observation can only feed a program the record serves")
    return errors


def _check_references(references):
    errors = []
    if references is None:
        return errors  # optional
    if not isinstance(references, list):
        errors.append("references must be a list when present")
        return errors
    for i, ref in enumerate(references):
        tag = f"references[{i}]"
        if not isinstance(ref, dict):
            errors.append(f"{tag} must be a mapping")
            continue
        links = ref.get("links")
        if (not isinstance(links, list) or not links
                or not all(isinstance(url, str) and url.strip() for url in links)):
            errors.append(f"{tag}.links must be a non-empty list of URLs")
        essence = ref.get("essence")
        if essence is None:
            continue
        if not isinstance(essence, list):
            errors.append(f"{tag}.essence must be a list when present")
            continue
        for j, frag in enumerate(essence):
            ftag = f"{tag}.essence[{j}]"
            if not isinstance(frag, dict):
                errors.append(f"{ftag} must be a mapping")
                continue
            facet = frag.get("facet")
            if not isinstance(facet, str) or not facet.strip():
                errors.append(
                    f"{ftag}.facet must be a non-empty string (facets are open-extensible)")
            text = frag.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{ftag}.text must be a non-empty string")
            partition = frag.get("partition")
            if partition is not None and partition not in PARTITIONS:
                errors.append(
                    f"{ftag}.partition must be one of {sorted(PARTITIONS)} when present, "
                    f"got: {partition!r}")
    return errors


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
    errors.extend(_check_envelope(fm, rec))
    errors.extend(_check_trigger(fm.get("trigger")))
    errors.extend(_check_programs(fm.get("programs")))
    errors.extend(_check_observations(fm.get("observations"), fm.get("programs")))
    errors.extend(_check_references(fm.get("references")))
    if not body.strip():
        errors.append(
            "body is empty — an entry must say something (presence); length is never gated")
    return errors


def main(argv):
    paths = argv[1:]
    if not paths:
        print("usage: dre_lint.py RECORD.md [RECORD.md ...]")
        return 2
    total = 0
    for path in paths:
        errors = lint(path)
        if errors:
            total += len(errors)
            print(f"[DRE-LINT] FAIL: {path} — {len(errors)} violation(s):")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"[DRE-LINT] PASS: {path}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
