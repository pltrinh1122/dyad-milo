# ADR-0010 — the `pgm-` program abstraction: a four-slot subclass of the dyad

- **Status:** proposed (2026-07-26) — Operator-authored via a riff-arc (`d-sense #21`); awaiting PR review
- **Drift-dimension:** **coverage** (defines the `program` abstraction the spec left thin) + **constraint**
  (a scope ceiling on `program`) + **goal-adjacent** (redefines what a program *is*). Every slot of this
  model was Operator-dictated on a `milo:dev` thread; milo:dev works the form (no-self-ratify holds).

## Context

gh-issue #19's `program[]` arc and ADR-0004 ("programs[] **sub-class** attachment") left the `program`
abstraction defined only operationally (`id · enrollment · Goal · Method · Telemetry · Adherence`, riding
the parent dyad's value/invariant). gh-issue **#21** then asked the boundary question: *when does a program
graduate to its own **dyad** — when it needs its own `craft_value` + `craft_invariant`?*

The `d-sense #21` intake grounded that a program has no value/invariant slot of its own and rides milo's
(`reduce-anxiety.md:69-70`), and that the discriminator was a faithful transposition of milo's own
register-split rule. But an **Operator riff-arc** then reframed the question rather than answering it: a
program *should* own its value/invariant, a divergent one need not spin out a dyad, and the whole abstraction
is cleanly an **object-style subclass** of the dyad. This ADR codifies that model; #21's original
value/invariant→dyad criterion is **superseded**.

## Decision

### 1. A program is a **four-slot mini-craft** — the dyad's craft block minus identity

| Dyad (`DYAD.md`) | Program |
|---|---|
| `craft` | `program` |
| `craft_telos` | `program_telos` |
| `craft_value` | `program_value` |
| `craft_invariant` | `program_invariant` |
| **Identity** (birth-hash, own agent, own Contract) | *— none —* |

Enrollment, telemetry (`observations[]`, ADR-0004), and adherence (ADR-0003) ride underneath as
**operational** attributes — the program's running machinery, not its definition.

### 2. `pgm-operating-invariant` — minimum two slots at init

A program initializes with a **minimum of two slots: `program` and `program_telos`** (what it is + where
it's going). `program_value` and `program_invariant` are **optional at init**, added as reps harden them
(wu-wei / presence-not-quality, applied to the program's own definition). Enforced mechanically by
`skills/pgm_lint.py` (§ 5).

### 3. Subclass inheritance — three axes

A `pgm-` inherits from the parent dyad (milo) unless it overrides:

- **Slots** — `program_value`/`program_invariant` **unset → inherit** milo's parent slots
  (honesty-over-appearance / compassion-toward-lapse); **set → own** (§ 4).
- **Methods** — `riff`, `d-re`, `d-rub`, … are **inherited from milo unless overridden** (e.g. a program
  may override `riff` with an elicitation-specific method). Method-override is a **behavioral** declaration
  (a prose/frontmatter pointer), **not** a linted slot — lint only if a real override earns the shape
  (ADR-0002 proportionality).
- **Identity** — birth-hash, own agent, own Contract are **not inheritable and not ownable** by a program.
  This is the one dyad-only block; **needing an identity is the program/dyad boundary** — the deferred
  "going solo" promotion.

### 4. Contradiction is allowed, isolated by delegation

A program's `program_value`/`program_invariant` **may contradict** milo's — this is permitted, because
**program execution is scoped and delegated to a sub-agent** running under the *program's* slots, while the
**main agent (milo) retains milo's parent slots**. The contradiction lives in the delegate's scope; milo's
identity is never corrupted. *This delegation is the mechanism that replaces "spin out a dyad"* — a program
never needs its own dyad merely to hold a divergent (even contradictory) value/invariant.

`reduce-anxiety` leaves value/invariant unset → inherits milo (no divergence). `emerging-identity` sets its
own (`being-over-having` / `never-outsource-worth`) → sub-agent-isolated — still a `pgm-`, no dyad.

### 5. Invocation grammar + CI-enforced fields

```
d-start: milo-practice session
  pgm-{program_id}: <arc intent>   # SET program scope → delegate to a program sub-agent
    d-re: <reflection>             # capture → unified store, programs:[program_id]
    riff: <method run>             # the program's method (inherited/overridden)
```

`pgm-{program_id}:` is a **scope-setter** (arc header), not a per-interaction prefix; the `d-re`/`riff`
under it inherit the program scope. This sharpens the `d-re-mode-invariant`: `milo:practice` = **run the
program's method (`riff`) + capture/land (`d-re`)** — still no system/mechanism work (that stays `milo:dev`).

Program **definitions are PII-clear and live in the public repo** (`dialectic/design/programs/*.md`), so
`pgm-fields` lint **here** (no dual-checkout — contrast ADR-0006 for PII records). `skills/pgm_lint.py`
enforces: required `program` + `program_telos`; `program_value`/`program_invariant` optional; `program_id`
↔ filename stem; `enrollment` present/valid; shape-if-present for extras. Fail-closed. Test pair
`tests/test_pgm_lint.py`; CI leg `.github/workflows/pgm-lint.yml` (mirrors `readme-lint.yml`).

## Alternatives rejected

- **Program→dyad on its own value/invariant** (#21's original criterion) — **superseded**: value/invariant
  are now program slots, and divergence is handled by delegation, not promotion. A dyad is reserved for a
  distinct **identity**.
- **Contradiction forbidden / specialize-only** (the `d-sense` proposal) — rejected: the Operator allows
  contradiction, made safe by sub-agent isolation.
- **All four slots required at init** — rejected against `pgm-operating-invariant` (min two; the rest earned).
- **Program execution in the main agent** — rejected: a contradictory program value/invariant would corrupt
  milo's parent slots; execution must be delegated to a scoped sub-agent.
- **Linting method-override behavior** — deferred (behavioral, not slot-shape; ADR-0002).

## Consequences

- `daily-reflection-spec.md §6`, `handover-protocol.md`, and `DYAD.md § Lexicon` gain the model (anchor edit
  lock-step via reviewed PR). `reduce-anxiety.md` conforms (declares the two required slots; value/invariant
  unset = inherit).
- **Retires ADR-0009's cross-dyad case:** every program is a milo `pgm-` in the one unified store → no
  "program owned by another dyad"; the store-side registry simplifies to in-milo; `dyad-pltrinh1122` needn't
  be born. Recorded as a note on ADR-0009.
- **Deferred (honest gaps):** the promotion term/trigger ("going solo"); the sub-agent **delegation
  mechanism** build itself — implementation for a later `milo:dev` arc, where **leo's hermetic 5-facet
  delegation imperative** (`dyad-leo` `delegation-imperative-complete`) is a ready thing to borrow;
  `emerging-identity`'s own disposition (program-with-set-slots vs a future dyad).
- **Grade n=0** — the model is unexercised; no `pgm-` has yet run under a delegated sub-agent.
