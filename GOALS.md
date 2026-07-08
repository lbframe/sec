# GOALS — `sec/` Security Enablement Toolkit

## North star

Engineers should be able to ask Claude Code *"prove this app meets a security bar,
and tell me exactly what to fix if it doesn't"* — and get a **reproducible,
evidence-backed attestation** in return. Provable security, not security theater.

The unit of value is an **attestation**: for a named standard and scope, a verdict
per requirement, each backed by concrete evidence (`file:line`, config, scan output,
test result), with an honest NEEDS-EVIDENCE state and a concrete remediation for
every gap.

## Priority #1 — OWASP ASVS (shipped, iterating)

The Application Security Verification Standard is the flagship because it is the
best practical, level-based, requirement-by-requirement AppSec bar.

**Done**
- [x] `asvs-verify` skill against authoritative **ASVS 5.0.0** data (345 reqs / 17
      chapters), with deterministic scoping, per-requirement evidence, honest
      NEEDS-EVIDENCE state, integrity-checked roll-up, and generated remediation.
- [x] Hybrid mechanism: chapter → deterministic tool mapping (`tool-map.json`) so
      provable requirements are verified by scanners, not opinion.

**Next**
- [ ] Ready-to-run check commands (opt-in, never automatic): for each `tool`
      chapter, have `scaffold` emit the *exact* command a developer can choose to
      run (`testssl.sh` for V12, `checkov`/`trivy` for V13, SCA/SBOM for V15, header
      scan for V3) plus where to paste the output into `evidence`. The developer
      runs it; the tool never executes scanners on its own, gates a build, or
      forces anything. This is a checker, not an enforcer.
- [ ] ASVS → CWE and ASVS → tool mappings from the OWASP `mappings/` directory, so
      each finding links to root-cause taxonomy and detection tooling.
- [x] A worked example attestation with real tool evidence in `docs/security/`
      (`example-asvs-attestation-v12-L1.md` — V12 via live openssl/curl).
- [ ] Diff mode: re-attest only what changed since the last commit-under-test.

## Priority #2 — Make evidence collection turnkey

Turn `types.md` from a catalogue into runnable capability. Each is a candidate
**skill wrapping a deterministic binary** (mechanism = the tool's output as proof):

- [ ] `sca-scan` — dependencies/SBOM → CVE evidence (feeds ASVS V15).
- [ ] `secret-scan` — gitleaks over history (feeds V11/V13).
- [ ] `tls-scan` — testssl.sh attestation (feeds V12).
- [ ] `iac-scan` — checkov/trivy config (feeds V13).
- [ ] `headers-scan` — HTTP security header posture (feeds V3).

These should share a common evidence format so `asvs-verify` can consume them.

## Priority #3 — Broaden the standards, reuse the pattern

Apply the same skill pattern (authoritative data → deterministic scope → evidenced
verdict → remediation) to the next-highest-value standards in `standards.md`:

- [ ] **NIST SSDF (800-218)** — secure SDLC practice attestation (supplier evidence).
- [ ] **CIS Benchmarks** — cloud/k8s/OS config attestation via existing scanners.
- [ ] **SLSA** — build provenance level attestation for a pipeline.
- [ ] **OWASP API Security Top 10 / MASVS** — for API- and mobile-shaped targets.

Prefer a shared "attest against standard X" engine over N bespoke skills where the
data model allows.

## Priority #4 — Program-level & serving surface

- [ ] **OWASP SAMM** maturity self-assessment skill (program vs. per-app).
- [ ] Evaluate an **MCP server** as the serving surface once ≥3 scanners and ≥2
      standards exist and multiple projects want to query attestations/controls
      live — the point at which MCP beats per-repo skills.
- [ ] Install/distribution: make skills available beyond this repo (global
      `~/.claude/skills` install or a small `install.sh`).

## Guardrails (apply to everything above)

1. **Provable, not plausible** — no evidence, no verdict.
2. **Fetch authoritative data; never recall requirement text.**
3. **Always allow an honest "not verified."**
4. **Skill-first, but pick the mechanism that maximizes provability** (binary for
   deterministic checks, MCP for shared stateful services).
5. **Run against the engineer's target**, never this repo's own paths.
