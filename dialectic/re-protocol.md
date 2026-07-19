---
doc: "dyad-milo — Re-protocol (the d-re discipline)"
home: "operational single-home for d-re; requirements/rationale live in dialectic/design/daily-reflection-spec.md"
grade: "n=1 (first lived reps 2026-07-18)"
updated: 2026-07-18
---

# Re-protocol — the `d-re` discipline

`d-re` is milo's **daily-reflection** interface — the base practice: the Operator externalizes a
reflection; milo records it with minimum assist. Externalization is held **necessary for behavioral
change**. This file is the operational *How*; the schema and rationale live in
`dialectic/design/daily-reflection-spec.md` (the requirements home) and are enforced by
`skills/dre_lint.py`.

## Interaction model

`d-re <free-form reflection>` →

1. milo persists it **verbatim** to the private client store, under the base envelope (`created` instant,
   PT `practice_day` bucket, `zone`, `trigger`, `programs`) — one record per entry.
2. milo materializes any cited reference (§ Reference materialization).
3. milo confirms the practice-day and current adherence.

**Minimum assist (wu-wei):** no structure demanded, no interrogation, no quality gate. milo **invites,
never nags** (coercion-free). The Operator writes; milo records.

## Acceptance value

- **Operator-side — presence, not quality.** A rep is accepted when an honest entry exists for the PT
  day. One sentence counts; length/depth are never gated (a quality bar feeds the perfectionism the
  practice addresses).
- **Agent-side — a rep is acceptance-complete when** milo has persisted it under the base envelope and
  materialized each cited reference, fail-closed on privacy (PII stays private) and honesty (never
  fabricate).

A day with no entry is a **lapse** — inferred from absence, met with compassion, no failure-marker.

## Reference materialization

A cited source materializes as **essence + provenance + link** (spec § 5):

- **Essence** — the fragments that pass the **leave-one-out inclusion test** (removing one gaps the
  entry's intent/motivation), each tagged by `facet` (semantic / trust / affirmation, open-extensible)
  and optionally `partition` (trigger-time / confirmed-after — feeds the BP#0 mirror).
- **Provenance** — supporting-but-removable context, held separate from essence.
- **Fidelity** — the honesty ledger (how obtained, fetch failures, corrections). Fail-closed: verify what
  you can, flag what you can't, withhold rather than invent.

The **mirror** — recognizing yourself in the source — is the selection lens, never a cached fragment.

## Sub-class telemetry (observations)

When a reflection serves an additional behavioral program, milo lists it in `programs[]` and — **only if
the entry gives the data** — records shared `observations[]` (spec § 6 / ADR-0004), each tagging the
program(s) it feeds. Observations are record-level and shared, so **one datum can serve several programs**
without being written twice. Same minimum-assist stance: **presence-not-quality holds at the sub-class
too** — milo never demands structured fields, never gates on how many observations are logged; a listed
program with no observation is complete. milo captures what the Operator states (fail-closed: never
fabricates an intensity, a marker, or a thought), and leaves the rest. First program: `reduce-anxiety`
(an observation log — see `dialectic/design/programs/reduce-anxiety.md`).

## Trigger

Every entry carries a `trigger`, never empty. `primary` = the real driver (an internal **state-capture** —
what I was feeling / doing / thinking — or an external prompt); `proximate` = the occasion, if distinct;
optional `boundary` / `setting`. A spontaneous trigger is a state-capture — **never "none."**

## Grade

n=1 — first lived reps 2026-07-18 (three entries). Unexercised beyond the Operator; the spec's `E0 / n=1`
caveats stand.
