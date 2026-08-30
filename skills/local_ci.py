#!/usr/bin/env python3
"""local_ci — run every CI leg locally, when the forge cannot.

**Why this exists.** GitHub Actions stopped executing: the monthly quota is
exhausted, so jobs are allocated no runner and complete in ~3 seconds with empty
output and no logs (issue #71). A check that never ran reports `failure`
indistinguishably from a check that ran and found a defect — the *same*
observational problem ADR-0013 solved for stale validators, arriving one layer up.

The forge legs are the mechanical half of `§ Operating-policy`'s git-workflow. With
them dark, `d-rub-with-land`'s durability rung is fail-closed on a red that carries
**zero information about the artifact**, which deadlocks every land. This module
restores the *signal* locally so the deadlock has a principled exit, and it is
deliberately **not** a licence to land on red: it produces a verdict that a human or
an adversarial sub-agent can act on, it does not merge anything.

**What it is honest about not being.** This is a local re-run of the same commands,
not an equivalent of CI:

- it runs your **working tree**, not a clean checkout of the merge commit, so
  uncommitted and untracked files are in scope where CI would never see them;
- it inherits **this machine's** Python and installed packages rather than the
  pinned `ubuntu-latest` + `setup-python` image;
- it cannot prove the tree it checked is the tree that will be merged.

Those gaps are why the verdict prints them rather than claiming CI-equivalence.
A local green means *these checks pass here*, which is strictly weaker than *CI is
green* — and saying so is the whole point (`craft_value`: honesty over appearance).

**Fail-closed, and specifically about skipping.** A leg that *cannot* run is a
**refusal**, never a silent skip folded into a green summary. Reporting PASS for a
check that did not execute is the exact defect this module exists to detect; it
would be absurd to reproduce it in the detector. Deliberate narrowing (`--only`,
`--public-only`) is honoured, but it downgrades the verdict to **PARTIAL** and names
every leg not run.

**Two resolution modes, deliberately different — matching what each CI job does:**

===================  ===================  ==========================================
leg                  runs the             why
===================  ===================  ==========================================
public-repo legs     **working tree**     CI checks out the PR head; the working tree
(tests, readme,                           is the artifact under test. Running these
pgm, adr)                                 canonically would verify the wrong bytes.
records leg          **canonical**        the private store has no linter; CI
(dre_lint)           (`canon_tool`)       dual-checks-out this repo's `dre_lint`
                                          (ADR-0006), and ADR-0015 requires an
                                          authoritative gate resolve from
                                          `origin/main`, never a local copy.
===================  ===================  ==========================================

Conflating those two would be a real defect in either direction, so the mode is a
property of each leg rather than a global flag.

Usage:
  python3 skills/local_ci.py [--records DIR] [--public-only] [--only LEG[,LEG...]]
                             [--list]

Exit: 0 = all requested legs passed · 1 = a leg failed · 2 = refused (a leg could
not be run, or a precondition is missing). PARTIAL never exits 0 as if whole — it
exits 0 only when every leg it *did* run passed, and the banner states what it skipped.
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

# The private client store's default location: a sibling clone. Records never live
# in this repo (DYAD.md § Externality) — this module only ever *reads* their path
# and prints pass/fail, exactly as the private repo's own workflow does. No record
# content is surfaced.
DEFAULT_RECORDS = "../dyad-milo-pltrinh1122/reflections"


def source_stamp():
    """Short content hash of this runner's own source (ADR-0013).

    A verdict is only as good as the thing that produced it. Stamping the summary
    makes a stale or edited local runner self-identifying, so a green report can be
    traced to the exact bytes that issued it rather than to a remembered version.
    """
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
    except OSError:
        return "unknown"


def repo_root():
    """The git top-level this runner should check, not this file's parent.

    Resolving by `__file__` would silently check a different repo than the one git
    is operating on — the failure mode `canon_tool.run_tool` documents for --local.
    """
    out = subprocess.run(("git", "rev-parse", "--show-toplevel"),
                         capture_output=True, check=False)
    if out.returncode != 0:
        return Path(__file__).resolve().parent.parent
    return Path(out.stdout.decode().strip())


class Leg:
    """One CI job, named for the workflow file it mirrors.

    ``needs_main_ref`` mirrors adr-lint.yml's fetch-depth: 0 + explicit fetch — the
    `accepted` check reads history, and adr_lint is fail-closed without it, so a
    shallow or fetch-less run turns every ratified ADR red for the wrong reason.
    """

    def __init__(self, name, workflow, steps, needs_main_ref=False):
        self.name = name
        self.workflow = workflow
        # [(label, argv_builder, empty_len)] — ``empty_len`` is the argv length when
        # the step's input glob matched nothing, or None for a step that takes no
        # inputs. Carried per step rather than inferred: guessing "does this argv
        # have inputs?" from its shape is how a no-input invocation gets handed to a
        # linter whose zero-argument behaviour is its own business.
        self.steps = steps
        self.needs_main_ref = needs_main_ref


def _glob(root, pattern):
    """Sorted matches. Sorted so a failure list is stable across runs and machines."""
    return sorted(str(p) for p in root.glob(pattern))


def public_legs(root):
    """The four workflows in this repo, mirrored leg for leg."""
    py = sys.executable or "python3"
    return [
        Leg("tests", "tests.yml", [
            ("full deterministic test suite",
             lambda: [py, "-m", "pytest", "tests/", "-q"], None),
        ]),
        Leg("readme-lint", "readme-lint.yml", [
            ("README conforms to the falsifiable-manifesto form",
             lambda: [py, "skills/readme_lint.py", "README.md"], None),
            ("linter's own test pair (No-Pure-G)",
             lambda: [py, "-m", "pytest", "tests/test_readme_lint.py", "-q"], None),
        ]),
        Leg("pgm-lint", "pgm-lint.yml", [
            ("program definitions conform to the four-slot model",
             lambda: [py, "skills/pgm_lint.py",
                      *_glob(root, "dialectic/design/programs/*.md")], 2),
            ("linter's own test pair (No-Pure-G)",
             lambda: [py, "-m", "pytest", "tests/test_pgm_lint.py", "-q"], None),
        ]),
        Leg("adr-lint", "adr-lint.yml", [
            ("ADR form + ratification provenance",
             lambda: [py, "skills/adr_lint.py",
                      *_glob(root, "dialectic/design/adr/*.md")], 2),
        ], needs_main_ref=True),
    ]


def records_leg(records_dir):
    """The private store's `lint-records` job, resolved canonically.

    Runs through ``canon_tool`` rather than ``skills/dre_lint.py`` so the gate is the
    one ADR-0015 requires — resolved from ``origin/main``, never the working tree.
    This is the one leg where a local copy would be the wrong answer, because CI's
    own dual-checkout (ADR-0006) is what it is standing in for.
    """
    py = sys.executable or "python3"
    return Leg("lint-records", "lint-records.yml (private store)", [
        ("all d-re records, canonical linter",
         lambda: [py, "skills/canon_tool.py", "dre_lint",
                  *sorted(str(p) for p in Path(records_dir).glob("*.md"))], 3),
    ])


def check_preconditions(root):
    """Return a list of refusal reasons. Empty means every leg can actually run.

    Checked up front and reported together: discovering a missing dependency four
    legs in wastes the run and tempts a partial result into being read as whole.
    """
    problems = []
    if shutil.which("git") is None:
        problems.append("git is not on PATH — adr-lint and the canonical resolve need it")
    for mod, why in (("yaml", "every linter parses YAML frontmatter"),
                     ("pytest", "three legs run test pairs")):
        probe = subprocess.run([sys.executable or "python3", "-c", f"import {mod}"],
                               capture_output=True, check=False)
        if probe.returncode != 0:
            problems.append(f"python module {mod!r} is not importable — {why} "
                            f"(CI installs it with `pip install pyyaml pytest`)")
    if not (root / "skills").is_dir():
        problems.append(f"{root} does not look like the dyad-milo repo (no skills/)")
    return problems


def ensure_main_ref(root):
    """Make `origin/main` present for adr_lint's history check. Best-effort by design.

    A fetch failure is not fatal here: adr_lint is itself fail-closed and will refuse
    rather than pass if the ref it needs is absent, so the honest behaviour is to let
    *it* produce the refusal rather than pre-empting with a guess about the cause.
    """
    subprocess.run(("git", "fetch", "origin", "main:refs/remotes/origin/main", "--force"),
                   cwd=root, capture_output=True, check=False)


def run_leg(leg, root):
    """Run one leg's steps in order, stopping at the first failure (as CI does)."""
    if leg.needs_main_ref:
        ensure_main_ref(root)
    for label, build, empty_len in leg.steps:
        argv = build()
        if empty_len is not None and len(argv) == empty_len:
            # The glob matched nothing. pgm-lint.yml handles this explicitly
            # (`nullglob` + an early `exit 0`), so mirror that rather than invoking
            # a linter with no arguments, whose zero-input behaviour is its own.
            #
            # The records leg is the deliberate exception: the client store always
            # has records, so an empty match means the path is wrong or the store is
            # missing — and a vacuous green over zero records is precisely the
            # "reported PASS without checking anything" defect this module exists to
            # catch. Refuse instead.
            if leg.name == "lint-records":
                return False, (f"{label}: no records matched — refusing a vacuous "
                               f"pass over zero records (check --records)")
            print(f"  · {label}: no inputs to check")
            continue
        print(f"  · {label}")
        result = subprocess.run(argv, cwd=root, check=False)
        if result.returncode != 0:
            return False, f"{label} (exit {result.returncode})"
    return True, None


def main(argv):
    parser = argparse.ArgumentParser(
        prog="local_ci.py",
        description="Run every CI leg locally, in lieu of GitHub Actions.")
    parser.add_argument("--records", default=DEFAULT_RECORDS,
                        help=f"private store's reflections dir (default {DEFAULT_RECORDS})")
    parser.add_argument("--public-only", action="store_true",
                        help="skip the records leg; verdict downgrades to PARTIAL")
    parser.add_argument("--only", help="comma-separated leg names; verdict is PARTIAL")
    parser.add_argument("--list", action="store_true", dest="list_legs",
                        help="list the legs and the workflow each mirrors, then exit")
    args = parser.parse_args(argv[1:])

    root = repo_root()
    records_dir = (root / args.records).resolve() if not Path(args.records).is_absolute() \
        else Path(args.records)

    legs = public_legs(root)
    skipped = []

    if args.public_only:
        skipped.append(("lint-records", "--public-only was passed"))
    elif not records_dir.is_dir():
        # A refusal, not a skip: the records leg is the one that gates the client
        # store, and quietly dropping it would hand back a green that never checked
        # the thing most likely to change.
        print(f"[LOCAL-CI] refused: no records directory at {records_dir}\n"
              f"  Pass --records DIR to point at the private store's reflections/, "
              f"or --public-only to run this repo's legs alone (verdict: PARTIAL).")
        return 2
    else:
        legs.append(records_leg(records_dir))

    if args.list_legs:
        for leg in legs:
            print(f"{leg.name:14s} ← {leg.workflow}")
        return 0

    if args.only:
        wanted = {n.strip() for n in args.only.split(",") if n.strip()}
        unknown = wanted - {leg.name for leg in legs}
        if unknown:
            print(f"[LOCAL-CI] refused: unknown leg(s): {', '.join(sorted(unknown))}")
            return 2
        skipped += [(leg.name, "not in --only") for leg in legs if leg.name not in wanted]
        legs = [leg for leg in legs if leg.name in wanted]

    problems = check_preconditions(root)
    if problems:
        print("[LOCAL-CI] refused — preconditions unmet:")
        for problem in problems:
            print(f"  - {problem}")
        return 2

    stamp = source_stamp()
    print(f"[LOCAL-CI] {len(legs)} leg(s) against {root} (local_ci@{stamp})\n")

    results = []
    for leg in legs:
        print(f"[{leg.name}] ← {leg.workflow}")
        ok, detail = run_leg(leg, root)
        results.append((leg.name, ok, detail))
        print(f"  {'PASS' if ok else 'FAIL'}: {leg.name}"
              f"{'' if ok else ' — ' + detail}\n")

    failed = [name for name, ok, _ in results if not ok]
    partial = bool(skipped)
    verdict = "FAIL" if failed else ("PARTIAL" if partial else "PASS")

    print(f"[LOCAL-CI] {verdict} — {len(results) - len(failed)}/{len(results)} "
          f"leg(s) passed (local_ci@{stamp})")
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}{'' if ok else ' — ' + detail}")
    for name, why in skipped:
        print(f"  SKIP  {name} — {why}")
    # Stated on every run, including green ones: a local pass is strictly weaker
    # than a CI pass, and the moment that caveat is dropped the two get conflated.
    print("  note: working tree, not a clean checkout of the merge commit; "
          "this machine's Python, not the pinned CI image. A local pass is "
          "evidence, not a CI-equivalent verdict.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
