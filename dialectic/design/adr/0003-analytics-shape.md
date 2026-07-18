# ADR-0003 — adherence analytics shape

- **Status:** accepted (2026-07-18)
- **Drift-dimension:** none (within spec §§ 9, 13) — recorded as a key build decision.

## Context

Spec § 9 requires program-agnostic, fail-closed adherence analytics; § 13 sets Python + TDD.
The tool lives PII-clear in `dyad-milo` but reads records from the private client repo.

## Decision

`skills/dre_adherence.py`, **standard-library only** (`zoneinfo` for PT-day bucketing, no third-
party deps beyond the repo's existing `pyyaml`):

- **Input:** a records directory (path arg) — points at the private repo when run; synthetic
  fixtures in tests.
- **Program-agnostic:** takes an optional `program` filter; BP#0 / base = all records (BP#0 is
  implicit, § 6).
- **Output:** covered-days / eligible-days since **enrollment (default 2026-07-18)**, plus
  rolling 7 / 30 / 90-day windows; PT calendar-day bucket via IANA `America/Los_Angeles`.
- **Lapse:** absence-inferred (an eligible PT day with zero entries).
- **Fail-closed:** a record that fails to parse is **skipped and reported**, never crashes the
  run and never fabricated; the tool only ever returns/prints a report — it never writes to the
  public repo. Any public surfacing of a number is a separate manual step, out of this tool.

## Consequences

- The tool is run against the private repo path; the public repo holds only the tool + tests
  with synthetic fixtures (no PII).
- `--as-of DATE` is supported so windows are reproducible/testable without a real clock.
