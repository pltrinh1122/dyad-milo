"""Deterministic V-pair for skills/pgm_lint.py (No-Pure-G invariant).

Fixtures are written to tmp_path. Validates only the machine-checkable program
schema (ADR-0010; daily-reflection-spec.md § 6) — the pgm-operating-invariant
(minimum two slots) + identity/filename agreement + shape-if-present.
"""

from skills.pgm_lint import lint

# A program that leaves value/invariant UNSET → inherits milo's parent slots.
# The two required slots (program + program_telos) are present. Mirrors
# reduce-anxiety after it conforms to the four-slot model.
INHERIT_FM = """\
---
program_id: reduce-anxiety
program: "Make anxiety legible — surface anxious feelings + somatic markers as they occur."
program_telos: "Understanding — the root cause found; the precondition for later intervention."
enrollment: 2026-07-19
---
"""

# A program that SETS its own value + invariant (may contradict milo's — allowed,
# sub-agent-isolated). Mirrors emerging-identity.
OWN_SLOTS_FM = """\
---
program_id: emerging-identity
program: "Explore and consolidate a coherent sense of self through elicitation."
program_telos: "A self-authored identity the Operator inhabits without external scaffolding."
program_value: "being-over-having"
program_invariant: "never-outsource-worth"
enrollment: 2026-07-25
---
"""

VALID_BODY = "\nA program definition. It elaborates the four-slot core below.\n"


def write_pgm(tmp_path, fm=INHERIT_FM, body=VALID_BODY, name="reduce-anxiety.md"):
    pgm = tmp_path / name
    pgm.write_text(fm + body)
    return pgm


# --- happy paths -----------------------------------------------------------

def test_inherit_program_passes(tmp_path):
    """Two required slots present, value/invariant unset (inherit) → valid."""
    assert lint(write_pgm(tmp_path)) == []


def test_own_slots_program_passes(tmp_path):
    """A program that sets its own value + invariant is valid."""
    assert lint(write_pgm(tmp_path, fm=OWN_SLOTS_FM, name="emerging-identity.md")) == []


def test_enrollment_optional(tmp_path):
    fm = """\
---
program_id: no-enrollment-yet
program: "A program not yet enrolled."
program_telos: "Somewhere."
---
"""
    assert lint(write_pgm(tmp_path, fm=fm, name="no-enrollment-yet.md")) == []


# --- pgm-operating-invariant (the two required slots) ----------------------

def test_missing_program_slot_fails(tmp_path):
    fm = """\
---
program_id: p
program_telos: "Somewhere."
---
"""
    errors = lint(write_pgm(tmp_path, fm=fm, name="p.md"))
    assert any("program is required" in e for e in errors)


def test_missing_program_telos_slot_fails(tmp_path):
    fm = """\
---
program_id: p
program: "What it is."
---
"""
    errors = lint(write_pgm(tmp_path, fm=fm, name="p.md"))
    assert any("program_telos is required" in e for e in errors)


def test_empty_required_slot_fails(tmp_path):
    fm = """\
---
program_id: p
program: "   "
program_telos: "Somewhere."
---
"""
    errors = lint(write_pgm(tmp_path, fm=fm, name="p.md"))
    assert any("program must be a non-empty string" in e for e in errors)


# --- identity / filename agreement -----------------------------------------

def test_program_id_missing_fails(tmp_path):
    fm = """\
---
program: "What it is."
program_telos: "Somewhere."
---
"""
    errors = lint(write_pgm(tmp_path, fm=fm, name="p.md"))
    assert any("program_id is required" in e for e in errors)


def test_program_id_filename_mismatch_fails(tmp_path):
    errors = lint(write_pgm(tmp_path, fm=INHERIT_FM, name="wrong-name.md"))
    assert any("does not match the filename stem" in e for e in errors)


# --- optional slots: shape-if-present --------------------------------------

def test_empty_optional_slot_fails(tmp_path):
    fm = """\
---
program_id: p
program: "What it is."
program_telos: "Somewhere."
program_value: ""
---
"""
    errors = lint(write_pgm(tmp_path, fm=fm, name="p.md"))
    assert any("program_value must be a non-empty string when set" in e for e in errors)


def test_bad_enrollment_fails(tmp_path):
    fm = """\
---
program_id: p
program: "What it is."
program_telos: "Somewhere."
enrollment: someday
---
"""
    errors = lint(write_pgm(tmp_path, fm=fm, name="p.md"))
    assert any("enrollment must be an ISO date" in e for e in errors)


# --- structural ------------------------------------------------------------

def test_no_frontmatter_fails(tmp_path):
    pgm = tmp_path / "p.md"
    pgm.write_text("# just a heading, no frontmatter\n")
    assert lint(pgm) == ["no YAML frontmatter block found"]


def test_empty_body_fails(tmp_path):
    assert any("body is empty" in e for e in lint(write_pgm(tmp_path, body="\n")))


def test_extra_keys_allowed(tmp_path):
    """Open-extensible: a method-override pointer (behavioral) is not a linted slot."""
    fm = """\
---
program_id: p
program: "What it is."
program_telos: "Somewhere."
methods: {riff: elicitation-mode}
---
"""
    assert lint(write_pgm(tmp_path, fm=fm, name="p.md")) == []
