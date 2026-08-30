"""Test pair for local_ci (daily-reflection-spec § 13 — every artifact ships its validator).

What these pin down is **not** "does CI pass" — that is the runner's job, and asserting
it here would make this suite fail whenever the repo has an unrelated defect. What is
pinned is the property the runner exists to guarantee: **it never reports a pass for a
check it did not run.** Every test below is a variation on that one claim, because that
is the claim issue #71 showed the forge itself failing to keep.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skills import local_ci  # noqa: E402


def _leg(name, steps, **kw):
    return local_ci.Leg(name, "test.yml", steps, **kw)


def _ok(argv=None):
    return lambda: [sys.executable, "-c", "raise SystemExit(0)"]


def _fail():
    return lambda: [sys.executable, "-c", "raise SystemExit(3)"]


class TestNeverPassesWhatItDidNotRun:
    """The core invariant, from several directions."""

    def test_failing_step_fails_the_leg(self, tmp_path):
        ok, detail = local_ci.run_leg(_leg("x", [("boom", _fail(), None)]), tmp_path)
        assert ok is False
        assert "boom" in detail and "exit 3" in detail

    def test_first_failure_stops_the_leg(self, tmp_path):
        """CI stops at the first failed step; a later green must not mask an earlier red."""
        marker = tmp_path / "ran"
        steps = [
            ("boom", _fail(), None),
            ("should not run",
             lambda: [sys.executable, "-c", f"open({str(marker)!r}, 'w').close()"], None),
        ]
        ok, _ = local_ci.run_leg(_leg("x", steps), tmp_path)
        assert ok is False
        assert not marker.exists(), "a step after a failure was executed"

    def test_empty_records_glob_refuses_rather_than_passing_vacuously(self, tmp_path):
        """Zero records must never read as green — the whole point of the module."""
        leg = _leg("lint-records", [("records", lambda: ["py", "canon", "dre_lint"], 3)])
        ok, detail = local_ci.run_leg(leg, tmp_path)
        assert ok is False
        assert "vacuous" in detail

    def test_empty_glob_on_a_public_leg_is_a_no_op_not_a_failure(self, tmp_path):
        """pgm-lint.yml's own `nullglob` + `exit 0` behaviour, mirrored exactly."""
        leg = _leg("pgm-lint", [("programs", lambda: ["py", "skills/pgm_lint.py"], 2)])
        ok, detail = local_ci.run_leg(leg, tmp_path)
        assert ok is True and detail is None

    def test_all_steps_pass_means_leg_passes(self, tmp_path):
        leg = _leg("x", [("a", _ok(), None), ("b", _ok(), None)])
        assert local_ci.run_leg(leg, tmp_path) == (True, None)


class TestRefusals:
    """Refusal is exit 2 and is never confusable with a pass (0) or a failure (1)."""

    def _run(self, *args, cwd):
        return subprocess.run([sys.executable, str(Path(local_ci.__file__)), *args],
                              cwd=cwd, capture_output=True, text=True, check=False)

    def test_missing_records_dir_refuses_with_exit_2(self, tmp_path):
        out = self._run("--records", str(tmp_path / "nope"),
                        cwd=Path(local_ci.__file__).parent.parent)
        assert out.returncode == 2
        assert "refused" in out.stdout
        assert "--public-only" in out.stdout, "the refusal must name the way forward"

    def test_unknown_leg_refuses(self, tmp_path):
        out = self._run("--public-only", "--only", "not-a-leg",
                        cwd=Path(local_ci.__file__).parent.parent)
        assert out.returncode == 2
        assert "unknown leg" in out.stdout


class TestHonestyOfTheVerdict:
    def test_list_names_every_workflow_it_mirrors(self):
        """Each leg must name its workflow, so the mapping is auditable, not implied."""
        out = subprocess.run(
            [sys.executable, str(Path(local_ci.__file__)), "--public-only", "--list"],
            cwd=Path(local_ci.__file__).parent.parent,
            capture_output=True, text=True, check=False)
        assert out.returncode == 0
        for workflow in ("tests.yml", "readme-lint.yml", "pgm-lint.yml", "adr-lint.yml"):
            assert workflow in out.stdout

    def test_public_legs_cover_every_workflow_in_the_repo(self):
        """A workflow added without a leg here would be silently unchecked locally."""
        root = Path(local_ci.__file__).resolve().parent.parent
        on_disk = {p.name for p in (root / ".github" / "workflows").glob("*.yml")}
        mirrored = {leg.workflow for leg in local_ci.public_legs(root)}
        assert on_disk == mirrored, (
            f"workflow/leg mismatch — unmirrored: {on_disk - mirrored}, "
            f"stale: {mirrored - on_disk}")

    def test_stamp_is_a_content_hash_of_this_runner(self):
        """ADR-0013: a verdict names the bytes that produced it."""
        import hashlib
        expected = hashlib.sha256(Path(local_ci.__file__).read_bytes()).hexdigest()[:12]
        assert local_ci.source_stamp() == expected

    def test_records_leg_resolves_canonically_not_from_the_working_tree(self):
        """ADR-0015: the record gate is never satisfied from a local copy."""
        argv = records_argv()
        assert "canon_tool.py" in argv[1]
        assert "--local" not in argv, "the authoritative gate must not run --local"

    def test_public_legs_run_the_working_tree_not_canonical(self):
        """The mirror image: CI checks out the PR head, so these verify local bytes."""
        root = Path(local_ci.__file__).resolve().parent.parent
        for leg in local_ci.public_legs(root):
            for _, build, _ in leg.steps:
                assert "canon_tool.py" not in " ".join(build()), (
                    f"{leg.name} would verify canonical bytes, not the tree under test")


def records_argv():
    leg = local_ci.records_leg(Path(local_ci.__file__).parent)
    _, build, _ = leg.steps[0]
    return build()
