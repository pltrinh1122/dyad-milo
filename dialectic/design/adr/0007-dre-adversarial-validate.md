# ADR-0007 — d-re closes with an adversarial-validate (`d-rub-with-land`)

- **Status:** proposed (2026-07-20) — Operator-directed (`d-re-process-constraints`); **awaiting PR
  review. This meta-change is human-disposed at merge — it must not self-ratify.**
- **Drift-dimension:** constraint — changes how `main` advances on `d-re` records: the adversarial-validate
  lands autonomously, and **HITL relocates from a pre-land PR-gate to a post-land validation on `main`** —
  the Operator reviews the *landed outcome*, not the PR. HITL is **not removed, it moves downstream**.
  Touches the worn-in **no-self-ratify** / "Operator disposes at merge" invariant (§ 12, DYAD.md
  § Operating-policy), so it is recorded as the escalation artifact § 13 requires. **Meta/instance split:**
  this relocation is for *record entries* (cheap to undo); discipline/anchor changes keep the pre-merge
  reviewed-PR gate.

## Context

Through the first reps the Validate-family (`d-rub`) and the land-to-`main` step were run **manually**,
one token at a time (see `2026-07-20` reps: `d-land`, then `d-rub` with "survivor lands on 'main'"). The
Operator directs that this close-out stop being manual: **every `d-re` should end with an
adversarial-validate** — an independent adversarial sub-agent executing `d-rub-with-land` on the
just-captured record.

The move `d-rub-with-land` was already lived manually; this ADR names it and makes it the standing final
step of the `d-re` discipline.

## Decision

`d-re` gains a **fourth, final acceptance step** (after persist-verbatim → materialize-references →
confirm-day/adherence): **adversarial-validate**.

1. **Independent adversary.** milo spawns an **adversarial sub-agent** — a *separate context* from the one
   that captured the record. This is the mechanism that keeps an autonomous land consistent with
   **no-self-ratify**: the disposer is not the generator.
2. **`d-rub` — bounded, adversarial.** The sub-agent is prompted to **break** the just-captured record
   (rub-protocol § "d-rub-with-land"), bounded to that record (bounded-target guard). It attacks, by
   execution:
   - **capture fidelity** — the body is verbatim what the Operator wrote (no silent edits);
   - **schema** — `dre_lint` PASS;
   - **bucket** — `practice_day` = the `zone` calendar day of `created`; filename agrees;
   - **honesty** — no fabricated telemetry; every `observations[]` datum traces to what the Operator said;
     each observation's `programs ⊆` the record's `programs`;
   - **durability precondition** — is it on `main` yet, or only on the branch.
3. **`with-land` — fail-closed.**
   - **Survives** (no real break) → the sub-agent **lands the survivor to `main`** via a forge-merged PR.
   - **Breaks** (a real defect) → **does NOT land**; surfaces the specific finding to the Operator; the
     record holds on the branch until corrected. A break is a **capture defect to fix**, never a
     failure-marker on the Operator (`craft_invariant`; compassion-toward-lapse).
4. **HITL — validate the outcome on `main`, not gate the PR.** The Operator still validates every landed
   record — but **after** the land, reviewing the outcome **on `main`**, not as a blocking pre-merge PR
   gate. This is proportionate (ADR-0002): a `d-re` record is **cheap to undo** — a `git revert` of one
   file — so a hard pre-land human gate buys little and taxes the cadence. The **pre-land** control is the
   adversarial sub-agent (fail-closed); the **post-land** control is Operator review + cheap revert. That
   post-land validation is itself a **candidate for later mechanization** (Operator: "eventually
   mechanized") — the human step is a placeholder for a future automated outcome-check, not a permanent
   gate.

**Scope: client-data `d-re` records only.** Anchors (`DYAD.md`/`CLAUDE.md`) are out of scope — they keep
the reviewed-PR + `anchor_guard` path. Discipline/mechanism changes (like this ADR) are **not** `d-re`
records and keep the human-disposed reviewed-PR path.

## Consequences

- **Presence-not-quality is preserved.** The adversary validates **fidelity + schema + honesty**, never
  reflection *quality / depth / length*. It is Agent-side rigor; the Operator still just writes one line.
  Wu-wei toward the Operator is unchanged (no new Operator burden, no quality gate that could feed the
  perfectionism the practice treats).
- **The load-bearing shift (surfaced, not buried):** `main` now advances on `d-re` records **without a
  per-instance human *merge*** — but **not without human validation**: HITL relocates to a **post-land
  review of the outcome on `main`** (decision 4). Mitigations that keep the spine intact: (a) dyad-rt
  **pre-push** still refuses any direct/force push to `main` — advance only via forge-merged PR; (b) the
  disposer is an *independent* adversary, not the generator; (c) scope is client data only, never anchors;
  (d) fail-closed on any break; (e) **the change is cheap to undo** — Operator review + `git revert` is a
  low-cost correction path. Residual: a defect can briefly live on `main` between land and review. Accepted
  **because the undo cost is low** (a record entry, not a schema/mechanism change). The Operator disposes
  this policy **once, here** (standing) — and disposes **this ADR** at merge (human-gated).
- **Proportionality (ADR-0002) — corrected.** An earlier draft called the land "the irreversible step";
  it is not — a `d-re` record land is **cheaply reversible** (revert one file). That is precisely why the
  gate need not block at the PR: the proportionate posture is a **light pre-land adversarial guard** (the
  sub-agent, fail-closed on honesty/fidelity) **plus post-land review**, not a heavy human pre-merge gate.
  The sub-agent earns its cost as the honesty/fidelity check, *not* as protection against an irreversible
  step. If it proves too heavy in practice, the falsifier below fires and the fallback is
  adversarial-validate on land only.
- **Enforcement model (honest).** The adversarial-validate is a **runtime discipline** (spawn + rub +
  land), not a static artifact; `dre_lint` continues to own the static-shape half by execution *inside*
  the rub. No new static linter is invented where there is nothing static to lint (anti-over-guard).

## Falsifiable claim

The adversarial-validate catches capture / honesty defects a plain `dre_lint` misses, **and** its
autonomous land — guarded by an independent adversary, bounded by cheap reversibility and a post-land
Operator review — preserves no-self-ratify. *Refuted if:* it **rubber-stamps** (never breaks a genuinely
broken record), or **over-breaks** (blocks clean records / bends into a quality gate), or a defect that a
human would have caught **survives past the post-land review** (not merely lands briefly — the post-land
gate is the backstop), or the undo of a landed defect proves **not** cheap after all (revert is contested
/ entangled), falsifying the proportionality premise. Held as a durative rub in
`reflect/dip-convergence.md` until milo's own reps grade it (n=0 at adoption).

## Addendum (2026-07-22) — three-layer capture model + no-self-lint (via #17 · d-fb → d-sense)

Surfaced from a `milo:practice` rep (gh-issue #17, `d-fb`) and Operator-disposed on `d-sense` intake:
this ADR's three rub checks are **assigned per capture layer**, making explicit what the close-out already
implied. (Model's home: `dialectic/re-protocol.md` § Capture model.)

- **fidelity ⟶ the body (Operator notes) — *verbatim*.** milo persists the reflection prose literally;
  generated phrasing leaking into the body is a fidelity break (e.g. the 07-22 "anxiety-themed" gloss).
- **honesty ⟶ classification/metadata — *generated*.** `trigger` / `observations` / `programs` / essence
  are milo's interpretive generation, bound by trace-to-source (no fabrication), **not** verbatim.
- **schema ⟶ data structure — *mechanical*.** The envelope / serialization / bucket is produced
  mechanically for consistency; `dre_lint` (run inside the rub) owns it.

**No capture-time self-lint (non-goal).** Capture is **un-gated**; validation gates the **land**. A
pre-commit self-lint is deliberately **not** reinstated because it is *redundant* (the adversary re-lints
before land) and *taxes the cadence* (presence-not-quality). The rationale is **redundancy + cadence — not
independence**: a self-lint is generator-side hygiene, not disposition, so it would not blur the
disposer≠generator independence this ADR relies on. (An earlier framing that called it an independence
risk was withdrawn on `d-sense` as overstated.)

**Honest n=1 caveats (folded from #17).** Mechanical generation is **not** clean-by-construction — it can
introduce interpretive drift into the body; the fidelity rung is the catch, and "no phrasing beyond what
the Operator stated" is the explicit body-fidelity check. "Reliable capture" is **n=1**. The safety
guarantee is *no invalid record reaches `main`* (land-gated), **not** *every record valid at the instant of
capture*.
