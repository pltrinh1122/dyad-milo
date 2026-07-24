# ADR-0009 — unified-by-client telemetry store (two homes, two axes)

- **Status:** proposed (2026-07-24) — Operator-ratified disposition (gh-issue #19); awaiting PR review
- **Drift-dimension:** **constraint** (amends the documented `§ Externality` *one-private-record-per-client*
  convention) + **coverage** (a cross-dyad enrollment mechanism no doc covers). Surfaced from a
  `milo:practice` thread via `d-fb` (#19), intaked via `d-sense` (Ground + scope + spine), Operator-disposed.
  This ADR is the escalation/codification artifact (spec § 12/13); the anchor amendment lands lock-step in a
  reviewed PR (no-self-ratify).

## Context

`§ Externality` framed the durable record as **two homes**: dyad information (public `dyad-milo`, PII-clear)
vs client information (a **separate private repo, one per client**, `dyad-milo-<client>`). That framing
implicitly bound *one client record* to *the dyad that owns it*.

A `d-re-mode` land surfaced a broader shape (#19): the Operator runs behavioral programs across **several
dyads** (e.g. `reduce-anxiety` here; a forthcoming `emerging-identity` under `dyad-pltrinh1122`), yet a
person has **one** lived telemetry stream. The Operator **ratified** the disposition that
`dyad-milo-<client>` is **THE Operator's unified telemetry store** — recording `d-re` telemetry for **all**
the client's programs, including programs *defined by other dyads*.

**Grounded, not assumed (d-rub · Ground rung, by execution).** The single-store capability already exists —
nothing new must be *built* for it:

- One store, three synthetic records serving `reduce-anxiety` (milo-owned) and `emerging-identity`
  (arbitrary / other-dyad-owned), one record tagged **both** → `dre_adherence` yields base 3/3, per-program
  2/3 and 2/3 from the **same store**; the dual-tagged record counts for **both** with **no double-write**.
- `dre_adherence` / `dre_lint` hardcode **no** program (ADR-0003 program-agnostic; `_matches` filters by
  `programs[]` membership). Full `tests/` suite green.

So the arc is a **codification**, not a build.

## Decision

### 1. Two homes, **two axes**

The public/private split runs along two axes; only one **unifies**:

- **Dyad information** — the fitness system + craft lessons — public `dyad-milo` (`reflect/`), PII-clear. *(unchanged)*
- **Program definition & mechanism** — PII-clear — lives in the **owning dyad's public repo** (`reduce-anxiety`
  here; other dyads' programs in their own repos). **Distributed, never unified.**
- **Client telemetry** — a client's lived `d-re` records + PII — **unifies into a single private per-client
  store** (`dyad-milo-<client>`), recording for **all** the client's programs across every dyad. Only
  *recording* unifies; program *definition / mechanism / access* stays distributed.

milo is the single, **program-agnostic telemetry-capture partner** across that store.

### 2. Repo name — **keep + redefine** (Operator-disposed)

The store keeps the name `dyad-milo-<client>` (`dyad-milo-pltrinh1122`); its **role** is redefined to the
unified store. Birth-hash is identity (`§ Identity`); the name is a mutable label, and a rename is costly
while the milo lineage in the path is load-bearing. The private-repo README role redefinition ("private
client record" → "the Operator's unified telemetry store") lands **in that private repo** — a separate,
parallel land this public PR cannot carry.

### 3. Cross-dyad enrollment — **store-side registry** (Operator-disposed)

A program defined in another dyad's public repo enrolls into the store through a **registry that lives with
the store** (private, PII-clear-metadata). Schema (proposed; the instance lives in the private store):

```yaml
# dyad-milo-<client>/reflections/registry.yaml  (home in the private store)
programs:
  reduce-anxiety:                     # program-id — see id-namespacing below
    def_home: dyad-milo               # owning dyad's public repo (where the definition lives)
    enrollment: 2026-07-19            # per-program enrollment date (the adherence window start)
  emerging-identity:
    def_home: dyad-pltrinh1122
    enrollment: <on-enroll>
```

The registry is the home for the two things a multi-program store needs that no doc covered:

- **Program-id global-uniqueness.** One store keyed by `program-id` across dyads ⇒ ids must be **unique per
  client** or two dyads' `reduce-anxiety` collide in the meter. **Rule:** an enrolled program-id is unique
  within the store; on collision, namespace by owning dyad (`<dyad>/<program>`). The registry is the
  uniqueness ledger.
- **Per-program enrollment dates.** `dre_adherence --enrollment` is a **single** value per invocation;
  enrollment dates currently live in prose in each program def. The registry gives them a machine-readable
  home so the per-program window is not passed by hand.

### 4. Tooling integration — **deferred** (wu-wei; honest gap)

Only one additional program is enrolled today (`reduce-anxiety`); `emerging-identity` is forthcoming. Per
wu-wei (build only what a purpose pulls on — the ADR-0004 precedent), this arc **codifies the convention +
schema** and **defers**: teaching `dre_adherence` to read `enrollment`/uniqueness from the registry, and the
registry linter (the TDD `§ Principles` pairing). Both are built when the **second cross-dyad program
actually enrolls** — the purpose that pulls them. Until then the meter takes `--enrollment` by hand, as it
does now.

## Alternatives rejected

- **Def-side pointer only** (each program def names its `telemetry_home`) — minimal and distributed, but
  leaves per-program enrollment dates and id-uniqueness **unresolved / manual**. Rejected as the sole
  mechanism; folded into the registry as the `def_home` field.
- **Both** (def points to store *and* store mirrors a registry) — more moving parts, two sources that can
  drift; rejected against wu-wei.
- **Rename the repo** — breaks the milo lineage in the path for no capability gain; rejected (keep + redefine).
- **Unify program *definitions/access* too** — collapses the distributed-mechanism axis; a program owned by
  another dyad would lose its home. Rejected: **only telemetry recording unifies.**
- **Build the registry tooling now** — form-ahead-of-spine with one enrolled program; deferred until a
  second dyad's program enrolls.

## Consequences

- `DYAD.md § Externality` gains the **two-axes** framing (reviewed PR, lock-step). `daily-reflection-spec.md`
  § 2 (Two homes) / § 6 pointers track it.
- The registry **schema** is fixed here; the **instance** + the tooling that reads it are deferred (§ 4) —
  an honest, recorded gap, not a silent omission.
- **Not the `§ Pins` generalization.** `§ Pins` defers generalization to *clients beyond the Operator* (many
  **clients**). This arc is **one client, many programs/dyads** — orthogonal; the pin is untouched.
- Rejected alternatives are pinned here against silent re-introduction (id-uniqueness and enrollment-home
  are real requirements the registry owns).
