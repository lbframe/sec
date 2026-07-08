| Area | Name | Type | Description | Benefit | Docs |
|---|---|---|---|---|---|
| Standards | OWASP ASVS | Verification standard | Defines application security verification requirements and levels. | Creates a measurable AppSec baseline. | https://owasp.org/www-project-application-security-verification-standard/ |
| Standards | OWASP Top 10 | Risk framework | Common web application security risks. | Prioritizes common web app risks. | https://owasp.org/www-project-top-ten/ |
| Standards | OWASP API Top 10 | Risk framework | Common API security risks. | Prioritizes API-specific risks. | https://owasp.org/www-project-api-security/ |
| Standards | OWASP MASVS | Verification standard | Mobile application security verification requirements. | Creates a mobile security baseline. | https://mas.owasp.org/ |
| Standards | OWASP SAMM | Maturity model | Software assurance maturity model. | Measures AppSec program maturity. | https://owasp.org/www-project-samm/ |
| Source | SAST | Scan | Static analysis of source code. | Finds coding flaws before runtime. | https://owasp.org/www-community/Source_Code_Analysis_Tools |
| Source | Secret scanning | Scan | Detects API keys, passwords, tokens, certificates, and private keys. | Prevents credential leakage. | https://github.com/gitleaks/gitleaks |
| Source | PII scanning | Scan | Detects sensitive personal data in code, logs, or files. | Reduces privacy and compliance risk. | https://microsoft.github.io/presidio/ |
| Dependencies | SCA | Scan | Scans third-party packages and libraries for known vulnerabilities. | Finds vulnerable dependencies. | https://owasp.org/www-project-dependency-check/ |
| Dependencies | License scanning | Scan | Detects open-source license obligations and conflicts. | Reduces legal and compliance risk. | https://scancode-toolkit.readthedocs.io/ |
| Dependencies | SBOM generation | Inventory | Generates a software bill of materials. | Creates supply-chain visibility. | https://cyclonedx.org/ |
| Dependencies | SBOM vulnerability scan | Scan | Scans SBOM components for known vulnerabilities. | Finds vulnerable components independent of build system. | https://cyclonedx.org/ |
| Supply Chain | SLSA provenance | Verification | Verifies build provenance and supply-chain integrity. | Reduces tampering and build compromise risk. | https://slsa.dev/ |
| Supply Chain | Artifact signing | Verification | Signs and verifies build artifacts and container images. | Proves artifact integrity and origin. | https://docs.sigstore.dev/ |
| Supply Chain | Registry scanning | Scan | Scans artifacts stored in image or package registries. | Prevents vulnerable artifacts from being promoted. | https://goharbor.io/ |
| Build | Binary scanning | Scan | Scans compiled binaries and packaged artifacts. | Finds embedded vulnerable components and secrets. | https://trivy.dev/ |
| Build | Binary hardening check | Scan | Checks ASLR, DEP, PIE, RELRO, stack canaries, and similar controls. | Verifies compiled binary hardening. | https://github.com/slimm609/checksec |
| Build | Malware scanning | Scan | Scans artifacts for known malware. | Reduces compromised artifact risk. | https://www.clamav.net/ |
| Containers | Container image scanning | Scan | Scans OS packages, app dependencies, secrets, and misconfigurations in images. | Blocks vulnerable images before deployment. | https://trivy.dev/ |
| Containers | Dockerfile linting | Scan | Detects insecure or poor Dockerfile patterns. | Improves image security and maintainability. | https://github.com/hadolint/hadolint |
| Containers | CIS Docker benchmark | Benchmark | Checks Docker host and daemon configuration. | Hardens container runtime configuration. | https://www.cisecurity.org/benchmark/docker |
| IaC | IaC scanning | Scan | Scans Terraform, CloudFormation, Helm, Kubernetes YAML, and similar files. | Catches insecure infrastructure before deployment. | https://www.checkov.io/ |
| Kubernetes | Kubernetes manifest scanning | Scan | Detects insecure workload specs and cluster manifests. | Prevents privilege escalation and unsafe deployments. | https://kubesec.io/ |
| Kubernetes | Kubernetes CIS benchmark | Benchmark | Checks cluster configuration against CIS guidance. | Hardens Kubernetes clusters. | https://github.com/aquasecurity/kube-bench |
| Kubernetes | RBAC analysis | Scan | Reviews Kubernetes roles, bindings, and excessive permissions. | Reduces privilege escalation risk. | https://github.com/alcideio/rbac-tool |
| Runtime | DAST | Scan | Black-box testing of a running application. | Finds runtime and configuration vulnerabilities. | https://owasp.org/www-community/Vulnerability_Scanning_Tools |
| Runtime | API security scanning | Scan | Tests REST, GraphQL, gRPC, and other APIs. | Finds API authorization and input handling issues. | https://owasp.org/www-project-api-security/ |
| Runtime | IAST | Scan | Uses instrumentation during testing to detect vulnerabilities. | Produces higher-confidence runtime findings. | https://owasp.org/www-project-devsecops-guideline/latest/02-Vulnerability-Scanning.html |
| Runtime | Fuzz testing | Test | Sends generated or mutated inputs to applications, parsers, and APIs. | Finds crashes and memory safety bugs. | https://llvm.org/docs/LibFuzzer.html |
| Runtime | RASP | Protection | Runtime application self-protection inside the app process. | Detects or blocks attacks during execution. | https://owasp.org/www-project-devsecops-guideline/latest/02-Vulnerability-Scanning.html |
| Network | Network vulnerability scanning | Scan | Scans hosts, ports, services, and known vulnerabilities. | Finds exposed and unpatched services. | https://greenbone.github.io/docs/ |
| Network | TLS scanning | Scan | Checks protocol versions, ciphers, certificates, and TLS configuration. | Improves cryptographic hygiene. | https://testssl.sh/ |
| Network | HTTP security header scanning | Scan | Checks headers such as CSP, HSTS, X-Frame-Options, and others. | Improves browser-side protections. | https://observatory.mozilla.org/ |
| Network | DNS and email security scanning | Scan | Checks DNSSEC, SPF, DKIM, DMARC, MX, and related records. | Reduces domain spoofing and DNS risk. | https://www.hardenize.com/ |
| Network | Attack surface scanning | Scan | Discovers exposed assets, domains, services, and endpoints. | Reduces unmanaged internet exposure. | https://github.com/projectdiscovery/nuclei |
| Cloud | CSPM | Scan | Continuously scans cloud accounts for insecure configuration. | Finds cloud misconfigurations and policy drift. | https://github.com/prowler-cloud/prowler |
| Cloud | IAM analysis | Scan | Reviews identities, policies, roles, and excessive permissions. | Enforces least privilege. | https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html |
| Compliance | CIS benchmark scanning | Benchmark | Checks systems and platforms against CIS benchmarks. | Supports hardening and audit evidence. | https://www.cisecurity.org/cis-benchmarks |
| Compliance | DISA STIG scanning | Benchmark | Checks systems against DISA STIG baselines. | Supports regulated and government-grade hardening. | https://public.cyber.mil/stigs/ |
| Compliance | SCAP scanning | Benchmark | Uses standardized compliance automation content. | Automates compliance validation. | https://www.open-scap.org/ |
| Manual | Threat modeling | Review | Reviews design, data flows, abuse cases, and trust boundaries. | Finds design flaws scanners miss. | https://learn.microsoft.com/security/engineering/threat-modeling |
| Manual | Penetration testing | Test | Human-led exploitation attempt against an app or environment. | Finds chained and business-logic issues. | https://owasp.org/www-project-web-security-testing-guide/ |
| Manual | Red team | Exercise | Simulated adversary activity across people, process, and technology. | Measures detection and response capability. | https://attack.mitre.org/ |
| Manual | Purple team | Exercise | Collaborative red-team and blue-team exercise. | Improves defensive controls and detections. | https://attack.mitre.org/ |
| Monitoring | Runtime threat detection | Monitoring | Detects suspicious runtime behavior in workloads and hosts. | Finds active compromise or policy violations. | https://falco.org/ |
| Monitoring | eBPF runtime security | Monitoring | Uses kernel-level telemetry for runtime security and observability. | Detects suspicious workload behavior with low overhead. | https://tetragon.io/ |
| Monitoring | Vulnerability drift scanning | Monitoring | Re-scans deployed assets as new CVEs are disclosed. | Finds newly vulnerable running systems. | https://trivy.dev/ |
