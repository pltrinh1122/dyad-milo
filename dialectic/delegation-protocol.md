---
doc: "dyad-milo — Delegation-protocol (the pgm- sub-agent imperative)"
home: "single-home for the milo-native delegation imperative; handover-protocol + DYAD.md § Lexicon point here; rationale ADR-0011"
grade: "n=1 — first exercised this arc (ADR-0011); milo-native minimal, not leo's 5-facet borrow (Operator disposition)"
updated: 2026-07-26
---

# Delegation-protocol — the `pgm-` sub-agent imperative

How `pgm-<program_id>:` becomes a **running sub-agent under the program's slots**, while **milo-main
retains milo's parent slots**. Extends the spawn pattern milo already runs for the `d-re`
adversarial-validate (ADR-0007: *"milo spawns a sub-agent — a separate context"*); the mechanism that makes
a divergent — even contradictory — `program_value/invariant` safe **without** a new dyad (ADR-0010 § 4).

Deliberately **milo-native and minimal** (Operator disposition) — not leo's five-facet DoD. Three parts, one
resolution rule, two invariants.

## The imperative — Slots · Interaction · Escalate

milo-main hands the spawned sub-agent exactly three things (hermetic — **zero back-channel**; the delegate
sees only what the imperative carries):

1. **Slots (resolved).** The program's four slots — `program`, `program_telos`, `program_value`,
   `program_invariant` — read from `dialectic/design/programs/<program_id>.md`, with **inherit-when-unset
   resolved by milo-main** (§ Resolution). These are the delegate's operating frame; it runs **as** the
   program, not as milo.
2. **Interaction.** The task for this turn — the `d-re` capture or the `riff` method-run to perform, in
   `milo:practice` mode (run the method + capture; **no system/mechanism work** — that never delegates).
3. **Escalate.** The halt-and-surface triggers — the delegate **stops and returns to milo-main** (never
   pushes on) when: a **mechanism need** surfaces (→ milo-main fires `d-fb`); **fail-closed** bites
   (PII uncertainty → withhold; can't verify → flag, never fabricate); or an **instruction contradicts its
   own `program_invariant`** (it holds the invariant, surfaces the conflict — it does not silently comply).

## Resolution — who holds which slots

- **milo-main holds milo's parent slots** (`craft_value` honesty-over-appearance / `craft_invariant`
  compassion-toward-lapse) and **resolves** the program's optional slots before spawning:
  **unset → substitute milo's**; **set → pass the program's own**.
- The **delegate operates only under the resolved slots in its imperative** — it **never reads milo's
  DYAD.md as its own frame**. This is the isolation: a `program_invariant` that contradicts milo's governs
  *inside the delegate's scope only*; milo-main is untouched, because the two never share a context.

## Two invariants

- **`delegation-hermetic`** — the delegate receives its whole frame in the imperative and has **no
  back-channel** to milo-main's context. (Isolation is real only if the delegate can't reach around it.)
- **`delegation-fail-closed`** — on uncertainty the delegate **withholds and surfaces**, never fabricates
  (honesty) and never leaks PII to a public surface (privacy). Inherited from `§ Principles`.

## Land — reuses ADR-0007

A delegated `riff` returns its distilled result to milo-main. A delegated `d-re` **capture lands through the
existing adversarial-validate** (ADR-0007): an independent adversarial sub-agent rubs the record and lands
the survivor to the private store; **no new land mechanism**. no-self-ratify holds — the capturing delegate
is not the lander.

## Grade

n=1 — first exercised this arc (ADR-0011: an `emerging-identity` delegate under set/divergent slots, and a
`reduce-anxiety` delegate under inherited slots). Unexercised as a repeated loop; re-grade when program
delegation carries its own lived reps.
