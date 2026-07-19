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

# A record serving the first additional program (reduce-anxiety) with shared,
# record-level observation telemetry. The base envelope is unchanged; each
# observation may tag the program(s) it feeds so one datum serves several.
SUBCLASS_FM = """\
---
record: d-re
created: 2026-07-19T06:26:58-07:00
practice_day: 2026-07-19
zone: America/Los_Angeles
trigger:
  primary: state-capture — anxiety high, surfacing somatically
programs: [reduce-anxiety]
observations:
  - programs: [reduce-anxiety]
    intensity: high
    somatic: sore teeth and jaws on waking (nocturnal bruxism)
    situation: just woke up
    antecedent: a night of teeth-clenching
---
"""

# One observation feeding TWO programs at once (criterion: same record serves
# telemetry for multiple programs, no duplication).
MULTIPROGRAM_FM = """\
---
record: d-re
created: 2026-07-19T06:26:58-07:00
practice_day: 2026-07-19
zone: America/Los_Angeles
trigger:
  primary: state-capture — anxiety high, surfacing somatically
programs: [reduce-anxiety, improve-sleep]
observations:
  - programs: [reduce-anxiety, improve-sleep]
    intensity: high
    somatic: sore teeth and jaws on waking (nocturnal bruxism)
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


# --- observations (shared sub-class telemetry, spec § 6) -------------------

def test_observations_valid_passes(tmp_path):
    rec = write_record(tmp_path, fm=SUBCLASS_FM, name="2026-07-19-01.md")
    assert lint(rec) == []


def test_one_observation_serves_multiple_programs_passes(tmp_path):
    # The acceptance criterion: same record (one datum) feeds two programs.
    rec = write_record(tmp_path, fm=MULTIPROGRAM_FM, name="2026-07-19-01.md")
    assert lint(rec) == []


def test_program_listed_without_observations_passes(tmp_path):
    # Presence-not-quality extends here: a program can ride the base free-flow
    # with NO observations. Never gated.
    fm = SUBCLASS_FM[: SUBCLASS_FM.index("observations:")] + "---\n"
    assert lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md")) == []


def test_empty_observations_list_passes(tmp_path):
    # Zero observations is valid — quantity/completeness is never gated.
    fm = SUBCLASS_FM[: SUBCLASS_FM.index("observations:")] + "observations: []\n---\n"
    assert lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md")) == []


def test_observation_open_extensible_extra_field_passes(tmp_path):
    # Observation fields are open-extensible (mirrors the essence-facet pattern).
    fm = SUBCLASS_FM.replace(
        "    antecedent: a night of teeth-clenching\n",
        "    antecedent: a night of teeth-clenching\n"
        "    felt_where: chest and jaw\n",
    )
    assert lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md")) == []


def test_observation_program_not_served_by_record_fails(tmp_path):
    # An observation can only feed a program the record's programs[] serves.
    fm = SUBCLASS_FM.replace(
        "  - programs: [reduce-anxiety]",
        "  - programs: [improve-sleep]",
    )
    errors = lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md"))
    assert any("observations[0].programs" in e and "serve" in e for e in errors)


def test_observation_programs_bp0_fails(tmp_path):
    fm = SUBCLASS_FM.replace(
        "  - programs: [reduce-anxiety]",
        "  - programs: [reduce-anxiety, BP#0]",
    )
    errors = lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md"))
    assert any("BP#0" in e or "implicit" in e for e in errors)


def test_observations_not_a_list_fails(tmp_path):
    fm = SUBCLASS_FM[: SUBCLASS_FM.index("observations:")] + "observations: high\n---\n"
    errors = lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md"))
    assert any("observations" in e and "list" in e for e in errors)


def test_observation_not_a_mapping_fails(tmp_path):
    fm = SUBCLASS_FM[: SUBCLASS_FM.index("observations:")] + (
        "observations:\n  - just a string\n---\n")
    errors = lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md"))
    assert any("observations[0]" in e and "mapping" in e for e in errors)


def test_observation_empty_field_fails(tmp_path):
    fm = SUBCLASS_FM.replace("intensity: high", 'intensity: ""')
    errors = lint(write_record(tmp_path, fm=fm, name="2026-07-19-01.md"))
    assert any("intensity" in e for e in errors)
