# ADR-0018 — the ADR lifecycle: ratification is independent of landing

- **Status:** proposed (2026-08-08)
- **Urgency:** high — it governs how every other ADR is disposed, and the set is unratified until it lands
- **Drift-dimension:** **constraint** — changes how an ADR becomes binding. It does not weaken
  `no-self-ratify`; it adds a second, independent gate where merge currently serves as both.
- **Origin:** Operator-directed (2026-08-06 → 08), after an audit found the trail misreporting itself.

## Context — what the audit found

Spec § 13 calls the ADR set *"the reviewable trail of the sensitive decisions."* On 2026-08-07 the
trail could not answer the simplest question asked of it — *which of these need my disposition?*

- **9 of 15** ADRs read `awaiting PR review` while living on `main`. `main` advances only through a
  forge-merged PR, so being on `main` *is* proof the review happened. The status was stale in every
  one, some by six weeks.
- **3 more** claimed `accepted` — and grounding found `2769ed8` **created ADRs 0001–0003 and marked
  them accepted in one commit, authored by the Agent.** A self-ratification, sitting in the trail
  for three weeks, in the artifact whose purpose is reviewability.

The three claiming review were the *worst* rows, not the safe ones: a false claim outranks an
absent one, because a reader treats it as settled and skips it.

## Decision

### 1. Never store what the substrate can answer

**Merge state is derivable** — `git cat-file -e origin/main:<path>` settles it, always correctly.
Writing it into the file duplicates a fact git already holds, in a place that drifts; that
duplication *is* what went stale. A third `landed` state would have been a *second* hand-maintained
copy — treating the symptom by extending the cause.

So `Status` carries the **review outcome only**: `proposed` | `accepted` | `rejected`, plus a date.
Two facts, two authorities, composed at read time:

| in force (git) | reviewed (field) | meaning |
|---|---|---|
| no | proposed | draft on a branch |
| **yes** | **proposed** | **in force, awaiting ratification** — the backlog |
| yes | accepted | settled |
| no | accepted | anomaly — reviewed but not landed, or reverted |

`proposed` for a merged-but-unreviewed ADR is exact, not sloppy: the decision is **enacted but not
ratified**. What made that feel wrong was expecting one word to answer two questions.

### 2. Ratification is a separate PR

The `accepted` flag comes only from an **explicit independent review**, landed by its **own later
PR** — never the PR that introduced the ADR. In some cases this duplicates a disposition already
given in conversation. **That duplication is the mechanism, not a side effect.**

- **The Operator's manual merge is the disposition.** The Agent may author the status-flip commit;
  what ratifies is the merge. This is cryptographically real without any key setup: a forge merge
  is committed by GitHub and carries its signature, so it attests *an authenticated GitHub session
  as the Operator clicked merge*. The Agent can forge an author string; it cannot forge that.
- **Batch is allowed** — one review PR may ratify many ADRs.
- **The review PR is status-only.** Bundling substantive change would make one merge conflate
  *landing new work* with *ratifying old work* — the conflation this rule exists to break.

**The honest ceiling:** a merge attests that the merge happened through the Operator's session. It
cannot attest that the ADR was *read*. No mechanism can. The friction is the point; the signature
proves only that the friction was applied.

### 3. Every ADR carries an agent lean, and it must precede the review

The lean is the Agent's Generate; the ratification is the Operator's Validate. **The lean has to
exist before the review, not arrive with it** — otherwise there is no moment where the
recommendation is considered separately from enacting it, which is `2769ed8`'s shape at set scale.

This is why canonicalization lands **first**, as its own PR, and the approval pass follows.

### 4. Urgency is its own field

Urgency and review-status are orthogonal: an urgent decision can be unreviewed, a trivial one
reviewed. `high` | `medium` | `low`, with a reason. It sequences the pass — and it is what lets a
review PR be **partial**, ratifying the urgent rows and leaving the rest.

### 5. Retroactive to all

Every ADR is `proposed` until independently reviewed, **including 0001–0003**, whose `accepted` is
withdrawn here. That is the uncomfortable half of the disposal and the honest one: they are the
only entries provably never reviewed.

## Mechanism — `skills/adr_lint.py`

Enforces the form, and reads the two git-derived facts rather than trusting a stored copy:

1. header carries `Status`, `Urgency`, `Drift-dimension`;
2. `Status` is canonical vocabulary + date, and carries **no merge-state claim**;
3. `Urgency` is a level plus a reason;
4. an `## Agent lean` section exists;
5. `accepted` only — the accept-commit differs from the create-commit **and** landed via a
   different merge. Fail-closed: if history is unavailable it refuses rather than passing.

**Check 5 is `2769ed8` made impossible.** It needs full history, so the ADR-lint workflow sets
`fetch-depth: 0`; the default shallow checkout would leave it unable to verify and, being
fail-closed, unable to pass.

## Consequences

- **The whole set is unratified** — 18 ADRs at `proposed`, and the approval pass is real work
  rather than a formality. That is the intended cost.
- **Leans on 15 ADRs are reconstructed after the fact** and are marked as such in each. A
  reconstructed lean that conveniently matches what was already built is weak evidence; labelling
  it is the minimum honesty. Reconstructing them was Operator-disposed with that risk stated.
- **`rejected` exists but is unexercised.** A review may decline.
- **What the linter cannot check:** whether the ADR was read. See the honest ceiling above.

## Agent lean

**Ratify** — with the bootstrap oddity named rather than hidden: this is the ADR that defines its
own ratification, so the first review pass ratifies the rule by the rule. That is circular in form
but not in substance; the Operator's merge is the disposition either way, and the rule simply makes
the next one legible.

The case for it is grounded rather than theoretical. `adr_lint`'s check 5, run against this repo's
real history, reports:

```
accepted was set by the same commit that created the ADR (2769ed8) —
that is self-ratification, not review
```

That is the defect it was built for, caught in the substrate rather than by anyone remembering to
look — the `mechanism over compliance` test the audit's other findings (#29, #30, #33) all failed.

**The honest counter, which I do not think carries:** this adds ceremony to a solo dyad where the
Operator already disposes everything in conversation. Two things answer it. The dispositions that
mattered here were given *in conversation and then lost* — the trail is what survives the session,
and it was wrong. And the cost is bounded: batching plus the urgency field means the pass is one
partial PR at a time, not eighteen separate acts.

**What I would watch for falsification:** if the review pass becomes a rubber stamp — batches
merged without a row ever being rejected or revised — then the friction is buying appearance rather
than review, and `craft_value` (honesty over appearance) says say so and change it. The `rejected`
outcome existing but never firing is the signal to watch.
