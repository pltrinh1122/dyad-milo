# ADR-0013 — validators self-identify (a gate claim carries which gate ran)

- **Status:** proposed (2026-08-06)
- **Urgency:** low — coverage, Operator-disposed 2026-08-06; ratification is near-formality
- **Drift-dimension:** coverage (spec § 12) — no mechanism made validator identity visible.
  Not constraint: `§ Principles` already binds gate claims via *verify by execution*; only
  enforcement was missing. Closes issue #33.

## Context

A `milo:practice` thread ran for ~17 days on a checkout at `f8bfcd2` (2026-07-20), 21 commits
behind `main`. Its working-tree `skills/dre_lint.py` was **322 lines with zero occurrences of the
ADR-0012 capture-fidelity gate**; canonical was **377 lines with the gate present**. Every
pre-commit lint run in that window executed a superseded validator while reporting
"`dre_lint` PASS". Verified by execution, 2026-08-06.

**Nothing under-gated actually landed.** The adversarial sub-agents were prompted to read the
linter from `origin/main` and their reports confirm they did; ADR-0006's private `lint-records`
CI dual-checks-out `dyad-milo@main` independently. Both authoritative paths held. **The
correctness was luck of prompt wording, not a mechanism** — had the prompts said "use the local
linter," the same 17 days would have produced silently under-gated lands.

So the defect is not a weak gate. **A non-authoritative check was reported as though it were the
gate.** The local lint was always advisory; it was narrated as a result.

## The rejected signal, and why

Issue #33 proposed surfacing *"your checkout is N commits behind."* Grounding refuted it:

- **Of the 21 commits, exactly 1 touched the validator** (`65f0919`, the ADR-0012 commit). The
  other 20 — **95%** — left `dre_lint` byte-identical. The "21 behind" figure was almost entirely
  noise; the whole signal rode on one commit.
- **The converse also holds.** While grounding `d-sense #32`, this repo's own working branch
  reported *"behind origin/main"* while `dre_lint` was byte-identical to canonical. A
  distance-based warning fires on a perfectly current validator.

Distance is noisy when harmless and silent when a checkout sits at 0-behind on a branch whose
validator has diverged. A signal that cries wolf 20 times in 21 trains its reader to ignore the
one that matters — a new place for staleness to hide, not a fix.

## Decision

**Each validator stamps its output with a short content hash of its own source.**

```
[DRE-LINT] PASS: 2026-08-06-01.md (dre_lint@c27895d63665)
```

`source_stamp()` returns `sha256(own source)[:12]`. Both PASS and FAIL lines carry it.

- **Content, not distance.** The stamp identifies *what actually executed*, which is the thing a
  gate claim depends on. Commit position is a proxy for it and a poor one.
- **Fires regardless of compliance** (`§ Principles` — mechanism over compliance). Nobody has to
  remember to check; a stale run is *self-identifying* in the output it already prints. This is
  the property #29 and #30 both lack.
- **All three linters** (`dre_lint`, `pgm_lint`, `readme_lint`) — same four lines each. Stamping
  one and leaving two unstamped would reproduce the blind spot next door.
- **Duplicated, not factored.** The three linters already each carry their own
  `split_frontmatter`, and whether to extract a shared module is the open question in **issue
  #31**. Four lines of duplication is the cheaper side of that trade until #31 is disposed;
  factoring now would pre-empt it.

`dre_adherence.py` is **not** stamped — it is analytics, not a gate, and makes no gate claim.

## Consequences

- **An unstamped PASS is now visibly pre-ADR-0013.** Verified against the real `f8bfcd2` linter:
  it prints no stamp, so output from a pre-gate validator is distinguishable on sight rather than
  by inspection.
- **A modified validator self-identifies.** The canonical file and the same file plus one comment
  produce different stamps (`c27895d63665` vs `ae426c1e9671`), so local edits and superseded
  versions are both visible.
- **The stamp reports; it does not enforce.** It makes a stale run legible — it does not refuse
  one, and does not resolve what "canonical" is. Comparing a stamp against canonical still takes
  a fetch. That gap is deliberate and left open as issue #33's disposition 3 (mechanized
  canonical-source resolution), which is larger and scoped separately.
- **Test pair** (spec § 13, test-then-code): 10 cases across the three linters — the stamp equals
  `sha256` of the module's own source, has the right shape, appears on both PASS and FAIL, and
  changes when the source changes.

## The lesson this is the third instance of

Craft lesson #10 — *a claimed gate is a liability until a mechanism backs it* — on a third
surface this session, after ADR-0012 (`dre_lint` blind to what it validated) and #29 (dyad-rt's
hooks non-executable, so no guard ever fired). The generalization issue #33 offers is worth
holding: **an ungrounded state claim is itself an unbacked gate.** Every instance so far — the
stale toolchain, the dead hooks, and a board-state claim of "four open issues" when there were
six — was caught by an Operator `d-rub`, never by a mechanism. This ADR converts one of those
from vigilance into a device.

## Agent lean

*Reconstructed 2026-08-08, not contemporaneous — this ADR carried no lean when written. Supplied from the record and its use since, per the backfill disposition; it is not what would have been said at the time.*

**Ratify.** Content identity rather than commit distance was the right signal — grounded at the time by 20 of 21 commits leaving the validator byte-identical. The stamp reports rather than enforces, and the enforcement half is tracked as ADR-0015.
