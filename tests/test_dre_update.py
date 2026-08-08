"""Deterministic V-pair for skills/dre_update.py (No-Pure-G invariant).

Fixtures are written to tmp_path. The suite NEVER touches real records — they
live in the private client repo and carry PII.

The modifier's claim is that **canonicalization buys a readable diff**. A naive
parse→modify→dump of one field rewrote 27 of 16 frontmatter lines on a
hand-formatted record (ADR-0016). Starting from canonical form the same edit
changes two. These tests hold it to that number, and to the two invariants that
make canonicalization safe at all: it changes no value, and it never touches
the body.
"""

import datetime as dt

import pytest
import yaml

from skills.dre_create import build_record, serialize
from skills.dre_lint import lint
from skills.dre_update import apply_updates, canonicalize, split_record

CREATED = dt.datetime(2026, 8, 6, 6, 33, 27, tzinfo=dt.timezone(dt.timedelta(hours=-7)))

HAND_FORMATTED = """\
---
record: d-re
created: 2026-08-06T06:33:27-07:00
practice_day: 2026-08-06
zone: America/Los_Angeles
trigger:
  primary: need to process guilt / seen / hope
  proximate: a news feed surfaced an article
programs: [reduce-anxiety]
references:
  - id: example-source
    citation: {title: Example, author: A. Writer}
    links:
      - https://example.com/article
    provenance: |
      how it was obtained,
      held across two lines
---
The reflection prose.
"""


def write(tmp_path, text, name="2026-08-06-01.md"):
    rec = tmp_path / name
    rec.write_text(text, encoding="utf-8")
    return rec


def canonical_fixture(**kw):
    return serialize(build_record(primary="need to process guilt / seen / hope",
                                  proximate="a news feed surfaced an article",
                                  programs=["reduce-anxiety"], created=CREATED, **kw),
                     body="The reflection prose.\n")


def changed_lines(before, after):
    import difflib
    return sum(1 for ln in difflib.unified_diff(before.splitlines(), after.splitlines())
               if ln[:1] in "+-" and not ln.startswith(("+++", "---")))


# --- the premise: canonical form buys a minimal diff -----------------------

def test_update_from_canonical_form_changes_two_lines(tmp_path):
    """The whole reason canonicalization was chosen (ADR-0017)."""
    before = canonical_fixture()
    rec = write(tmp_path, before)
    after = apply_updates(rec, sets={"trigger.proximate": "an updated occasion"})
    assert changed_lines(before, after) == 2


def test_update_on_hand_formatted_record_is_why_canonicalization_is_needed(tmp_path):
    """Documents the cost being bought out — the same edit, uncanonicalized."""
    rec = write(tmp_path, HAND_FORMATTED)
    after = apply_updates(rec, sets={"trigger.proximate": "an updated occasion"})
    assert changed_lines(HAND_FORMATTED, after) > 10


# --- canonicalize: value-preserving, idempotent, body-verbatim ------------

def test_canonicalize_changes_no_value(tmp_path):
    rec = write(tmp_path, HAND_FORMATTED)
    before = yaml.safe_load(split_record(HAND_FORMATTED)[0])
    after = yaml.safe_load(split_record(canonicalize(rec))[0])
    assert before == after


def test_canonicalize_is_idempotent(tmp_path):
    rec = write(tmp_path, HAND_FORMATTED)
    once = canonicalize(rec)
    rec.write_text(once, encoding="utf-8")
    assert canonicalize(rec) == once


def test_canonicalize_preserves_the_body_verbatim(tmp_path):
    body = "  spaces  \n\ttab\n\nblank above\n"
    rec = write(tmp_path, HAND_FORMATTED.replace("The reflection prose.\n", body))
    assert split_record(canonicalize(rec))[1] == body


def test_canonicalize_preserves_a_literal_delimiter_in_the_body(tmp_path):
    body = "the Operator wrote:\n---\nand kept going\n"
    rec = write(tmp_path, HAND_FORMATTED.replace("The reflection prose.\n", body))
    assert split_record(canonicalize(rec))[1] == body


def test_constructor_output_is_already_canonical(tmp_path):
    """Constructor and canonicalizer must agree, or every new record is rewritten
    on its first update."""
    text = canonical_fixture()
    rec = write(tmp_path, text)
    assert canonicalize(rec) == text


def test_canonicalized_record_still_lints(tmp_path):
    rec = write(tmp_path, HAND_FORMATTED)
    rec.write_text(canonicalize(rec), encoding="utf-8")
    assert lint(rec) == []


# --- update: the layer it may touch, and the layer it may not -------------

def test_update_sets_a_nested_path(tmp_path):
    rec = write(tmp_path, canonical_fixture())
    fm = yaml.safe_load(split_record(
        apply_updates(rec, sets={"trigger.boundary": "work"}))[0])
    assert fm["trigger"]["boundary"] == "work"


def test_update_never_touches_the_body(tmp_path):
    body = "The reflection prose.\n"
    rec = write(tmp_path, canonical_fixture())
    after = apply_updates(rec, sets={"trigger.proximate": "changed"})
    assert split_record(after)[1] == body


def test_update_unsets_an_optional_field(tmp_path):
    rec = write(tmp_path, canonical_fixture())
    fm = yaml.safe_load(split_record(
        apply_updates(rec, unsets=["trigger.proximate"]))[0])
    assert "proximate" not in fm["trigger"]


@pytest.mark.parametrize("path", ["record", "created", "practice_day", "zone"])
def test_update_refuses_the_immutable_envelope(tmp_path, path):
    """created/zone move the adherence bucket and the filename — that is a
    re-file, not an update; practice_day is computed; record is the type."""
    rec = write(tmp_path, canonical_fixture())
    with pytest.raises(ValueError, match="immutable"):
        apply_updates(rec, sets={path: "2026-01-01"})


def test_update_refuses_an_unknown_top_level_field(tmp_path):
    rec = write(tmp_path, canonical_fixture())
    with pytest.raises(ValueError, match="unknown"):
        apply_updates(rec, sets={"nonsense": "x"})


# --- #26 stays impossible through the update path too ---------------------

@pytest.mark.parametrize("value", [
    "continuing the identity thread (2026-08-05 entries #1-#4).",
    "#1-#4 leading hash",
    'he wrote "llm" in scare quotes',
])
def test_hash_bearing_updates_survive(tmp_path, value):
    rec = write(tmp_path, canonical_fixture())
    text = apply_updates(rec, sets={"trigger.proximate": value})
    rec.write_text(text, encoding="utf-8")
    assert lint(rec) == []
    assert yaml.safe_load(split_record(text)[0])["trigger"]["proximate"] == value


def test_updated_record_still_lints(tmp_path):
    rec = write(tmp_path, canonical_fixture())
    rec.write_text(apply_updates(rec, sets={"trigger.proximate": "x"}), encoding="utf-8")
    assert lint(rec) == []


# --- split_record ---------------------------------------------------------

def test_split_record_rejects_a_file_without_frontmatter(tmp_path):
    rec = write(tmp_path, "# no frontmatter\n")
    with pytest.raises(ValueError, match="frontmatter"):
        split_record(rec.read_text())


# --- the script invocation path -------------------------------------------
#
# These tests exist because the suite missed a real defect: importing via the
# `skills` package works under pytest (repo root on sys.path) but NOT when the
# module is run as `python3 skills/dre_update.py`. Testing only the importable
# surface left the documented invocation unexercised — the same gap that hid
# the identical break in dre_adherence (ADR-0017).

import subprocess
import sys as _sys
from pathlib import Path as _Path

REPO_ROOT = _Path(__file__).resolve().parent.parent


def run_script(*args):
    return subprocess.run([_sys.executable, str(REPO_ROOT / "skills" / "dre_update.py"),
                           *args], capture_output=True, text=True)


def test_runs_as_a_script_for_set(tmp_path):
    rec = write(tmp_path, canonical_fixture())
    res = run_script(str(rec), "--set", "trigger.proximate=an updated occasion")
    assert res.returncode == 0, res.stderr
    assert yaml.safe_load(split_record(rec.read_text())[0])["trigger"]["proximate"] \
        == "an updated occasion"


def test_runs_as_a_script_for_canonicalize(tmp_path):
    rec = write(tmp_path, HAND_FORMATTED)
    res = run_script("--canonicalize", str(rec))
    assert res.returncode == 0, res.stderr
    assert lint(rec) == []


def test_script_refuses_immutable_field(tmp_path):
    rec = write(tmp_path, canonical_fixture())
    res = run_script(str(rec), "--set", "created=2020-01-01T00:00:00-07:00")
    assert res.returncode == 2
    assert "immutable" in res.stdout


def test_script_refuses_canonicalize_combined_with_set(tmp_path):
    rec = write(tmp_path, canonical_fixture())
    res = run_script("--canonicalize", str(rec), "--set", "trigger.proximate=x")
    assert res.returncode == 2
