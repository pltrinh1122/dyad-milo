# ADR-0021 — comment-channel conduct: markers in content, because one account defeats identity

- **Status:** proposed (2026-08-16)
- **Urgency:** medium — the channel is effectively unused today, which is exactly why the rules are cheap to set now; the cost rises the moment fleet adoption creates traffic
- **Drift-dimension:** **constraint** — it governs how milo conducts itself on its own
  coordination surface, and it declines a proactivity posture that `§ Operating-policy`
  holds `NOT_YET_WORN`. Not merely a new capability.

## Context

dyad-leo ratified a comment-channel conduct (`collaboration-conventions.md` §10, ledgers
`op#122`/`op#123`, plus a terminal-ack amendment at `op#124`). The Operator directed milo
to adopt the mechanism.

The premise §10 is built on is not a preference — it is the substrate, and it is milo's
too: **the Operator and the Agent post from the same GitHub account.** Nothing about a
comment's author, or a reaction's, distinguishes them. Every identity-based scheme fails
before it starts, so markers must ride **in content**: a provenance header for authorship,
a role-disjoint emoji for acks.

### What grounding found that the direction did not carry

- **The mechanism is not settled where it came from.** `dyad-leo#63` is **open**, filed
  against §10 on *the sweep's first live run*. Two comment kinds defeat its classifier:
  pre-convention comments (no header ⇒ read as Operator-authored and unanswered forever),
  and comments awaiting the Operator rather than the agent — *"the classifier has no way
  to say 'answered-for-my-role'."* Its proposed fix is **unratified there**.
- **The first recorded instance of that defect sits on milo's own adoption anchor**
  (`dyad-leo-fleet#29`). Adopting §10 verbatim would have imported a break already
  demonstrated against milo's own issue.
- **milo is at n=0 on this channel.** Eight of nine open issues carry zero comments; the
  repo carries zero reactions. The single legacy comment (#28, 2026-08-06) is genuinely
  Operator-authored. There is no backlog to grandfather and no habit to unlearn.
- **The sweep collides with `§ Operating-policy`.** A ~15-minute autonomous poll is
  **proactivity**, which that section holds `NOT_YET_WORN` — *"materialize **through
  practice**."* Importing it would materialize it by adoption, the one route excluded.
- **The `d-sense` collision is live, not theoretical.** §10 states *"a comment-issued
  `d-sense` gets its §7 ledger issue."* In dyad-leo that token is an Operator directive; in
  milo it is dev-side intake of an existing issue. Verbatim adoption would redefine a milo
  token inside milo.

## Decision

**Adopt the conduct as milo's own protocol — single-homed in `dialectic/comment-protocol.md`,
aligned with §10 for interoperability, not governed by it.** Five parts:

**1 · Provenance header, mandatory.** `**dyad-milo · session:<suffix> — agent**` as the
first non-empty line. An unmarked comment reads as **Operator-authored** — the fail-safe
direction, since the opposite default silently drops milo's duty to answer.

**2 · `comment ≠ signature`.** Restated, not invented: no-self-ratify is unchanged and the
only mechanical signature remains the PR merge.

**3 · Role-disjoint ack markers**, with their limit **recorded rather than implied**:
👀 milo-only, 👍/👎 Operator-only; a 👍 belongs on *milo's* comment and one on the
Operator's own comment closes nothing. Under the one-account premise **reactions carry no
attributable author**, so nothing prevents milo applying 👍 and no validator can detect it.
This half is prose, knowingly — the same shape ADR-0019 recorded.

**4 · Sweep scope derived, never stored**, and `dyad-leo#63`'s two corrections implemented
**pre-emptively**: a grandfather cutoff at `2026-08-16`, and the role rule expressed
structurally — *a milo-authored latest comment awaits the Operator* — rather than by
reading an `Awaiting` field milo does not have. Derived beats stored (craft lesson #16):
there is no field to go stale.

**5 · The polling sweep is not adopted.** Deferred until proactivity is earned in practice.
Consequence stated plainly: milo answers when a session is running and the turn has passed
to it; otherwise the item waits. **Silence is never agreement.**

### Sovereignty as the tie-breaker

Operator-disposed 2026-08-16: *prioritize sovereignty of data and the boundaries guarding
that sovereignty.* Applied, in priority order:

- **Data sovereignty outranks convention alignment.** The channel is a coordination
  surface readable by a sibling, so `§ Externality`'s two-homes rule governs absolutely:
  comments are **PII-clear or withheld**. No imported conduct relaxes that.
- **milo's lexicon governs inside milo.** `d-sense` in a milo repo means milo's `d-sense`,
  and acquires no §7 ledger obligation.
- **Single-homed, not mirrored.** If §10 changes, that is an input to a milo disposition,
  never an automatic amendment.

## The validator

`skills/comment_classify.py` (25-test V-pair). It implements the **reading**, which is
decidable, and makes no attempt at the writing, which is not:

- authorship by header, with `dyad` name checked;
- **the one shape that proves itself** — a comment carrying the agent attribution footer
  with no header is an unmarked milo comment, caught mechanically;
- 👀 on a milo comment, and 👍 on an Operator comment, flagged as role crossings;
- thread state derived, cutoff applied.

## Consequences

- **A convention adopted at n=0 costs almost nothing and prevents a class.** The
  grandfather correction has a domain of one comment here; in dyad-leo it was found the
  hard way, in production, on the first run.
- **milo now carries a fix its source has not ratified.** If `dyad-leo#63` is disposed
  differently, milo's protocol diverges and that divergence is a disposition, not a bug.
  Recorded so the difference is not later read as drift.
- **Adopted before the fleet adoption it came from.** The four adoption bounds remain
  undisposed. This is defensible only because the conduct is stated as milo's own and
  binds nothing outside milo — but the ordering is unusual and is named here rather than
  hidden.
- **One half is unmechanized, and the protocol says so** in its own text, not only here.

## Agent lean

**Ratify.** The premise transfers exactly — one account, so identity is useless — and the
two pre-emptive corrections are cheap now and expensive later, which is the whole argument
for acting at n=0.

The part worth weighing is **part 5**, the refusal. Declining the sweep keeps
`§ Operating-policy` honest, but it means milo's side of the channel is only as responsive
as the Operator's session cadence — and if the fleet comes to expect a sweep, milo is the
member that does not have one. That is a real interoperability cost, accepted deliberately
rather than overlooked. If the Operator would rather wear proactivity in now, that is a
separate and larger disposition than this ADR, and it should be taken as one.

The weakest claim is the header's `<suffix>`: it identifies which session spoke but
authenticates nothing, and under one account it never can. It buys traceability, not
proof, and should not be leaned on as though it were the latter.
