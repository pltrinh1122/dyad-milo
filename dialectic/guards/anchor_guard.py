#!/usr/bin/env python3
"""CSI Guard — anchor-integrity for dyad-milo's Dyad Runtime (dyad-rt).

A self-administered mechanical trap — the engine is its own enforcement vector, no external
authority. The mechanical error IS the steering wheel; we never swallow it. Adapted from
dyad-touchstone's anchor_guard (cairn's gift, cycle-39).

ARMED    when an anchor file is staged for a commit on `main` directly.
DISARMED when the change is moved to a PR branch (the Merge stays the Operator's gate).

Anchors = the dyad's loadable shared model (DYAD.md) + its substrate shim (CLAUDE.md).
Low-reversibility: they change only through a reviewed PR. Pure stdlib (no dependency drift).
"""
import subprocess
import sys

ANCHORS = {"DYAD.md", "CLAUDE.md", "GEMINI.md"}


def _git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True
    ).stdout.strip()


def armed():
    """Return the sorted anchor files that trip the trap, or [] if clear."""
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != "main":
        return []
    staged = set(_git("diff", "--cached", "--name-only").splitlines())
    return sorted(staged & ANCHORS)


def main():
    touched = armed()
    if touched:
        sys.stderr.write(
            "🚨 CSI ANCHOR-INTEGRITY TRAP ARMED 🚨\n"
            f"Anchor file(s) staged on `main` directly: {', '.join(touched)}\n"
            "Anchors are low-reversibility — they change only through a reviewed PR.\n"
            "To DISARM: move the change to a PR branch —\n"
            "  git switch -c <branch>   # carries your staged change\n"
            "  git commit ...           # commit on the branch, then open a PR\n"
            "The Merge stays the Operator's gate (wu-wei: the human is not forced to override).\n"
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
