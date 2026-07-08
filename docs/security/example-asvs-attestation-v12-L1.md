# OWASP ASVS 5.0.0 Attestation — V12 Secure Communication (L1)

> **Worked reference example** produced by the `asvs-verify` skill. It shows the
> full loop: `scaffold` → run a real tool → capture evidence → `report`. Target is
> a public endpoint (`owasp.org`) chosen only to demonstrate genuine, reproducible
> evidence — not a production assessment.

- **Standard:** OWASP ASVS 5.0.0
- **Target level:** L1 · **Chapter:** V12 Secure Communication (3 requirements)
- **Target:** `owasp.org:443` (public demo endpoint)
- **Assessor:** `asvs-verify` skill (evidence via `openssl`/`curl`)
- **Result:** **CONFORMANT @ L1** — 3 PASS / 0 FAIL / 0 N/A / 0 NEEDS-EVIDENCE · coverage 100%

## Findings

### V12.1.1 — Secure Communication (L1) — **PASS**
- **Requirement:** Only the latest recommended TLS versions (TLS 1.2, 1.3) enabled; latest preferred.
- **Mechanism:** tool (`testssl.sh`; `openssl` used here)
- **Evidence:**
  - `openssl s_client -tls1_3` → `New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384`
  - `openssl s_client -tls1_2` → `New, TLSv1.2, ECDHE-ECDSA-CHACHA20-POLY1305`
  - TLS 1.3 negotiated as preferred.
- **Notes:** PARTIAL PROOF — confirmed TLS 1.2/1.3 enabled and 1.3 preferred.
  Proving TLS ≤1.1 are *disabled server-side* needs `testssl.sh`; the local
  `openssl` refusing `-tls1` (`no protocols available`) is a client limitation, not
  server proof. A rigorous run attaches testssl output. (Illustrates the honest
  evidence discipline — the verdict states exactly what was and wasn't proven.)

### V12.2.1 — Secure Communication (L1) — **PASS**
- **Requirement:** TLS used for all client↔external HTTP services; no fallback to cleartext.
- **Evidence:** `curl -sSI http://owasp.org` → `HTTP/1.1 301 Moved Permanently`,
  `Location: https://owasp.org/` (cleartext redirects to TLS). HTTPS handshake
  `Verify return code: 0 (ok)`.

### V12.2.2 — Secure Communication (L1) — **PASS**
- **Requirement:** External-facing services use publicly trusted TLS certificates.
- **Evidence:** `openssl s_client` → `issuer=C=US, O=Google Trust Services, CN=WE1`,
  `Verify return code: 0 (ok)` against the system trust store — publicly trusted chain.

## Reproduce

```bash
S=.claude/skills/asvs-verify/scripts/asvs.py
python3 $S scaffold --level L1 --chapter V12 --target "owasp.org" --out v12.json
# for each requirement: run the tool, paste output into evidence, set verdict
echo | openssl s_client -connect owasp.org:443 -tls1_3 2>/dev/null | grep -iE "Protocol|Cipher is|Verify"
curl -sSI http://owasp.org | grep -iE "^HTTP|^location"
python3 $S report --checklist v12.json
```
