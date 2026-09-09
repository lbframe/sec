---
name: asvs-verify
description: "Evaluate an application against the OWASP ASVS 5.0 at a chosen level (L1/L2/L3), producing an evidence-backed attestation with a PASS/FAIL/N-A/NEEDS-EVIDENCE verdict per requirement, and generate concrete remediations for gaps. Use when an engineer asks to assess, verify, attest, audit, or measure a codebase/app against OWASP ASVS or application security requirements, achieve provable AppSec, or find out what to fix to reach an ASVS level."
---

# ASVS Verify & Attest

Turn "is this app secure?" into a **reproducible, evidence-backed attestation**
against OWASP ASVS 5.0 — and, for every gap, a concrete remediation.

This skill runs against a **target repo/app the engineer names**, not against the
`sec` toolkit repo itself. Never hardcode paths; ask for or infer the target.

## The `asvs` command (prerequisite: `uv`)

The deterministic engine is packaged as a single named command — **`asvs`** — so
you never invoke raw Python or care where the script lives. It needs
[`uv`](https://docs.astral.sh/uv/) on the machine (like spec-kit); if `uv` is
missing, tell the engineer to install it rather than falling back to `python3`.

`asvs` is stdlib-only and its ASVS dataset is bundled, so every command works from
**any** working directory — including inside the engineer's target repo.

**Install it once, at the start of the assessment, then call `asvs` bare.** This
matters because this skill usually runs from *inside the target repo* (cwd = the
app under test), where a relative skill path would not resolve. `$SKILL` below is
the **absolute path to this skill's own directory** — the directory containing this
`SKILL.md` (you know it at runtime; it is *not* the target repo's
`.claude/skills/...`).

```bash
SKILL="<absolute path to this skill directory>"   # the dir holding this SKILL.md
uv tool install --from "$SKILL" asvs-verify        # puts `asvs` on PATH, cwd-independent
asvs stats --level L2                               # now works from any directory
```

Prefer that. If you'd rather not install, every command also runs zero-install as
`uvx --from "$SKILL" asvs <cmd>` (resolves fresh each call). Commands below are
written as bare `asvs …`.

## Core principle: provable, not plausible

An attestation is only worth the evidence behind it. Three rules are absolute:

1. **Scope is derived, never recalled.** The set of applicable requirements comes
   from the `asvs` command reading the authoritative dataset — not from memory.
   ASVS 5.0 has 345 reqs / 17 chapters and a level model that *differs from 4.0.3*
   (see `references/levels.md`). Do not hand-type requirement IDs or text.
2. **Every PASS/FAIL carries evidence.** A `file:line`, a config value, a scan
   output, or a test result. "I read it and it looks fine" is not evidence.
3. **NEEDS-EVIDENCE is a valid, honest answer.** If a requirement needs a runtime
   test you didn't run, mark it NEEDS-EVIDENCE. A truthful "not verified" is worth
   more than a fabricated PASS. `asvs report` treats any remaining
   NEEDS-EVIDENCE as **INCOMPLETE** and refuses to call the run conformant.

## Prefer tools over opinion (the hybrid mechanism)

Many requirements are provable deterministically. `asvs_verify/data/tool-map.json` maps
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
asvs stats    --level L2                      # see the scope
asvs scaffold --level L2 --target "acme-api" --out asvs.json
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
- For N/A, put the scope justification in `evidence` as a nonblank string;
  `notes` or `remediation` alone do not suffice. No remediation is required for N/A.
- When unsure or a runtime test wasn't performed, leave NEEDS-EVIDENCE. Don't guess.

### 4. Roll up & attest
```bash
asvs report --checklist asvs.json
```
This prints coverage/conformance, and **fails the integrity check** if any PASS/FAIL
lacks evidence, any FAIL lacks a remediation, a verdict is invalid, or an N/A
lacks justification in `evidence`. Integrity problems produce INCOMPLETE and exit
code `1`; fix those before publishing. With no integrity problems, exit code `0`
is preserved even for NON-CONFORMANT (documented FAIL) or INCOMPLETE
(NEEDS-EVIDENCE). The code reports document integrity, not security conformance.
Then render the human report from `templates/attestation.md` (save to the target
repo's `docs/security/asvs-attestation-<level>.md`, per that repo's conventions).

### 5. Remediation path
For a repo that isn't yet conformant, group FAILs by chapter and produce a
prioritized remediation plan: what to fix, the ASVS ID it closes, and the mechanism
to prove the fix (re-run the same tool). Map systemic gaps to broader controls in
`../../../standards.md` (e.g. crypto → FIPS 140-3, supply chain → SLSA/SSDF).

## Commands reference (`asvs`)

| Command | Purpose |
|---------|---------|
| `asvs chapters` | List the 17 chapters. |
| `asvs stats --level L2 [--chapter V6,V7]` | Requirement counts in scope. |
| `asvs list --level L1 --chapter V6` | Print applicable requirement text. |
| `asvs scaffold --level L2 --target NAME --out f.json` | Emit the checklist to fill. |
| `asvs report --checklist f.json` | Roll up + integrity-check the filled checklist. |

## Files

- `pyproject.toml` — packages the engine as the `asvs` command (stdlib-only, no deps).
- `asvs_verify/__init__.py` — deterministic requirement/scope/report engine.
- `asvs_verify/data/asvs-5.0.0.json` — authoritative OWASP dataset (source of truth).
- `asvs_verify/data/tool-map.json` — chapter → mechanism → deterministic tools.
- `references/levels.md` — level model & chapter/mechanism table.
- `templates/attestation.md` — the human-readable attestation report.

## Updating the dataset

When OWASP publishes a new version, locate the current version's flattened JSON
export in the OWASP/ASVS repo (the filename embeds the version, so it changes each
release — do not assume the URL below is stable). Replace the bundled file at
`asvs_verify/data/asvs-5.0.0.json` (its single source of truth — the `asvs`
command reads it from there), then verify the level model still keys off a single
`L` field before trusting it:
```bash
# find the current export (version dir + filename both change between releases):
curl -sSL "https://api.github.com/repos/OWASP/ASVS/contents/5.0/docs_en" | grep _en.json
# then fetch that file, e.g. for 5.0.0:
curl -sSL https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.json -o asvs_verify/data/asvs-5.0.0.json
```
