#!/usr/bin/env python3
"""Pre-push guard — main-history protection for dyad-milo's Dyad Runtime (dyad-rt).

The UNBYPASSABLE spine of the runtime (native-adaptation of dyad-touchstone's dyad-rt):
git-layer, so it fires regardless of the harness permission mode — including under
`bin/claude`, where the native permission gate is OFF and the runtime is the authority.

`main` advances ONLY through a PR merged on the forge (server-side); a *local* push that
updates `refs/heads/main` — direct, force, or delete — is never legitimate here.

Reads the git pre-push payload on stdin (one line per ref being pushed):
    <local ref> <local sha> <remote ref> <remote sha>

REFUSES any line whose <remote ref> is refs/heads/main. Visible escape: `--no-verify`
(the Operator's deliberate override — wu-wei: the human is never forced). Pure stdlib.
"""
import sys

PROTECTED = "refs/heads/main"


def _is_zero(sha):
    """A delete carries an all-zero local sha (40 hex for sha1, 64 for sha256)."""
    return len(sha) > 0 and set(sha) <= {"0"}


def offending(lines):
    """Return [(remote_ref, kind), ...] for every line that touches `main`."""
    hits = []
    for line in lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        _local_ref, local_sha, remote_ref, _remote_sha = parts
        if remote_ref == PROTECTED:
            kind = "delete" if _is_zero(local_sha) else "direct/force update"
            hits.append((remote_ref, kind))
    return hits


def main():
    hits = offending(sys.stdin.read().splitlines())
    if hits:
        kinds = ", ".join(sorted({k for _, k in hits}))
        sys.stderr.write(
            "🚨 DYAD-RT MAIN-HISTORY GUARD 🚨\n"
            f"Refused: local push to `main` ({kinds}).\n"
            "`main` advances only through a PR merged on the forge (server-side),\n"
            "never a local push. This guard is the runtime's unbypassable spine —\n"
            "it fires even with the native permission gate OFF (bin/claude).\n"
            "[STEERING VECTOR] Open a PR instead:\n"
            "  git switch -c <branch> && git push -u origin <branch>\n"
            "  gh pr create ...        # then merge on the forge\n"
            "Visible escape (deliberate Operator override): git push --no-verify\n"
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
