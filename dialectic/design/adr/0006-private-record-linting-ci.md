# ADR-0006 — private-record linting via CI-time dual-checkout

- **Status:** proposed (2026-07-19) — Operator-disposed strategy; awaiting PR review
- **Drift-dimension:** none (infra; realizes spec § 13's validator intent) — recorded as a key
  build decision. Closes the gap tracked in issue #10.

## Context

`tests.yml` claimed *"Records … live in the private client repo (PII) and are linted there, not
here"* — but no such linting was wired: `dyad-milo-pltrinh1122` had no CI, no submodule, no
reference to `dre_lint` (falsified 2026-07-19). A `d-re` record's schema — including the
`observations[]` shape (ADR-0004) — was validated by nothing automated; it rode a manual lint. A
claimed gate with no mechanism.

The linter is **canonical in the public repo** (two homes — DYAD.md § Externality): the private
repo must *use* it, not fork it. Three ways to consume it were weighed (issue #10): a **vendored
copy** (drifts from `dre_lint`), a **git submodule** (exact-version but heavy clones + working-tree
friction), or **CI-time dual-checkout**. The Operator disposed **dual-checkout**.

## Decision

A `lint-records` workflow in the **private** repo checks out the public `dyad-milo` at `ref: main`
into a subdir, installs `pyyaml`, and runs the canonical linter over the records, fail-closed:

```
python3 .dyad-milo-public/skills/dre_lint.py reflections/*.md
```

- **No copy, no submodule.** The linter is never vendored (no drift) and never enters the private
  working tree (checkout is CI-only, into a dotted path).
- **Self-contained invocation.** `dre_lint` imports only stdlib + `pyyaml` (only `dre_adherence`
  imports the `skills` package), so a single-file call needs no packaging.
- **Two homes hold.** The job reads only the private repo's own records and prints pass/fail — no
  record content is surfaced; the linter + synthetic fixtures stay PII-clear in the public repo.
- **`tests.yml` comment corrected** to point at the private workflow (the claim becomes true).

## Consequences

- Tracking `dyad-milo@main` means a linter change can turn the private CI red **with no private
  change** — the *intended* drift signal (records must satisfy the current canonical schema). Pin
  to a SHA only if reproducibility is later needed (recorded here so the trade-off is explicit).
- **No unit test for the YAML config** (proportionate — ADR-0002): a CI-config artifact validates
  by executing in CI; the workflow's own first run is its proof. `dre_lint` itself keeps its
  Python test pair in the public repo.
- The public `dyad-milo` `tests.yml` job is unchanged (synthetic fixtures only, by design —
  ADR-0003); record-linting is the private repo's job.
