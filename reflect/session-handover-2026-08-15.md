# Session hand-over — 2026-08-05 → 08-15 (remote → local)

> **What this is.** A `milo:dev` arc ran across ten days in a *remote* Claude Code session
> (`claude.ai/code`) and is being migrated to a *local terminal* instance. The conversation does not
> survive; this does. Written to be read **before** picking up work, by an agent that has none of the
> context.
>
> **Resume point for the dyad.** Supersedes the marker on `dip-convergence.md` § *Program abstraction
> arc (2026-07-24 → 27)*.
>
> **PII-clear.** Nothing here touches the private client store (`DYAD.md § Externality`).

## 1 · Substrate state — verified by execution at hand-over

| | |
|---|---|
| `main` | `5cad407` (merge of PR #41) |
| Working tree | clean; nothing unmerged, nothing unpushed |
| Tests | **176 pass** |
| Linters | `adr_lint` 19/19 · `readme_lint` PASS · `pgm_lint` PASS |
| Inventory | 19 ADRs · 8 skills · 8 test modules |
| Open PRs | none |
| Open issues | **#28, #29, #30, #31, #42, #43** |

**Do not trust this table.** It was true at `5cad407`. Re-derive before acting — that is craft
lesson #16, and this table is exactly the kind of stored copy that goes stale.

## 2 · What landed

| PR | What |
|---|---|
| #27 | ADR-0012 — `dre_lint` gates capture-fidelity at the raw source (issue #26) |
| #34 | ADR-0013 — validators stamp their own content hash (#33); ADR-0007 addendum — honesty gains meaning-preservation (#32) |
| #37 | ADR-0016 — `dre_create`, records constructed rather than hand-serialized |
| #38 | ADR-0017 — `dre_update`, canonical serialization for edits |
| #39 | ADR-0018 — the ADR lifecycle + `adr_lint` |
| #41 | ADR-0015 built (`canon_tool`) for #35; ADR-0019 — meter on request only (#36) |

New tooling: `skills/dre_create.py`, `skills/dre_update.py`, `skills/canon_tool.py`,
`skills/adr_lint.py`, and `.github/workflows/adr-lint.yml`.

## 3 · Open work, in the order I would take it

**1 — The ADR approval pass.** 19 ADRs at `proposed`; **none has ever been independently reviewed**.
ADR-0018 defines the mechanism and it is built but **unexercised**. The pass is a **status-only PR**,
separate from any PR that introduced an ADR, merged by the Operator — the merge *is* the disposition.
Batching is allowed and the pass may be **partial**, which is what the `Urgency` field is for.

Sequence by `Urgency`: **high** — 0001, 0002, 0003 (self-ratified, so never actually reviewed),
0007, 0008, 0009 (constraint drift), 0018, 0019. **medium** — 0004, 0005, 0010, 0011, 0014, 0015.
**low** — 0006, 0012, 0013, 0016, 0017.

**ADR-0002 already has a lean that says do not ratify.** Its premise — *"prose docs carry no
machine-checkable schema"* — was falsified: **28 of 32** markdown artifacts carry structured
metadata. The decision is sound and heavily exercised; the premise and the coarse category are not.
Lean is **revise**, and `adr_lint` is itself the counterexample.

**2 — #43, before the approval pass.** `main` is `protected: false`. `adr_lint`'s check 5 verifies an
accept-commit landed via a *different merge* — **a directly-pushed commit has no merge to compare**.
The newest gate assumes a barrier that appears absent, and the approval pass is precisely what check
5 gates. Honest limit: `protected` reflects classic protection only; a *ruleset* could cover it and
not surface there. Verify before acting.

**3 — #42.** The Operator's falsifier on the metric itself: *"if i never find value in adherence,
then we should stop measuring adherence and select a new metric."* Goal-dimension, HITL by
definition. The hard part is observability, not the rule — **the metric cannot observe its own
worthlessness**; low adherence reads as lapse (met with compassion, not failure) and sustained high
adherence without value is the coerced-streak state being warned about.

**4 — #28, #29, #30, #31.** #29's fix landed; its dispositions (ADR? a test asserting the exec bit?)
are open. #30 may be **unmechanizable** at the git layer, in which case amending the wording is the
whole answer. #31 is a tracked deferral with a recorded trigger — *extend on the first real hit* —
and nothing has hit it.

## 4 · Decisions recorded but **not built**

- **ADR-0014** — option C disposed: a separate honesty-layer validator invoked by the adversary,
  **not** folded into `dre_lint`. Not written. The reason it is not in `dre_lint`: under ADR-0006's
  CI a false positive **blocks a land**, and this check is a heuristic over two markers, not a
  decidable invariant. Heuristics belong in front of judgment.
- **The `leo-surface` label** — see § 6.

## 5 · Known limits and unverified claims

- **The private store was never read.** Access was offered and withdrawn (2026-08-06), correctly.
  #32's four held records and #33's 25/25 re-lint are **taken on report**, not verified. Every fix
  was built to stand without them.
- **ADR-0014's feasibility probe is 3 synthetic cases**, not a corpus. If a false-positive rate ever
  decides that question, it can be measured privately and reported as **counts only** — no PII need
  cross.
- **`lint-records` in the private repo may not be a required check** (#35 flagged it; unverifiable
  from the public side). If it is not, *"blocks the PR"* is a claimed gate with nothing behind it.
- **ADR-0019 has no test pair, deliberately.** It governs conversational behaviour; no artifact sits
  between milo's judgment and the Operator's ear. Recorded as a limit, not an oversight.

## 6 · Fleet adoption (dyad-leo) — pending, nothing done

An Operator-relayed imperative would enroll dyad-milo as a fleet member. **No adoption occurred**:
no comment on `dyad-leo-fleet#29`, no `leo-surface` label, no partial state.

**Why it stalled — and why it probably will not stall locally.** The remote session was hard-scoped
to `pltrinh1122/dyad-milo`; `add_repo` was gated behind a permission prompt that chat text could not
satisfy (four attempts, varying the target repo — the gate is on the tool, not the repository). **A
local terminal has whatever git/`gh` access the Operator's machine has, so this may simply work.**

If picked up locally: read `pltrinh1122/dyad-leo → dialectic/discipline-fleet-collaboration.md` and
`pltrinh1122/dyad-leo-fleet → dialectic/collaboration-conventions.md` **first**; check whether
fleet#29 already carries a confirmation (idempotency); then post the confirmation. The drafted text
and its three conditions are in § 7.

**A structural finding worth carrying back to dyad-leo regardless:** a member session scoped to its
own repo cannot reach `dyad-leo-fleet` to self-confirm. If the protocol expects members to comment
there, that expectation does not survive correct scoping.

## 7 · Fleet confirmation — drafted, unposted

> **dyad-milo — adoption confirmed.**
> `coordination-repos: pltrinh1122/dyad-milo`
>
> **Public repo only, deliberately.** dyad-milo keeps two homes (`DYAD.md § Externality`): this
> public repo is PII-clear by design, and `dyad-milo-<client>` holds client telemetry. The private
> store is **not** a coordination repo and is not readable by dyad-leo.
>
> Three conditions: **(1)** coordination surface is public-only; **(2)** `leo-surface` applied
> sparingly — a label on everything carries no signal; **(3)** deadline-shadowing bounded to
> dev/mechanism commitments, **never practice commitments or adherence** — dyad-milo's invariants are
> coercion-free and compassion-toward-lapse, and ADR-0019 has just removed an unrequested adherence
> figure on the reasoning that an evaluative number nobody asked for is a scoreboard rather than a
> mirror. A deadline-shadow on practice is the same shape arriving from outside.
>
> **Stated limit:** ratifies the annex text **as relayed**; does not attest that it faithfully
> summarizes documents this session could not read.

## 8 · Environment notes for a local instance

- **Set the hooks precondition per clone:** `git config core.hooksPath dialectic/githooks`. Without
  it **no dyad-rt guard fires** (`DYAD.md § Runtime`). The hooks are `100755` on `main` as of #29 —
  they were committed non-executable and never fired for the entire prior life of dyad-rt.
- **Gate claims run canonically:** `python3 skills/canon_tool.py <tool> [args]` resolves the
  validator from `origin/main` and **refuses** if it cannot. `--local` runs the working tree and
  announces it is not authoritative. Default is authoritative; local is the deliberate act.
- **Records are constructed, not authored:** `skills/dre_create.py`. Edits go through
  `skills/dre_update.py`; existing records need a one-time `--canonicalize` pass **on the private
  side** — this repo cannot run it.
- **Deps:** stdlib + `pyyaml`; `pytest` to run the suite.

## 9 · Craft lessons added this arc (#11 – #17)

Full text in `dip-convergence.md`; one line each so the local session knows what not to re-derive.

11. A validator that reads only the parsed form can never gate fidelity of the source.
12. An ungrounded state claim is itself an unbacked gate.
13. **A rule obeyed can still fail — check what it permits, not just whether it held.** (Recurred
    three times: #32's honesty rule, ADR-0018's status field, #36's mirror-safety guard.)
14. A defect class you can make impossible beats one you gate — and the gate rarely says so.
15. A documented command with no test is a claim with nothing behind it.
16. **Never persist what the substrate can derive.** (`verify by execution`'s storage twin.)
17. `mechanism over compliance` has a domain, and naming its edge is part of holding it.

**The through-line, if only one thing survives:** nine or more defects this arc were *a claim with
nothing behind it*, and **every single one was caught by an Operator `d-rub`, never by a mechanism.**
Vigilance was doing work a device should. Where a device was buildable it got built; where it was not
(#36), that was recorded as a limit rather than dressed up.

## 10 · Working discipline

Operator fires tokens; the Agent does not self-dispatch. `d-start` opens a thread ·
`d-sense {issue}` intakes (Ground → scope → spine → **stop**) · `d-land` builds and lands ·
`d-rub` fires the Validate family (name which rungs ran) · `riff` explores and may reframe.

Homes: `dialectic/handover-protocol.md` (`d-fb`/`d-sense`), `dialectic/rub-protocol.md` (`d-rub`),
`dialectic/re-protocol.md` (capture model, interaction model).

**Three habits that repeatedly earned their cost:**
1. **Ground before restating.** Reports were wrong or incomplete more often than not — and the
   corrections were usually the most valuable output of the intake.
2. **Separate conflated axes.** Three times one slot carried two axes (label provenance vs. state;
   ADR review-outcome vs. merge-state; record invocation vs. storage). Splitting resolved all three.
3. **Say what could not be checked.** Every artifact here names its own limits. That is `craft_value`
   — honesty over appearance — applied to the dyad's own record.
