# ADR-0005 — reduce-anxiety: the first additional behavioral program

- **Status:** proposed (2026-07-19) — Operator-disposed scope; awaiting PR review
- **Drift-dimension:** coverage — the first program materialized beyond the implicit BP#0.
  Surfaced at `d-start`, scope Operator-disposed; disposed at merge (no-self-ratify).

## Context

Across the first lived reps a behavioral program took shape: `2026-07-18-01` named
anxiety-from-perfectionism; `2026-07-19-01` sharpened it into a state-capture (anxiety surfacing
somatically as nocturnal bruxism — sore teeth/jaws on waking) **plus a method** — *"identify the
root cause by logging anxious feelings whenever they occur"* — and tagged it `#goal-reduce-anxiety`.
That record is the first to name a program beyond BP#0; it is the purpose that pulls `programs[]`
from an empty discriminator into its first materialization (mechanism: ADR-0004).

## Decision

**`reduce-anxiety`** is registered as the first additional behavioral program.

- **Home:** `dialectic/design/programs/reduce-anxiety.md` (goal · method · enrollment · sub-class
  schema · adherence relationship · what stays deferred). BP#0 keeps its own home (`design/bp0.md`):
  it is the implicit bootstrap, not a discriminator-listed program.
- **Method (this arc):** an **occurrence log** — capture anxious feelings as they occur (intensity,
  somatic markers, context/trigger) so a pattern → root cause can surface. This is the antecedent /
  capture front of CBT, *not yet* the restructuring front.
- **Sub-class telemetry:** the `reduce-anxiety` `program_telemetry` block (ADR-0004) —
  `occurrences[]`, every field optional and open-extensible, **never gated** (presence-not-quality).
- **Enrollment: 2026-07-19** (the day the Operator declared the program with a method). Earlier
  anxiety-themed records are **not** retro-tagged — that would inflate the program's adherence and
  is not what was declared (honesty over appearance). Its meter rides the existing program-agnostic
  tool: `dre_adherence.py --program reduce-anxiety --enrollment 2026-07-19`.
- **Modality:** CBT-flavored, consistent with the current (contingent, pinned-swappable) grounding
  modality — not a modality lock.

## Consequences

- `programs[]` is materialized: `2026-07-19-01` moves from `programs: []` to
  `programs: [reduce-anxiety]` with an occurrence-log block (in the private client record; the
  public repo holds only the mechanism + tests with synthetic fixtures, no PII).
- **Deferred, honestly:** the fuller CBT-intervention restructuring fields (spec § 3) are **not**
  built this arc — added only when a rep pulls them. `reduce-anxiety` opens the sub-class arc with
  the occurrence-log slice; it does not close it.
- Adherence for `reduce-anxiety` is a **separate meter** from the base (BP#0). A base-only day
  (an entry with no `reduce-anxiety`) is a lapse *for the program*, not for the base — met with
  compassion, no failure-marker (`craft_invariant`).
