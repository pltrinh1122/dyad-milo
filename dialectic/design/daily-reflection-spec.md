---
doc: "dyad-milo — daily-reflection (d-re) telemetry spec"
status: "requirements-closed 2026-07-18; hand-off for codification"
home: "the clean spec codification implements; provenance in reflect/dip-convergence.md"
grade: "n=1 (first lived reps 2026-07-18); unexercised beyond the Operator"
---

# daily-reflection (`d-re`) — telemetry spec

The requirements for milo's first program. Requirements phase closed 2026-07-18 (Generate +
Validate; Operator-disposed). This is the **hand-off contract** for codification: the Agent codifies
autonomously within it and escalates to the Operator (HITL) only on **drift** (§ 12). Lived practice
data stays in the private client record; this spec is PII-clear.

## 1. Goal

`d-re` is the base practice: the Operator externalizes a reflection ("thought-record / reflection-entry")
each day. Externalization is held to be **necessary for behavioral change** (the reframe/clarity does not
come as reliably when kept internal). The daily-reflection is dual-natured — a rep the Operator does **and**
the **instrument** that will measure every other behavioral program. Destination (`craft_telos`): ~90%
adherence with unaided self-recovery; graduation = practice flows from identity, needing no external push.

## 2. Invariants (constraints — a breach is drift → escalate)

- **Coercion-free.** Motivation runs on curiosity + purpose, constrained by identity — never obligation.
  Entailed by graduation (a coerced practice collapses when the coercer is removed). No quotas, no streak /
  loss-aversion mechanics, no nagging. The ~90% figure is *self-observation, not a target to hit*.
- **Presence-not-quality (the floor).** A rep is accepted when an honest entry exists for the day; one
  sentence counts. Quality/length/depth are never a gate (a quality bar feeds the perfectionism the
  practice addresses).
- **Fail-closed, twice.** *Privacy:* PII never leaves the private client record; unattended mechanisms
  write private-only; any public surfacing is a separate, manual, gated step that itself fails closed;
  uncertainty → withhold. *Honesty:* never fabricate; verify what you can, flag what you can't, withhold
  rather than invent.
- **Two homes (PII boundary).** Mechanism/craft (PII-clear) → public `dyad-milo`. Lived data, PII →
  private `dyad-milo-<client>`.
- **Wu-wei.** Minimum structure; build only what a purpose pulls on. Free-form until structure is earned.

## 3. Base-class telemetry — `ReflectionEntry`

Free-flowing regardless of behavioral programs. Behavioral programs attach sub-class telemetry via the
`programs[]` discriminator (§ 6). One record = one entry.

- **`body`** — free-flowing reflection prose. Unstructured; the presence-not-quality floor lives here.
- **Envelope:**
  - `created` — absolute instant, ISO-8601 with offset (timezone-agnostic storage).
  - `practice_day` — the PT **calendar day** via IANA `America/Los_Angeles` (DST-correct); the adherence
    bucket.
  - `zone` — `America/Los_Angeles` (so bucketing is reproducible).
  - `trigger` — § 4.
  - `references` — § 5 (0..n, optional).
  - `programs` — § 6 (default empty).
- **Not base (→ CBT-intervention sub-class, deferred):** emotion intensity before/after ratings,
  hot-thought + belief rating, evidence for/against, distortion label, behavioral action.

## 4. `trigger` schema (D1: layered-light)

Always present; never empty. `stated`/`spontaneous` is a *description of a layer*, not a top-level split;
a trigger can be an internal need wearing an external occasion.

```
trigger:
  primary: >-        # the real driver; never empty. May be an internal state-capture
    <text>           #   (spontaneous: what was I feeling / doing / thinking) OR external.
  proximate: >-      # optional; the occasion that surfaced it, if distinct from primary.
    <text>
  boundary: <text>   # optional (e.g. partial-read; fired after a few dots)
  setting: <text>    # optional (who / where)
```

Rules: `primary` is mandatory and never "none" — a spontaneous entry's primary is the state-capture.
Fail-closed: uncaptured sub-fields are omitted, never fabricated.

## 5. `references[]` schema (D3)

```
references:                       # 0..n; optional per entry
  - id: <slug>
    citation: {title, author, date, outlet}
    links: [<url>, ...]           # 1..n — canonical + mirrors
    essence:                      # 0..n distilled fragments
      - id: <E-id>
        facet: semantic | trust | affirmation | <open-extensible>
        partition: trigger-time | confirmed-after   # optional (D2)
        text: "<verbatim quote, or tight paraphrase>"
    provenance: >- <text>         # supporting-but-removable; held SEPARATE from essence
    fidelity: >- <text>           # per-reference honesty ledger: how obtained, failures, corrections
```

Rules:
- **Essence inclusion (pinned):** a fragment is essence iff removing it leaves a gap in explaining the
  entry's **intent/motivation** (multi-facet leave-one-out). Facets **open-extensible**. The *mirror*
  (self-recognition in the source) is the selection lens, not a cached fragment.
- **Partition (D2):** `trigger-time` = read among the dots before the entry fired; `confirmed-after` =
  met on later reading. Optional, populated only when it carries mirror signal; never required. Feeds the
  BP#0 *mirror* (self-knowledge), never a content-optimizer.
- **Essence text** = verbatim when available; tight paraphrase **flagged** when not.
- **Provenance separate** from essence; **fidelity per-reference**; fail-closed on both.

## 6. `programs[]` discriminator (D4)

`programs: []` — the *additional* behavioral programs this entry serves. **BP#0 is implicit** (every entry
feeds it by existing) and is never listed; a pure base reflection has `programs: []`. Contents are
program-ids. The sub-class-telemetry **attachment mechanism is deferred** to the sub-class arc — the base
defines only the discriminator.

## 7. Behavioral-Program #0 — "ensure telemetry isn't starved"

Persistent grounding / bootstrap program: its behavior *is* the base act (make entries), so its adherence
*is* the base meter, and it is prior to every other program. Owns the "don't starve" half of the telemetry
policy; the grounded discriminators (essence invariant, base/sub-class boundary, presence-not-quality) own
"don't drown." Policy: **maximize input, distill per discriminator.**

- **"More is better" = gradient above the presence floor, never a threshold** (a volume quota = coercion).
- **BP#0's motivation engine is a *mirror*, not an *optimizer*** (coercion-free-motivation-design). It
  reflects self-knowledge back to the Operator (what tends to open a curiosity-gap); it must never optimize
  content on a "fired-an-entry" reward (that reproduces attention-economy coercion — falsified via SDT /
  Fogg / Loewenstein / Goodhart).
- **BP#0 telemetry** = base-presence for now; a starvation-detector (max-gap / cadence) added only if a
  lapse-tail appears.
- **Candidate pull-mechanism (TODO, undesigned):** surface curiosity-relevant reading to widen entry
  surface-area — a *pull*, never a *push*. Guard: mirror-safe only while NOT tuned on an entry-firing reward.

## 8. `d-re` discipline (interaction model + acceptance value)

- **Interaction model:** `d-re <free-form reflection>` → milo persists it verbatim to the private store
  (enveloped, timestamped) → milo materializes any cited reference (§ 5) → milo confirms the practice-day
  and current adherence. **Minimum assist:** no structure demanded, no interrogation, no quality gate;
  milo invites, never nags.
- **Acceptance value — two sides:** *Operator-side* = presence (an honest entry exists for the PT day).
  *Agent-side* = persist under the base envelope; materialize each cited reference as essence + provenance +
  link, fail-closed. A day with no entry is a **lapse** — inferred from absence, met with compassion, no
  failure-marker.

## 9. Adherence + analytics

- **Adherence** = covered-days / eligible-days; a PT day with ≥1 entry = covered. Eligible-days start at
  **enrollment (2026-07-18)**. Reported **since-start + rolling 7 / 30 / 90-day**.
- **Lapse** = absence-inferred (a PT day with zero entries); no explicit failure marker.
- **Analytics location:** code lives PII-clear in `dyad-milo`, reads the private records. Program-agnostic
  from day one (takes a program-id; daily-reflection/BP#0 = program #0) so later programs reuse the meter.
- **Fail-closed publishing:** unattended, analytics writes to the private record only. Any public surfacing
  (a de-dated rate — the n=1 proof) is a separate manual gated step that itself fails closed.

## 10. Records: identity, filenames, retrofit

- Filenames: `reflections/YYYY-MM-DD-NN.md` (NN = intra-day sequence, 01-based). Multiple entries per day
  allowed; adherence counts the day.
- **Retrofit the three day-1 records** to this spec: rename the first (`2026-07-18.md` → `-01`); drop the
  legacy `program: daily-reflection` field; ensure `trigger` / `references[]` / `programs[]` conform.
  Preserve all lived content and timestamps verbatim.

## 11. Codification scope (what to build)

- **`dialectic/re-protocol.md`** — the `d-re` discipline (interaction model + acceptance value +
  reference-materialization rule), single-home; `DYAD.md`/`README` need no change beyond a pointer if any.
- **A base-class telemetry schema doc** (§§ 3–6) — the canonical schema.
- **A BP#0 note** (§ 7).
- **Adherence analytics tooling** (§ 9) — implementation Agent's choice, design-for-scale.
- **Retrofit** the day-1 records (§ 10).
- **Lift PII-clear craft lessons** to `reflect/`: *coercion-free ⇐ graduation*, *the essence inclusion
  criterion*, *externalization is necessary for behavioral change*, *presence-not-perfection*,
  *coercion-free-motivation-design (mirror not optimizer)*.

## 12. Autonomy & HITL escalation contract

The Agent codifies **autonomously** within this spec and reports. Escalate to the Operator (HITL) on **drift**:

- **Goal drift** — anything that changes *what the system is for* (§ 1) or the telos.
- **Constraint drift** — anything that would bend or breach an invariant (§ 2): coercion-free,
  presence-not-quality, fail-closed (privacy/honesty), the PII two-homes boundary, wu-wei.
- **Coverage drift** — a requirement this spec does not cover, or an ambiguity that forces a design choice
  not disposed here (i.e. would require the Agent to self-ratify a requirements-level decision).

Everything else — naming, file structure, analytics implementation, formatting, mechanical retrofit — is
Agent's discretion, reported not escalated. All public changes land on the working branch; `main` advances
only through a reviewed PR (Operator disposes at merge — no-self-ratify holds).

## 13. Out of scope / deferred

- **CBT-intervention sub-class** (the § 3 "not base" fields) — next arc.
- **`programs[]` attachment mechanism** — sub-class arc.
- **Generalization beyond the Operator** (other clients) — pinned (`DYAD.md § Pins`).
- **Grounding-modality lock** (CBT contingent) — pinned.
- **BP#0 pull-mechanism / starvation-detector** — build only when earned (§ 7).
