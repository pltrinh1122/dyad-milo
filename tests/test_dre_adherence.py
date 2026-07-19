"""Deterministic V-pair for skills/dre_adherence.py.

Synthetic fixtures in tmp_path only — never real records (PII). `as_of` is
always passed explicitly so windows are reproducible without a real clock.
"""

import datetime as dt

from skills.dre_adherence import adherence, load_records

ENROLL = dt.date(2026, 7, 18)


def make_record(d, day, programs="[]", name=None, created=None, body="a reflection"):
    created = created or f"{day}T09:00:00-07:00"
    name = name or f"{day}-01.md"
    (d / name).write_text(
        "---\n"
        "record: d-re\n"
        f"created: {created}\n"
        f"practice_day: {day}\n"
        "zone: America/Los_Angeles\n"
        "trigger:\n  primary: x\n"
        f"programs: {programs}\n"
        "---\n"
        f"{body}\n"
    )


def test_perfect_adherence(tmp_path):
    for day in ("2026-07-18", "2026-07-19", "2026-07-20"):
        make_record(tmp_path, day)
    records, skipped = load_records(tmp_path)
    assert skipped == []
    rep = adherence(records, enrollment=ENROLL, as_of=dt.date(2026, 7, 20))
    assert rep["since_start"] == {"covered": 3, "eligible": 3, "rate": 1.0, "lapses": 0}


def test_lapse_counts(tmp_path):
    make_record(tmp_path, "2026-07-18")
    make_record(tmp_path, "2026-07-20")
    records, _ = load_records(tmp_path)
    rep = adherence(records, enrollment=ENROLL, as_of=dt.date(2026, 7, 20))
    assert rep["since_start"]["covered"] == 2
    assert rep["since_start"]["eligible"] == 3
    assert rep["since_start"]["lapses"] == 1
    assert abs(rep["since_start"]["rate"] - 2 / 3) < 1e-9


def test_multiple_entries_same_day_count_once(tmp_path):
    make_record(tmp_path, "2026-07-18", name="2026-07-18-01.md")
    make_record(tmp_path, "2026-07-18", name="2026-07-18-02.md",
                created="2026-07-18T11:00:00-07:00")
    records, _ = load_records(tmp_path)
    rep = adherence(records, enrollment=ENROLL, as_of=dt.date(2026, 7, 18))
    assert rep["since_start"]["covered"] == 1
    assert rep["since_start"]["eligible"] == 1


def test_program_filter(tmp_path):
    make_record(tmp_path, "2026-07-18", programs="['physical-fitness']")
    records, _ = load_records(tmp_path)
    as_of = dt.date(2026, 7, 18)
    assert adherence(records, program=None, enrollment=ENROLL, as_of=as_of)["since_start"]["covered"] == 1
    assert adherence(records, program="physical-fitness", enrollment=ENROLL, as_of=as_of)["since_start"]["covered"] == 1
    assert adherence(records, program="nutrition", enrollment=ENROLL, as_of=as_of)["since_start"]["covered"] == 0


def test_reduce_anxiety_program_measured_from_its_enrollment(tmp_path):
    # The first additional program materialized: its adherence rides the same
    # program-agnostic meter, with its own (later) enrollment day.
    make_record(tmp_path, "2026-07-19", programs="['reduce-anxiety']")
    make_record(tmp_path, "2026-07-20", programs="['reduce-anxiety']")
    records, _ = load_records(tmp_path)
    rep = adherence(records, program="reduce-anxiety",
                    enrollment=dt.date(2026, 7, 19), as_of=dt.date(2026, 7, 20))
    assert rep["since_start"] == {"covered": 2, "eligible": 2, "rate": 1.0, "lapses": 0}
    # A base-only day (no reduce-anxiety) is a lapse for the program, not the base.
    make_record(tmp_path, "2026-07-21")  # base entry, programs: []
    records, _ = load_records(tmp_path)
    rep = adherence(records, program="reduce-anxiety",
                    enrollment=dt.date(2026, 7, 19), as_of=dt.date(2026, 7, 21))
    assert rep["since_start"]["covered"] == 2
    assert rep["since_start"]["eligible"] == 3
    assert rep["since_start"]["lapses"] == 1


def test_one_record_counts_for_multiple_programs(tmp_path):
    # Same record serves telemetry for multiple programs: it is covered for each
    # program its programs[] lists, and for the base.
    make_record(tmp_path, "2026-07-19", programs="['reduce-anxiety', 'improve-sleep']")
    records, _ = load_records(tmp_path)
    as_of = dt.date(2026, 7, 19)
    enroll = dt.date(2026, 7, 19)
    assert adherence(records, program="reduce-anxiety", enrollment=enroll, as_of=as_of)["since_start"]["covered"] == 1
    assert adherence(records, program="improve-sleep", enrollment=enroll, as_of=as_of)["since_start"]["covered"] == 1
    assert adherence(records, program=None, enrollment=enroll, as_of=as_of)["since_start"]["covered"] == 1


def test_bp0_program_is_base(tmp_path):
    make_record(tmp_path, "2026-07-18")
    records, _ = load_records(tmp_path)
    rep = adherence(records, program="BP#0", enrollment=ENROLL, as_of=dt.date(2026, 7, 18))
    assert rep["since_start"]["covered"] == 1  # BP#0 == base == all


def test_fail_closed_skips_malformed(tmp_path):
    make_record(tmp_path, "2026-07-18")
    (tmp_path / "broken.md").write_text("---\nnot: [valid\n---\nbody\n")
    (tmp_path / "noday.md").write_text("---\nrecord: d-re\n---\nbody\n")
    records, skipped = load_records(tmp_path)
    assert len(records) == 1
    assert len(skipped) == 2
    rep = adherence(records, enrollment=ENROLL, as_of=dt.date(2026, 7, 18))
    assert rep["since_start"]["covered"] == 1  # still computes on the good record


def test_rolling_windows(tmp_path):
    make_record(tmp_path, "2026-08-20")
    records, _ = load_records(tmp_path)
    rep = adherence(records, enrollment=ENROLL, as_of=dt.date(2026, 8, 20))
    assert rep["rolling"][7] == {"covered": 1, "eligible": 7, "rate": 1 / 7, "lapses": 6}
    # since-start eligible = 18 Jul .. 20 Aug inclusive = 34 days
    assert rep["since_start"]["eligible"] == 34
    assert rep["since_start"]["covered"] == 1
