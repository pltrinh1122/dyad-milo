"""Deterministic V-pair for skills/dre_lint.py (No-Pure-G invariant).

Fixtures are written to tmp_path. The suite NEVER touches real records — they
live in the private client repo and carry PII. It validates only the machine-
checkable base-class schema (daily-reflection-spec.md §§ 3-6).
"""

from pathlib import Path

from skills.dre_lint import lint

# A fully-loaded valid record: envelope + trigger (primary/proximate) + one
# reference with an essence fragment. created's PT calendar day == practice_day.
VALID_FM = """\
---
record: d-re
created: 2026-07-18T06:33:27-07:00
practice_day: 2026-07-18
zone: America/Los_Angeles
trigger:
  primary: need to process guilt / seen / hope
  proximate: a news feed surfaced an article
programs: []
references:
  - id: example-source
    citation: {title: Example, author: A. Writer, date: 2026-07-15, outlet: Example Daily}
    links:
      - https://example.com/article
    essence:
      - id: E1
        facet: semantic
        partition: trigger-time
        text: "a short verbatim fragment"
    provenance: supporting context, held separate from essence
    fidelity: how it was obtained; verify status
---
"""

# Minimal valid record: envelope + spontaneous primary trigger, no references.
MINIMAL_FM = """\
---
record: d-re
created: 2026-07-18T07:54:03-07:00
practice_day: 2026-07-18
zone: America/Los_Angeles
trigger:
  primary: a spontaneous state-capture (what I was feeling / doing / thinking)
programs: []
---
"""

VALID_BODY = "\nA free-flowing reflection. It can be as short as it needs to be.\n"


def write_record(tmp_path, fm=VALID_FM, body=VALID_BODY, name="2026-07-18-01.md"):
    rec = tmp_path / name
    rec.write_text(fm + body)
    return rec


# --- happy paths -----------------------------------------------------------

def test_valid_record_passes(tmp_path):
    assert lint(write_record(tmp_path)) == []


def test_minimal_record_without_references_passes(tmp_path):
    assert lint(write_record(tmp_path, fm=MINIMAL_FM, name="2026-07-18-02.md")) == []


def test_short_body_passes_presence_not_quality(tmp_path):
    # One word is a complete rep — length is never gated.
    assert lint(write_record(tmp_path, body="\nok.\n")) == []


# --- envelope --------------------------------------------------------------

def test_empty_body_fails(tmp_path):
    errors = lint(write_record(tmp_path, body="\n   \n"))
    assert any("body" in e for e in errors)


def test_missing_frontmatter_fails(tmp_path):
    rec = tmp_path / "2026-07-18-01.md"
    rec.write_text("# no frontmatter\n")
    assert any("frontmatter" in e for e in lint(rec))


def test_wrong_record_type_fails(tmp_path):
    fm = VALID_FM.replace("record: d-re", "record: journal")
    assert any("record" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_bad_practice_day_fails(tmp_path):
    fm = VALID_FM.replace("practice_day: 2026-07-18", 'practice_day: "07/18/2026"')
    assert any("practice_day" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_created_without_offset_fails(tmp_path):
    fm = VALID_FM.replace("2026-07-18T06:33:27-07:00", "2026-07-18T06:33:27")
    errors = lint(write_record(tmp_path, fm=fm))
    assert any("created" in e and "offset" in e for e in errors)


def test_invalid_zone_fails(tmp_path):
    fm = VALID_FM.replace("zone: America/Los_Angeles", "zone: Mars/Olympus")
    assert any("zone" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_bucket_mismatch_fails(tmp_path):
    # created is 06:33 PT on the 18th, so practice_day must be the 18th.
    fm = VALID_FM.replace("practice_day: 2026-07-18", "practice_day: 2026-07-19")
    errors = lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md"))
    assert any("practice_day" in e and "bucket" in e for e in errors)


def test_filename_practice_day_mismatch_fails(tmp_path):
    errors = lint(write_record(tmp_path, name="2026-07-19-01.md"))
    assert any("filename" in e for e in errors)


# --- trigger ---------------------------------------------------------------

def test_missing_trigger_primary_fails(tmp_path):
    fm = VALID_FM.replace("  primary: need to process guilt / seen / hope\n", "")
    assert any("primary" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_empty_trigger_primary_fails(tmp_path):
    fm = VALID_FM.replace("primary: need to process guilt / seen / hope", 'primary: ""')
    assert any("primary" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_trigger_primary_none_fails(tmp_path):
    # "spontaneous" is never "none".
    fm = VALID_FM.replace("primary: need to process guilt / seen / hope", 'primary: "none"')
    assert any("primary" in e for e in lint(write_record(tmp_path, fm=fm)))


# --- programs --------------------------------------------------------------

def test_programs_not_list_fails(tmp_path):
    fm = VALID_FM.replace("programs: []", "programs: physical-fitness")
    assert any("programs" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_programs_listing_bp0_fails(tmp_path):
    # BP#0 is implicit; never listed.
    fm = VALID_FM.replace("programs: []", 'programs: ["BP#0"]')
    errors = lint(write_record(tmp_path, fm=fm))
    assert any("BP#0" in e or "implicit" in e for e in errors)


# --- references ------------------------------------------------------------

def test_reference_without_links_fails(tmp_path):
    fm = VALID_FM.replace("    links:\n      - https://example.com/article\n", "    links: []\n")
    assert any("link" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_reference_empty_facet_fails(tmp_path):
    fm = VALID_FM.replace("facet: semantic", 'facet: ""')
    assert any("facet" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_reference_bad_partition_fails(tmp_path):
    fm = VALID_FM.replace("partition: trigger-time", "partition: someday")
    assert any("partition" in e for e in lint(write_record(tmp_path, fm=fm)))


def test_reference_empty_text_fails(tmp_path):
    fm = VALID_FM.replace('text: "a short verbatim fragment"', 'text: ""')
    assert any("text" in e for e in lint(write_record(tmp_path, fm=fm)))
