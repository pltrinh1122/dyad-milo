---
doc: "dyad-milo — Rub-protocol (the d-rub checklist)"
home: "single-home for d-rub; DYAD.md § Contract points here and does not restate it"
source: "borrow from dyad-touchstone dialectic/rub-protocol.md @ 3d3a4fc (2026-07-15), re-grounded in milo's own § Contract"
grade: "unexercised in milo (n=0 at adoption); the source's lived rung-proofs are touchstone's, not milo's"
updated: 2026-07-16
---

# Rub-protocol — the `d-rub` checklist

`d-rub` is milo's **Validate-family interface**. `§ Contract` names the two families that must
not collapse — **Generate + Validate**; `d-rub` is how the Operator fires the Validate family:
**one token, escalating rigor, Agent-determined depth**. The Operator types `d-rub`; the Agent
decides how far up the ladder the ask needs, runs it, and **names which rung(s) it ran** — so the
move stays reviewable (the Agent surfaces, the Operator disposes).

## The four rungs — one job, escalating rigor

Grounds G0's three Validate mechanisms (inherited with the form's Contract) plus the plain
orientation act that isn't Validate work at all:

1. **Ground** — establish a claim or assumption against reality, **by execution**: run the actual
   command, check the actual state. Never narrate from memory or a stale cache. A bare
   substrate-state claim (`"all merged"`, `"the branch is clean"`) falls here by default.
2. **Read** — orient: report the re-derived state. **Do not act.** The lightest rung; most asks
   stop here.
3. **Triangulate** — reach the same answer two independent ways and compare; used when one
   grounding pass doesn't earn enough confidence, or corroboration itself is the point.
4. **Rub** — attack a **stated** move or claim; try to break it. **Bounded to that target** — not
   the whole situation. Firing this rung **pre-authorizes the Operator to bear re-alignment**: a
   *solicited* contest, so surfacing the break is invited (it defuses rationalization-defense),
   never a breach of no-self-ratify's spirit.

## Guards (carried from the source, held)

- **Fact-check ≠ attack.** Verifying a stated claim against its source is Ground+Read, not Rub; it
  does not need the whole ladder. The question is *how far this ask had to escalate*, not *which
  marker*.
- **Anxiety-grain / over-guard.** The unbounded "falsify everything" reading is never licensed —
  even the full ladder stays scoped to the *stated* target. Wu-wei: minimum force.
- **`introspect:` stays separate** — examining the Agent's own cognition is not a `d-rub` move
  (no external substrate to query there).

## `d-rub-with-land` — the `d-re` closing move

A **compound move**: an adversarial `d-rub` bounded to a just-captured `d-re` record, followed by a land
of the survivor. It is the **final step of every `d-re`** (re-protocol § Interaction model step 4;
ADR-0007), run by an **adversarial sub-agent** — a *separate context* from the one that captured the
record, so the disposer is never the generator (**no-self-ratify**, mechanized).

- **Rungs it runs:** **Ground + Rub**, bounded to that one record (never the whole repo — bounded-target
  guard). The adversary attacks, by execution: **capture-fidelity** (body verbatim, no silent edits),
  **schema** (`dre_lint` PASS), **bucket** (`practice_day` = the `zone` day of `created`; filename agrees),
  **honesty** (no fabricated telemetry; each `observations[]` datum traces to what the Operator wrote;
  observation `programs ⊆` the record's), and the **durability precondition** (on `main` yet, or only the
  branch).
- **…-with-land — fail-closed:** **survives** → land the survivor to `main` via a forge-merged PR;
  **breaks** → **do not land**, surface the specific finding, hold on the branch for correction. A break is
  a capture defect to fix, never a failure-marker on the Operator (`craft_invariant`).
- **Scope:** client-data `d-re` records only. Anchors and discipline/mechanism changes keep the
  human-disposed reviewed-PR path — they are not `d-re` records and do not auto-land.

## Durative rubs

A rub whose verdict isn't in yet — a test held across runs — lives in the **ledger**
(`reflect/dip-convergence.md`), alongside milo's other open hypotheses and the README's `E`-scale.
Milo keeps **no separate rubbings collection** (proportionate to milo's substrate; add one only if
a durative rub earns its own home).

## Honest grade

Adopted as a **borrow** from dyad-touchstone @ `3d3a4fc`; **n=0 in milo** — unexercised here at
adoption. Touchstone's own protocol carries the source's lived rung-proofs; milo has not yet run
its own. Re-grade when milo's rungs carry milo's proofs.

## Falsifiable claim (inherited)

One Agent-escalated token improves Validate coverage (Triangulation stops being invisible) and
ergonomics (one word, not four to pick between) more than it costs in friction on the
plain-orientation case. *Refuted if:* the Agent consistently over- or under-escalates without
being told the rung, or the Operator finds themselves typing something more verbose than `d-rub`
just to ask for a quick status check.
