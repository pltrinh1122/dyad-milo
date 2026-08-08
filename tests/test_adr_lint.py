"""Deterministic V-pair for skills/adr_lint.py (No-Pure-G invariant).

Fixtures are written to tmp_path; the git-provenance tests build **real, tiny
git repositories** there rather than mocking, because the check being verified
is exactly "what does git say" — a mocked answer would prove nothing.

The case that matters is `2769ed8`: a single Agent-authored commit that created
ADRs 0001-0003 *and* marked them `accepted`. Self-ratification, undetected for
three weeks. `test_accepted_in_the_creating_commit_fails` is that commit,
reconstructed.
"""

import subprocess

import pytest

from skills.adr_lint import lint, parse_header, source_stamp

HEADER = """\
# ADR-0099 — a decision

- **Status:** proposed (2026-08-08)
- **Urgency:** medium — cited by two other ADRs
- **Drift-dimension:** coverage — recorded for review

## Context

Something happened.

## Agent lean

Ratify. The reasoning holds.
"""


def write(tmp_path, text=HEADER, name="0099-a-decision.md"):
    adr = tmp_path / name
    adr.write_text(text, encoding="utf-8")
    return adr


# --- happy path ------------------------------------------------------------

def test_canonical_adr_passes(tmp_path):
    assert lint(write(tmp_path)) == []


def test_real_adrs_pass(tmp_path):
    """The repo's own set must satisfy the form it declares."""
    from pathlib import Path
    adr_dir = Path(__file__).resolve().parent.parent / "dialectic" / "design" / "adr"
    failures = {p.name: lint(p) for p in sorted(adr_dir.glob("*.md")) if lint(p)}
    assert not failures, failures


# --- required fields -------------------------------------------------------

@pytest.mark.parametrize("field", ["Status", "Urgency", "Drift-dimension"])
def test_missing_required_field_fails(tmp_path, field):
    text = "\n".join(ln for ln in HEADER.splitlines() if not ln.startswith(f"- **{field}:"))
    errors = lint(write(tmp_path, text + "\n"))
    assert any(field in e and "missing" in e for e in errors)


# --- Status: review outcome only, never merge state ------------------------

def test_status_carrying_merge_state_fails(tmp_path):
    """The defect the audit found in 9 of 15 ADRs."""
    text = HEADER.replace("proposed (2026-08-08)",
                          "proposed (2026-08-08) — Operator-disposed; awaiting PR review")
    errors = lint(write(tmp_path, text))
    assert any("Status" in e for e in errors)


@pytest.mark.parametrize("bad", [
    "proposed", "accepted 2026-08-08", "in-review (2026-08-08)",
    "proposed (08-08-2026)", "**proposed — decision NOT made.**",
])
def test_non_canonical_status_fails(tmp_path, bad):
    errors = lint(write(tmp_path, HEADER.replace("proposed (2026-08-08)", bad)))
    assert any("Status" in e for e in errors)


@pytest.mark.parametrize("good", ["proposed", "accepted", "rejected"])
def test_canonical_status_vocabulary_passes(tmp_path, good):
    text = HEADER.replace("proposed (2026-08-08)", f"{good} (2026-08-08)")
    # `accepted` additionally needs git provenance; check the header rule alone.
    assert not [e for e in lint(write(tmp_path, text), check_git=False) if "Status" in e]


# --- Urgency ---------------------------------------------------------------

@pytest.mark.parametrize("bad", ["urgent — now", "high", "medium"])
def test_bad_urgency_fails(tmp_path, bad):
    errors = lint(write(tmp_path, HEADER.replace("medium — cited by two other ADRs", bad)))
    assert any("Urgency" in e for e in errors)


@pytest.mark.parametrize("good", ["high", "medium", "low"])
def test_urgency_levels_pass(tmp_path, good):
    text = HEADER.replace("medium — cited by two other ADRs", f"{good} — a stated reason")
    assert lint(write(tmp_path, text)) == []


# --- the lean must exist before the review ---------------------------------

def test_missing_agent_lean_fails(tmp_path):
    text = HEADER.split("## Agent lean")[0]
    errors = lint(write(tmp_path, text))
    assert any("Agent lean" in e for e in errors)


# --- git provenance: the 2769ed8 case --------------------------------------

def git_repo(tmp_path):
    def run(*args):
        subprocess.run(("git", *args), cwd=tmp_path, check=True,
                       capture_output=True, text=True)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@t")
    run("config", "user.name", "Tester")
    return run


ACCEPTED = HEADER.replace("proposed (2026-08-08)", "accepted (2026-08-08)")


def test_accepted_in_the_creating_commit_fails(tmp_path, monkeypatch):
    """`2769ed8` reconstructed: created and accepted by one commit."""
    run = git_repo(tmp_path)
    adr = write(tmp_path, ACCEPTED)
    run("add", "-A")
    run("commit", "-q", "-m", "codify: ADRs, born accepted")
    monkeypatch.chdir(tmp_path)
    errors = lint(adr.name)
    assert any("self-ratification" in e for e in errors)


def test_accepted_in_a_separate_commit_passes_the_provenance_check(tmp_path, monkeypatch):
    run = git_repo(tmp_path)
    adr = write(tmp_path)
    run("add", "-A")
    run("commit", "-q", "-m", "add ADR as proposed")
    adr.write_text(ACCEPTED, encoding="utf-8")
    run("add", "-A")
    run("commit", "-q", "-m", "review pass: ratify")
    monkeypatch.chdir(tmp_path)
    assert not [e for e in lint(adr.name) if "self-ratification" in e]


def test_accepted_without_git_history_refuses_rather_than_passes(tmp_path, monkeypatch):
    """Fail-closed: a shallow checkout must not silently ratify."""
    adr = write(tmp_path, ACCEPTED)
    monkeypatch.chdir(tmp_path)
    errors = lint(adr.name)
    assert any("git history unavailable" in e or "self-ratification" in e
               or "too shallow" in e for e in errors)


def test_proposed_needs_no_git_history(tmp_path, monkeypatch):
    """Only `accepted` makes a claim git has to back."""
    adr = write(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert lint(adr.name) == []


# --- header parsing --------------------------------------------------------

def test_wrapped_field_value_is_folded():
    fields = parse_header(
        "- **Status:** proposed (2026-08-08)\n"
        "- **Drift-dimension:** coverage — a long reason\n"
        "  that wraps onto a second line\n")
    assert "wraps onto a second line" in fields["Drift-dimension"]


# --- provenance stamp (ADR-0013) -------------------------------------------

def test_output_carries_the_stamp(tmp_path, capsys):
    from skills import adr_lint
    adr_lint.main(["adr_lint.py", str(write(tmp_path))])
    assert f"adr_lint@{source_stamp()}" in capsys.readouterr().out


def test_runs_as_a_script(tmp_path):
    """The documented entry point, exercised (craft lesson #15)."""
    import sys as _sys
    from pathlib import Path as _Path
    repo = _Path(__file__).resolve().parent.parent
    res = subprocess.run([_sys.executable, str(repo / "skills" / "adr_lint.py"),
                          str(write(tmp_path))], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
