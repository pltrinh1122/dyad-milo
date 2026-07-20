---
doc: "dyad-milo — Handover-protocol (practice → dev seam: d-fb / d-sense)"
home: "single-home for d-fb + d-sense + the d-re-mode-invariant hand-over loop; DYAD.md § Operating-policy points here"
grade: "n=0 at adoption (2026-07-20); bootstrap instance = gh-issue #14"
updated: 2026-07-20
---

# Handover-protocol — practice → dev, seamless

milo runs in two thread modes. The **`d-re-mode-invariant`** (`DYAD.md § Operating-policy`) keeps them
apart: a **`milo:practice`** thread does client-record **capture + land only**; all craft/mechanism work
is deferred to a **`milo:dev`** thread. This protocol is the seam between them — how practice **reports** a
mechanism need and dev **picks it up** without loss.

## The loop

```
milo:practice — hits a d-re-mode issue / mechanism need
   │  d-fb {feedback}       → opens a PII-clear hand-over gh-issue, then STOPS (never implements)
   ▼
[hand-over gh-issue]        ← the artifact; label `milo:dev`; template makes intake seamless
   │  d-sense {gh-issue#}   → milo:dev Grounds + scopes + surfaces the spine, then STOPS for disposition
   ▼
Operator disposes → implement (dev) → land via reviewed PR → close the issue
```

## Thread mode (how milo knows which side it is on)

Mode is set by **how the thread was opened**, and the token the Operator fires *is* the signal — no
separate marker required:

- **`d-re …`** opens a **`milo:practice`** thread — capture + land only.
- **`d-start` / `d-arc …`** opens a **`milo:dev`** thread — craft/mechanism work.
- `d-fb` is practice-side; `d-sense` is dev-side. (A mechanically-checkable branch-name marker may be
  added later *if* a thread's mode ever needs to be enforced by a guard — not built until earned, wu-wei.)

## `d-fb {feedback}` — practice-side report

Fired on a practice thread when a `d-re-mode` operation reveals a mechanism issue or need. milo:

1. **opens a hand-over gh-issue** in the **public** `dyad-milo` repo from the `d-fb` template
   (`.github/ISSUE_TEMPLATE/d-fb-handover.md`), labeled `milo:dev` + `d-fb` — capturing the feedback
   verbatim, the context (which `d-re-mode` op), the provenance (surfaced-from-practice), and open questions;
2. **does not implement** — practice reports, never builds (the `d-re-mode-invariant`);
3. **fail-closed on PII (§ two homes):** the issue is mechanism-level and **PII-clear** — client specifics
   stay in the private record; a feedback item that can't be stated PII-clear is abstracted or withheld,
   never leaked to a public issue.

Acceptance-complete when the hand-over artifact exists, PII-clear, and the practice thread has implemented
nothing.

## `d-sense {gh-issue#}` — dev-side intake

Fired on a dev thread to **intake** a reported issue **before** implementation. milo:

1. **Grounds** the report (d-rub Ground) — is the problem real? reproduce / check the actual state; never
   take the report at face value;
2. **scopes** it — which **drift dimension** (goal / constraint / coverage, spec § 12), blast radius, in vs out;
3. **surfaces the spine** — the proposed approach/altitude — and **STOPS for the Operator's disposition**
   (spine-before-form; no-self-ratify). `d-sense` never slides into building.

Acceptance-complete when the report is grounded, scoped, and the spine is on the table — implementation is
a *separate*, disposed step (often a `d-arc`).

## The hand-over artifact (gh-issue)

The vehicle is a **GitHub issue** in the public repo (PII-clear), **one per feedback item**, from the
`d-fb` template. gh-issue **#14** is the bootstrap instance. Structured so a `d-sense` pickup is seamless —
context · the mechanism need · what stays on practice · open dispositions. Closed when the dev
implementation lands. (Rejected: a running-log issue and a cairn-only note — neither gives per-item forge
tracking/labels; ADR-0008.)

## Fail-closed / no-self-ratify (across the seam)

- **PII** — the hand-over is public → PII-clear or withheld.
- **no-self-ratify** — practice surfaces (`d-fb`), dev grounds + proposes (`d-sense`), the **Operator
  disposes**; Generate + Validate never collapse across the seam.
- **spine-before-form** — `d-sense` stops at the spine; building is a later, disposed step.

## Grade

n=0 at adoption (2026-07-20). Bootstrap: gh-issue #14 (the milo:dev hand-over that surfaced this arc).
Unexercised as a repeated loop; re-grade when `d-fb` / `d-sense` carry their own lived reps.
