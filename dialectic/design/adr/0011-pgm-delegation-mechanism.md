# ADR-0011 — the `pgm-` sub-agent delegation mechanism

- **Status:** proposed (2026-07-26)
- **Urgency:** medium — coverage; builds the mechanism ADR-0010 deferred
- **Drift-dimension:** **coverage** — builds the mechanism ADR-0010 § 4 deferred (program execution
  delegated to a scoped sub-agent). No anchor change (`§ Lexicon` already carries "executes delegated to a
  scoped sub-agent"; wu-wei).

## Context

ADR-0010 made a program a **subclass of the dyad** whose `program_value`/`program_invariant` may **contradict**
milo's — safe *only if* execution is **delegated to a scoped sub-agent** running under the program's slots
while milo-main retains the parent's. That delegation was named and deferred. This ADR builds it.

**Grounded (not greenfield):** milo already spawns separate-context sub-agents — ADR-0007's
adversarial-validate (*"milo spawns an adversarial sub-agent — a separate context"*), prompt-driven, no
`.claude/agents/` files. The `pgm-` mechanism **extends that pattern** to program execution.

## Decision

### 1. Substrate — prompt-driven spawn (Operator-disposed)

milo-main spawns a separate-context sub-agent via a generic `pgm-` imperative **filled from the program def**
(`dialectic/design/programs/<program_id>.md`) — single-sourcing the slots, no per-program agent files.
(`.claude/agents/` named types only if a durable one later earns it — rejected here as proliferation +
slot-drift.)

### 2. Contract — milo-native minimal (Operator-disposed)

Not leo's five-facet DoD (`leo:delegation-imperative-complete`) — a lighter, milo-native imperative:
**Slots · Interaction · Escalate**, hermetic, fail-closed, mode = `milo:practice`. Single-home:
`dialectic/delegation-protocol.md`.

### 3. Isolation — milo-main resolves, delegate runs hermetically

milo-main **holds** milo's parent slots and **resolves** the program's optional slots before spawning
(**unset → milo's; set → the program's own**), passing *resolved* slots into the imperative. The delegate
operates **only** under those slots (zero back-channel) — a contradictory `program_invariant` governs the
delegate's scope alone; milo-main is untouched because the two never share a context.

### 4. Land — reuses ADR-0007

A delegated `riff` returns its distilled result; a delegated `d-re` **capture lands through the existing
adversarial-validate** (ADR-0007). No new land mechanism; no-self-ratify holds (capturer ≠ lander).

## The n=1 exercise (grounded by execution, 2026-07-26)

Two delegates spawned under the mechanism (PII-clear meta-tasks):

- **`emerging-identity` (set/divergent slots)** — operated under `being-over-having` / `never-outsource-worth`,
  **applied** the invariant (declined to route worth through output; used elicitation, conferring no worth),
  and **explicitly confirmed** its frame was the program's slots, "not milo's craft slots." **Isolation of a
  divergent value/invariant held.**
- **`reduce-anxiety` (unset/inherit)** — operated under the resolved-to-milo slots (honesty-over-appearance /
  compassion-toward-lapse), confirmed inherited. **Inherit-resolution held.**

**Honest finding (the exercise earned it):** the inherit-path delegate **read milo's `DYAD.md`** to verify
the inherited wording — so **hermeticity is prompt-enforced, not sandbox-enforced**: a delegate *can* reach
the repo's anchor. Isolation held on the divergent case because the delegate **honored its scope**, not
because a guard blocked it. This mirrors ADR-0008's honest gap (the mode invariant "rests on the mode being
honored, not a guard"). A hard sandbox (a delegate that cannot read milo's anchor as its own frame) is the
**future mechanization** — built only if the boundary is ever crossed in practice (mechanism-over-compliance,
wu-wei). For now the contract carries `delegation-hermetic` as a stated invariant, not a mechanical fence.

## Alternatives rejected

- **leo's five-facet DoD** — considered (a scar-tested borrow); Operator chose milo-native minimal
  (Slots·Interaction·Escalate). leo's deferred coherence/recipient-fit facets stay out.
- **`.claude/agents/` per-program files** — proliferation + slot-drift from the def; rejected for
  prompt-driven spawn.
- **Execution in the main agent** — would corrupt milo's parent slots on a contradictory program; rejected.
- **A hard sandbox now** — form-ahead-of-spine (no boundary crossed yet); deferred to the honest gap above.

## Consequences

- `dialectic/delegation-protocol.md` (new single-home) + `handover-protocol.md` (`pgm-<id>:` → spawn) carry
  the mechanism; `emerging-identity.md` is the first program with **set** slots (exercising isolation).
- **Deferred:** the hard-sandbox mechanization (honest gap); the promotion ("going solo"); a repeated-loop
  grade (n=1 here).
- Grade **n=1** — first exercised this arc; unproven as a repeated loop.

## Agent lean

*Reconstructed 2026-08-08, not contemporaneous — this ADR carried no lean when written. Supplied from the record and its use since, per the backfill disposition; it is not what would have been said at the time.*

**Ratify, with the honest gap stated in the ADR.** Delegation was grounded n=1 by execution. Hermeticity remains **prompt-enforced, not sandbox-enforced** — a delegate can read milo's anchor — and that is named in the ADR rather than papered over. Ratifying accepts a mechanism whose fence is not yet real.
