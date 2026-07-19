# ADR-0004 — shared observation telemetry (programs[] sub-class attachment)

- **Status:** proposed (2026-07-19) — Operator-disposed scope + shape; awaiting PR review
- **Drift-dimension:** coverage — opens the mechanism spec §§ 6/14 explicitly **defer**
  ("the sub-class arc"). Surfaced at `d-start`; the Operator disposed the fuller scope
  ("also design the sub-class telemetry") and, against two acceptance criteria (below), the
  **shape** (shared `observations[]`). This ADR is the escalation artifact (§ 13); `main`
  advances only through the reviewed PR (no-self-ratify).

## Context

Spec § 6 defines `programs[]` as the discriminator of the *additional* programs an entry serves
(BP#0 implicit, never listed) and **defers the sub-class-telemetry attachment mechanism**. The
first candidate program surfaced in a lived record (`2026-07-19-01`, `#goal-reduce-anxiety`), so
the mechanism now has a purpose pulling on it (wu-wei).

The Operator set two acceptance criteria:

1. **Sufficient metadata** for the telemetry to actually assist the goal (find the root cause of
   the anxiety) — a bare intensity/somatic pair is too thin.
2. **One record serves telemetry for multiple programs** — a single datum (e.g. the bruxism
   observation) may be evidence for `reduce-anxiety` *and* a future `improve-sleep`, without
   being written twice.

A first draft keyed telemetry **by program** (`program_telemetry: {reduce-anxiety: {…}}`). That
fails criterion 2: a shared datum duplicates under each program's block. Rejected.

The load-bearing invariant question is unchanged: telemetry must stay **optional and non-gated**
— a required/structured schema would bend **presence-not-quality** and **coercion-free** (§ 2), so
the mandatory reading is **rejected as constraint drift**, not self-ratified.

## Decision

Structured telemetry lives in a **shared, record-level `observations[]`** — a list of observation
mappings, *not* keyed by program — each of which may tag the program(s) it feeds:

```yaml
programs: [reduce-anxiety]        # discriminator (a list → multi-program is native)
observations:                     # record-level, SHARED; 0..n; optional, never gated
  - at: 2026-07-19T06:26:58-07:00 # when → time-of-day / cadence patterns
    programs: [reduce-anxiety]     # which program(s) this datum feeds (⊆ record programs; omit = all)
    intensity: high               # free-text or a light rating — never a forced scale
    somatic: sore teeth/jaws on waking (nocturnal bruxism)
    situation: just woke up        # where / what / who
    antecedent: a night of teeth-clenching   # what preceded it — the root-cause front
    thought: <the interpretation that ran>   # antecedent capture (NOT the deferred belief-rating)
    behavior: <what I did in response>
    relief: <what eased it, if anything>
    note: <free text>
```

Invariants (enforced by `dre_lint._check_observations`, proportionate — ADR-0002):

- **Presence-not-quality extends here.** Observations are **never required** and **never gated on
  quantity/completeness**. A listed program with no observation rides the base free-flowing body;
  `observations: []` is valid. The linter checks *shape-if-present* only.
- **One datum, many programs (criterion 2).** An observation's own `programs` is a list ⊆ the
  record's `programs[]` (an observation can only feed a program the record serves) and never BP#0.
  Omitting it means the observation feeds every program the record serves. The adherence meter
  (ADR-0003) already counts a record for each program in its top-level `programs[]`.
- **Sufficient, open-extensible fields (criterion 1).** A vocabulary aimed at root-cause work
  (`at`, `intensity`, `somatic`, `situation`, `antecedent`, `thought`, `behavior`, `relief`,
  `note`); extra keys allowed (mirrors the essence-`facet` pattern). These are the **observational**
  ABC front (antecedent / thought / behavior *capture*) — **not** the deferred CBT **restructuring**
  (challenge / re-rate / reframe).
- **Single-source, frontmatter-only** (ADR-0001).

## Consequences

- One new linter check (`_check_observations`) + its test pairs; the base envelope, `references[]`,
  and `dre_adherence` are unchanged (the meter was already program-agnostic — ADR-0003).
- The **keyed-per-program** alternative and the **mandatory-schema** alternative are recorded here
  as rejected (duplication; constraint drift) so a later edit does not silently re-introduce them.
- The fuller CBT-intervention **restructuring** fields (spec § 3) remain deferred — added only when
  a rep pulls them (see ADR-0005). `observations[]` carries the capture front now.
