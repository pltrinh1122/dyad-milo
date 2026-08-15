#!/usr/bin/env python3
"""canon_tool — run a dyad-milo validator from its **canonical** source.

Closes the live half of #33/#35. The adversarial-validate resolved its
validators by **sub-agent prompt wording**: each `d-rub-with-land` prompt happened
to say "read `skills/dre_lint.py` from `origin/main`", and the sub-agents did. That
was correct in practice and a **habit, not a mechanism** — different wording, and
the same 17 days that ran a 322-line `dre_lint` with no ADR-0012 gate would have
produced silently under-gated lands.

ADR-0015 disposed **option D**: an authoritative invocation resolves its validator
from `origin/main`, so there is no stale local validator in the gate path because
the local one is never the gate. This is ADR-0006's proven CI dual-checkout applied
to local and sub-agent invocation.

**Two consumers, opposite needs** — conflating them is what made this look hard:

===================  ==============  ==================================
invocation           runs            why
===================  ==============  ==================================
authoritative        **canonical**   the claim is about the record, and
(rub · land · gate)                  only the canonical gate supports it
development          working tree    forcing canonical would make the
(``--local``)                        validator untestable while edited
===================  ==============  ==================================

**Authoritative is the default.** Development is an explicit opt-in that announces
itself — the safe path free, the unsafe one a deliberate act, mirroring dyad-rt's
`--no-verify`. (The DFD framing of ADR-0015 surfaced that `mode` is a data flow
nothing carried; this is where it enters.)

**Fail-closed.** If canonical cannot be resolved, the run is **refused** — never
satisfied from the local copy. A silent fallback would reproduce the exact defect
while appearing to fix it.

**The canonical bytes are written to a temp file, not piped to ``python3 -``.**
Piping would set ``__file__`` to ``<stdin>`` and break ADR-0013's ``source_stamp()``,
so a gate claim would stop naming the gate that ran — losing the other half of the
mechanism to fix this one.

Usage:
  python3 skills/canon_tool.py TOOL [ARGS...]      # canonical (default)
  python3 skills/canon_tool.py --local TOOL [ARGS...]
"""

import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

CANONICAL_REF = "origin/main"   # tracking, per ADR-0006's deliberate choice
TOOL_DIR = "skills"


class CanonicalUnavailable(Exception):
    """Canonical source could not be resolved. Fail-closed; never fall back."""


def _git(*args):
    try:
        out = subprocess.run(("git", *args), capture_output=True, check=False)
    except OSError:
        return None
    return out.stdout if out.returncode == 0 else None


def resolve_canonical(tool, ref=CANONICAL_REF):
    """Return the canonical source text of ``skills/<tool>.py``.

    Fetches first so ``origin/main`` is current — a stale remote-tracking ref is
    exactly the staleness this exists to remove. Raises rather than degrading.
    """
    _git("fetch", "origin", "main", "--quiet")     # best-effort; verified below
    blob = _git("show", f"{ref}:{TOOL_DIR}/{tool}.py")
    if blob is None:
        raise CanonicalUnavailable(
            f"cannot resolve {ref}:{TOOL_DIR}/{tool}.py — no canonical source. "
            f"Refusing rather than running a local copy (ADR-0015, fail-closed). "
            f"Use --local to run the working tree deliberately.")
    return blob.decode("utf-8")


def _exec(source, tool, args):
    """Execute ``source`` as ``__main__`` from a real file, so __file__ works."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{tool}.py"
        path.write_text(source, encoding="utf-8")
        argv = sys.argv
        try:
            sys.argv = [str(path), *args]
            runpy.run_path(str(path), run_name="__main__")
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
        finally:
            sys.argv = argv
    return 0


def run_tool(tool, args, local=False):
    """Run ``tool``. Returns its exit code, or 2 when refused."""
    if local:
        # Resolve against the repo git is operating on, not this file's own
        # directory — otherwise the two modes silently mean different repos.
        top = _git("rev-parse", "--show-toplevel")
        root = Path(top.decode().strip()) if top else Path(__file__).resolve().parent.parent
        path = root / TOOL_DIR / f"{tool}.py"
        if not path.is_file():
            print(f"[CANON] refused: no such tool in {root / TOOL_DIR}: {tool}")
            return 2
        print(f"[CANON] --local: running the WORKING TREE — this is NOT canonical, "
              f"and any gate claim from it is not authoritative.")
        return _exec(path.read_text(encoding="utf-8"), tool, args)
    try:
        source = resolve_canonical(tool)
    except CanonicalUnavailable as exc:
        print(f"[CANON] refused: {exc}")
        return 2
    return _exec(source, tool, args)


def main(argv):
    args = argv[1:]
    local = False
    if args and args[0] == "--local":
        local, args = True, args[1:]
    if not args:
        print("usage: canon_tool.py [--local] TOOL [ARGS...]")
        return 2
    return run_tool(args[0], args[1:], local=local)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
