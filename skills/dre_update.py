#!/usr/bin/env python3
"""dre_update — modify a ``d-re`` record, canonically.

**Why canonicalization.** A record's diff is what the review path reads:
``d-rub-with-land`` rubs it, and the Operator disposes at merge. A naive
parse→modify→dump of **one field** on a hand-formatted record rewrote **27 of
16** frontmatter lines — flow mappings expanded, block scalars requoted, the
ISO-8601 ``T`` dropped. No value changed and it still linted: *safe, but
illegible*. Illegible is disqualifying here, because it hides the real edit —
and would hide a silently normalized possessive (#32) inside reformatting noise.

Starting from **canonical** form the same edit changes **two lines**. So records
are normalized once (``--canonicalize``) and every update thereafter emits a
minimal diff. Operator-disposed 2026-08-08; ADR-0017.

**Serialization is shared with the constructor, deliberately.** ``serialize`` is
imported from ``dre_create`` rather than reimplemented: if the two disagreed by
one character, every constructed record would be rewritten wholesale on its
first update, which is precisely the defect this module exists to remove. That
coupling is a correctness requirement, distinct from the open question in issue
#31 about factoring the linters' shared helpers.

**Layer discipline** (``re-protocol.md`` § Capture model). The body is the
Operator's verbatim words — this module never parses, reflows, or re-serializes
it; it is carried across byte-for-byte. The envelope (``record``, ``created``,
``practice_day``, ``zone``) is **immutable** here: ``created``/``zone`` move the
adherence bucket and therefore the filename, which is a re-file rather than an
update, and ``practice_day`` is computed. What this module edits is the
**generated/classification** layer — which is exactly the layer that needs
correcting when an adversarial-validate holds a record.

**No self-lint.** Capture stays un-gated (ADR-0007); ``dre_lint`` remains the
independent validator and the adversary re-lints before any land.

Usage:
  python3 skills/dre_update.py RECORD.md --set trigger.proximate="…" [--set …]
                                          [--unset trigger.boundary] [--print]
  python3 skills/dre_update.py --canonicalize RECORD.md [RECORD.md ...]
"""

import argparse
import sys
from pathlib import Path

import yaml

# Invoked as a script (`python3 skills/dre_update.py`), only `skills/` is on
# sys.path, so the package import below fails. Under pytest or `-m` the repo
# root is already there and this is a no-op. `dre_adherence` carried the same
# defect unnoticed — its docstring and reduce-anxiety.md both documented a
# script invocation that had never run.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skills.dre_create import KEY_ORDER, serialize  # noqa: E402

IMMUTABLE = ("record", "created", "practice_day", "zone")
EDITABLE = ("trigger", "programs", "observations", "references")


def split_record(text):
    """Return ``(frontmatter_text, body)``.

    Splits at the **first** closing delimiter, so a literal ``---`` inside the
    Operator's prose survives untouched.
    """
    if not text.startswith("---\n"):
        raise ValueError("no YAML frontmatter block found")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter block is not closed")
    return text[4:end + 1], text[end + 5:]


def _load(path):
    text = Path(path).read_text(encoding="utf-8")
    fm_text, body = split_record(text)
    record = yaml.safe_load(fm_text)
    if not isinstance(record, dict):
        raise ValueError("frontmatter is not a YAML mapping")
    return record, body


def canonicalize(path):
    """Re-emit a record in canonical serialization. Values are never changed.

    Value-preservation is asserted, not assumed: a normalization that altered a
    record would be a fidelity defect wearing a formatting fix's clothes.
    """
    record, body = _load(path)
    text = serialize(record, body)
    after, after_body = split_record(text)
    if yaml.safe_load(after) != record or after_body != body:
        raise ValueError(
            f"canonicalization would change {path} — refusing (fail-closed)")
    return text


def _resolve(record, path):
    """Walk a dotted path to ``(container, key)``, refusing what must not move."""
    parts = path.split(".")
    if parts[0] in IMMUTABLE:
        raise ValueError(
            f"{parts[0]} is immutable — created/zone move the adherence bucket and "
            f"the filename (a re-file, not an update); practice_day is computed")
    if parts[0] not in EDITABLE:
        raise ValueError(f"unknown field {parts[0]!r} — editable: {', '.join(EDITABLE)}")
    node = record
    for part in parts[:-1]:
        if not isinstance(node, dict):
            raise ValueError(f"cannot descend into {path!r}")
        node = node.setdefault(part, {})
    if not isinstance(node, dict):
        raise ValueError(f"cannot set {path!r} — parent is not a mapping")
    return node, parts[-1]


def apply_updates(path, sets=None, unsets=None):
    """Apply ``--set``/``--unset`` and return the new record text."""
    record, body = _load(path)
    for dotted, value in (sets or {}).items():
        node, key = _resolve(record, dotted)
        node[key] = value
    for dotted in (unsets or []):
        node, key = _resolve(record, dotted)
        node.pop(key, None)
    ordered = {k: record[k] for k in KEY_ORDER if k in record}
    ordered.update({k: v for k, v in record.items() if k not in KEY_ORDER})
    return serialize(ordered, body)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="dre_update.py", description="Modify a d-re record, canonically.")
    parser.add_argument("records", nargs="+", metavar="RECORD.md")
    parser.add_argument("--set", action="append", default=[], dest="sets",
                        metavar="PATH=VALUE", help="dotted path; repeatable")
    parser.add_argument("--unset", action="append", default=[], metavar="PATH")
    parser.add_argument("--canonicalize", action="store_true",
                        help="normalize serialization; change no value")
    parser.add_argument("--print", action="store_true", dest="to_stdout")
    args = parser.parse_args(argv[1:])

    if args.canonicalize and (args.sets or args.unset):
        print("[DRE-UPDATE] refused: --canonicalize changes no value; "
              "run it separately from --set/--unset")
        return 2
    if not args.canonicalize and not (args.sets or args.unset):
        print("[DRE-UPDATE] refused: nothing to do — give --set/--unset or --canonicalize")
        return 2
    if not args.canonicalize and len(args.records) > 1:
        print("[DRE-UPDATE] refused: --set/--unset take exactly one record")
        return 2

    sets = {}
    for raw in args.sets:
        if "=" not in raw:
            print(f"[DRE-UPDATE] refused: --set expects PATH=VALUE, got {raw!r}")
            return 2
        key, value = raw.split("=", 1)
        sets[key.strip()] = value

    changed = 0
    for path in args.records:
        try:
            text = canonicalize(path) if args.canonicalize else apply_updates(
                path, sets=sets, unsets=args.unset)
        except (ValueError, yaml.YAMLError) as exc:
            print(f"[DRE-UPDATE] refused: {path} — {exc}")
            return 2
        if args.to_stdout:
            sys.stdout.write(text)
            continue
        before = Path(path).read_text(encoding="utf-8")
        if text == before:
            print(f"[DRE-UPDATE] unchanged: {path}")
            continue
        Path(path).write_text(text, encoding="utf-8")
        changed += 1
        print(f"[DRE-UPDATE] wrote: {path}")
    if not args.to_stdout and args.canonicalize:
        print(f"[DRE-UPDATE] canonicalized {changed} of {len(args.records)} record(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
