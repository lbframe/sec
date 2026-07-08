---
name: "ASVS Verify & Attest"
description: "Evaluate an application against the OWASP ASVS 5.0 at a chosen level (L1/L2/L3), producing an evidence-backed attestation with a PASS/FAIL/N-A/NEEDS-EVIDENCE verdict per requirement, and generate concrete remediations for gaps. Use when an engineer asks to assess, verify, attest, audit, or measure a codebase/app against OWASP ASVS or application security requirements, achieve provable AppSec, or find out what to fix to reach an ASVS level."
---

# ASVS Verify & Attest

Turn "is this app secure?" into a **reproducible, evidence-backed attestation**
against OWASP ASVS 5.0 — and, for every gap, a concrete remediation.

This skill runs against a **target repo/app the engineer names**, not against the
`sec` toolkit repo itself. Never hardcode paths; ask for or infer the target.

## Core principle: provable, not plausible

An attestation is only worth the evidence behind it. Three rules are absolute:

1. **Scope is derived, never recalled.** The set of applicable requirements comes
   from `scripts/asvs.py` reading the authoritative dataset — not from memory.
   ASVS 5.0 has 345 reqs / 17 chapters and a level model that *differs from 4.0.3*
   (see `references/levels.md`). Do not hand-type requirement IDs or text.
2. **Every PASS/FAIL carries evidence.** A `file:line`, a config value, a scan
   output, or a test result. "I read it and it looks fine" is not evidence.
3. **NEEDS-EVIDENCE is a valid, honest answer.** If a requirement needs a runtime
   test you didn't run, mark it NEEDS-EVIDENCE. A truthful "not verified" is worth
   more than a fabricated PASS. `scripts/asvs.py report` treats any remaining
   NEEDS-EVIDENCE as **INCOMPLETE** and refuses to call the run conformant.

## Prefer tools over opinion (the hybrid mechanism)

Many requirements are provable deterministically. `references/tool-map.json` maps
each chapter to a mechanism:

- **`tool`** (V3, V12, V13, V15…): run the scanner; its output *is* the evidence.
  e.g. V12 Secure Communication → `testssl.sh`; V15 dependencies → SCA/SBOM;
  V13 Configuration → `checkov`/`prowler`/`trivy`; V3 headers → header scan.
- **`inspection`** (V6, V8, V10, V16…): auth/authz/OAuth/logging logic no scanner
  reaches — reason over the code, cite `file:line`.
- **`hybrid`**: run the tool AND reason about what it can't see (business logic).

Reach for a tool whenever a mapping exists; fall back to inspection only where no
scanner can produce the proof. The full tool catalogue is `../../../types.md`.

## Workflow

### 1. Scope
- Identify the **target** (repo path, app, endpoints) and confirm what's in/out.
- Pick the **level**: default **L2**; L1 for a fast/black-box baseline; L3 only
  when regulated data / money / safety justify it (`references/levels.md`).
- Optionally narrow to chapters (e.g. an auth review → `V6,V7,V8,V9,V10`).

### 2. Generate the checklist (deterministic)
```bash
python3 scripts/asvs.py stats    --level L2                      # see the scope
python3 scripts/asvs.py scaffold --level L2 --target "acme-api" --out asvs.json
```
`asvs.json` has one row per applicable requirement, each pre-seeded with
`verdict: NEEDS-EVIDENCE`, its `mechanism`, and `suggested_tools`.

### 3. Verify each requirement
Work chapter by chapter. For each requirement:
- If mechanism is `tool`/`hybrid`: **run the tool** against the target, capture the
  output, and record it as `evidence`. (Install/invoke per `../../../types.md`.)
- If `inspection`: locate the relevant code/config, decide, and cite `file:line`.
- Set `verdict` to PASS / FAIL / N/A / NEEDS-EVIDENCE. Fill `evidence`. For any
  FAIL, write a concrete `remediation` (generate it now — do not pre-load prose).
- When unsure or a runtime test wasn't performed, leave NEEDS-EVIDENCE. Don't guess.

### 4. Roll up & attest
```bash
python3 scripts/asvs.py report --checklist asvs.json
```
This prints coverage/conformance, and **fails the integrity check** if any PASS/FAIL
lacks evidence or any FAIL lacks a remediation. Fix those before publishing.
Then render the human report from `templates/attestation.md` (save to the target
repo's `docs/security/asvs-attestation-<level>.md`, per that repo's conventions).

### 5. Remediation path
For a repo that isn't yet conformant, group FAILs by chapter and produce a
prioritized remediation plan: what to fix, the ASVS ID it closes, and the mechanism
to prove the fix (re-run the same tool). Map systemic gaps to broader controls in
`../../../standards.md` (e.g. crypto → FIPS 140-3, supply chain → SLSA/SSDF).

## Commands reference (`scripts/asvs.py`)

| Command | Purpose |
|---------|---------|
| `chapters` | List the 17 chapters. |
| `stats --level L2 [--chapter V6,V7]` | Requirement counts in scope. |
| `list --level L1 --chapter V6` | Print applicable requirement text. |
| `scaffold --level L2 --target NAME --out f.json` | Emit the checklist to fill. |
| `report --checklist f.json` | Roll up + integrity-check the filled checklist. |

## Files

- `references/asvs-5.0.0.json` — authoritative OWASP dataset (source of truth).
- `references/levels.md` — level model & chapter/mechanism table.
- `references/tool-map.json` — chapter → mechanism → deterministic tools.
- `templates/attestation.md` — the human-readable attestation report.
- `scripts/asvs.py` — deterministic requirement/scope/report engine.

## Updating the dataset

When OWASP publishes a new version, locate the current version's flattened JSON
export in the OWASP/ASVS repo (the filename embeds the version, so it changes each
release — do not assume the URL below is stable). Drop the file in `references/`,
then verify the level model still keys off a single `L` field before trusting it:
```bash
# find the current export (version dir + filename both change between releases):
curl -sSL "https://api.github.com/repos/OWASP/ASVS/contents/5.0/docs_en" | grep _en.json
# then fetch that file, e.g. for 5.0.0:
curl -sSL https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.json -o references/asvs-5.0.0.json
```
