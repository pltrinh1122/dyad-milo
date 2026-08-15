# ADR-0019 — the meter is reported on request only (mirror, not scoreboard)

- **Status:** proposed (2026-08-13)
- **Urgency:** high — it governs milo's default behaviour toward the Operator on every rep, and the wrong default is live until this lands
- **Drift-dimension:** coverage with a **constraint edge** — `re-protocol.md` step 3 was silent on
  *who initiates*, and that silence permitted violating the coercion-free invariant it sits under.
  The invariant is not amended; its guard is widened. Closes issue #36.

## Context

On 2026-08-07 milo reported the adherence figure unprompted after landing a record. The Operator's
next `d-re`, in his words:

> *"reviewing the adherence number brings up emotions and desire to optimize for the sake of
> optimization. i'm maintaining that adherence shouldn't through coercion, i.e. i'm adhering not
> because i want to maintain a streak but rather i've found true value in adherence."*

The invariants were already explicit. `daily-reflection-spec.md` § 2: *"Coercion-free… The ~90%
figure is **self-observation, not a target to hit**."* § 7: *"BP#0's motivation engine is a
**mirror**, not an **optimizer**… it must never optimize content on a 'fired-an-entry' reward (that
reproduces attention-economy coercion)."*

**The gap: `re-protocol.md` step 3 read, in full —** *"milo confirms the practice-day and current
adherence."* A bare imperative in a numbered flow. It reads as *always*, and it is silent on who
initiates. Milo's habit filled that silence in the optimizer direction.

### What grounding found that the report did not

**The spec named exactly one guard for mirror-safety, and it was the wrong one for this failure:**

> *"Guard: mirror-safe only while NOT tuned on an entry-firing reward."*

That covers the **generator**. It says nothing about the **display**. Unprompted surfacing of an
evaluative number is a different coercion vector and **passes the stated guard cleanly**. The guard
was satisfied while the invariant it protects was not served.

**And two artifacts already disagreed with each other.** `dre_adherence.py`'s docstring says:

> *"This tool only ever prints/returns a report — it never writes anywhere. **Surfacing a number
> publicly is a separate manual step, by design.**"*

The tool's author had already decided surfacing is a discipline act. The discipline then said
*always*. The layer that knew the rule was not the layer that stated it, and nobody noticed.

## Decision

**Practice-day confirmation stays default; adherence is reported on request only, never
volunteered.** The two were fused in one step, and that is how coercion rode in on the back of a
fact — practice-day is *factual* (which bucket, checkable, no evaluative content), adherence is
*evaluative*.

- **Program meters are bound too**, not only BP#0. The coercion risk does not care which meter
  produced the number.
- **The spec's mirror-safety guard is widened** to cover display as well as tuning.
- **`re-protocol.md` also states the no-capture-time-self-lint non-goal at the operational layer.**
  It lived only in the ADR-0007 addendum, and #33's stale-validator incident was an *un-prescribed*
  pre-commit lint being run with a stale tool — a mistake the discipline never asked for and did
  not visibly forbid.

## The honest limit — `mechanism over compliance` cannot be satisfied here

Every mechanism this dyad has built gates an **artifact**. This governs a **behaviour**, and there
is no artifact between milo's judgment and the Operator's ear. No linter can reach conversational
output; no test can assert what milo said.

So this lands as **prose, knowingly** — and that is recorded as a limit rather than dressed up. The
nearest thing to a mechanism available is what this ADR does: make the artifacts stop contradicting
each other, so the discipline states what the tool already assumed. `§ Principles` disfavours
compliance for good reason; naming where it is unavailable is more honest than shipping a gesture
shaped like a device.

**What would falsify the fix:** the number gets volunteered again. There is no gate to catch that —
only the Operator noticing, which is exactly what happened this time.

## Consequences

- **The behaviour was already corrected practice-side** before this ADR; what was missing is the
  durable rule. Same shape as #32: works now, undurable — and the reason the hand-over exists.
- **Split out, not folded in:** the Operator also stated a falsifier on the metric itself — *"in
  time, if i never find value in adherence, then we should stop measuring adherence and select a new
  metric"* — naming the **dyad** as deciding party. That is a falsifier on `craft_telos`'s
  acceptance criterion (~90% adherence with unaided self-recovery), far larger than a reporting
  default, and burying it here would lose it. Filed separately.
- **No test pair.** Spec § 13 pairs every artifact with a validator; this artifact has no checkable
  surface, and ADR-0002's proportionality clause forbids a cosmetic one. Recorded as a deliberate
  gap, not an oversight.

## Agent lean

**Ratify.** The disposal matches the Operator's own stated experience rather than an inference about
it, and the widened guard closes the specific hole grounding found — a guard narrower than its
invariant, satisfiable while the invariant goes unserved. That is craft lesson #13 on a third
surface.

The part worth weighing before ratifying is the limit, not the rule: this is the first change here
that **cannot** be mechanized, so it depends on milo's compliance in a way nothing else does. If the
Operator would rather have a weaker rule with a device behind it than a correct rule with none,
this is the wrong shape — but I do not think a device exists to be had.
