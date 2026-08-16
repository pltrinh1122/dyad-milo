# ADR-0020 — cross-repo issue hierarchy: native parent-child links, and the two prohibitions they create

- **Status:** proposed (2026-08-16)
- **Urgency:** high — the fleet-adoption imperative is in flight and dyad-leo's desk design creates exactly these links; the permissive default is the one in force until this is disposed
- **Drift-dimension:** **constraint** — it does not merely add a carrier, it binds what may be
  linked across the `§ Externality` two-homes boundary at the issue layer. The invariant is not
  amended; a hole in its enforcement surface is closed before the mechanism that opens it is adopted.

## Context

dyad-leo's `collaboration-conventions.md` §9 places Sub-Matters *"wherever the work naturally
lives — op, fleet, dyad-leo, or a sibling's coordination layer,"* attached as *"native GitHub
sub-issues **where the platform permits the cross-repo link**; otherwise the Matter body's
`Sub-Matters:` ref list plus the `(M<n>)` title mark."*

That hedge had never been exercised: zero cross-repo instances existed, and the fallback branch —
the one every fleet-spanning Sub-Matter would actually use — had never run. Meanwhile three Matter
bodies carried hand-maintained `Sub-Matters:` lists, and M137 carried **both** a ref list and 12
native sub-issues: two representations of one relation, with nothing keeping them in sync. That is
craft lesson #16 (*never persist what the substrate can derive*) with a live instance attached.

**The five repos in scope, and the fact everything below turns on:**

| repo | visibility | owner |
|---|---|---|
| `dyad-leo` | private | `pltrinh1122` (User) |
| `dyad-leo-op` | private | `pltrinh1122` |
| `dyad-leo-fleet` | private | `pltrinh1122` |
| **`dyad-milo`** | **public** | `pltrinh1122` |
| `dyad-pltrinh1122` | private | `pltrinh1122` |

One public repo among five. Every hazard in this ADR sits on that one boundary.

## What execution established

Probed 2026-08-15/16 against live repos; all scratch issues deleted, all repos verified clean.

| # | finding | method |
|---|---|---|
| 1 | Same-owner cross-repo links are **permitted, bidirectionally** | linked `dyad-milo` ↔ `ChatGPT-Sandbox` both ways |
| 2 | Depth caps at **7 edges / 8 nodes**, and the budget is **global to a chain**, not per-repo | alternating two-repo chain refused the 8th edge with the identical error as a single-repo chain |
| 3 | Different-owner links are **refused opaquely** — `"Not Found"`, not an owner error | attempted `dyad-milo` ← `github/docs` |
| 4 | `subIssuesSummary` counts **direct children only**, never the subtree | 8-node chain; root read `total: 1` |
| 5 | A parent reads **100% complete with open descendants**, and GitHub permits closing a parent whose children are open | closed a mid-chain parent; its parent immediately read `percentCompleted: 100` over five open descendants |
| 6 | **Public parent + private child leaks the count** to anonymous callers | unauthenticated `curl` returned `sub_issues_summary: {total: 1}` while the private repo itself returned `404` |
| 7 | Private parent + public child is **clean** — no `parent` key, no title, no repo name | unauthenticated `curl` and anonymous page load |
| 8 | Dependencies work cross-repo, and **leak the same way, with no safe direction** | `issue_dependencies_summary` read `blocked_by: 1` anonymously while `GET …/dependencies/blocked_by` returned `[]` |
| 9 | Issue types are **unavailable** on a User account (`404`), available on orgs including free-plan | `orgs/*/issue-types` across three orgs |

**Finding 6 in full, because it is the reason this ADR is `constraint` and not `coverage`.** GitHub
redacts *identity* but not *quantity*. An anonymous observer of a public issue learns how many
private children it has and what fraction are complete. Counts and completion percentages are the
shape of adherence telemetry — precisely what `§ Externality` unifies into the private store and
what ADR-0019 removed from milo's own default reporting. The web UI shows `Relationships: None yet`
while the REST API reports `total: 1`: the privacy-preserving surface achieves privacy by stating
something false, and the honest surface leaks. For dependencies it is worse — three surfaces
disagree, and the same API contradicts itself.

## Decision

**1 · Native parent-child links become the sole carrier of the Matter → Sub-Matter relation.**
The `Sub-Matters:` body ref-lists are retired; finding 1 removes the fallback's entire domain.
The `(M<n>)` title mark is a **separate axis** — row-level attribution in flat queries — and is out
of scope here; it survives or retires on whether `render_desk.py` resolves parents, which is
dyad-leo's call.

**2 · Depth-1 invariant: Sub-Matters sit exactly one level below their Matter.**
Not because the platform limits it — it allows seven — but because finding 4 means the derived
close-condition is only *true* at depth 1. At depth ≥ 2, finding 5 makes a Matter capable of
reporting 100% complete over an open subtree: not merely incomplete, but wrong in the reassuring
direction. The platform's headroom is to be deliberately unused.

**3 · The public-parent prohibition (asymmetric).**
**A public issue must never be the parent of a private issue.** Concretely: no `dyad-milo` issue may
parent an issue in `dyad-leo`, `dyad-leo-op`, `dyad-leo-fleet`, or `dyad-pltrinh1122`. The reverse —
private parent, public child — is safe (finding 7) and is the direction the fleet already designed
for. The rule is asymmetric, which is exactly why it must be a device rather than a note: asymmetric
rules get remembered backwards.

**4 · No cross-visibility dependencies, in either direction.**
Sub-issues have a safe direction; dependencies do not, because both counts ride on the same issue
(finding 8). A `blocked_by`/`blocking` edge may only join two issues of the same visibility class —
i.e. nothing may cross the `dyad-milo` boundary.

**5 · Any future move to an organization must be atomic across all five repos.**
Finding 9 makes an org attractive: it would buy a first-class `Matter` issue **type**, closing the
one axis where Jira's Epic beats this substrate, at zero cost on a free plan. But finding 3 means a
half-migrated fleet has links refusing with `"Not Found"` and no diagnostic. All five move together
or none do.

## The validator this ships with

`test-then-code` (spec § 13) and the proportionality test (ADR-0002) both bite here: the failure
mode is a privacy leak, and a leak is not cheaply reversible — public data may be cached or indexed
after deletion. That warrants a device, not a prose rule.

**Proposed: `skills/xrepo_lint.py`** — for every open issue in the public repo, assert that (a)
every child resolves to a **public** repository, and (b) every dependency counterpart does too. Both
are single authenticated GraphQL queries; the check is decidable, not heuristic, so it belongs in
CI rather than in front of judgment (the ADR-0014 cut). It runs from the public side and needs no
private access, so it does not cross the two-homes boundary to enforce it.

**Not built here.** This ADR proposes; building is a separate disposed step.

## Boundary — what this ADR can and cannot decide

Four of the five repos are dyad-leo's, and `discipline-fleet-collaboration.md` reserves a sibling's
internal conventions to that sibling (`no-double-docket`; `leo:sibling-repo-sovereignty`). So:

- **Binding on dyad-milo:** decisions 3 and 4 as they touch any `dyad-milo` issue, and the validator.
- **Recommendation to dyad-leo, for its own ratification:** decisions 1, 2, and 5.

dyad-milo cannot legislate the fleet's carrier, and this ADR does not pretend to. What it *can* do
is refuse the leak on its own side, which is sufficient — because `dyad-milo` is the only public
repo of the five, every prohibited edge has one end inside dyad-milo's authority.

## Honest limits

- **Two cases are inferred, not measured.** (a) `public blocking private` — the mirror of finding 8
  — should leak identically since both counts share one summary object, but was not run. (b) The
  User↔Org refusal is predicted from finding 3, not tested; the available org repos are shared or
  community surfaces and a scratch issue there is outward-facing, so the probe was stopped rather
  than decided unilaterally.
- **Internal-visibility repos are unreachable on this account** — `members_can_create_internal_repositories`
  is absent on all three orgs, none of which is enterprise. Whether the count leak behaves
  differently there is unanswerable here, and moot for this fleet.
- **The private store was not touched.** `dyad-milo-pltrinh1122` is deliberately absent from the
  scope table; nothing here was verified against it, and nothing here requires reading it.
- **Local `gh` is 2.45.0**; the `--parent` / `--blocked-by` flags need ≥ 2.94.0. All probes ran
  through `gh api`, which is unaffected. The validator must not assume the CLI flags exist.

## Consequences

- **One relation, one home.** The duplicated `Sub-Matters:` lists stop drifting because they stop
  existing. M137's double representation is the worked example.
- **The close-condition becomes a derived fact rather than an assertion** — but only under decision
  2. Adopting 1 without 2 buys a number that lies.
- **A prohibition arrives with the capability that creates it.** Before finding 1, the leak was
  unreachable; after it, one API call away. This is the narrow window in which the guard is free.
- **`(M<n>)` and the renderer are untouched.** Deliberately: that is a second axis and dyad-leo's.
- **If the org migration is ever taken, this ADR is its precondition**, not a follow-on — the atomicity
  requirement is cheapest to honour before links exist to break.

## Agent lean

**Ratify decisions 3, 4 and the validator; forward 1, 2 and 5 to dyad-leo as a recommendation.**

The part I would weigh before ratifying is not the leak — that is measured, reproducible, and
one-call reachable — but the **coupling**. Decisions 1 and 3 are different animals: 1 is a
convenience improvement, 3 is a privacy constraint. House habit says split conflated axes, and I
considered filing them apart. I kept them together because the coupling *is* the finding: adopting
the carrier is what makes the leak reachable, and a split invites the carrier to land while the
guard waits behind a second disposition. If that reasoning does not hold for the Operator, splitting
is the right correction and decision 3 should go first, alone.

The weaker claim here is decision 2. It is inferred from how `subIssuesSummary` behaves rather than
from any stated GitHub guarantee, so a future platform change to transitive rollup would retire it.
Recorded as contingent on an observed behaviour, not a documented contract.
