# CLAUDE.md — `sec/` Security Enablement Toolkit

Guidance for Claude Code when working in this repository.

## Mission

Give engineers **skills and tools that make security provable** — not asserted.
Every capability here should turn a vague "is this secure?" into a **reproducible,
evidence-backed answer**: a specific verdict, tied to a named standard, backed by a
`file:line` / config value / scan output / test result, with a concrete remediation
for every gap.

**Priority #1 is OWASP ASVS**: evaluate an application against ASVS, attest each
requirement at a chosen level (L1/L2/L3), and — where it falls short — say exactly
what to fix. See `.claude/skills/asvs-verify/`. Everything else in the roadmap
(`GOALS.md`) serves the same provable-security standard.

## What's here

| Path | What it is |
|------|-----------|
| `standards.md` | Curated catalogue of ~80 security & compliance **standards** (NIST, ISO, PCI, OWASP, SLSA, regional/regulatory…), each with benefit + canonical URL. The "what good looks like" reference. |
| `types.md` | Curated catalogue of security **tooling categories** (SAST, SCA, SBOM, DAST, TLS/header/IaC/container/cloud scanning, threat modeling…), each with a concrete open tool + URL. The "how to get evidence" reference. |
| `.claude/skills/asvs-verify/` | **Flagship skill** — ASVS 5.0 verify & attest engine (see below). |
| `GOALS.md` | The phased roadmap: what to build next and why. |
| `docs/` | Reports, ADRs, design notes (see `prj/CLAUDE.md` file-organization table). |
| `scripts/` | Repo-level helper scripts. |

`standards.md` and `types.md` are the **knowledge base** the skills draw on:
a skill decides *which standard* applies and *which tool* produces the evidence.

## Design philosophy — how to package a capability

The user's default is **a Claude skill**, because most security verification is
judgment-heavy (read code, gather evidence, reason about design, write remediation).
But pick the mechanism that makes the result *most provable*:

| Mechanism | Use when | Example |
|-----------|----------|---------|
| **Claude skill** (default) | Reasoning, evidence-gathering, remediation, orchestrating other tools, honest "can't verify" judgment. | `asvs-verify` |
| **Deterministic binary/CLI** | The check is mechanical and its output *is* the proof. Wrap or invoke it; don't reimplement in prose. | `testssl.sh`, `checkov`, `trivy`, `gitleaks`, the bundled `asvs` command |
| **MCP server** | A stateful/queryable service many sessions reuse (a control database, a live scanner API). | (roadmap) |

The strongest pattern is **hybrid**: a skill orchestrates deterministic tools where
they exist (their output is the evidence) and reserves LLM reasoning for what no
scanner can reach (authz intent, business logic, design flaws). `asvs-verify` is
built this way and is the template for future skills.

### Non-negotiables for any security capability added here
1. **Provable, not plausible** — a verdict without evidence is not a verdict.
2. **Authoritative data, fetched not recalled** — pull requirement/control data
   from the source (e.g. the OWASP repo); never hand-type it from memory.
3. **An honest "not verified" state** — always allow NEEDS-EVIDENCE; a truthful
   "I didn't test this" beats a fabricated pass.
4. **Runs against a target the engineer names** — never hardcode this repo's paths.
5. **A checker, not an enforcer** — these are developer tools that *check* on
   request. Nothing here auto-executes scanners, gates a build, blocks a commit, or
   forces a workflow. Surface what to verify and how; the developer chooses what to
   run and when. Suggest commands, don't run them behind the developer's back.

## The flagship: `asvs-verify`

Located at `.claude/skills/asvs-verify/`. It:
- derives the applicable ASVS 5.0 requirement set for L1/L2/L3 **deterministically**
  from the bundled authoritative dataset (the `asvs` command, `asvs_verify/`);
- assigns each requirement a mechanism (tool / inspection / hybrid) via
  `asvs_verify/data/tool-map.json`, preferring scanner evidence where it exists;
- produces an attestation with a PASS / FAIL / N/A / **NEEDS-EVIDENCE** verdict and
  evidence per requirement, integrity-checked (no evidence-free PASS, no
  remediation-free FAIL);
- generates concrete remediations for gaps.

Quick check that it works (requires [`uv`](https://docs.astral.sh/uv/)):
```bash
uvx --from .claude/skills/asvs-verify asvs stats --level L2
```

It auto-activates when an engineer asks to assess/verify/attest/audit an app
against ASVS or application-security requirements.

## Working conventions
- Keep `standards.md` / `types.md` in their table format; add rows, don't restructure.
- New skills go under `.claude/skills/<name>/` with the same layout as `asvs-verify`
  (SKILL.md + `references/` + `scripts/` + `templates/`). Use the `skill-builder`
  skill for frontmatter.
- Product docs (reports, ADRs) live in `docs/`, not next to tool config — see the
  parent `prj/CLAUDE.md`.
- This repo describes security *for other repos*; skills take the target as input.
