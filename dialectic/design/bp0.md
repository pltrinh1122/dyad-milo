---
doc: "dyad-milo — Behavioral-Program #0 (ensure telemetry isn't starved)"
home: "rationale in daily-reflection-spec.md § 7 and reflect/dip-convergence.md"
updated: 2026-07-18
---

# Behavioral-Program #0 — ensure telemetry isn't starved

The persistent grounding / **bootstrap** program. Its behavior *is* the base act (make `d-re` entries),
so its adherence *is* the base meter, and it is **prior to every other program** — all are measured
through the base. It is **implicit**: never listed in a record's `programs[]` (spec § 6).

- **Policy: maximize input, distill per discriminator.** BP#0 owns "don't **starve**"; the grounded
  discriminators (essence inclusion, base/sub-class boundary, presence-not-quality) own "don't **drown**."
- **"More is better" = a gradient above the presence floor, never a threshold** (a volume quota = coercion).
- **The motivation engine is a *mirror*, not an *optimizer*** (coercion-free-motivation-design): it
  reflects self-knowledge back to the Operator (what tends to open a curiosity-gap). It must **never**
  optimize content on a "fired-an-entry" reward — that reproduces attention-economy coercion (falsified
  via SDT / Fogg / Loewenstein / Goodhart; see `reflect/dip-convergence.md`).
- **Telemetry:** base-presence for now; a starvation-detector (max-gap / cadence) is added only if a
  lapse-tail appears (wu-wei).
- **Candidate pull-mechanism (TODO, undesigned):** surface curiosity-relevant reading to widen the
  entry surface-area — a *pull*, never a *push*. Mirror-safe only while NOT tuned on an entry-firing reward.
