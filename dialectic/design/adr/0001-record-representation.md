# ADR-0001 — d-re record representation

- **Status:** accepted (2026-07-18)
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
