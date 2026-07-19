---
doc: "dyad-milo — d-re base-class telemetry schema (at-a-glance)"
home: "canonical rationale in daily-reflection-spec.md §§ 3-6; enforced by skills/dre_lint.py"
updated: 2026-07-19
---

# d-re base-class telemetry schema (at-a-glance)

Canonical home: `daily-reflection-spec.md` §§ 3-6 (rationale) + `skills/dre_lint.py` (executable
enforcement). A record = **YAML frontmatter + free-flowing Markdown body** (ADR-0001); `references[]`
is single-source in the frontmatter.

```yaml
---
record: d-re
created: <ISO-8601 instant with offset>    # absolute; timezone-agnostic storage
practice_day: <YYYY-MM-DD>                  # PT calendar day = adherence bucket
zone: America/Los_Angeles                   # IANA; makes the bucket reproducible + DST-correct
trigger:
  primary: <text>                           # REQUIRED; never empty or "none"
  proximate: <text>                         # optional; the occasion, if distinct
  boundary: <text>                          # optional
  setting: <text>                           # optional
references:                                 # optional; 0..n
  - id: <slug>
    citation: {title, author, date, outlet}
    links: [<url>, ...]                      # >= 1
    essence:
      - {id, facet, partition, text}         # facet open-extensible; partition: trigger-time|confirmed-after (optional)
    provenance: <text>                       # held separate from essence
    fidelity: <text>                         # honesty ledger; fail-closed
programs: []                                # additional programs; BP#0 implicit, never listed
program_telemetry:                          # optional sub-class attachment (§ 6 / ADR-0004)
  <program-id>:                             # key ⊆ programs; never BP#0; block never required
    <program-specific, open-extensible fields>   # e.g. reduce-anxiety → occurrences[]
---
<free-flowing reflection prose — presence-not-quality; length is never gated>
```

**Enforced invariants** (`dre_lint`): `record == d-re`; `practice_day` is the `zone` calendar day of
`created` (DST-correct bucket); filename `YYYY-MM-DD[-NN]` agrees with `practice_day`; `trigger.primary`
present and never "none"; `programs` a list that never lists BP#0; each reference has ≥1 link, each
essence fragment a non-empty `facet` + `text` and a valid `partition` if present; `program_telemetry` (if
present) a mapping whose every key is listed in `programs` and never BP#0, each block a mapping —
**never required, never gated on quantity** (presence-not-quality extends to the sub-class); registered
programs (`reduce-anxiety`) get a proportionate field-shape check, fields open-extensible; the body is
non-empty (its length is never checked). Filenames: `reflections/YYYY-MM-DD-NN.md`.
