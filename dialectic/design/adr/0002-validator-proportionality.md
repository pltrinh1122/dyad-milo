# ADR-0002 — validator proportionality

- **Status:** proposed (2026-07-18)
- **Urgency:** high — self-ratified, and the most-cited ADR in the set (six others lean on it); its premise was falsified 2026-08-07
- **Drift-dimension:** constraint (spec § 13 "non-code ↔ linter" vs its own proportionality
  clause) — resolved by the clause; recorded for PR review.

## Context

Spec § 13 requires a linter for every non-code artifact, **and** says validators must be
"proportionate (wu-wei): they check the load-bearing invariants … not cosmetics." Taken
literally, every prose doc (protocol, spec, BP#0 note, craft-lesson entries) would need a
linter — but prose docs carry no machine-checkable schema, so such a linter could only check
cosmetics, which the clause forbids.

## Decision

The **load-bearing, machine-checkable** non-code artifact is the `d-re` **record** (envelope +
`references[]` schema, presence-not-quality). It gets the real linter — `skills/dre_lint.py` —
with its own test pair.

Prose docs (`re-protocol.md`, the spec, the BP#0 note, craft lessons) are **not** linted:
they have no schema to enforce and a prose linter would be cosmetic. They rely on review.
(`README.md` keeps its existing `readme_lint` under its own separate discipline.)

## Consequences

- One new linter (`dre_lint`) covers the records — the only artifact whose invariants are
  mechanical.
- Prose correctness is a review concern, not a CI gate — consistent with presence-not-quality
  and wu-wei.

## Agent lean

*Reconstructed 2026-08-08, not contemporaneous — this ADR carried no lean when written. Supplied from the record and its use since, per the backfill disposition; it is not what would have been said at the time.*

**Revise, not ratify** — and this reverses an earlier *ratify* lean. A `d-rub` on 2026-08-07 falsified the premise: the ADR argues *prose docs carry no machine-checkable schema*, but **28 of 32** markdown artifacts carry structured metadata, and the protocol docs share `doc/home/grade/updated` exactly. The decision (proportionate validators, never cosmetics) is sound and heavily exercised; the *premise* and the coarse category "prose doc" are not. `adr_lint` does not contradict this ADR — it falsifies its premise, since ADRs are prose docs with a lintable schema.
