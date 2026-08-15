"""Deterministic V-pair for skills/canon_tool.py (No-Pure-G invariant).

Tests build **real, tiny git repositories** in tmp_path — the thing under test
is "which bytes did we execute, and where did they come from," and a mocked
answer would prove nothing.

Closes the live half of #33/#35: the adversarial-validate resolved its
validators by **sub-agent prompt wording**. Correct in practice, but a habit
rather than a mechanism — different wording and the same 17 days produce
silently under-gated lands. ADR-0015 disposed option D: authoritative
invocations resolve from `origin/main`; development invocations use the working
tree and say so; fail-closed when canonical cannot be resolved.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from skills.canon_tool import CanonicalUnavailable, resolve_canonical, run_tool

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL = REPO_ROOT / "skills" / "canon_tool.py"

STUB = """\
import hashlib, sys
from pathlib import Path
def source_stamp():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
def main(argv):
    print(f"[STUB] ran (stub@{source_stamp()}) args={argv[1:]}")
    return 0
if __name__ == "__main__":
    sys.exit(main(sys.argv))
"""


def origin_repo(tmp_path, tool_body=STUB):
    """An 'origin' with skills/stub.py on main, cloned to a working copy."""
    origin, work = tmp_path / "origin", tmp_path / "work"
    origin.mkdir()

    def git(cwd, *args):
        subprocess.run(("git", *args), cwd=cwd, check=True, capture_output=True, text=True)

    git(origin, "init", "-q", "-b", "main")
    git(origin, "config", "user.email", "t@t")
    git(origin, "config", "user.name", "T")
    (origin / "skills").mkdir()
    (origin / "skills" / "stub.py").write_text(tool_body, encoding="utf-8")
    git(origin, "add", "-A")
    git(origin, "commit", "-q", "-m", "canonical stub")
    subprocess.run(("git", "clone", "-q", str(origin), str(work)),
                   check=True, capture_output=True)
    return origin, work, git


# --- authoritative is the default; canonical bytes are what run --------------

def test_resolves_canonical_bytes_not_the_working_tree(tmp_path, monkeypatch):
    origin, work, git = origin_repo(tmp_path)
    (work / "skills" / "stub.py").write_text(
        STUB.replace("[STUB] ran", "[STUB] LOCAL EDIT"), encoding="utf-8")
    monkeypatch.chdir(work)
    source = resolve_canonical("stub")
    assert "[STUB] ran" in source
    assert "LOCAL EDIT" not in source, "resolved the working tree instead of canonical"


def test_run_tool_executes_canonical_when_working_tree_diverges(tmp_path, monkeypatch, capsys):
    origin, work, git = origin_repo(tmp_path)
    (work / "skills" / "stub.py").write_text(
        STUB.replace("[STUB] ran", "[STUB] LOCAL EDIT"), encoding="utf-8")
    monkeypatch.chdir(work)
    rc = run_tool("stub", ["--flag"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "[STUB] ran" in out and "LOCAL EDIT" not in out
    assert "--flag" in out, "arguments were not forwarded"


def test_stamp_survives_resolution(tmp_path, monkeypatch, capsys):
    """ADR-0013's stamp reads Path(__file__); piping to `python3 -` would break it.

    The stamp must report the CANONICAL bytes' hash, so a gate claim names the
    gate that actually ran.
    """
    import hashlib
    origin, work, git = origin_repo(tmp_path)
    monkeypatch.chdir(work)
    run_tool("stub", [])
    out = capsys.readouterr().out
    expected = hashlib.sha256(
        (origin / "skills" / "stub.py").read_bytes()).hexdigest()[:12]
    assert f"stub@{expected}" in out


def test_canonical_tracks_origin_not_a_pin(tmp_path, monkeypatch, capsys):
    """ADR-0006 chose tracking deliberately; a canonical change takes effect."""
    origin, work, git = origin_repo(tmp_path)
    (origin / "skills" / "stub.py").write_text(
        STUB.replace("[STUB] ran", "[STUB] v2"), encoding="utf-8")
    git(origin, "add", "-A")
    git(origin, "commit", "-q", "-m", "canonical moves")
    monkeypatch.chdir(work)
    run_tool("stub", [])
    assert "[STUB] v2" in capsys.readouterr().out


# --- fail-closed: never fall back silently ----------------------------------

def test_unresolvable_canonical_refuses(tmp_path, monkeypatch):
    """ADR-0015's non-negotiable: refuse, never satisfy from the local copy."""
    origin, work, git = origin_repo(tmp_path)
    subprocess.run(("git", "remote", "remove", "origin"), cwd=work, check=True,
                   capture_output=True)
    subprocess.run(("git", "update-ref", "-d", "refs/remotes/origin/main"), cwd=work,
                   check=True, capture_output=True)
    monkeypatch.chdir(work)
    with pytest.raises(CanonicalUnavailable):
        resolve_canonical("stub")


def test_unknown_tool_refuses(tmp_path, monkeypatch):
    origin, work, git = origin_repo(tmp_path)
    monkeypatch.chdir(work)
    with pytest.raises(CanonicalUnavailable):
        resolve_canonical("no_such_tool")


def test_refusal_does_not_execute_anything(tmp_path, monkeypatch, capsys):
    origin, work, git = origin_repo(tmp_path)
    subprocess.run(("git", "remote", "remove", "origin"), cwd=work, check=True,
                   capture_output=True)
    subprocess.run(("git", "update-ref", "-d", "refs/remotes/origin/main"), cwd=work,
                   check=True, capture_output=True)
    monkeypatch.chdir(work)
    rc = run_tool("stub", [])
    out = capsys.readouterr().out
    assert rc == 2
    assert "[STUB]" not in out, "refused but executed anyway"
    assert "refus" in out.lower()


# --- development mode: explicit opt-in, and it announces itself -------------

def test_local_mode_uses_the_working_tree_and_says_so(tmp_path, monkeypatch, capsys):
    """The DFD finding: mode defaults to authoritative; local is a deliberate act."""
    origin, work, git = origin_repo(tmp_path)
    (work / "skills" / "stub.py").write_text(
        STUB.replace("[STUB] ran", "[STUB] LOCAL EDIT"), encoding="utf-8")
    monkeypatch.chdir(work)
    rc = run_tool("stub", [], local=True)
    out = capsys.readouterr().out
    assert rc == 0
    assert "LOCAL EDIT" in out
    assert "NOT canonical" in out, "local mode must announce that it is non-authoritative"


def test_local_mode_works_offline(tmp_path, monkeypatch, capsys):
    origin, work, git = origin_repo(tmp_path)
    subprocess.run(("git", "remote", "remove", "origin"), cwd=work, check=True,
                   capture_output=True)
    monkeypatch.chdir(work)
    assert run_tool("stub", [], local=True) == 0


# --- exit codes propagate (a gate's verdict must survive the wrapper) -------

def test_tool_exit_code_propagates(tmp_path, monkeypatch):
    failing = STUB.replace("return 0", "return 1")
    origin, work, git = origin_repo(tmp_path, tool_body=failing)
    monkeypatch.chdir(work)
    assert run_tool("stub", []) == 1


# --- the documented entry point (craft lesson #15) --------------------------

def test_runs_as_a_script(tmp_path):
    origin, work, git = origin_repo(tmp_path)
    res = subprocess.run([sys.executable, str(TOOL), "stub"], cwd=work,
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert "[STUB] ran" in res.stdout
