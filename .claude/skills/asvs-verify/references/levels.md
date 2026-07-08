# ASVS 5.0 Level Model (authoritative, derived from the dataset)

OWASP ASVS 5.0.0 contains **345 requirements** across **17 chapters (V1–V17)**.

Each requirement carries a single field `L` = the **minimum level at which it
applies**. Levels are **cumulative** — a higher level is a strict superset:

| Target | Includes | Count | Intended for |
|--------|----------|-------|--------------|
| **L1** | `L == 1` | **70**  | Baseline for *all* applications; verifiable largely by testing without source access. |
| **L2** | `L <= 2` | **253** | Applications handling sensitive data (most business apps). The recommended default target. |
| **L3** | `L <= 3` | **345** | High-value / high-assurance apps (payments, health, critical infra) needing defense-in-depth. |

> ⚠️ This is a **change from ASVS 4.0.3**, which used 14 chapters and separate
> per-level boolean columns. Do not carry 4.0.3 numbering or leveling into 5.0
> work. Always derive scope from `scripts/asvs.py`, never from memory.

## Chapters

| Code | Chapter | Primary verification mechanism |
|------|---------|--------------------------------|
| V1  | Encoding and Sanitization | hybrid (SAST + DAST) |
| V2  | Validation and Business Logic | hybrid |
| V3  | Web Frontend Security | tool (header scan, DAST) |
| V4  | API and Web Service | hybrid |
| V5  | File Handling | hybrid |
| V6  | Authentication | inspection |
| V7  | Session Management | hybrid |
| V8  | Authorization | inspection (business logic) |
| V9  | Self-contained Tokens (JWT) | hybrid |
| V10 | OAuth and OIDC | inspection |
| V11 | Cryptography | hybrid |
| V12 | Secure Communication (TLS) | **tool** (testssl.sh) |
| V13 | Configuration | **tool** (checkov, prowler, trivy) |
| V14 | Data Protection | hybrid |
| V15 | Secure Coding and Architecture | **tool** (SCA, SBOM, SAST) |
| V16 | Security Logging and Error Handling | inspection |
| V17 | WebRTC | inspection |

See `tool-map.json` for the machine-readable chapter→mechanism→tools mapping,
and `../../../types.md` for the full tool catalogue.

## Choosing a target level

- Default to **L2** unless the engineer states otherwise.
- Use **L1** for a fast baseline or when only black-box access is available.
- Use **L3** only when the app's risk profile (regulated data, safety, money)
  justifies the cost, or when a customer/contract mandates it.
