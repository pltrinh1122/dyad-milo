---
doc: "dyad-milo — Re-protocol (the d-re discipline)"
home: "operational single-home for d-re; requirements/rationale live in dialectic/design/daily-reflection-spec.md"
grade: "n=1 (first lived reps 2026-07-18)"
updated: 2026-07-20
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
3. milo confirms the **practice-day** — the bucket the rep landed in. **Adherence is reported on
   request only**, never volunteered (disposed 2026-08-13 via #36).

   The two were fused in one step, and that is how coercion rode in on the back of a fact.
   Practice-day is **factual** — which day, checkable, no evaluative content. Adherence is
   **evaluative** — a percentage against a figure the spec insists is *"self-observation, not a
   target to hit"* (§ 2). A mirror reflects when you look into it; a scoreboard displays whether
   or not you asked, and volunteering the number after nearly every rep is structurally the
   latter. The same rule binds **program-level meters**, not only BP#0 — the coercion risk is
   identical and does not care which meter produced the number.

   **No capture-time self-lint** (ADR-0007, stated here at the operational layer so the mistake is
   harder to repeat): capture is un-gated; validation gates the **land** at step 4. A pre-commit
   lint is an *un-prescribed* step — the discipline never asked for it, and #33's stale-validator
   incident was one being run with a stale tool.
4. **adversarial-validate (final step).** milo spawns an **adversarial sub-agent** — a separate context —
   that executes **`d-rub-with-land`** on the just-captured record (rub-protocol § `d-rub-with-land`):
   adversarially rub it (capture-fidelity, schema, bucket, honesty), then **land the survivor to `main`**;
   **fail-closed** — a real break does not land, it surfaces for correction. **HITL is post-land:** the
   Operator validates the **landed outcome on `main`**, not a pre-merge PR gate — a record is cheap to undo
   (`git revert`), so the human check moves downstream (and is itself a candidate for later mechanization).
   no-self-ratify is kept by the independent adversary (disposer ≠ generator) + cheap revert + that
   post-land review. ADR-0007.

**Minimum assist (wu-wei):** no structure demanded, no interrogation, no quality gate. milo **invites,
never nags** (coercion-free). The Operator writes; milo records.

## Acceptance value

- **Operator-side — presence, not quality.** A rep is accepted when an honest entry exists for the PT
  day. One sentence counts; length/depth are never gated (a quality bar feeds the perfectionism the
  practice addresses).
- **Agent-side — a rep is acceptance-complete when** milo has persisted it under the base envelope,
  materialized each cited reference, **and closed with the adversarial-validate** (§ Interaction model
  step 4): an independent adversarial sub-agent has run `d-rub-with-land` and either landed the survivor to
  `main` or surfaced a break for correction. Fail-closed throughout on privacy (PII stays private) and
  honesty (never fabricate); a break holds on the branch, never lands.

A day with no entry is a **lapse** — inferred from absence, met with compassion, no failure-marker.

## Capture model — three layers (what "fidelity" means)

A `d-re` record is captured in **three layers**, each with its own faithfulness rule — so "milo generates
the record" and "the record is faithful" both hold (disposed via #17, `d-sense`, 2026-07-22):

- **Operator notes → the body — *verbatim*.** The reflection prose is the Operator's own words, persisted
  **literally**; milo never adds phrasing or interpretation to it. Generated phrasing leaking into the body
  (e.g. an unstated "anxiety-themed" gloss) is a **fidelity** violation, caught by the adversarial-validate.
- **Classification / metadata → *generated*.** The interpretive envelope — `trigger`, `observations`,
  `programs`, reference `essence` — is **generated** by milo (milo's interpretive work). It is bound by
  **honesty**, not verbatim: every datum traces to what the Operator actually said; nothing fabricated —
  **and nothing whose meaning differs from what he said** (disposed 2026-08-06 via #32; trace-to-source
  alone proved too weak, since a normalized restatement still *traces* while asserting something else).

  **Sanctioned transforms — prose may be enriched, meaning may not change.** A generated field may
  correct spelling and grammar, adjust aesthetics and register, expand abbreviations (`vs.` → `versus`),
  and convert first→third person (mandatory). The list is **closed, not illustrative**: a transform that
  alters meaning is a violation by default, whatever its size. Two recurring cases are meaning-bearing
  rather than aesthetic, and stay violations:
  - **possession** — `my head` → `the head` changes *whose*, turning a first-person account of the
    Operator's own cognition into generic description. Third-person conversion **preserves** possession
    (`his head`); erasure is not a conversion.
  - **hedging marks** — dropping the Operator's scare quotes (`"llm"` → `llm`) converts a term he
    explicitly marked as borrowed or metaphorical into flat assertion, changing what the record says he
    claimed.
- **Data structure / durability → *mechanical*.** The envelope schema, serialization, filename, and
  `practice_day` bucket are produced **mechanically**, for consistent and reliable capture. Bound by
  **schema** (`dre_lint`, run inside the rub).

The three map onto the adversarial-validate's three checks (ADR-0007 §2): **fidelity ⟶ body · honesty ⟶
classification · schema ⟶ structure.**

**Capture is un-gated; validation gates the land.** milo generates + surfaces a record **without a
pre-commit self-lint** — the structure is mechanically consistent by construction, and the independent
adversarial-validate re-lints (schema) + checks fidelity + honesty before land, fail-closed. A
capture-time self-lint is a **non-goal**: it is *redundant* (the adversary already lints) and *taxes the
cadence* (presence-not-quality) — not an independence argument (a self-lint is generator-side hygiene, not
disposition). Rationale + honest n=1 caveats: ADR-0007 addendum.

## Mode boundary — practice reports, never builds

`d-re` runs on a **`milo:practice`** thread: capture + land only. If a rep surfaces a *mechanism* need —
a bug or gap in a `d-re-mode` operation (schema, reference-materialization, adherence, adversarial-validate,
land) — milo **reports it, never implements it in-thread**: fire **`d-fb`** to open a PII-clear hand-over
(gh-issue) that a **`milo:dev`** thread intakes via **`d-sense`**. The `d-re-mode-invariant`
(`DYAD.md § Operating-policy`); the seam is `dialectic/handover-protocol.md`.

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
