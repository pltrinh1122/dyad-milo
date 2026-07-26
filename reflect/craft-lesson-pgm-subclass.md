# Craft lesson — the program as a subclass of the dyad (2026-07-26, PII-clear)

A reusable craft pattern that fell out of the `d-sense #21` riff-arc (codified in ADR-0010). Deposited
standalone (Operator disposition) because the shape generalizes beyond the one arc.

## The lesson

**A program is a subclass of the dyad — inherit-by-default, override-on-demand, minus identity.** When we
asked "when does a program need to become its own *dyad*?", the honest answer was *almost never* — because
the thing that felt like it forced a new dyad (a program wanting its **own** value/invariant) is better
modelled as **subclassing**:

- **Slots** — a program owns `program_value`/`program_invariant`; **unset → inherit** the parent's, **set →
  own**.
- **Methods** (`riff`, `d-re`, …) — **inherited unless overridden**.
- **Identity** (birth-hash, own agent, own Contract) — the **one non-inheritable block**. Needing it is the
  only real program→dyad boundary.

## The load-bearing move — contradiction-by-delegation

The reason a program can hold a value/invariant that **contradicts** the parent's *without* corrupting the
parent is that **execution is delegated to a scoped sub-agent** running under the program's slots, while the
**main agent retains the parent's**. Isolation, not promotion, is what makes divergence safe. This is why
"spin out a new dyad" was the wrong mechanism: it solved by *duplication* a problem that *scoping* already
solves. (When the delegation build comes, `dyad-leo`'s hermetic 5-facet delegation imperative is the ready
borrow.)

## Two discriminators that generalized

The arc reused, on a new boundary, discriminators milo had already earned:

1. **Register-split** (`dip-convergence` §123–145) — *split iff the two jobs can't both be served faithfully
   in one frame.* Applied to programs: serve a program under a contradicting parent value and it distorts.
2. **Scaffold-removal ("training wheels")** — the parent's value/invariant are training wheels; a program
   keeps them (inherit) until its own foundation can bear weight. The *same shape* underlies **graduation**
   (the Operator's wheels come off the whole dyad) and the deferred program **promotion** — same move, two
   subjects. Naming had to mark the subject (why "wheels-off" alone collides with graduation).

**Portable takeaway:** when a sub-unit seems to demand its own top-level home, first ask whether *subclassing
+ scoped delegation* gives it everything except **identity** — and whether identity is actually what it
needs. Usually it isn't, and a new top-level home is duplication the scope already covers.
