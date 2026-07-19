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
`programs[]`; it attaches sub-class telemetry via shared record-level `observations[]` (spec § 6 / ADR-0004).

## Goal

Reduce anxiety by first making it **legible** — surfacing the anxious feelings and their somatic
markers as they occur, so a pattern and a **root cause** can be found. The near-term telos is
*understanding* (root cause), a precondition for later intervention; the craft telos is unchanged
(~90% adherence, unaided self-recovery).

## Method (this arc — observation log)

*"Log anxious feelings whenever they occur."* Each observation is captured lightly, with enough
metadata to let a **root cause** surface from the pattern:

- `at` — when it occurred (time-of-day / cadence patterns; may be logged in batch at reflection time).
- `intensity` — how strong (free-text or a light rating; **never a forced scale** — coercion-free).
- `somatic` — bodily markers (e.g. sore teeth/jaws from nocturnal bruxism / nighttime clenching).
- `situation` — where / what / who (the setting).
- `antecedent` — what preceded it (the candidate trigger — the root-cause front).
- `thought` — the interpretation that ran (CBT antecedent *capture*, not challenged/re-rated).
- `behavior` — what I did in response.
- `relief` — what eased it, if anything.
- `note` — free text.

All fields optional and **open-extensible**. This is the antecedent / capture front of CBT — **not**
yet the restructuring front (challenge / evidence / reframe stays deferred).

## Telemetry (shared observations — ADR-0004)

Observations live at the **record level** (shared), each tagging the program(s) it feeds — so one
datum can serve `reduce-anxiety` *and* a future program (e.g. `improve-sleep`) without duplication:

```yaml
programs: [reduce-anxiety]
observations:
  - programs: [reduce-anxiety]
    intensity: high
    somatic: sore teeth and jaws on waking (nocturnal bruxism)
    situation: just woke up
    antecedent: a night of teeth-clenching
```

**Presence-not-quality holds here too:** observations are optional and never gated on quantity. A
`reduce-anxiety` day with no structured observation — just the free-flowing body — still counts.
Enforced by `skills/dre_lint.py` (`_check_observations`); shape-if-present only.

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
