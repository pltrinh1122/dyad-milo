# dyad-rt — the Dyad Runtime (architecture + provenance)

> The reasoning behind `DYAD.md § Runtime`. Lives here, not in the anchor: the anchor pays a
> per-prompt injection tax, so it holds only the loadable operating model; the why/history
> lives here. Native-adaptation of dyad-touchstone's dyad-rt (which adapted dyad-cairn's),
> 2026-07-09.

## What dyad-rt is

The runtime that takes over when the **native harness permission gate is turned OFF**
(`bin/claude` → `claude --dangerously-skip-permissions`). With the harness no longer prompting,
*something* must still guard the irreversible acts. dyad-rt is that something: the dyad's own,
git-layer enforcement plus discipline.

The launch is a **per-launch Operator election** — `claude` (gate on) vs `bin/claude` (gate
off) — deliberately NOT baked into config (`defaultMode: bypassPermissions`). Path-invoked and
ratified by merge, it is the Operator's opt-in, never an Agent self-grant. That distinction is
the whole reason a wrapper is legitimate where a checked-in config default is not.

## Why this fits dyad-milo's craft

dyad-milo's craft is building the Operator's mental-fitness. dyad-rt is that craft turned on the substrate:
a permission prompt on every reversible write is an **attention tax** — it spends the Operator's
scarce mental-stamina on acts that don't warrant it. dyad-rt removes that tax (gate off) and
re-spends the attention budget only where it belongs: the **irreversible** step, guarded
mechanically. Minimum force by reversibility (wu-wei), applied to the operator's own attention.

## What we ported the *pattern* from — kept, dropped, inverted

Rubbed against dyad-touchstone's actual source (`github.com/pltrinh1122/dyad-touchstone`), not
its description.

**Kept:** the reasoning — a native-gate-off launcher plus a mechanical enforcement layer as the
authority, gating at the irreversible step; and touchstone's own hardest lesson (below).

**Dropped:** cairn/touchstone's Neutral-Quarry ownership ABAC and the "all git/gh through
PATH-shim wrappers" law. That machinery serves *external-code commissions*; dyad-milo's craft is
a mental-fitness *system* with **no external-code quarries**. Porting it verbatim would carry
weight we don't use while barely covering the exposure `bin/claude` actually opens.

**Inverted — the load-bearing divergence (inherited, held).** Enforcement must NOT depend on the
agent *remembering* to route through a wrapper. A rule bypassable by forgetting is shine, not a
guard — and shine-over-streak is the exact fragility dyad-milo's craft exists to distrust. So the
enforcement is a **git-layer hook** (`core.hooksPath=dialectic/githooks`) that fires
**mechanically, regardless of the agent** — including with the native gate off, because git
hooks sit below the harness.

## The guards

- **pre-push** → `dialectic/guards/main_history_guard.py` — refuses a *local* push to
  `refs/heads/main` (direct / force / delete). `main` advances only through a forge-merged PR
  (server-side). The **unbypassable spine**.
- **pre-commit** → `dialectic/guards/anchor_guard.py` — refuses an anchor (`DYAD.md`/`CLAUDE.md`)
  staged on `main` directly (anchors are low-reversibility; they change only through a reviewed
  PR).

Both gate the **irreversible** step, never the reversible write. `--no-verify` is the visible,
deliberate Operator escape (wu-wei: the human is never forced).

## Envelope honesty

The guards are git-layer, so the **non-git destructive class** (`rm -rf <subdir>`,
`git reset --hard`, `git clean -fd`) has **no** hook. In DYAD mode that class rests on an
isolated/disposable run host, not on the runtime. **Precondition:** `core.hooksPath` set per
clone — unset = *no guard fires*. Use `bin/claude` only where that envelope holds.

## The touchstone lesson we did not repeat

Touchstone shipped a `bin/claude` whose safety header asserted a pre-push envelope they had not
built — the doc *shone* (fluent, plausible) and failed the *streak* (no hook actually fired).
So for dyad-milo the guards were **built and verified before** the launcher's claims were
trusted: the pre-push guard was exercised against a simulated `refs/heads/main` payload and
refused it; a feature-branch payload passed. A launcher's *description* of protection is
worthless; only the mechanism that fires is the guard.

## Maturity — candidate, not doctrine

By live→write→share: the runtime is at **live** with **zero real catches** — built and
mechanically verified this session, but it has caught no real mistake in the wild yet. The
*envelope* is a verified fact (pin-able now); the *design claim* — "mechanical-over-compliance is
the right runtime for us" — wants living before it hardens to doctrine.

## Deliberately unbuilt (parked)

- **Context-steering shim** (a `bin/git`-style wrapper that *warns* without being the authority).
  Skipped: bypassable anyway, and the hook spine already covers the irreversible step. Build only
  if a real friction demands it (minimum force).
- **SessionStart/End standup hooks** (touchstone has them): not adopted — dyad-milo has no
  standup/standdown scripts, and asserting hooks that point at non-existent scripts is the same
  copy-artifact failure this design refuses.
