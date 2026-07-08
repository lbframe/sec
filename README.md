# `sec` — Provable Security Toolkit for Engineers

A developer's toolkit for turning *"is this app secure?"* into a **reproducible,
evidence-backed answer** — a verdict per requirement, tied to a named standard,
backed by a `file:line` / config value / scan output / test result, with a concrete
fix for every gap.

> **It's a checker, not an enforcer.** Everything here runs *on request*. Nothing
> auto-executes scanners, gates a build, or blocks a commit. You decide what to
> check and when.

**Priority #1 is OWASP ASVS**: evaluate an app against the Application Security
Verification Standard 5.0, attest each requirement at a level (L1/L2/L3), and — where
it falls short — get told exactly what to fix.

---

## Contents

- [What you get](#what-you-get)
- [Install](#install)
- [Quick start (5 minutes)](#quick-start-5-minutes)
- [Using the ASVS skill](#using-the-asvs-skill)
- [The `asvs.py` engine (CLI reference)](#the-asvspy-engine-cli-reference)
- [Verdicts & what "provable" means](#verdicts--what-provable-means)
- [Evidence tools per chapter](#evidence-tools-per-chapter)
- [The knowledge bases](#the-knowledge-bases)
- [Worked example](#worked-example)
- [FAQ](#faq)

---

## What you get

| Capability | What it is | Where |
|-----------|-----------|-------|
| **`asvs-verify` skill** | Claude Code skill that scopes, verifies, and attests an app against OWASP ASVS 5.0, and writes remediations for gaps. | `.claude/skills/asvs-verify/SKILL.md` |
| **`asvs.py` engine** | Deterministic CLI: derives the applicable requirement set per level, scaffolds an attestation checklist, and integrity-checks the result. Works standalone (no LLM needed). | `.claude/skills/asvs-verify/scripts/asvs.py` |
| **Authoritative ASVS data** | OWASP ASVS 5.0.0 — 345 requirements, 17 chapters — fetched from OWASP, not typed from memory. | `.claude/skills/asvs-verify/references/asvs-5.0.0.json` |
| **Tool map** | Which deterministic scanner produces evidence for each chapter. | `.claude/skills/asvs-verify/references/tool-map.json` |
| **Attestation template** | The human-readable report format. | `.claude/skills/asvs-verify/templates/attestation.md` |
| **`standards.md`** | ~80 security & compliance standards (NIST, ISO, PCI, OWASP, SLSA…) — the "what good looks like" reference. | `standards.md` |
| **`types.md`** | Security tooling categories (SAST, SCA, SBOM, DAST, TLS/IaC/container/cloud scanning…) with a concrete tool for each — the "how to get evidence" reference. | `types.md` |

---

## Install

### Prerequisites
- **Python 3.8+** (tested on 3.13) — for the `asvs.py` engine. No third-party packages.
- **Claude Code** — to use the `asvs-verify` skill conversationally.
- **Optional scanners** — only when you want to *prove* a specific requirement:
  `openssl`, `testssl.sh`, `checkov`, `trivy`, `gitleaks`, an SCA/SBOM tool, etc.
  Install these as you need them; see [`types.md`](types.md) for the catalogue.
  You install nothing up front — the tool tells you what to run when a requirement calls for it.

### Option A — use it inside this repo (zero setup)
The skill lives at `.claude/skills/asvs-verify/`, so it's **auto-discovered whenever
you run Claude Code in this repo**. Just start Claude here and ask to attest an app.

Verify the engine runs:
```bash
python3 .claude/skills/asvs-verify/scripts/asvs.py stats --level L2
```

### Option B — make the skill available in *all* your repos
Copy (or symlink) the skill into your personal skills directory:
```bash
# copy:
cp -r .claude/skills/asvs-verify ~/.claude/skills/asvs-verify

# …or symlink so it tracks this repo (updates when you pull):
ln -s "$(pwd)/.claude/skills/asvs-verify" ~/.claude/skills/asvs-verify
```
Restart Claude Code. The skill now activates in any project when you ask to
assess/verify/attest an app against ASVS. It always runs against the **target repo
you name**, never this one.

> The engine finds its data via paths relative to `asvs.py`, so copying/symlinking
> the whole `asvs-verify/` folder keeps it self-contained.

---

## Quick start (5 minutes)

The flow is **scope → scaffold → verify → report**.

```bash
S=.claude/skills/asvs-verify/scripts/asvs.py

# 1. SCOPE — see what an L2 assessment covers (253 requirements)
python3 $S stats --level L2

# 2. SCAFFOLD — generate a checklist for one area, e.g. authentication
python3 $S scaffold --level L2 --chapter V6,V7,V8 --target "my-api" --out asvs.json

# 3. VERIFY — open asvs.json; for each requirement set a verdict + evidence.
#    (Do this yourself, or let the Claude skill do it — see next section.)

# 4. REPORT — roll up + integrity-check (refuses evidence-free passes)
python3 $S report --checklist asvs.json
```

You'll get a summary like:
```
VERDICT          COUNT  PERCENT
PASS                 3   100.0%
...
RESULT: CONFORMANT @ L2
```

---

## Using the ASVS skill

The skill is the recommended way to *fill in* the checklist — it reads the target
code, runs the right check, gathers evidence, and writes remediations. In Claude Code,
just ask in natural language. Examples:

- *"Attest this repo against OWASP ASVS L2."*
- *"Verify the authentication and session chapters (V6, V7) of ./my-api against ASVS."*
- *"What do I need to fix to reach ASVS L1?"*
- *"Run an ASVS L2 assessment and write the attestation to docs/security/."*

What the skill does, step by step:
1. **Scope** — confirms the target, picks a level (defaults to **L2**), optionally
   narrows to chapters.
2. **Scaffold** — runs `asvs.py scaffold` to get the exact applicable requirements.
3. **Verify each requirement** — for chapters mapped to a **tool**, it tells you the
   command to run (or runs it if you ask) and captures the output as evidence; for
   **inspection** chapters (auth logic, authz, OAuth), it reads the code and cites
   `file:line`. When something needs a runtime test that wasn't done, it marks
   **NEEDS-EVIDENCE** rather than guessing.
4. **Report** — runs `asvs.py report` (integrity-checked) and renders the
   human-readable attestation from the template.
5. **Remediate** — for every FAIL, a concrete fix and the ASVS ID it closes.

> Skills auto-activate from your request — you don't invoke them by name. If it
> doesn't trigger, say "use the asvs-verify skill".

---

## The `asvs.py` engine (CLI reference)

Deterministic, standalone, no LLM required. `python3 asvs.py <command>`.

| Command | Purpose | Example |
|---------|---------|---------|
| `chapters` | List the 17 ASVS chapters. | `asvs.py chapters` |
| `stats` | Requirement counts per chapter for a level. | `asvs.py stats --level L2` |
| `list` | Print the applicable requirement text. | `asvs.py list --level L1 --chapter V6` |
| `scaffold` | Emit a fill-in attestation checklist (JSON). | `asvs.py scaffold --level L2 --target "api" --out c.json` |
| `report` | Roll a filled checklist into a summary + integrity check. | `asvs.py report --checklist c.json` |

Common flags: `--level {L1,L2,L3}` (default L2), `--chapter V6,V7` (comma-separated,
optional), `--target "name"`, `--out file.json`.

**Levels are cumulative** (verified from the data): L1 = 70 reqs · L2 = 253 · L3 = 345.

---

## Verdicts & what "provable" means

Every requirement gets one of four verdicts. This is the heart of "provable, not plausible":

| Verdict | Meaning | Evidence required? |
|---------|---------|--------------------|
| **PASS** | Met, demonstrated by concrete evidence. | **Yes** — `file:line`, config, scan output, or test result. |
| **FAIL** | Not met. | **Yes** — evidence of the gap **and** a remediation. |
| **N/A** | Doesn't apply (feature absent). | **Yes** — why it can't apply. |
| **NEEDS-EVIDENCE** | Not yet verified by what was performed. | The honest default — never guess a PASS. |

`asvs.py report` **enforces** this: it flags any PASS/FAIL missing evidence and any
FAIL missing a remediation, and treats any remaining NEEDS-EVIDENCE as **INCOMPLETE**.
An attestation is only **CONFORMANT** when every in-scope requirement is verified with
zero FAILs.

---

## Evidence tools per chapter

Each chapter has a verification **mechanism** (`references/tool-map.json`):

- **`tool`** — a scanner's output *is* the proof. Run it, paste the output.
  - V3 Web Frontend → HTTP header scan · V12 Secure Communication → `testssl.sh` /
    `openssl` · V13 Configuration → `checkov` / `trivy` / `prowler` ·
    V15 Secure Coding → SCA / SBOM (`cyclonedx`, dependency-check).
- **`inspection`** — logic no scanner reaches; read the code, cite `file:line`.
  - V6 Authentication · V8 Authorization · V10 OAuth/OIDC · V16 Logging.
- **`hybrid`** — run the tool *and* reason about what it can't see (business logic).
  - V1, V2, V4, V5, V7, V9, V11, V14.

You choose to run these; the toolkit never runs them for you. Full catalogue with
install links: [`types.md`](types.md).

---

## The knowledge bases

Two curated references the skill draws on — useful on their own:

- **[`standards.md`](standards.md)** — ~80 security & compliance standards with a
  one-line benefit and canonical URL each. Use it to decide *which bar* applies
  (e.g. crypto → FIPS 140-3, supply chain → SLSA/SSDF, cloud config → CIS Benchmarks).
- **[`types.md`](types.md)** — security tooling categories (source, dependency,
  supply-chain, build, container, IaC, runtime, network, cloud, compliance, manual)
  with a concrete tool + link for each. Use it to decide *which tool* produces evidence.

---

## Worked example

A real, reproducible attestation lives at
[`docs/security/example-asvs-attestation-v12-L1.md`](docs/security/example-asvs-attestation-v12-L1.md)
— ASVS **V12 Secure Communication** at L1 against a public endpoint, with genuine
`openssl`/`curl` evidence, rolling up to **CONFORMANT @ L1**. It shows the full loop
end to end and doubles as a template for your own reports.

---

## FAQ

**Does this run scanners or block my build automatically?**
No. It's a checker you invoke deliberately. It suggests what to run; you run it. It
never gates commits or CI.

**Which ASVS version?** 5.0.0 (current). The data is fetched from the OWASP repo. To
update when OWASP publishes a new version, see the "Updating the dataset" section in
`.claude/skills/asvs-verify/SKILL.md`.

**Do I need all those scanners installed?** No. Install a tool only when you want to
prove the requirement it covers. Many inspection-based chapters need no tools at all.

**Can I use the engine without Claude?** Yes — `asvs.py` is standalone Python. The
skill adds the reasoning (verifying requirements, writing remediations); the engine
handles scoping, scaffolding, and integrity-checking on its own.

**What's next?** See [`GOALS.md`](GOALS.md) — opt-in ready-to-run check commands,
ASVS→CWE mappings, and the same attestation pattern extended to SSDF, CIS, and SLSA.

---

*Design principles and contribution conventions: [`CLAUDE.md`](CLAUDE.md). Roadmap:
[`GOALS.md`](GOALS.md).*
