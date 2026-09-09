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
- [Using with Codex](#using-with-codex)
- [Quick start (5 minutes)](#quick-start-5-minutes)
- [Using the ASVS skill](#using-the-asvs-skill)
- [The `asvs` command (CLI reference)](#the-asvs-command-cli-reference)
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
| **`asvs` command** | Deterministic CLI (run via [`uv`](https://docs.astral.sh/uv/)): derives the applicable requirement set per level, scaffolds an attestation checklist, and integrity-checks the result. Works standalone (no LLM needed). | `.claude/skills/asvs-verify/` (`uvx --from … asvs`) |
| **Authoritative ASVS data** | OWASP ASVS 5.0.0 — 345 requirements, 17 chapters — fetched from OWASP, not typed from memory. Bundled with the command. | `.claude/skills/asvs-verify/asvs_verify/data/asvs-5.0.0.json` |
| **Tool map** | Which deterministic scanner produces evidence for each chapter. | `.claude/skills/asvs-verify/asvs_verify/data/tool-map.json` |
| **Attestation template** | The human-readable report format. | `.claude/skills/asvs-verify/templates/attestation.md` |
| **`standards.md`** | ~80 security & compliance standards (NIST, ISO, PCI, OWASP, SLSA…) — the "what good looks like" reference. | `standards.md` |
| **`types.md`** | Security tooling categories (SAST, SCA, SBOM, DAST, TLS/IaC/container/cloud scanning…) with a concrete tool for each — the "how to get evidence" reference. | `types.md` |

---

## Install

### Prerequisites
- **[`uv`](https://docs.astral.sh/uv/)** — runs the `asvs` command as a named tool
  and provisions Python for you. That's the only hard dependency (the engine itself
  is stdlib-only, no third-party packages). Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **Claude Code** — to use the `asvs-verify` skill conversationally.
- **Optional scanners** — only when you want to *prove* a specific requirement:
  `openssl`, `testssl.sh`, `checkov`, `trivy`, `gitleaks`, an SCA/SBOM tool, etc.
  Install these as you need them; see [`types.md`](types.md) for the catalogue.
  You install nothing up front — the tool tells you what to run when a requirement calls for it.

### Option A — use it inside this repo (zero setup)
The skill lives at `.claude/skills/asvs-verify/`, so it's **auto-discovered whenever
you run Claude Code in this repo**. Just start Claude here and ask to attest an app.

Verify the engine runs (no install — `uvx` builds and runs it on the fly):
```bash
uvx --from .claude/skills/asvs-verify asvs stats --level L2
```

### Option B — put `asvs` on your PATH, and the skill in *all* your repos
Install the command once, then call it bare from any directory:
```bash
uv tool install --from .claude/skills/asvs-verify asvs-verify
asvs stats --level L2          # now works anywhere
```
To make the *skill* activate in every project, copy or symlink it into your personal
skills directory:
```bash
# copy:
cp -r .claude/skills/asvs-verify ~/.claude/skills/asvs-verify
# …or symlink so it tracks this repo (updates when you pull):
ln -s "$(pwd)/.claude/skills/asvs-verify" ~/.claude/skills/asvs-verify
```
Restart Claude Code. The skill now activates in any project when you ask to
assess/verify/attest an app against ASVS. It always runs against the **target repo
you name**, never this one.

> The ASVS dataset is bundled *inside* the `asvs_verify` package and resolved via
> `importlib.resources`, so `asvs` works from any working directory — including
> inside the target repo you're attesting — no matter where it's installed.

---

## Using with Codex

Prerequisites: a Codex client with local Agent Skills support, `uv`, and a checkout
of this repository that preserves symbolic links. The engine requires Python 3.9+
(which `uv` can provision). Claude Code is not required for this option.

Start a fresh Codex session **in `sec`**:

```bash
cd /absolute/path/to/sec
codex
```

Codex discovers `.agents/skills/asvs-verify`, a relative symlink to the existing
`.claude/skills/asvs-verify/` directory. Both clients use the same **ASVS Verify &
Attest** instructions, with the technical name `asvs-verify`.

In Codex CLI, use `/skills` to select `asvs-verify`, or type `$asvs-verify` in a
client that supports skill mentions. Name the external application with an
explicit path, for example:

```text
$asvs-verify Assess /absolute/path/to/my-api against OWASP ASVS L2.
```

The named application is the assessment target. `$SKILL` in the skill's commands
is the absolute path to the skill directory in `sec`, not the application path.
The workflow remains scope → scaffold → verify → report → remediation, with L2
as the default; the session's instructions and permissions still apply.

This is local discovery in `sec`: it does **not** install the skill for sessions
opened in other repositories. Keep the repository intact; copying only the skill
folder loses its relative references to root-level `types.md` and `standards.md`.
See [Codex's local skill discovery documentation](https://learn.chatgpt.com/docs/build-skills).

---

## Quick start (5 minutes)

The flow is **scope → scaffold → verify → report**.

```bash
# Point `asvs` at the skill dir once (or `uv tool install` it — see Option B):
alias asvs='uvx --from .claude/skills/asvs-verify asvs'

# 1. SCOPE — see what an L2 assessment covers (253 requirements)
asvs stats --level L2

# 2. SCAFFOLD — generate a checklist for one area, e.g. authentication
asvs scaffold --level L2 --chapter V6,V7,V8 --target "my-api" --out asvs.json

# 3. VERIFY — open asvs.json; for each requirement set a verdict + evidence.
#    (Do this yourself, or let the Claude skill do it — see next section.)

# 4. REPORT — roll up + integrity-check (refuses evidence-free passes)
asvs report --checklist asvs.json
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
2. **Scaffold** — runs `asvs scaffold` to get the exact applicable requirements.
3. **Verify each requirement** — for chapters mapped to a **tool**, it tells you the
   command to run (or runs it if you ask) and captures the output as evidence; for
   **inspection** chapters (auth logic, authz, OAuth), it reads the code and cites
   `file:line`. When something needs a runtime test that wasn't done, it marks
   **NEEDS-EVIDENCE** rather than guessing.
4. **Report** — runs `asvs report` (integrity-checked) and renders the
   human-readable attestation from the template.
5. **Remediate** — for every FAIL, a concrete fix and the ASVS ID it closes.

> Skills auto-activate from your request — you don't invoke them by name. If it
> doesn't trigger, say "use the asvs-verify skill".

---

## The `asvs` command (CLI reference)

Deterministic, standalone, no LLM required. Run as `asvs <command>` (installed) or
`uvx --from .claude/skills/asvs-verify asvs <command>` (zero-install).

| Command | Purpose | Example |
|---------|---------|---------|
| `chapters` | List the 17 ASVS chapters. | `asvs chapters` |
| `stats` | Requirement counts per chapter for a level. | `asvs stats --level L2` |
| `list` | Print the applicable requirement text. | `asvs list --level L1 --chapter V6` |
| `scaffold` | Emit a fill-in attestation checklist (JSON). | `asvs scaffold --level L2 --target "api" --out c.json` |
| `report` | Roll a filled checklist into a summary + integrity check. | `asvs report --checklist c.json` |

Common flags: `--level {L1,L2,L3}` (default L2), `--chapter V6,V7` (comma-separated,
optional), `--target "name"`, `--out file.json`.

**Levels are cumulative** (verified from the data): L1 = 70 reqs · L2 = 253 · L3 = 345.

### Report exit codes

For a readable checklist JSON with the expected structure, `asvs report` separates
document integrity from the application's security result:

| Condition | Result | Exit code |
|-----------|--------|-----------|
| All requirements PASS or justified N/A, no integrity problems | CONFORMANT | `0` |
| At least one documented FAIL, no unverified requirements or integrity problems | NON-CONFORMANT | `0` |
| At least one NEEDS-EVIDENCE, no integrity problems | INCOMPLETE | `0` |
| Any integrity problem, regardless of other verdicts | INCOMPLETE | `1` |
| Invalid command-line arguments | Existing argparse error | `2` |

Integrity problems include PASS/FAIL without evidence, FAIL without remediation,
invalid verdicts, and N/A without justification in `evidence`. A FAIL or
NEEDS-EVIDENCE alone does not cause a process failure. File-reading, malformed-JSON
and unexpected-structure errors retain their existing failure behavior; this is
not general schema validation.

**Compatibility change:** integrity problems previously printed warnings while
returning `0`; shell consumers now receive `1`. Older N/A entries without
justification could contribute to CONFORMANT and now make the attestation
INCOMPLETE with exit code `1`. Complete their `evidence` with an actual scope
justification before using them again. There is no automatic migration or invented
justification, and `report` never rewrites the input checklist.

### Reproduce the CLI tests

From the repository root, use a temporary uv environment (leaves any user tool
installation intact):

```bash
ASVS_TEST_DIR=$(mktemp -d)
uv venv "$ASVS_TEST_DIR/venv"
uv pip install --python "$ASVS_TEST_DIR/venv/bin/python" .claude/skills/asvs-verify
"$ASVS_TEST_DIR/venv/bin/python" -B -m unittest discover -s tests -v
```

The stdlib `unittest` suite runs synthetic checklists through both the installed
`asvs` console command and `python -m asvs_verify` in subprocesses, from temporary
directories outside the repository. It checks results, exit codes, diagnostics,
and preservation of input bytes. It does not assess the quality of evidence or run
scanners.

---

## Verdicts & what "provable" means

Every requirement gets one of four verdicts. This is the heart of "provable, not plausible":

| Verdict | Meaning | Evidence required? |
|---------|---------|--------------------|
| **PASS** | Met, demonstrated by concrete evidence. | **Yes** — `file:line`, config, scan output, or test result. |
| **FAIL** | Not met. | **Yes** — evidence of the gap **and** a remediation. |
| **N/A** | Doesn't apply (feature absent). | **Yes** — why it can't apply, in `evidence`. |
| **NEEDS-EVIDENCE** | Not yet verified by what was performed. | The honest default — never guess a PASS. |

For N/A, `evidence` must be a nonempty string after trimming leading/trailing
whitespace for the check. Missing, empty, whitespace-only, `null`, and non-text
values are invalid; text only in `notes` or `remediation` does not suffice. A
justified N/A needs no remediation. The check only verifies the presence of text;
the assessor remains responsible for whether the justification is relevant.

`asvs report` **enforces** this: it flags any PASS/FAIL missing evidence, any
FAIL missing a remediation, any invalid verdict, and any unjustified N/A as
integrity problems. These and any remaining NEEDS-EVIDENCE make the result **INCOMPLETE**.
An attestation is only **CONFORMANT** when every in-scope requirement is verified with
zero FAILs and no integrity problems.

---

## Evidence tools per chapter

Each chapter has a verification **mechanism** (`asvs_verify/data/tool-map.json`):

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

**Can I use the engine without Claude?** Yes — `asvs` is a standalone command (run it
with `uvx --from .claude/skills/asvs-verify asvs …`, or `uv tool install` it). The
skill adds the reasoning (verifying requirements, writing remediations); the command
handles scoping, scaffolding, and integrity-checking on its own.

**What's next?** See [`GOALS.md`](GOALS.md) — opt-in ready-to-run check commands,
ASVS→CWE mappings, and the same attestation pattern extended to SSDF, CIS, and SLSA.

---

*Design principles and contribution conventions: [`CLAUDE.md`](CLAUDE.md). Roadmap:
[`GOALS.md`](GOALS.md).*
