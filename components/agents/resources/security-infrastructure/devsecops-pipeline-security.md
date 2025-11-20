# DevSecOps Pipeline Security

Comprehensive guide for implementing security automation in CI/CD pipelines with shift-left practices, continuous scanning, and security gates.


## 📑 Table of Contents

- [Security Pipeline Integration](#security-pipeline-integration)
  - [Complete CI/CD Security Pipeline](#complete-cicd-security-pipeline)
- [Security Gates & Thresholds](#security-gates-thresholds)
  - [Security Gate Implementation](#security-gate-implementation)
- [Container Security Scanning](#container-security-scanning)
  - [Multi-Layer Container Security](#multi-layer-container-security)
  - [Container Image Hardening](#container-image-hardening)
- [Secrets Management in Pipelines](#secrets-management-in-pipelines)
  - [Secret Rotation and Dynamic Secrets](#secret-rotation-and-dynamic-secrets)
- [Security Testing Tools](#security-testing-tools)
  - [SAST Tools Comparison](#sast-tools-comparison)
  - [DAST Tools](#dast-tools)
- [Infrastructure Security Testing](#infrastructure-security-testing)
  - [Terraform Security Scanning](#terraform-security-scanning)
- [Best Practices](#best-practices)

---
## Security Pipeline Integration

### Complete CI/CD Security Pipeline

```yaml
# GitLab CI/CD with comprehensive security scanning integration
stages:
  - scan
  - build
  - test
  - security
  - deploy
  - monitor

# Static Application Security Testing (SAST)
sast:
  stage: scan
  image: semgrep/semgrep
  script:
    - semgrep --config=p/security-audit --json -o sast-report.json .
    - semgrep --config=p/owasp-top-ten --json -o owasp-report.json .
  artifacts:
    reports:
      sast: sast-report.json

# Software Composition Analysis (SCA)
dependency-check:
  stage: scan
  image: owasp/dependency-check
  script:
    - /usr/share/dependency-check/bin/dependency-check.sh --project "$CI_PROJECT_NAME" --scan . --format JSON --out dependency-report.json
  artifacts:
    reports:
      dependency_scanning: dependency-report.json
  allow_failure: true

# Build with provenance tracking
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  after_script:
    - docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

# Dynamic Application Security Testing (DAST)
dast:
  stage: security
  image: owasp/zap2docker-stable
  script:
    - zap-baseline.py -t $STAGING_URL -r dast-report.html
  artifacts:
    reports:
      dast: dast-report.html
  only:
    - merge_requests

# Infrastructure as Code scanning
iac-scan:
  stage: scan
  image: bridgecrewio/checkov
  script:
    - checkov -d . --framework terraform,kubernetes,dockerfile -o json > iac-scan-results.json
  artifacts:
    reports:
      iac_scan: iac-scan-results.json

# Secrets scanning
secrets-scan:
  stage: scan
  image: trufflesecurity/trufflehog:latest
  script:
    - trufflehog filesystem . --json > secrets-scan.json || true
  artifacts:
    reports:
      secret_detection: secrets-scan.json

# Security policy enforcement
security-policy:
  stage: security
  script:
    - |
      if grep -r "hardcoded_password" . ; then
        echo "ERROR: Hardcoded credentials detected"
        exit 1
      fi
    - |
      if grep -r "http://" . | grep -v ".md" ; then
        echo "WARNING: Unencrypted HTTP usage detected"
      fi
  allow_failure: true
```

## Security Gates & Thresholds

### Security Gate Implementation

```typescript
// Security gate implementation with threshold enforcement
interface SecurityGates {
  // Pre-deployment gates
  preDeployment: {
    criticalVulnerabilities: {
      threshold: 0,
      failBuild: true,
      action: 'Block deployment',
    },
    highVulnerabilities: {
      threshold: 2,
      failBuild: false,
      action: 'Require security review',
    },
    licenseCompliance: {
      threshold: '100%',
      failBuild: true,
      action: 'Block deployment',
    },
    codeQuality: {
      threshold: 'A grade',
      failBuild: false,
      action: 'Create tech debt ticket',
    },
  };

  // Runtime security gates
  runtimeSecurity: {
    containerImageScanning: {
      registry: 'ECR / GCR / ACR',
      scanFrequency: 'per push + daily',
      blockedSeverities: ['Critical', 'High'],
      autoQuarantine: true,
    },
    policyEnforcement: {
      admissionController: 'OPA/Kyverno',
      policies: [
        'Require image pull policy: Always',
        'Enforce resource limits',
        'Block privileged containers',
        'Require security context',
        'Enforce network policies',
      ],
    },
  };
}
```

## Container Security Scanning

### Multi-Layer Container Security

```bash
# Trivy comprehensive container scanning
trivy image --severity HIGH,CRITICAL myapp:latest

# Scan filesystem for vulnerabilities
trivy fs --security-checks vuln,config /path/to/project

# Scan IaC templates
trivy config terraform/

# Generate SBOM (Software Bill of Materials)
trivy image --format cyclonedx myapp:latest > sbom.json

# Scan Kubernetes manifests
trivy k8s --report summary deployment.yaml
```

### Container Image Hardening

```dockerfile
# Multi-stage build for minimal attack surface
FROM golang:1.21 AS builder
WORKDIR /build
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o app

# Distroless base image (no shell, no package manager)
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /build/app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]

# Security scanning in CI/CD
# RUN trivy image --exit-code 1 --severity CRITICAL .
```

## Secrets Management in Pipelines

### Secret Rotation and Dynamic Secrets

```yaml
# HashiCorp Vault integration in CI/CD
vault-secrets:
  stage: .pre
  image: vault:latest
  script:
    - export VAULT_ADDR="https://vault.company.com"
    - export VAULT_TOKEN=$(vault write -field=token auth/jwt/login role=ci-role jwt=$CI_JOB_JWT)
    - vault kv get -field=api_key secret/myapp/prod > api_key.txt
  artifacts:
    paths:
      - api_key.txt
    expire_in: 5 minutes

# AWS Secrets Manager rotation
rotate-secrets:
  stage: deploy
  script:
    - |
      aws secretsmanager rotate-secret \
        --secret-id prod/db/password \
        --rotation-lambda-arn arn:aws:lambda:region:account:function:rotate-secret
```

## Security Testing Tools

### SAST Tools Comparison

| Tool | Languages | Strengths | Use Case |
|------|-----------|-----------|----------|
| Semgrep | 30+ languages | Fast, customizable rules | General purpose SAST |
| Bandit | Python | Deep Python analysis | Python security |
| gosec | Go | Go-specific patterns | Go security |
| ESLint | JavaScript/TypeScript | Extensive plugins | Frontend security |
| CodeQL | 10+ languages | Semantic analysis | Deep code analysis |

### DAST Tools

| Tool | Type | Strengths | Use Case |
|------|------|-----------|----------|
| OWASP ZAP | Proxy | OWASP Top 10 | Web application testing |
| Burp Suite | Proxy | Manual + automated | Penetration testing |
| Nuclei | Scanner | Template-based | Vulnerability scanning |
| w3af | Framework | Plugin architecture | Web app auditing |

## Infrastructure Security Testing

### Terraform Security Scanning

```bash
# Checkov for Terraform
checkov -d . --framework terraform --output json

# tfsec for Terraform-specific security issues
tfsec . --format json --out tfsec-report.json

# Terrascan for policy-as-code
terrascan scan -i terraform -t aws

# Custom OPA policies
opa eval -d policies/ -i terraform.json "data.terraform.deny"
```

## Best Practices

**Shift-Left Security**: Integrate security scanning as early as possible in development lifecycle. Provide fast feedback to developers.

**Security as Code**: Define all security policies, rules, and configurations as code. Version control and automate everything.

**Continuous Monitoring**: Don't just scan at build time. Monitor runtime behavior, dependencies, and infrastructure continuously.

**Developer Experience**: Make security tools fast and actionable. Don't overwhelm developers with false positives.

**Fail Fast, Fail Safe**: Block critical issues immediately but allow medium/low issues with warning + tracking ticket.
