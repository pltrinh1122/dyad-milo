---
doc: "dyad-milo — Comment-protocol (conduct on the issue comment channel)"
home: "single-home for the provenance header, the role-split ack markers, and the sweep-scope rule; DYAD.md § Operating-policy points here"
interop: "aligned with dyad-leo-fleet/dialectic/collaboration-conventions.md §10 so the surfaces interoperate; NOT governed by it — see § Sovereignty"
grade: "n=0 at adoption (2026-08-16); milo's comment channel is effectively unused — 8 of 9 open issues carry zero comments, zero reactions repo-wide"
updated: 2026-08-16
---

# Comment-protocol — conduct on the issue comment channel

Deliberation about an issue happens as **comments on that issue**. This is the seam's
durable half: `handover-protocol.md` governs what a `d-fb` or `d-sense` *is*, and this
governs how the Operator and milo **talk on the artifact** without either losing track of
whose turn it is. PRs already have their own review channel and are out of scope.

## The premise — one account, so identity is never a discriminator

The Operator and milo post from the **same GitHub account**. Nothing about a comment's or
a reaction's author distinguishes them. Every marker must therefore be carried **in
content**:

- **authorship** → a provenance header;
- **acknowledgement** → a role-disjoint emoji.

A rollup count is role-blind and must never be read as proof of who acted. This premise is
not a design preference; it is the substrate, and every rule below obeys it.

## Sovereignty — why this is milo's document

dyad-leo's `collaboration-conventions.md` §10 states the same conduct for the fleet. This
file is **milo's own**, aligned with §10 so the two surfaces interoperate, and **not
governed by it**. Three consequences, in priority order (Operator-disposed 2026-08-16:
*prioritize sovereignty of data and the boundaries guarding that sovereignty*):

1. **Data sovereignty outranks convention alignment.** The comment channel is a
   **coordination surface**, readable by a sibling dyad. `DYAD.md § Externality`'s
   two-homes rule governs it absolutely: comments here are **PII-clear or withheld**,
   exactly as `handover-protocol.md § d-fb` requires of the issue body. A conduct rule
   imported from any sibling never relaxes this, and where the two would conflict, this
   wins.
2. **milo's lexicon governs inside milo.** Where a fleet term collides with a milo token,
   milo's definition holds here. The live instance: **`d-sense`** is dyad-leo's
   *Operator directive asserting intent*, and milo's *dev-side intake of an existing
   gh-issue* (`handover-protocol.md`). A comment containing `d-sense` in a milo repo means
   **milo's**, and does not acquire dyad-leo's §7 ledger obligation.
3. **Single-homed here, not copied from there.** This states milo's rules in milo's terms.
   It is not a mirror of §10 and will not be kept byte-identical to it; if §10 changes,
   that is an input to a milo disposition, never an automatic amendment.

## The provenance header

Every milo comment opens with, as its **first non-empty line**:

```
**dyad-milo · session:<suffix> — agent**
```

`<suffix>` is the session's branch tail where the branch carries one, else a short stable
session token. It identifies *which* session spoke; it is not a credential.

**A comment without the header reads as Operator-authored.** That is the fail-safe
direction — an unmarked comment stays *in* scope, so the opposite default cannot silently
drop milo's duty to answer. Shipping an unmarked milo comment is a violation of this
protocol, and `skills/comment_classify.py` catches the one shape that proves itself: a
comment carrying the agent attribution footer with no header.

## Comment ≠ signature

A comment never ratifies. `§ Contract`'s **no-self-ratify** is unchanged: the Operator
disposes, and the only mechanical signature is the **PR merge** (`§ Operating-policy`).
An Operator comment carries the same authority as the same words in chat; it is not a
merge, a close, or a ratification.

## The ack markers — role-disjoint by emoji

| mark | meaning | who applies |
|---|---|---|
| 👀 `eyes` | acknowledged; no substantive reply warranted | **milo only** |
| 👍 `+1` | **terminal ack** — exchange closed, nothing further coming | **Operator only** |
| 👎 `-1` | disposition declined; milo must respond | **Operator only** |

**Placement.** A 👍 belongs on **milo's** comment and closes the exchange there — the loop
is *Operator disposes in words → milo acts and reports in words → Operator 👍 on that
report*. A 👍 on the Operator's **own** comment is **not** a terminal ack and closes
nothing: milo has not acted yet, and reading it as closure would drop the duty.

**Decision-bearing exchanges close in words**, never by reaction alone. Reaction-ack is
reserved for the trivial tail.

### The recorded limit — this half is not mechanizable here

Under the one-account premise, **reactions carry no attributable author**. Nothing
prevents milo applying 👍, and no validator can detect that it did. `§ Principles`
disfavours compliance for good reason, and this is a place where a device is unavailable:
the marker convention is **prose, knowingly**, in the same shape ADR-0019 recorded.

What *is* mechanized is the reading, not the writing: `comment_classify.py` flags 👀 on a
milo-authored comment and 👍 on an Operator-authored comment, because those are decidable
from content plus reaction type. The gap is deliberate and named rather than dressed up.

## Sweep scope — whose turn it is

Scope is **derived from the thread**, never stored in a field (craft lesson #16 — nothing
to go stale):

| state | condition |
|---|---|
| `quiet` | no comments |
| `exempt-pre-convention` | every comment predates the cutoff |
| `awaiting-agent` | latest live comment is Operator-authored and un-acked |
| `acknowledged` | latest live comment is Operator-authored and carries 👀 |
| `awaiting-operator` | latest live comment is **milo-authored** |
| `closed` | a 👍 sits on a milo-authored comment |

Two corrections are implemented **pre-emptively**, taken from dyad-leo's own open defect
report against §10 (`dyad-leo#63`, unratified there) rather than waiting to relive them:

1. **Grandfather cutoff (`2026-08-16`).** Comments predating this convention carry no
   header and would otherwise read as Operator-authored-and-unanswered *forever*. They are
   exempt. milo's entire legacy is one comment (issue #28, 2026-08-06), which is genuinely
   Operator-authored — so the correction costs nothing here and prevents the class.
2. **The role rule, derived rather than stored.** §10's classifier *"has no way to say
   'answered-for-my-role'"*; dyad-leo's proposed fix reads an `Awaiting` field. milo's
   issues carry no such field, so the rule is derived structurally instead — **a
   milo-authored latest comment awaits the Operator** and leaves scope. What awaits the
   Operator surfaces to the Operator, never through a milo ack.

## What is deliberately **not** adopted

**The polling sweep.** §10 has an active session poll every ~15 minutes. `DYAD.md §
Operating-policy` holds proactivity `NOT_YET_WORN` — *"concurrency/WIP, tooling,
proactivity materialize **through practice**."* A timed autonomous poll is proactivity
materialized **by import**, which is the one route that line excludes. Deferred until it
is earned in practice, not until a sibling has it.

Consequence, stated plainly: milo answers the channel **when a session is running and the
Operator's turn has passed to it** — at session start, or when the thread is read. With no
session, an item simply waits. **Silence is never agreement**, and no item's state changes
by silence.

## Grade

**n=0 at adoption.** milo's comment channel is effectively unused — 8 of 9 open issues
carry zero comments and the repo carries zero reactions — so every rule here is
unexercised. That is also why adopting now is cheap: there is no backlog to grandfather
and no habit to unlearn. Re-grade when the channel carries its own lived reps.

## Falsifiable claim

Carrying authorship and turn-state **in content** makes the channel readable under a
one-account constraint that defeats every identity-based scheme. *Refuted if:* an unmarked
milo comment ships and is read as the Operator's; a thread is treated as closed on a
reaction the Operator never applied; the derived sweep-scope rule strands a live thread
that genuinely awaited milo; or the header decays into ceremony nobody reads.
