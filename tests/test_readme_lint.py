"""Deterministic V-pair for skills/readme_lint.py (No-Pure-G invariant).

All fixture READMEs are written to tmp_path — the suite never touches the
real README.md except read-only in the exemplar test, and never writes to
any substrate file (ledger-isolation lesson, DYAD_LEDGER.md REFLECT
2026-07-08 19:05:41 'Start').
"""

from pathlib import Path

from skills.readme_lint import lint

REPO_ROOT = Path(__file__).resolve().parent.parent

VALID_FRONTMATTER = """\
---
doc: "README.md — test manifesto"
kind: derived-view
genre: "falsifiable manifesto"
rule: "cite the source, never this lens"
belief:
  statement: "test belief"
  foundation: belief
  stance: thesis
  status: hypothesis
grade: "survives — intra-dyad"
coverage: "E0 — no outside attack yet."
dogma: false
caution: "status is the headline"
cta: "bring friction"
canonical_home:
  - "ANCHOR.md § Real Heading"
governed_by: [test:no-dogma]
updated: 2026-07-08
---
"""

VALID_BODY = """\

# Test manifesto

**Claim 1 — The belief.** Something falsifiable. → *Break it:* show the counterexample.

**Claim 2 — The invitation.** Tested in one dyad only; come attack it.
"""


def write_fixture(tmp_path, frontmatter=VALID_FRONTMATTER, body=VALID_BODY):
    (tmp_path / "ANCHOR.md").write_text("## Real Heading\ncanonical content\n")
    readme = tmp_path / "README.md"
    readme.write_text(frontmatter + body)
    return readme


def test_exemplar_readme_passes():
    """The repo's own README.md is the exemplar and must conform."""
    assert lint(REPO_ROOT / "README.md") == []


def test_valid_fixture_passes(tmp_path):
    assert lint(write_fixture(tmp_path)) == []


def test_missing_frontmatter_field_fails(tmp_path):
    broken = VALID_FRONTMATTER.replace('coverage: "E0 — no outside attack yet."\n', "")
    errors = lint(write_fixture(tmp_path, frontmatter=broken))
    assert any("coverage" in e for e in errors)


def test_dogma_true_fails(tmp_path):
    broken = VALID_FRONTMATTER.replace("dogma: false", "dogma: true")
    errors = lint(write_fixture(tmp_path, frontmatter=broken))
    assert any("dogma" in e for e in errors)


def test_settled_status_fails(tmp_path):
    broken = VALID_FRONTMATTER.replace("status: hypothesis", "status: settled")
    errors = lint(write_fixture(tmp_path, frontmatter=broken))
    assert any("belief.status" in e for e in errors)


def test_non_derived_view_kind_fails(tmp_path):
    broken = VALID_FRONTMATTER.replace("kind: derived-view", "kind: content-home")
    errors = lint(write_fixture(tmp_path, frontmatter=broken))
    assert any("derived-view" in e for e in errors)


def test_unresolvable_canonical_home_file_fails(tmp_path):
    broken = VALID_FRONTMATTER.replace("ANCHOR.md § Real Heading", "MISSING.md § Real Heading")
    errors = lint(write_fixture(tmp_path, frontmatter=broken))
    assert any("MISSING.md" in e for e in errors)


def test_unresolvable_canonical_home_heading_fails(tmp_path):
    broken = VALID_FRONTMATTER.replace("§ Real Heading", "§ Ghost Heading")
    errors = lint(write_fixture(tmp_path, frontmatter=broken))
    assert any("Ghost Heading" in e for e in errors)


def test_claim_without_falsifier_fails(tmp_path):
    body = VALID_BODY.replace(" → *Break it:* show the counterexample.", "")
    errors = lint(write_fixture(tmp_path, body=body))
    assert any("Claim 1" in e and "falsifier" in e for e in errors)


def test_final_invitation_claim_needs_no_falsifier(tmp_path):
    """The last claim may be the standing invitation (exemplar's Claim 6)."""
    assert lint(write_fixture(tmp_path)) == []


def test_no_claims_fails(tmp_path):
    errors = lint(write_fixture(tmp_path, body="\n# No claims here\n"))
    assert any("no numbered claims" in e for e in errors)


def test_missing_frontmatter_block_fails(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Just a plain readme\n")
    errors = lint(readme)
    assert any("frontmatter" in e for e in errors)
