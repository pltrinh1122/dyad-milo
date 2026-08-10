#!/usr/bin/env python3
"""adr_lint — schema gate for Architecture Decision Records.

The ADR set is spec § 13's *"reviewable trail of the sensitive decisions."* An
audit on 2026-08-07 found the trail misreporting its own state: **9 of 15 ADRs
said "awaiting PR review" while living on `main`**, and 3 more claimed
`accepted` having been marked so by the **Agent, in the same commit that created
them** (`2769ed8`) — a self-ratification sitting undetected for three weeks.

This linter is the mechanism behind the lifecycle those findings produced
(ADR-0018). Two rules do the work:

**1. Never store what the substrate can answer.** Merge state is derivable —
``git cat-file -e origin/main:<path>`` settles it, always correctly. Writing it
into the file duplicates a fact git already holds, in a place that drifts; that
duplication *is* what went stale. So ``Status`` carries the **review outcome
only** (``proposed`` / ``accepted`` / ``rejected``), and any merge-state claim
in the header is a violation. "In force" and "reviewed" are two axes, composed
at read time from two authorities.

**2. Ratification must be independent of authorship.** ``accepted`` may only be
set by a commit that is **not** the commit which created the ADR, and that
reached ``main`` through a **different merge** than the one that landed it —
i.e. its own later PR. The Agent may author that commit; the Operator's manual
merge is the disposition (ADR-0018). Both facts are read from git, never stored.

Checks:
  1. header carries ``Status``, ``Urgency`` and ``Drift-dimension``.
  2. ``Status`` is ``proposed|accepted|rejected`` + an ISO date, and nothing else
     — no merge-state claim ("awaiting PR review", "merged", "on main").
  3. ``Urgency`` is ``high|medium|low`` with a reason.
  4. an ``## Agent lean`` section exists — the recommendation the Operator
     reviews against. It must exist *before* review, never arrive with it.
  5. ``accepted`` only: the accept-commit differs from the create-commit, and
     landed via a separate merge (git-derived; requires full history).

Usage: python3 skills/adr_lint.py ADR.md [ADR.md ...]
Exit 0 = all pass; exit 1 = itemized failures on stdout.
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

STATUS_RE = re.compile(r"^\s*(proposed|accepted|rejected)\s+\((\d{4}-\d{2}-\d{2})\)\s*$")
URGENCY_RE = re.compile(r"^\s*(high|medium|low)\b\s*(?:—|-|:)?\s*(.*)$", re.S)
FIELD_RE = re.compile(r"^- \*\*([A-Za-z-]+):\*\*\s*(.*)$")
LEAN_RE = re.compile(r"^##+\s+Agent lean\b", re.M)
# Merge state is derivable from git; a claim about it in the header is the
# stale-by-construction defect this linter exists to prevent.
MERGE_CLAIM_RE = re.compile(
    r"awaiting\s+(?:a\s+)?(?:PR\s+)?review|awaiting\s+merge|merged|on\s+main|landed", re.I)
REQUIRED = ("Status", "Urgency", "Drift-dimension")


def source_stamp():
    """Short content hash of this validator's own source (ADR-0013)."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]


def parse_header(text):
    """Return {field: value} for the leading ``- **Field:** value`` block.

    Values may wrap onto continuation lines; those are folded in so a wrapped
    Status is read whole rather than truncated at the line break.
    """
    fields, current = {}, None
    for line in text.splitlines():
        match = FIELD_RE.match(line)
        if match:
            current = match.group(1)
            fields[current] = match.group(2).strip()
        elif current and line.startswith("  ") and line.strip():
            fields[current] += " " + line.strip()
        elif line.startswith("## "):
            break
        elif not line.strip():
            current = None
    return fields


def _git(*args):
    try:
        out = subprocess.run(("git", *args), capture_output=True, text=True, check=False)
    except OSError:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _main_ref():
    """The ref standing for ``main``, or None if none resolves.

    Checkouts differ in which refs they create — a CI job may land in detached
    HEAD with no remote-tracking branch. Resolving defensively and **reporting**
    when none is found is the difference between a check that ran and a check
    that silently didn't (craft lesson #10).
    """
    for ref in ("origin/main", "refs/remotes/origin/main", "main"):
        if _git("rev-parse", "--verify", "-q", ref) is not None:
            return ref
    return None


def _landing_merge(sha, main_ref):
    """The merge commit that brought ``sha`` onto main, or None if not merged."""
    out = _git("log", "--merges", "--ancestry-path", "--format=%H", f"{sha}..{main_ref}")
    if out is None:
        return None
    merges = [line for line in out.splitlines() if line.strip()]
    return merges[-1] if merges else None


def check_accept_provenance(path):
    """``accepted`` must be set independently of the ADR's own landing.

    Read from git, never stored: the accept-commit must differ from the
    create-commit, and must have reached ``main`` through a different merge —
    its own later PR (ADR-0018). This is exactly what `2769ed8` violated.
    """
    errors = []
    created = _git("log", "--format=%H", "--reverse", "--diff-filter=A", "--", str(path))
    accepted = _git("log", "-S", "**Status:** accepted", "--format=%H", "--", str(path))
    if created is None or accepted is None:
        return ["accepted: git history unavailable — cannot verify independent review "
                "(CI needs fetch-depth: 0); refusing to pass it silently"]
    create_sha = created.splitlines()[0] if created.splitlines() else None
    accept_sha = accepted.splitlines()[0] if accepted.splitlines() else None
    if not create_sha or not accept_sha:
        return ["accepted: cannot locate the commit that set it — history too shallow"]
    if create_sha == accept_sha:
        return [f"accepted was set by the same commit that created the ADR "
                f"({accept_sha[:7]}) — that is self-ratification, not review "
                f"(ADR-0018)"]
    main_ref = _main_ref()
    if main_ref is None:
        # Silently skipping here would leave a gate that reports PASS without
        # having run — the defect this whole ADR set is about. Say so instead.
        errors.append(
            "accepted: cannot resolve a `main` ref, so the separate-PR check could "
            "not run — refusing to pass it silently (CI must fetch origin/main)")
        return errors
    create_merge = _landing_merge(create_sha, main_ref)
    accept_merge = _landing_merge(accept_sha, main_ref)
    if create_merge and accept_merge and create_merge == accept_merge:
        errors.append(
            f"accepted landed in the same PR as the ADR itself (merge "
            f"{accept_merge[:7]}) — review must be its own later PR (ADR-0018)")
    return errors


def lint(path, check_git=True):
    adr = Path(path)
    if not adr.is_file():
        return [f"file not found: {path}"]
    text = adr.read_text(encoding="utf-8")
    fields = parse_header(text)

    errors = []
    for name in REQUIRED:
        if name not in fields:
            errors.append(f"missing header field: {name}")

    status = fields.get("Status", "")
    if status:
        bare = status.replace("*", "").strip()
        match = STATUS_RE.match(bare)
        if not match:
            errors.append(
                f"Status must be 'proposed|accepted|rejected (YYYY-MM-DD)' and carry "
                f"nothing else — got: {bare!r}")
        elif MERGE_CLAIM_RE.search(bare):
            errors.append(
                "Status must not claim merge state — it is derivable from git and a "
                "stored copy goes stale (ADR-0018)")
        if MERGE_CLAIM_RE.search(status) and STATUS_RE.match(bare):
            pass  # already reported above when it matters

    urgency = fields.get("Urgency", "")
    if urgency:
        match = URGENCY_RE.match(urgency.replace("*", "").strip())
        if not match:
            errors.append(
                f"Urgency must be 'high|medium|low — <reason>' — got: {urgency!r}")
        elif not match.group(2).strip():
            errors.append("Urgency must give a reason — it sequences the review pass")

    if not LEAN_RE.search(text):
        errors.append(
            "missing '## Agent lean' section — the Operator reviews against a stated "
            "recommendation, and it must exist before the review, not arrive with it")

    if check_git and STATUS_RE.match(fields.get("Status", "").replace("*", "").strip() or "") \
            and fields.get("Status", "").replace("*", "").strip().startswith("accepted"):
        errors.extend(check_accept_provenance(adr))
    return errors


def main(argv):
    paths = argv[1:]
    if not paths:
        print("usage: adr_lint.py ADR.md [ADR.md ...]")
        return 2
    stamp = source_stamp()
    total = 0
    for path in paths:
        errors = lint(path)
        if errors:
            total += len(errors)
            print(f"[ADR-LINT] FAIL: {path} (adr_lint@{stamp}) — {len(errors)} violation(s):")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"[ADR-LINT] PASS: {path} (adr_lint@{stamp})")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
