# ADR-0017 — records are canonically serialized (the modifier)

- **Status:** proposed (2026-08-08)
- **Urgency:** low — coverage, Operator-disposed 2026-08-08; amends ADR-0001's serialization only
- **Drift-dimension:** coverage for the modifier; **amends ADR-0001** — the representation is
  unchanged (YAML frontmatter + verbatim body), but its *serialization* is now normative rather
  than free.
- **Origin:** `d-sense` (2026-08-07) → two-PR split. PR 2 of 2; the constructor is ADR-0016.

## Context

`d-re` records are edited after capture — the eight #26 repairs were edits, and every
adversarial-validate hold is a correction. So the update path matters as much as the create path.

**The naive update defeats the reason it was asked for.** A parse→modify→dump of **one field** on
a hand-formatted record rewrote **27 of 16** frontmatter lines: flow mappings expanded, block
scalars requoted, the ISO-8601 `T` dropped from `created`.

Two things were checked rather than assumed, and both came back reassuring — **no value changed**
(parsed mappings equal, block scalar round-trips identically) and the result **still passed
`dre_lint`**. So the naive modifier is *safe but illegible*, and illegible is disqualifying: the
review path that gates every land (`d-rub-with-land` rubbing the diff, Operator disposing at
merge) reads exactly that diff. It would also make the #32 class harder to catch — a silently
normalized possessive hides inside a wall of reformatting.

## Decision

**Normalize records once; every update thereafter emits a minimal diff.**

Grounded before building on it — the same edit, starting from canonical form:

```
   primary: need to process guilt / seen / hope
-  proximate: a news feed surfaced an article
+  proximate: 'continuing the thread (entries #1-#4).'
```

**2 lines, against 27.** Serialization is idempotent, so the property holds for every subsequent
edit rather than decaying.

Weighed and rejected (Operator-disposed): a **surgical text edit** locating the target scalar by
source marks — precise, but it preserves whatever formatting a record happens to carry, so records
stay permanently heterogeneous and the diff quality depends on how each was originally written.
And **`ruamel.yaml`**, which preserves formatting round-trip but adds the first dependency beyond
`pyyaml`, on which ADR-0006's self-contained-invocation property leans.

### Layer discipline

- **Body — never touched.** Carried across byte-for-byte, never parsed or reflowed. A literal
  `---` inside the Operator's prose survives (`re-protocol.md` § Capture model: body ⟶ verbatim).
- **Envelope — immutable here.** `created`/`zone` move the adherence bucket *and therefore the
  filename*, which is a **re-file, not an update**; `practice_day` is computed; `record` is the
  type. All four are refused.
- **Classification — what the modifier edits.** Exactly the layer an adversarial-validate holds a
  record over (#32).

### Serialization is shared with the constructor, deliberately

`serialize` is imported from `dre_create` rather than reimplemented. If the two disagreed by one
character, **every constructed record would be rewritten wholesale on its first update** — the
precise defect this ADR removes. That coupling is a correctness requirement, distinct from issue
#31's open question about factoring the *linters'* shared helpers. A test asserts the agreement
directly.

### No self-lint

Capture stays un-gated (ADR-0007). `dre_lint` remains the independent validator and the adversary
re-lints before any land; the refusals here are parameter requirements, not a validation pass.

## Consequences

- **Existing records must be canonicalized once** — 25 in the private store. `--canonicalize` is
  value-preserving and **asserts** it (re-parses and compares, refusing fail-closed if anything
  would change). It is idempotent, so a partial run is safe to repeat. **This repo cannot run it**;
  the private side must, and the diff of that one-time pass will be large by design.
- **ADR-0001 is amended, not replaced.** Representation identical; serialization now normative.
  Records become *constructed and canonically maintained* rather than authored.
- **Heterogeneous history.** Records land in canonical form from here; the one-time pass is a
  visible seam in the private repo's history. Accepted — it buys every future diff.

## A defect this PR found next door

`dre_adherence.py` carried the **identical** import bug this module hit: `from skills.… import`
resolves under pytest (repo root on `sys.path`) but **not** when the module is run as a script.

Its own docstring says `Usage: python3 skills/dre_adherence.py RECORDS_DIR`, and
`programs/reduce-anxiety.md` documents that exact command. **It had never worked.** The tool that
measures the craft's own telos metric — adherence, ~90% target — could not be run the way both its
docstring and the program definition instruct.

Fixed here alongside `dre_update` (one line each, same fix), rather than left broken pending its
own issue.

**Why the suite missed it, and what changed:** the tests imported the *module* and never invoked
the *script*, so the documented entry point was untested surface. Both modules now have subprocess
tests exercising the real invocation. This is craft lesson #10 again — *a claimed gate is a
liability until a mechanism backs it* — on a **usage claim** rather than a gate: a documented
command with no test is a claim with nothing behind it.

## Agent lean

**Ratify.** Canonicalization was grounded before it was built (2 changed lines against 27) and is asserted value-preserving rather than assumed. Its cost is real and lands on the Operator: 25 private records need a one-time pass this repo cannot run.
