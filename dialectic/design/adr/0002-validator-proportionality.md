# ADR-0002 — validator proportionality

- **Status:** accepted (2026-07-18)
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
