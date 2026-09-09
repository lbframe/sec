# OWASP ASVS {{version}} Attestation — {{target}}

- **Standard:** OWASP ASVS {{version}}
- **Target level:** {{level}}  ({{total}} requirements in scope)
- **Scope of assessment:** <components / repos / endpoints assessed; what was OUT of scope>
- **Assessor:** <name / "Claude Code asvs-verify skill, reviewed by <engineer>">
- **Date:** <YYYY-MM-DD>
- **Commit / build under test:** <git sha, image digest>

## Result

| Metric | Value |
|--------|-------|
| Conformance (PASS + N/A) | {{pass_pct}} |
| Coverage (verified, not NEEDS-EVIDENCE) | {{coverage_pct}} |
| PASS / FAIL / N/A / NEEDS-EVIDENCE | {{p}} / {{f}} / {{na}} / {{ne}} |
| **Verdict** | **{{CONFORMANT / NON-CONFORMANT / INCOMPLETE}}** |

> An attestation is **INCOMPLETE** while any requirement is NEEDS-EVIDENCE or any
> integrity problem remains (including an unjustified N/A). Otherwise it is
> **NON-CONFORMANT** if any in-scope requirement is FAIL. Only a run with zero
> NEEDS-EVIDENCE, zero FAIL and no integrity problems is CONFORMANT at the target level.

## Verdict vocabulary

| Verdict | Meaning | Evidence required? |
|---------|---------|--------------------|
| **PASS** | Requirement met, demonstrated by concrete evidence. | **Yes** — `file:line`, config value, scan output, or test result. |
| **FAIL** | Requirement not met. | **Yes** — evidence of the gap **and** a remediation. |
| **N/A** | Requirement does not apply (feature absent). | **Yes** — nonblank justification in Evidence (`evidence` in the JSON checklist) for why it cannot apply. |
| **NEEDS-EVIDENCE** | Not yet verifiable by what was performed (e.g. needs a runtime test not run). | Honest default; never guess a PASS. |

## Findings (per requirement)

<!-- One block per requirement. Generated from `asvs scaffold`, then filled in. -->

### {{id}} — {{chapter_name}} ({{min_level}})
- **Requirement:** {{requirement}}
- **Mechanism:** {{mechanism}} — {{suggested_tools}}
- **Verdict:** {{PASS|FAIL|N/A|NEEDS-EVIDENCE}}
- **Evidence:** {{file:line / config / scan output / test result / scope justification for N/A}}
- **Remediation (if FAIL):** {{concrete fix, with reference to standards.md/types.md where relevant}}
- **Notes:** {{}}

## Open remediations (FAIL summary)

| ID | Requirement | Severity | Owner | Remediation |
|----|-------------|----------|-------|-------------|
| | | | | |

## Not verified (NEEDS-EVIDENCE summary)

| ID | Requirement | What would verify it |
|----|-------------|----------------------|
| | | |
