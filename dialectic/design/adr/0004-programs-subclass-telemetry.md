# ADR-0004 — programs[] sub-class-telemetry attachment mechanism

- **Status:** proposed (2026-07-19) — Operator-disposed scope; awaiting PR review
- **Drift-dimension:** coverage — opens the mechanism spec §§ 6 / 14 explicitly
  **defer** ("the sub-class arc"). Surfaced to the Operator at `d-start`; the Operator
  disposed the fuller scope ("also design sub-class telemetry"). This ADR is the
  escalation artifact (§ 13); `main` advances only through the reviewed PR (no-self-ratify).

## Context

Spec § 6 defines `programs[]` as a discriminator of the *additional* behavioral programs an
entry serves (BP#0 implicit, never listed) and **defers the sub-class-telemetry attachment
mechanism** to a later arc. The first candidate additional program surfaced in a lived record
(`2026-07-19-01`, `#goal-reduce-anxiety`), so the mechanism now has a purpose pulling on it
(wu-wei: build only what a purpose pulls on).

The design fork with teeth is **not** the YAML shape — it is whether sub-class telemetry is a
**required structured schema** or an **optional, non-gated** attachment. A required/gated
schema would bend two invariants (§ 2): **presence-not-quality** (a completeness bar feeds the
perfectionism the practice addresses) and **coercion-free** (a mandatory field-set is a quota
by another name). Making sub-class telemetry mandatory is therefore **constraint drift** and is
**rejected here, not self-ratified**.

## Decision

Sub-class telemetry attaches in the record frontmatter as an **optional** `program_telemetry`
mapping keyed by program-id — inheritance discriminated by the `programs[]` value:

```yaml
programs: [reduce-anxiety]
program_telemetry:            # optional; presence-not-quality extends here
  reduce-anxiety:
    occurrences:              # program-specific, open-extensible, never gated
      - intensity: high
        somatic: sore teeth and jaws on waking (nocturnal bruxism)
        context: on waking this morning
```

Load-bearing invariants (enforced by `dre_lint._check_program_telemetry`, proportionate — ADR-0002):

- **Presence-not-quality extends to the sub-class.** A block is **never required** and **never
  gated on quantity/completeness**. A program listed in `programs[]` with **no** block is valid —
  it rides the base free-flowing body. An empty block (`{}`) is valid. The linter checks
  *shape-if-present* only.
- **Discriminator integrity.** Every `program_telemetry` key must be listed in `programs[]` (a
  block can only attach to a program the entry serves) and must **never** be BP#0 (implicit — it
  *is* the base; it has no sub-class telemetry).
- **Open-extensible fields** (mirrors the essence-`facet` pattern): registered programs get a
  proportionate field-shape check via a small validator registry
  (`PROGRAM_TELEMETRY_VALIDATORS`); unregistered program-ids attach a free-form mapping.
- **Single-source, frontmatter-only** (ADR-0001): the sub-class block lives in frontmatter with
  the rest of the machine-readable record; the body stays free-flowing prose.

## Consequences

- One new linter check (`_check_program_telemetry`) + its test pair; the base envelope,
  `references[]`, and `dre_adherence` are unchanged (the meter was already program-agnostic —
  ADR-0003).
- The **rejected** alternative (mandatory structured sub-class schema) is recorded here as
  constraint drift so a future edit does not silently re-introduce it.
- The **fuller CBT-intervention restructuring fields** (spec § 3: hot-thought + belief rating,
  evidence for/against, distortion label, before/after intensity deltas) remain **deferred** —
  today's method is occurrence capture toward a root cause, not restructuring. The mechanism is
  built to carry them when a rep pulls them (see ADR-0005).
