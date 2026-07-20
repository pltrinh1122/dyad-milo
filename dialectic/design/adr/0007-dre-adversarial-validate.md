# ADR-0007 — d-re closes with an adversarial-validate (`d-rub-with-land`)

- **Status:** proposed (2026-07-20) — Operator-directed (`d-re-process-constraints`); **awaiting PR
  review. This meta-change is human-disposed at merge — it must not self-ratify.**
- **Drift-dimension:** constraint — shifts how `main` advances on `d-re` records from *per-instance
  Operator merge* to *an independent adversarial-agent gate*. Touches the worn-in **no-self-ratify** /
  "Operator disposes at merge" invariant (§ 12, DYAD.md § Operating-policy). Recorded here because that is
  exactly the escalation artifact § 13 requires.

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

**Scope: client-data `d-re` records only.** Anchors (`DYAD.md`/`CLAUDE.md`) are out of scope — they keep
the reviewed-PR + `anchor_guard` path. Discipline/mechanism changes (like this ADR) are **not** `d-re`
records and keep the human-disposed reviewed-PR path.

## Consequences

- **Presence-not-quality is preserved.** The adversary validates **fidelity + schema + honesty**, never
  reflection *quality / depth / length*. It is Agent-side rigor; the Operator still just writes one line.
  Wu-wei toward the Operator is unchanged (no new Operator burden, no quality gate that could feed the
  perfectionism the practice treats).
- **The load-bearing shift (surfaced, not buried):** `main` now advances on `d-re` records **without a
  per-instance human merge**. Mitigations that keep the spine intact: (a) dyad-rt **pre-push** still refuses
  any direct/force push to `main` — advance only via forge-merged PR; (b) the disposer is an *independent*
  adversary, not the generator; (c) scope is client data only, never anchors; (d) fail-closed on any break.
  Residual: this is a real move from *human* to *independent-agent* disposition on `main`. The Operator
  disposes that policy **once, here** (standing) — and disposes **this ADR** at merge (human-gated).
- **Proportionality (ADR-0002).** A per-`d-re` sub-agent is heavier than a bare `dre_lint`. Justified: the
  land is the irreversible step (`main`); guarding it proportionately is worth a sub-agent. If it proves
  too heavy in practice, the falsifier below fires and the fallback is adversarial-validate on land only.
- **Enforcement model (honest).** The adversarial-validate is a **runtime discipline** (spawn + rub +
  land), not a static artifact; `dre_lint` continues to own the static-shape half by execution *inside*
  the rub. No new static linter is invented where there is nothing static to lint (anti-over-guard).

## Falsifiable claim

The adversarial-validate catches capture / honesty defects a plain `dre_lint` misses, **and** its
autonomous land preserves no-self-ratify. *Refuted if:* it **rubber-stamps** (never breaks a genuinely
broken record), or **over-breaks** (blocks clean records / bends into a quality gate), or an autonomous
land ever advances `main` on a defect a human reviewer would have caught. Held as a durative rub in
`reflect/dip-convergence.md` until milo's own reps grade it (n=0 at adoption).
