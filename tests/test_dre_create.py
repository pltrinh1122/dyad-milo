"""Deterministic V-pair for skills/dre_create.py (No-Pure-G invariant).

Fixtures are written to tmp_path. The suite NEVER touches real records — they
live in the private client repo and carry PII.

The constructor's claim is *construction over validation*: a record it builds
cannot carry the defect classes the linter exists to catch, because the values
never pass through hand-written YAML text. These tests hold it to that claim by
running the canonical ``dre_lint`` over its output — the integration proof —
and by regression-testing the ` #` truncation that ADR-0012 had to gate
(issue #26).
"""

import datetime as dt

import pytest
import yaml

from skills.dre_create import build_record, next_filename, practice_day_for, serialize
from skills.dre_lint import lint


def write(tmp_path, text, name):
    rec = tmp_path / name
    rec.write_text(text, encoding="utf-8")
    return rec


# --- the integration proof: constructed records satisfy the canonical gate ---

def test_constructed_record_passes_the_canonical_linter(tmp_path):
    text = serialize(build_record(
        primary="need to process guilt / seen / hope",
        created=dt.datetime(2026, 8, 6, 6, 33, 27,
                            tzinfo=dt.timezone(dt.timedelta(hours=-7))),
    ), body="A free-flowing reflection.\n")
    assert lint(write(tmp_path, text, "2026-08-06-01.md")) == []


def test_fully_loaded_record_passes(tmp_path):
    text = serialize(build_record(
        primary="state-capture — anxiety high",
        proximate="a news feed surfaced an article",
        boundary="work",
        setting="desk",
        programs=["reduce-anxiety", "improve-sleep"],
        observations=[{"programs": ["reduce-anxiety"], "intensity": "high",
                       "somatic": "sore jaw on waking"}],
        references=[{"id": "example-source",
                     "citation": {"title": "Example", "author": "A. Writer"},
                     "links": ["https://example.com/article"],
                     "essence": [{"id": "E1", "facet": "semantic",
                                  "partition": "trigger-time", "text": "a fragment"}],
                     "provenance": "how it was obtained",
                     "fidelity": "verify status"}],
        created=dt.datetime(2026, 8, 6, 6, 33, 27,
                            tzinfo=dt.timezone(dt.timedelta(hours=-7))),
    ), body="Reflection prose.\n")
    assert lint(write(tmp_path, text, "2026-08-06-01.md")) == []


# --- #26 regression: the defect class the constructor makes impossible ------

@pytest.mark.parametrize("value", [
    "continuing the identity thread (2026-08-05 entries #1-#4).",   # mid-value
    "#1-#4 leading hash consumes everything",                        # leading
    "tagged pgm#1-token",                                            # not a comment
    'he wrote "llm" in scare quotes',                                # quotes
    "vs. versus — punctuation",
])
def test_hash_bearing_values_survive_construction(tmp_path, value):
    """A serializer quotes what YAML would otherwise truncate (issue #26)."""
    text = serialize(build_record(primary="a trigger", proximate=value,
                                  created=dt.datetime(2026, 8, 6, 12, 0,
                                      tzinfo=dt.timezone(dt.timedelta(hours=-7)))),
                     body="body.\n")
    rec = write(tmp_path, text, "2026-08-06-01.md")
    assert lint(rec) == []
    parsed = yaml.safe_load(text.split("---\n")[1])
    assert parsed["trigger"]["proximate"] == value, "on-disk text and parsed value diverged"


# --- computed, not checked: bucket + filename ------------------------------

def test_practice_day_is_the_zone_calendar_day():
    created = dt.datetime(2026, 8, 6, 6, 33, tzinfo=dt.timezone(dt.timedelta(hours=-7)))
    assert practice_day_for(created, "America/Los_Angeles").isoformat() == "2026-08-06"


def test_practice_day_is_dst_correct_across_the_utc_boundary():
    """23:30 PT on the 6th is 06:30 UTC on the 7th — the bucket is the PT day."""
    created = dt.datetime(2026, 8, 7, 6, 30, tzinfo=dt.timezone.utc)
    assert practice_day_for(created, "America/Los_Angeles").isoformat() == "2026-08-06"


def test_filename_agrees_with_practice_day_and_sequences(tmp_path):
    day = dt.date(2026, 8, 6)
    assert next_filename(tmp_path, day) == "2026-08-06-01.md"
    (tmp_path / "2026-08-06-01.md").write_text("x")
    assert next_filename(tmp_path, day) == "2026-08-06-02.md"
    (tmp_path / "2026-08-06-02.md").write_text("x")
    assert next_filename(tmp_path, day) == "2026-08-06-03.md"


def test_sequence_ignores_other_days(tmp_path):
    (tmp_path / "2026-08-05-01.md").write_text("x")
    assert next_filename(tmp_path, dt.date(2026, 8, 6)) == "2026-08-06-01.md"


# --- three-layer capture model: the body is verbatim -----------------------

def test_body_is_written_verbatim(tmp_path):
    body = "  leading spaces, trailing spaces  \n\ttab\nblank line follows\n\n# not a heading\n"
    text = serialize(build_record(primary="t"), body=body)
    assert text.split("---\n", 2)[2] == body


def test_body_containing_frontmatter_delimiter_is_preserved(tmp_path):
    body = "the Operator wrote a literal delimiter:\n---\nand kept going\n"
    text = serialize(build_record(primary="t"), body=body)
    assert text.split("---\n", 2)[2] == body


# --- construction-time refusals (parameters, not a self-lint) --------------

def test_primary_is_required():
    with pytest.raises(ValueError, match="primary"):
        build_record(primary="")


def test_primary_none_is_refused():
    with pytest.raises(ValueError, match="none"):
        build_record(primary="none")


def test_bp0_in_programs_is_refused():
    with pytest.raises(ValueError, match="BP#0"):
        build_record(primary="t", programs=["BP#0"])


def test_observation_program_not_served_is_refused():
    with pytest.raises(ValueError, match="observations"):
        build_record(primary="t", programs=["reduce-anxiety"],
                     observations=[{"programs": ["improve-sleep"]}])


def test_naive_created_is_refused():
    with pytest.raises(ValueError, match="offset"):
        build_record(primary="t", created=dt.datetime(2026, 8, 6, 6, 33))


def test_invalid_zone_is_refused():
    with pytest.raises(ValueError, match="zone"):
        build_record(primary="t", zone="Mars/Olympus")


# --- serialization shape ---------------------------------------------------

def test_key_order_matches_the_schema():
    """dre-schema.md order — readable diffs depend on a stable key order."""
    rec = build_record(primary="t", programs=["reduce-anxiety"],
                       observations=[{"intensity": "high"}])
    fm = serialize(rec, body="b\n").split("---\n")[1]
    keys = [ln.split(":")[0] for ln in fm.splitlines()
            if ln and not ln[0].isspace() and not ln.startswith("-")]
    assert keys == ["record", "created", "practice_day", "zone", "trigger",
                    "programs", "observations"]


def test_created_keeps_the_iso8601_t_separator():
    """PyYAML would re-emit a datetime as 'YYYY-MM-DD HH:MM:SS'; the schema says ISO-8601."""
    text = serialize(build_record(
        primary="t",
        created=dt.datetime(2026, 8, 6, 6, 33, 27,
                            tzinfo=dt.timezone(dt.timedelta(hours=-7)))), body="b\n")
    assert "created: '2026-08-06T06:33:27-07:00'" in text or \
           "created: 2026-08-06T06:33:27-07:00" in text


def test_omitted_optionals_are_absent_not_null():
    fm = yaml.safe_load(serialize(build_record(primary="t"), body="b\n").split("---\n")[1])
    assert "proximate" not in fm["trigger"]
    assert "references" not in fm
    assert "observations" not in fm
    assert fm["programs"] == []
