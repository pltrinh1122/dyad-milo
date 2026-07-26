---
doc: "dyad-milo — behavioral program: emerging-identity (a pgm- that sets its own value + invariant)"
home: "model in dialectic/design/adr/0010-pgm-subclass-model.md; delegation mechanism in ADR-0011"
program_id: emerging-identity
program: "Explore and consolidate a coherent sense of self through elicitation — surface who the Operator is becoming, held apart from role, output, and others' regard."
program_telos: "A self-authored identity the Operator inhabits without external scaffolding — worth felt from being, not earned from having or doing."
program_value: "being-over-having — worth is a state of being, not an accumulation of achievements, possessions, or regard."
program_invariant: "never-outsource-worth — the Operator's worth is never made contingent on external validation, comparison, or output; a session that sources worth externally is the breach."
# enrollment unset → the program is defined but not yet enrolled; set on the first
#   emerging-identity record (honesty over appearance — no retro-enrollment). ADR-0010 § 2.
updated: 2026-07-26
---

# Behavioral program — `emerging-identity`

A `pgm-` under milo (ADR-0010) that **sets its own** `program_value` + `program_invariant` — the
first program whose slots **diverge from** milo's parent slots. Where `reduce-anxiety` leaves
value/invariant unset (→ inherits milo's honesty-over-appearance / compassion-toward-lapse),
`emerging-identity` declares its own (`being-over-having` / `never-outsource-worth`).

## Why it stays a program, not a dyad

Its own value/invariant do **not** make it dyad-shaped (ADR-0010 supersedes that criterion). Because
execution is **delegated to a scoped sub-agent** running under *these* slots while **milo-main retains
milo's** (ADR-0011), a divergence — even a contradiction — with milo's parent slots is **isolated in the
delegate**, never corrupting milo's identity. A dyad is reserved for a distinct **identity** (birth-hash,
own agent, own Contract), which this program does not need.

## Method (this arc — elicitation)

Overrides the inherited `riff` with an **elicitation** method: open, non-leading prompts that surface the
Operator's own account of who they are becoming — never supplying the identity, only eliciting it (coherent
with `never-outsource-worth`: the worth and the account are the Operator's, not the agent's to confer).
Invoked `pgm-emerging-identity:` in `milo:practice`; `d-re` captures, the elicitation `riff` runs the method.

## Telemetry / Adherence

Rides the shared record-level `observations[]` (ADR-0004) and the program-agnostic meter (ADR-0003) once
enrolled. Lived records live PII-only in the private unified telemetry store (`§ Externality`; ADR-0009).

## Deferred

- **Enrollment** — set on the first lived `emerging-identity` record (no retro-tagging).
- **Promotion to a dyad ("going solo")** — deferred; only a need for distinct *identity* would trigger it,
  and delegation already isolates the divergent slots.
