# ADR-0014 — mechanical backstop for meaning-bearing markers (DECISION OPEN)

- **Status:** **proposed — decision NOT made.** This ADR is the escalation artifact, not a record
  of a disposal (spec § 13: *"a decision an ADR finds crosses into drift is escalated (HITL), not
  self-ratified — the ADR is the escalation artifact"*).
- **Drift-dimension:** coverage, with a **constraint edge** — option B would move a rule across the
  three-layer capture model's boundary, which is an invariant of ADR-0007's model.
- **Origin:** issue #32 disposition 3, deferred at `d-sense` and again at `d-land`.

## Context

The ADR-0007 addendum (2026-08-06) settled *what* honesty demands of generated fields:
trace-to-source **+ meaning-preservation**, with a closed list of sanctioned transforms. It
deliberately did **not** settle *how that is enforced*.

Two violation classes survived the disposition, both meaning-bearing rather than aesthetic:

| marker | violation | why it is meaning, not style |
|---|---|---|
| **possession** | `my head` → `the head` | changes *whose* — a first-person account of the Operator's own cognition becomes generic description. Third-person conversion preserves it (`his head`); erasure is not a conversion. |
| **hedging marks** | `"llm"` → `llm` | a term the Operator marked as borrowed becomes flat assertion — it changes what the record says he claimed. |

Enforcement today is the **adversarial-validate's judgment** (ADR-0007). Its record is
**4 detections in 4 opportunities** — detection has never been the failure. The recurrence is
generator-side, which the written rule now addresses.

**What is and is not mechanizable.** "Did meaning change?" is not decidable in general — it
requires semantic alignment between a paraphrase and its source. The two markers above *are*
mechanically detectable, because each is a surface feature whose removal reliably alters meaning.
Probed 2026-08-06 (3 synthetic cases, PII-clear):

- a record exhibiting both classes → flagged
- a faithful record → clean
- a **sanctioned** third-person paraphrase (`my`→`his`, possession preserved) → clean

So any backstop is necessarily a **heuristic over two known classes**, not a gate on the honesty
rule. That distinction drives the options below.

## The decision to be made

Should the two markers get a mechanical backstop — and if so, where does it live?

### Option A — no backstop; judgment only

Status quo after the addendum. The adversary enforces; the written rule handles prevention.

- **For:** wu-wei — the adversary is already at 4/4, and the addendum targets the actual
  (generator-side) failure. No new artifact, no false-positive surface.
- **Against:** leaves the honesty layer with **no device**, resting on the judgment of a
  sub-agent that must remember to look. This session's craft lesson #12 (*an ungrounded state
  claim is itself an unbacked gate*) argues against calling that settled.

### Option B — fold the check into `dre_lint`

- **For:** it inherits **ADR-0006's private `lint-records` CI**, so it would fire on every record
  automatically. That is the genuine mechanism-over-compliance property #29, #30 and #33 all lack.
- **Against, structural:** `dre_lint` owns the **mechanical/schema** layer. This rule belongs to
  the **generated/honesty** layer, which the three-layer model assigns to the adversary. Folding it
  in makes the schema linter **body-aware for the first time** and blurs a boundary ADR-0007 drew
  deliberately.
- **Against, and heavier — an adherence risk.** Under ADR-0006 CI, a **false positive blocks a
  land.** The check is a heuristic; a body reading "my pattern" beside a generated field that
  legitimately says "the pattern" about something else would fail a *correct* record. `craft_telos`
  is adherence, and a validator that taxes the daily rep to catch a style regression is trading the
  wrong currency. ADR-0002's proportionality clause points the same way.

### Option C — a separate honesty-layer validator, invoked by the adversary

A distinct script (e.g. `skills/dre_honesty.py`) run as part of `d-rub-with-land`, alongside — not
inside — `dre_lint`.

- **For:** keeps the three-layer boundary intact; the honesty layer gets a sharper tool without the
  schema layer growing responsibilities that aren't its own.
- **For:** a heuristic's flags land in front of **judgment**, which is the correct adjudicator for
  a heuristic. The adversary can dismiss a false positive; CI cannot.
- **For:** it does not weaken enforcement the way it first appears — the adversary is *already* the
  honesty layer's mechanism (ADR-0007) and already runs `dre_lint` as a protocol step. One more
  script in that step is no more compliance-dependent than the rub itself.
- **Against:** it does not fire in CI, so a land that skips the rub skips the check. It is a
  sharper instrument for an existing mechanism, not a new independent one.

## Evidence limits — stated, not buried

The feasibility probe is **3 synthetic cases**, not a corpus. A real false-positive rate cannot be
measured from the public repo: the records live in the private store, and Operator access to it was
offered and then **withdrawn** (2026-08-06), correctly — a dev thread's output is public artifacts,
and pulling PII into it creates a leak path that did not previously exist.

**This gap is closable without any private access changing hands:** the probe can be run against
the real corpus on the private side, reporting only counts (records scanned, flags raised, flags
judged false). If the decision turns on false-positive rate — and under option B it should — that
measurement is the missing input, and it is cheap.

## Agent leaning (not a disposal)

**C**, and this **revises the leaning recorded at `d-sense`**, which framed the choice as
linter-versus-adversary with the linter holding the CI advantage. That framing missed the
consequence that decides it: under ADR-0006, a `dre_lint` false positive does not merely warn — it
**blocks a land**. A heuristic wired to a blocking gate converts a fidelity aid into an adherence
tax, and adherence is the telos. `dre_lint` is for decidable invariants; this is not one.

The counter worth holding: option C's check only fires when the rub runs, so it is a better
instrument rather than a new guarantee. If the Operator's priority is an independent device that
fires regardless — the #29/#30/#33 property — only B delivers it, and then the false-positive rate
must be measured first.

## Consequences of leaving this open

The addendum's rule stands and is enforced by the adversary either way; **nothing is unguarded
while this is undisposed.** What is deferred is whether that enforcement gains a mechanical
instrument. Recorded here so the deferral is tracked rather than resident in a closed PR
description — the failure mode issue #28 exists to name.
