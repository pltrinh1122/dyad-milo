# ADR-0012 — capture-fidelity gated at the raw source (inline-comment truncation)

- **Status:** proposed (2026-08-05) — Operator-disposed scope; awaiting PR review
- **Drift-dimension:** coverage (a validator gap, spec § 12) **with a constraint edge** — the
  fail-closed *honesty* invariant (§ 2). Closes issue #26.

## Context

An unquoted (plain) YAML scalar containing ` #` ends there: YAML reads the rest of the line as a
comment. The parsed value and the text on disk silently diverge —

```
on disk : continuing the identity thread (2026-08-05 entries #1-#4).
parsed  : continuing the identity thread (2026-08-05 entries
```

In the private telemetry store this hit `trigger.proximate` on **8 records**, every one of which
had passed `dre_lint` and landed. The records were repaired client-side (practice scope); this ADR
is about the mechanism that let them through.

**Why the gate missed it.** Every check in `dre_lint` ran **post-parse**, against the value PyYAML
returned. By then the loss is already invisible: a truncated-but-non-empty string satisfies
"non-empty string" exactly as well as a faithful one. The validator could not see what it was
supposed to be validating.

Grounding the report by execution (`d-sense`, 2026-08-05) widened it past the reported symptom:

| form | result | before |
|---|---|---|
| `text (entries #1-#4).` | truncated mid-value | silent PASS |
| `#1-#4 …` (leading `#`) | value consumed entirely → `None` | silent PASS — **reads as "not captured"** |
| `pgm#1-tag` (no preceding space) | intact | correctly untouched |
| quoted, either style | intact | correctly untouched |
| `text\t#1-#4` | ScannerError | already loud |
| a truncated mapping **key** | ScannerError | already loud |

Two findings the issue had not scoped. First, the **leading-`#` form is the same defect and the
more dangerous one**: on any optional field the value becomes `None`, indistinguishable from a
field the Operator never filled in — silence that reads as honest absence. Second, the failure is
**not field-specific**; it reaches `trigger.*`, every `observations[]` free-text field, and
`references[].provenance`/`fidelity`.

## Decision

**Gate the raw source, for any plain scalar, in `dre_lint`.** A tenth check composes the
frontmatter to a node tree carrying source marks (`yaml.compose`, SafeLoader) alongside the
existing `safe_load`, walks it, and fails any **plain-style** scalar whose line-tail begins with
`#`.

- **The rule is "the tail *begins* with `#` after whitespace", not "contains one."** That is
  precisely where YAML terminates a plain scalar, so it catches truncation without
  false-positiving on a later quoted `#` elsewhere in the same flow mapping
  (`{title: X, author: "A #1"}`).
- **Quoted and block scalars are skipped** — they carry a style and lose nothing.
- **Keys are not walked** — a truncated key is a scanner error, so it can never land silently.
  Proportionality (ADR-0002): no check earns its place against a failure mode that is already loud.
- **Additive.** The nine existing checks are untouched; `safe_load` still feeds them.

Weighed and rejected: a **regex over the raw block** (simpler, but needs hand-rolled handling for
quoted values, full-line comments, and block scalars — everything the parser's own marks get
right), and a **round-trip re-serialize/compare** (brittle across formatting-equivalent forms).

## Consequences

- **Inline trailing comments become illegal in `d-re` frontmatter; full-line comments stay legal.**
  This is the honest cost, and it is deliberate: YAML cannot distinguish a truncation from an
  intended trailing comment, so fail-closed picks capture-fidelity over comment ergonomics. For a
  telemetry record — where the frontmatter *is* the captured datum — that is the right trade.
- **The private store's `lint-records` CI (ADR-0006) will apply this on its next run**, since it
  tracks `dyad-milo@main`. Records carrying a legitimate inline comment would newly fail. This is
  the intended drift signal, and the repair is mechanical (quote the value) — but it lands without
  a private-repo change, so it is called out here.
- **The gap is structural to the shared frontmatter idiom, not to `dre_lint`.** `pgm_lint` and
  `readme_lint` use the identical `split_frontmatter` + `safe_load` pattern and have the same blind
  spot. Both public program definitions scan clean today, so the exposure is **latent, not live**;
  the Operator scoped this fix to `dre_lint` (wu-wei — build what a purpose pulls on). Recorded
  here so the latency is tracked rather than forgotten: extend on the first sign of a real hit.
- **Test pair** (spec § 13, test-then-code): 11 cases — both truncation forms across
  `trigger.primary`/`proximate`, `observations[]`, `references[]`, and a sequence entry; plus the
  pass-through cases that keep the gate honest (quoted, `pgm#1-token`, full-line comment, block
  scalar, and every pre-existing fixture unchanged).

## Why this is an ADR and not a bug fix

Craft lesson #10 — *a claimed gate is a liability until a mechanism backs it* — recurring on a new
surface. ADR-0007 lists **capture-fidelity** as a rung `d-rub-with-land` checks; `dre_lint` was
carrying part of that claim and could not honour it, because a post-parse validator is structurally
blind to a parse-time loss. Eight landed records is the proof. The lesson generalizes past this
defect: **a validator that reads only the parsed form can never gate fidelity of the source** —
wherever a claim is about what is *written*, the check has to reach the raw text.
