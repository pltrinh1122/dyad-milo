# ADR-0008 — practice→dev hand-over (d-fb / d-sense) + the d-re-mode-invariant

- **Status:** proposed (2026-07-20) — Operator-declared invariant + `d-arc` goal; awaiting PR review
- **Drift-dimension:** **constraint** — governs *where* craft/mechanism changes may be authored (a mode
  boundary), plus **coverage** (two new interface tokens + a protocol). The invariant is Operator-declared
  (gh-issue #14); this ADR is the codification/escalation artifact (§ 13).

## Context

Issue #14 declared the **`d-re-mode-invariant`**: a `milo:practice` thread does client-record capture +
land only; all craft/mechanism changes defer to a `milo:dev` thread. It flagged PR #13 as the violation
(mechanism work authored on a practice branch). Left open (issue #14 items 1 & 3): codify the invariant,
and standardize the practice→dev **hand-over vehicle**. The Operator's `d-arc` set the goal — make the
hand-over *seamless* — and seeded two tokens: `d-fb` (record feedback) and `d-sense` (intake before
implementation).

## Decision

1. **Codify the `d-re-mode-invariant`** in `DYAD.md § Operating-policy` (worn-in): practice reports, dev
   builds; a mechanism need surfaced in practice is **reported, not implemented in-thread**.
2. **`dialectic/handover-protocol.md`** — single-home for the loop and the two tokens:
   - **`d-fb {feedback}`** (practice-side) → opens a **PII-clear hand-over gh-issue** and stops; no
     in-thread implementation.
   - **`d-sense {gh-issue#}`** (dev-side) → **Grounds + scopes + surfaces the spine, then stops for
     disposition** (spine-before-form; no-self-ratify). Never slides into building.
3. **Vehicle = one gh-issue per feedback item**, from `.github/ISSUE_TEMPLATE/d-fb-handover.md`, labeled
   `milo:dev`. gh-issue #14 is the bootstrap instance.
4. **Thread mode** is set by the opening token (`d-re` → practice; `d-start`/`d-arc` → dev); the token the
   Operator fires (`d-fb` vs `d-sense`) is itself the signal — no separate marker until a guard needs one.

## Alternatives rejected

- **Running-log issue** / **cairn-only note** — neither gives per-item forge tracking, labels, or a clean
  close-on-land; the gh-issue-per-item vehicle does (and matches how #14 already works).
- **`d-sense` auto-implements** low-risk items — collapses spine-before-form and no-self-ratify across the
  seam; rejected. Intake and implementation stay separate, disposed steps.
- **Mandatory branch-name mode marker** — deferred (wu-wei): the token choice already signals mode; add a
  mechanical marker only if a guard must enforce it.

## Consequences

- Closes issue #14 items 1 (codify the invariant) & 3 (standardize the vehicle); item 2 (PR #13) already
  merged.
- The two-homes (PII), no-self-ratify, and spine-before-form principles now extend **across the
  practice/dev seam**, not just within a thread.
- **Not mechanically enforced yet** (honest gap): the invariant rests on the mode being honored, not on a
  guard. A branch-name marker + a dyad-rt check is the future mechanization (mechanism-over-compliance) —
  built only if the boundary is crossed in practice.
