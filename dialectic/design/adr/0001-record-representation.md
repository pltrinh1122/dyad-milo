# ADR-0001 — d-re record representation

- **Status:** proposed (2026-07-18)
- **Urgency:** high — self-ratified in the creating commit — the record asserts a review that never happened
- **Drift-dimension:** coverage (representation of spec § 5) — within bounds; recorded for PR review.

## Context

Spec § 5 depicts `references[]` as YAML. The first lived record (entry #1) materialized its
reference as rich Markdown body sections (citation, links, essence fragments, provenance,
fidelity). Codification needs **one** canonical, lintable representation. A hybrid
(frontmatter index + body prose) would be two sources of the same data — drift risk, and the
linter could validate only one of them.

## Decision

A `d-re` record is **YAML frontmatter + a free-flowing Markdown body**:

- **Frontmatter** carries the entire machine-readable record: the envelope (`record`,
  `created`, `practice_day`, `zone`, `trigger`, `programs`) **and** the full `references[]`
  (citation, links, essence fragments with `facet`/`partition`, provenance, fidelity — prose
  fields use YAML block scalars).
- **Body** carries *only* the free-flowing reflection prose (spec § 3).

Single-source: the linter validates the frontmatter; nothing to keep in sync.

## Consequences

- Entry #1 retrofit moves its `## Reference` body sections **into** frontmatter `references[]`.
- Frontmatter is verbose for reference-heavy entries — accepted, in exchange for lintability and
  no body/frontmatter drift.
- The body stays free-flowing; presence-not-quality lives there (the linter never gates on body
  length).

## Agent lean

*Reconstructed 2026-08-08, not contemporaneous — this ADR carried no lean when written. Supplied from the record and its use since, per the backfill disposition; it is not what would have been said at the time.*

**Ratify.** Single-source frontmatter has held for three weeks and the drift it was chosen to prevent (body/frontmatter divergence) has not appeared. Its cost — verbose frontmatter for reference-heavy entries — was accepted explicitly and has not bitten. ADR-0017 amends its serialization without disturbing the representation.
