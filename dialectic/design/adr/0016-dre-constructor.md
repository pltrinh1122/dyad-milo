# ADR-0016 — a constructor for `d-re` records (construction over validation)

- **Status:** proposed (2026-08-07) — Operator-disposed (`d-sense`, two-PR split); awaiting PR review
- **Drift-dimension:** coverage — new tooling on the capture path; no invariant moves. ADR-0001's
  representation is unchanged, ADR-0007's un-gated-capture non-goal is respected, and `dre_lint`
  keeps its role.
- **Origin:** Operator riff (2026-08-07) → `d-sense`. Covers the **constructor only**; the modifier
  is deferred to its own PR by Operator disposition.

## Context

Records are hand-serialized YAML. Issue #26 was the consequence: an unquoted plain scalar
containing ` #` silently loses its tail, and **8 records landed corrupted** having passed lint.
ADR-0012 closed that by gating the raw source.

The riff that preceded this ADR found something the gate does not say about itself: **ADR-0012
exists only because records pass through hand-written YAML text.** The defect is an artifact of
*how records are produced*, not of the schema. A serializer cannot emit it — verified by
execution, PyYAML quotes the value automatically:

```
proximate: 'continuing the identity thread (2026-08-05 entries #1-#4).'
```

## Decision

**A constructor builds the record structurally and serializes once** (`skills/dre_create.py`).
Values are parameters; they never pass through hand-written YAML.

Five of `dre_lint`'s ten checks stop being failable for constructed records — not removed,
**unfailable**:

| check | why it cannot fail |
|---|---|
| 1 `record: d-re` · 2 date/zone/offset types | construction |
| 3 `practice_day` = `zone` day of `created` · 4 filename agreement | **computed**, never supplied |
| 10 capture-fidelity (` #` truncation) | nothing is hand-serialized |

### What this deliberately does **not** change

- **`dre_lint` stays, unchanged and independent.** The constructor is generator-side; the linter
  is validator-side and the adversary's check. Retiring it because the constructor is correct
  would collapse **Generate + Validate** — the one thing the Contract forbids. Records are also
  still **hand-edited** after creation (the eight #26 repairs were edits), so the parse path never
  goes away.
- **No capture-time self-lint.** ADR-0007 makes this an explicit non-goal: capture is un-gated,
  validation gates the *land*, and the adversarial-validate re-lints before anything reaches
  `main`. The constructor's refusals are **parameter requirements** — you cannot build a record
  without a trigger — not a validation pass.
- **The representation (ADR-0001) is untouched.** Still YAML frontmatter + free-flowing Markdown
  body, still files in git. What changes is that records are *constructed* rather than *authored*.
- **No ADR-0013 stamp.** The constructor makes no gate claim, so it falls outside that ADR's
  scope for the same reason `dre_adherence` does: stamps attest gates, not generators.

### Body handling — the verbatim layer

The body is written **literally**: never parsed, reflowed, or re-serialized. A literal `---`
inside the Operator's prose survives, and so does every space and blank line. That is the
three-layer capture model's fidelity rule (`re-protocol.md` § Capture model) enforced by
construction rather than by care.

## Deferred to the modifier PR — with the evidence that forces the choice

The update path is **not** in this ADR. Grounding found a direct conflict with the stated goal of
"git persistence and change tracking": a naive parse→modify→dump of **one field** rewrote
**27 of 16 frontmatter lines** — flow mappings expanded, block scalars requoted, the ISO-8601 `T`
separator dropped from `created`.

Two things were checked rather than assumed, and both came back reassuring: **no value changed**
(parsed mappings equal, block scalar round-trips identically), and the rewritten record **still
passed the canonical linter**. So the naive modifier is *safe* but *illegible* — and illegible is
disqualifying here, because the review path that gates every land runs on the diff. It would also
make the #32 class harder to catch: a silently normalized possessive hides inside a wall of
reformatting.

**Agent lean for that PR:** the **surgical text edit** — locate the target scalar by source marks
(the `yaml.compose` machinery ADR-0012 already uses) and replace only that span. It is the only
shape that leaves formatting untouched, and the machinery is already in the repo. `ruamel.yaml`
would be cheaper but adds the first dependency beyond `pyyaml`, which ADR-0006's
self-contained-invocation property leans on; one-time canonicalization is cheapest but rewrites 25
existing client records and re-opens ADR-0001. Not disposed here.

## Consequences

- **A defect class is retired rather than gated** — for records that come through this path.
  ADR-0012 stays load-bearing for every other path, which is why it is not superseded.
- **`created` is emitted as an ISO-8601 string, not a YAML timestamp.** PyYAML re-emits a datetime
  as `YYYY-MM-DD HH:MM:SS±HH:MM`, which parses and lints but no longer matches the form
  `dre-schema.md` documents. Quoting it keeps text and schema agreeing.
- **Key order is fixed to the schema's** — stable order is what keeps a record's diff readable,
  and the whole review path runs on diffs.
- **Machine-facing interface.** Observations and references are passed as JSON, which is friction
  to type and unambiguous to generate. milo invokes this, not the Operator; the Operator's
  interface remains `d-re:` in conversation, and `craft_telos` (adherence) is unaffected.
- **Test pair** (spec § 13, test-then-code): 24 cases, red before the code existed — including a
  parametrized #26 regression over five `#`-bearing values, DST-correct bucket computation across
  the UTC boundary, filename sequencing, and verbatim-body preservation of a literal `---`. The
  integration proof is that constructed records are run through the **canonical `dre_lint`**.
