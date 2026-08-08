# ADR-0015 — canonical-source resolution for gate invocations

- **Status:** proposed (2026-08-08)
- **Urgency:** medium — decision disposed 2026-08-08 (option D); ratification confirms a fresh call
- **Drift-dimension:** coverage — no mechanism resolves *which* validator an authoritative
  invocation should run. A **constraint edge** appears only in options that would make a gate claim
  refuse rather than warn.
- **Origin:** issue #33 disposition 3, deferred at `d-sense` and again at `d-land`.

## Context

ADR-0013 made validators **self-identifying**: every PASS/FAIL now carries `name@<hash>` of the
source that ran. That closed the *legibility* half of #33 — a stale run is visible in output it
already prints.

**It deliberately did not close the resolution half.** The stamp says what ran; it does not say
what *should* have run, and comparing the two still takes a fetch and someone choosing to do it.

What the incident actually turned on: the adversarial sub-agents were **prompted** to read the
linter from `origin/main`, and did. Nothing under-gated landed because of prompt wording. Had the
prompts said "use the local linter," the same 17 days would have produced silently under-gated
lands. `§ Principles` is explicit that this is the wrong kind of guarantee — *mechanism over
compliance: enforce with a device that fires regardless of compliance, not a prose instruction.*
Prompt text is a prose instruction.

**One path is already mechanized.** ADR-0006's private `lint-records` CI dual-checks-out
`dyad-milo@main` and runs the canonical linter — that path cannot go stale. The gap is the
**interactive/local path**: an agent or Operator invoking a validator from a working tree.

### The distinction that shapes the options

Two consumers want opposite things, and conflating them is why this looks harder than it is:

| invocation | must run | why |
|---|---|---|
| **authoritative** — the rub, a land, any "gate passed" claim | **canonical** | the claim is about the record, and only the canonical gate can support it |
| **development** — editing the validator itself | **local** | forcing canonical here would make the linter untestable while being changed |

Option B below fails by ignoring this; the others handle it differently.

## The decision to be made

How does an authoritative validator invocation resolve *canonical*, without depending on anyone
remembering to make it do so?

### Option A — nothing beyond the stamp

The stamp makes staleness legible; a reader who cares compares it.

- **For:** wu-wei. The incident produced **zero** bad lands, and ADR-0013 already converts the
  failure from invisible to visible. n=1 may not earn a second mechanism.
- **For:** no network dependency, no new artifact, no new failure mode.
- **Against:** legibility is not enforcement. It restores the property that *someone must look* —
  which is the compliance the issue was filed against. Every instance of this class so far
  (#29, #30, #33, and a mis-stated board count) was caught by an Operator `d-rub`, never by a
  device; option A leaves that record unchanged.

### Option B — the validator self-checks (fetches canonical, compares its own stamp)

`dre_lint` resolves `origin/main`'s copy at startup and warns or fails on mismatch.

- **For:** fully self-contained; fires on every invocation.
- **Against:** makes a schema validator **network-dependent** — slow, fragile, broken offline, and
  a layering inversion (a linter should not know about git remotes).
- **Against, decisive:** it cannot tell development from authoritative use. Every iteration while
  *editing* the linter would warn or fail. This is the same shape as the false-positive problem in
  ADR-0014: a check that obstructs correct work to catch a rare fault trades the wrong currency.

### Option C — a separate preflight/toolchain check

A small script (e.g. `dialectic/guards/toolchain_check.py`) that resolves canonical and reports
drift, invoked at session start or before gate claims.

- **For:** clean separation — validators validate; provenance is somebody else's job. No network
  dependency inside the linters.
- **For:** could be wired to the dyad-rt hooks, which **now actually fire** (the #29 exec-bit fix),
  making it mechanical rather than advisory.
- **Against:** the natural hook points are the wrong moments. `pre-commit`/`pre-push` guard the
  *irreversible* step, but a stale gate claim is made at **lint time**, well before either. A
  preflight that isn't hooked is back to compliance.

### Option D — canonical-by-construction for authoritative invocations

Generalize ADR-0006's already-proven pattern to the interactive path: an authoritative invocation
resolves the validator from `origin/main` rather than the working tree — a thin wrapper doing what
the sub-agent prompts were doing by hand. Development invocations keep using the local file, and
ADR-0013's stamp already marks their output as non-canonical.

- **For:** it **dissolves** the question rather than answering it. There is no stale local
  validator in the gate path because the local one is never the gate.
- **For:** it mechanizes precisely the behaviour that saved the incident, and reuses a pattern
  already working in ADR-0006 rather than inventing one.
- **For:** composes with ADR-0013 — canonical by construction for gates, visibly stamped otherwise.
  The two together close both halves of #33.
- **Against:** requires network per authoritative invocation.
- **Design note if chosen — fail-closed.** Inability to resolve canonical must **refuse the gate
  claim**, never silently fall back to the local copy. A silent fallback would reproduce the exact
  defect while appearing to fix it. This is the constraint edge flagged above: it makes a gate
  claim capable of refusing, which is a stronger posture than warning.

## Relationship to the open board

Same species as **#30** (`core.hooksPath` — a precondition that must be remembered per clone) and
**#29** (a guard that could not fire). All three are *assumed preconditions, silent when violated*.
Worth disposing with an eye to whether one shape answers several, rather than three unrelated
mechanisms — the sequencing concern already recorded on #33 disposition 1.

## Evidence limits — stated, not buried

How the practice thread actually invokes its validators is **practice-side and not visible from
this repo**. The option analysis rests on the public structure (ADR-0006's CI, the linters, the
dyad-rt hooks) and on #33's own account of the sub-agent prompts, which I could not verify. If the
invocation path differs materially from what that account describes, option C's and D's wiring
points may be wrong even though the trade-offs stand.

## Agent lean

**D, scoped to authoritative invocations**, with A as the defensible wu-wei fallback.

D is the only option that removes the failure mode instead of monitoring it, and it costs little
because it copies a pattern already proven in ADR-0006. The two-consumer distinction is what makes
it safe: it never obstructs work on the validator itself, which is where B breaks.

The honest case for **A**: the incident caused no bad lands, ADR-0013 already made recurrence
visible, and the dyad has one instance. Choosing A with a **recorded trigger** — build D on the
first stale-stamp actually observed — would be consistent with how ADR-0012 deferred the sibling
linters (#31). That is a legitimate disposal, not a dodge.

I would not choose B or C: B cannot separate development from authoritative use, and C's hook
points don't line up with the moment a gate claim is made.

## Disposition

**Operator-disposed 2026-08-08: option D**, scoped to authoritative invocations — a gate
invocation resolves its validator from `origin/main`; development invocations keep the working-tree
copy and are marked non-canonical by ADR-0013's stamp.

**Fail-closed is part of the disposal:** if canonical cannot be resolved, the gate claim is
*refused*, never silently satisfied from the local copy — a silent fallback would reproduce the
defect while appearing to fix it.

**The open design question it inherits:** `mode` is a data flow nothing carries today. The DFD
framing surfaced it — process 1 consumes an input that does not exist. The safe default is
**authoritative**: an undeclared invocation resolves canonical, and development is the explicit
opt-in, mirroring dyad-rt's `--no-verify` (the safe path free, the unsafe one a deliberate act).
Not built; this ADR records the shape.

## Consequences of the shape chosen

ADR-0013's stamp stands and ADR-0006's CI path remains mechanized, so **the authoritative land path
was never exposed** while this sat open. Until D is built, the interactive path still rests on
prompt wording and habit — which is the dependency the disposal removes, not one it accepts.
