---
doc: "dyad-milo — behavioral program: reduce-anxiety (first additional program)"
home: "rationale in dialectic/design/adr/0005-reduce-anxiety-first-program.md; mechanism in ADR-0004"
program_id: reduce-anxiety
enrollment: 2026-07-19
updated: 2026-07-19
---

# Behavioral program — `reduce-anxiety`

The **first additional** behavioral program (beyond the implicit BP#0). Materialized 2026-07-19
from the lived record that named it (`#goal-reduce-anxiety`, `2026-07-19-01`). Listed in a record's
`programs[]`; it attaches sub-class telemetry via `program_telemetry` (spec § 6 / ADR-0004).

## Goal

Reduce anxiety by first making it **legible** — surfacing the anxious feelings and their somatic
markers as they occur, so a pattern and a **root cause** can be found. The near-term telos is
*understanding* (root cause), a precondition for later intervention; the craft telos is unchanged
(~90% adherence, unaided self-recovery).

## Method (this arc — occurrence log)

*"Log anxious feelings whenever they occur."* Each occurrence is captured lightly:

- `intensity` — how strong (free-text or a light rating; **never a forced scale** — coercion-free).
- `somatic` — bodily markers (e.g. sore teeth/jaws from nocturnal bruxism / nighttime clenching).
- `context` — what was happening / the trigger.
- `at` — optional time (occurrences may be logged in batch at reflection time).
- `note` — free text.

All fields optional and **open-extensible**. This is the antecedent / capture front of CBT — **not**
yet the restructuring front.

## Telemetry (sub-class — ADR-0004)

```yaml
programs: [reduce-anxiety]
program_telemetry:
  reduce-anxiety:
    occurrences:
      - intensity: high
        somatic: sore teeth and jaws on waking (nocturnal bruxism)
        context: on waking this morning
```

**Presence-not-quality holds at the sub-class too:** the block is optional and never gated on
quantity. A `reduce-anxiety` day with no structured occurrences — just the free-flowing body — still
counts. Enforced by `skills/dre_lint.py` (`_check_program_telemetry`); shape-if-present only.

## Adherence

Rides the program-agnostic meter (ADR-0003) with its own enrollment:

```
python3 skills/dre_adherence.py <private-records-dir> --program reduce-anxiety --enrollment 2026-07-19
```

Covered = a PT day with ≥1 record listing `reduce-anxiety`; enrollment 2026-07-19. A base entry with
no `reduce-anxiety` is a lapse **for this program**, not for the base — absence-inferred, met with
compassion, no failure-marker (`craft_invariant`). Earlier anxiety-themed records are **not**
retro-tagged (honesty over appearance).

## Deferred (build only when a rep pulls it)

- **CBT-intervention restructuring fields** (spec § 3): hot-thought + belief rating, evidence
  for/against, distortion label, behavioral action, before/after intensity deltas.
- **Starvation / cadence detector** for the occurrence log — added only if the method needs it.
