# Threat Modeling & Security Assessment

Comprehensive threat modeling methodologies, risk assessment frameworks, vulnerability assessment, penetration testing, and security architecture review.


## 📑 Table of Contents

- [Threat Modeling Methodologies](#threat-modeling-methodologies)
  - [STRIDE Threat Modeling](#stride-threat-modeling)
  - [PASTA Threat Modeling](#pasta-threat-modeling)
- [Risk Assessment Frameworks](#risk-assessment-frameworks)
  - [Quantitative Risk Analysis](#quantitative-risk-analysis)
  - [Qualitative Risk Matrix](#qualitative-risk-matrix)
- [Vulnerability Assessment](#vulnerability-assessment)
  - [Vulnerability Scanning Strategy](#vulnerability-scanning-strategy)
  - [Vulnerability Prioritization](#vulnerability-prioritization)
- [Penetration Testing](#penetration-testing)
  - [Penetration Testing Phases](#penetration-testing-phases)
  - [Common Attack Vectors](#common-attack-vectors)
- [Security Architecture Review](#security-architecture-review)
  - [Security Architecture Checklist](#security-architecture-checklist)
- [MITRE ATT&CK Framework](#mitre-attck-framework)
  - [Mapping Threats to ATT&CK](#mapping-threats-to-attck)
- [Best Practices](#best-practices)

---
## Threat Modeling Methodologies

### STRIDE Threat Modeling

```typescript
interface STRIDEThreats {
  // Spoofing Identity
  spoofing: {
    description: 'Impersonating user or system',
    examples: [
      'Credential theft',
      'Session hijacking',
      'Man-in-the-middle attacks',
      'IP spoofing',
    ],
    mitigations: [
      'Strong authentication (MFA)',
      'Mutual TLS',
      'Certificate pinning',
      'Anti-CSRF tokens',
    ],
  };

  // Tampering with Data
  tampering: {
    description: 'Malicious modification of data',
    examples: [
      'SQL injection',
      'Log tampering',
      'Configuration changes',
      'Code injection',
    ],
    mitigations: [
      'Input validation',
      'Integrity checks (HMAC)',
      'Digital signatures',
      'Immutable infrastructure',
    ],
  };

  // Repudiation
  repudiation: {
    description: 'Denying actions without proof',
    examples: [
      'Transaction denial',
      'Audit log deletion',
      'Non-repudiation failures',
    ],
    mitigations: [
      'Comprehensive audit logging',
      'Digital signatures',
      'Timestamp authorities',
      'Blockchain ledgers',
    ],
  };

  // Information Disclosure
  informationDisclosure: {
    description: 'Exposure of sensitive information',
    examples: [
      'Data breach',
      'Directory traversal',
      'Error message leakage',
      'Side-channel attacks',
    ],
    mitigations: [
      'Encryption at rest and in transit',
      'Access controls',
      'Data classification',
      'Secure error handling',
    ],
  };

  // Denial of Service
  denialOfService: {
    description: 'Preventing legitimate access',
    examples: [
      'DDoS attacks',
      'Resource exhaustion',
      'Algorithmic complexity attacks',
      'Application crashes',
    ],
    mitigations: [
      'Rate limiting',
      'Resource quotas',
      'Auto-scaling',
      'DDoS protection (CloudFlare, AWS Shield)',
    ],
  };

  // Elevation of Privilege
  elevationOfPrivilege: {
    description: 'Gaining unauthorized access levels',
    examples: [
      'Privilege escalation',
      'Authentication bypass',
      'Authorization flaws',
      'Insecure deserialization',
    ],
    mitigations: [
      'Principle of least privilege',
      'Role-based access control',
      'Input validation',
      'Secure defaults',
    ],
  };
}
```

### PASTA Threat Modeling

```markdown
## Process for Attack Simulation and Threat Analysis (PASTA)

### Stage I: Define Business Objectives
- Identify business-critical assets
- Define security requirements
- Establish risk tolerance
- Compliance requirements

### Stage II: Define Technical Scope
- Application architecture
- Data flows
- Trust boundaries
- External dependencies
- Technology stack

### Stage III: Application Decomposition
- Entry points
- Assets
- Trust levels
- Use cases
- Abuse cases

### Stage IV: Threat Analysis
- Threat intelligence
- Attack patterns (MITRE ATT&CK)
- Vulnerability databases
- Historical incidents

### Stage V: Vulnerability & Weakness Analysis
- Known vulnerabilities (CVE)
- Design flaws
- Configuration issues
- Code weaknesses

### Stage VI: Attack Modeling & Simulation
- Attack trees
- Attack scenarios
- Exploit feasibility
- Impact analysis

### Stage VII: Risk & Impact Analysis
- Likelihood assessment
- Impact assessment
- Risk scoring (CVSS)
- Prioritization
```

## Risk Assessment Frameworks

### Quantitative Risk Analysis

```python
# Quantitative risk calculation
class RiskAssessment:
    def calculate_annual_loss_expectancy(self):
        """
        ALE = SLE × ARO
        ALE: Annual Loss Expectancy
        SLE: Single Loss Expectancy
        ARO: Annual Rate of Occurrence
        """

        # Example: Data breach scenario
        asset_value = 10_000_000  # $10M in customer data
        exposure_factor = 0.8     # 80% of data exposed
        sle = asset_value * exposure_factor  # $8M

        aro = 0.1  # 10% chance per year (once every 10 years)

        ale = sle * aro  # $800,000 annual loss expectancy

        return {
            'sle': sle,
            'aro': aro,
            'ale': ale,
            'justification': f'Invest up to ${ale:,.0f} annually in controls'
        }
```

### Qualitative Risk Matrix

```yaml
risk_matrix:
  likelihood:
    rare: 1        # < 5% probability
    unlikely: 2    # 5-25% probability
    possible: 3    # 25-50% probability
    likely: 4      # 50-75% probability
    almost_certain: 5  # > 75% probability

  impact:
    insignificant: 1   # Minimal impact
    minor: 2           # Limited impact
    moderate: 3        # Significant impact
    major: 4           # Severe impact
    catastrophic: 5    # Critical impact

  risk_levels:
    low: [1-4]        # Accept risk
    medium: [5-9]     # Monitor risk
    high: [10-15]     # Mitigate risk
    critical: [16-25] # Immediate action required
```

## Vulnerability Assessment

### Vulnerability Scanning Strategy

```bash
# Network vulnerability scanning with Nmap + NSE
nmap -sV -sC --script vuln 192.168.1.0/24

# Web application scanning with Nikto
nikto -h https://example.com -ssl -Tuning 123bde

# SSL/TLS scanning
testssl.sh --full https://example.com

# Subdomain enumeration
subfinder -d example.com -o subdomains.txt
httpx -l subdomains.txt -o live_subdomains.txt

# Nuclei for template-based scanning
nuclei -l live_subdomains.txt -t cves/ -t exposures/
```

### Vulnerability Prioritization

```typescript
interface VulnerabilityPrioritization {
  // CVSS v3.1 scoring
  cvss: {
    base_score: number;      // 0.0 - 10.0
    temporal_score: number;  // Adjusted for exploitability
    environmental_score: number; // Adjusted for business impact
  };

  // Exploit Prediction Scoring System (EPSS)
  epss: {
    probability: number;  // 0.0 - 1.0 (likelihood of exploitation)
    percentile: number;   // Comparison to other vulnerabilities
  };

  // Business context
  business_context: {
    asset_criticality: 'Critical' | 'High' | 'Medium' | 'Low';
    data_sensitivity: 'Confidential' | 'Internal' | 'Public';
    internet_facing: boolean;
    compensating_controls: string[];
  };

  // Final priority
  priority: 'P0' | 'P1' | 'P2' | 'P3' | 'P4';
}
```

## Penetration Testing

### Penetration Testing Phases

```markdown
## Phase 1: Reconnaissance (Passive & Active)
- OSINT gathering
- DNS enumeration
- Subdomain discovery
- Technology fingerprinting
- Social engineering reconnaissance

## Phase 2: Scanning & Enumeration
- Port scanning
- Service enumeration
- Web application scanning
- Vulnerability scanning
- Configuration review

## Phase 3: Exploitation
- Exploit development/adaptation
- Payload delivery
- Initial access
- Privilege escalation
- Persistence mechanisms

## Phase 4: Post-Exploitation
- Credential dumping
- Lateral movement
- Data exfiltration
- Covering tracks
- Maintaining access

## Phase 5: Reporting
- Executive summary
- Technical findings
- Proof of concept
- Risk assessment
- Remediation recommendations
```

### Common Attack Vectors

```yaml
attack_vectors:
  web_applications:
    - SQL injection
    - Cross-site scripting (XSS)
    - Cross-site request forgery (CSRF)
    - Server-side request forgery (SSRF)
    - XML external entity (XXE)
    - Insecure deserialization
    - Authentication bypass
    - Authorization flaws

  network_infrastructure:
    - Man-in-the-middle attacks
    - ARP spoofing
    - DNS poisoning
    - SSL/TLS downgrade
    - Port redirection
    - VLAN hopping

  authentication:
    - Brute force attacks
    - Credential stuffing
    - Password spraying
    - Session hijacking
    - JWT manipulation
    - OAuth/SAML flaws

  cloud_specific:
    - IAM misconfigurations
    - S3 bucket exposure
    - SSRF to metadata service
    - Container escape
    - Kubernetes RBAC bypass
```

## Security Architecture Review

### Security Architecture Checklist

```yaml
architecture_review:
  authentication:
    - Multi-factor authentication implemented
    - Strong password policies
    - Session management secure
    - OAuth/SAML properly configured
    - API authentication (API keys, JWT)

  authorization:
    - Role-based access control (RBAC)
    - Principle of least privilege
    - Attribute-based access control (ABAC)
    - Resource-level permissions
    - Authorization checks on all endpoints

  data_protection:
    - Encryption at rest (AES-256)
    - Encryption in transit (TLS 1.3)
    - Key management (KMS, Vault)
    - Data classification
    - Data retention policies
    - Secure data disposal

  network_security:
    - Network segmentation
    - Firewall rules (ingress/egress)
    - DDoS protection
    - VPN/private connectivity
    - Zero-trust network access

  logging_monitoring:
    - Centralized logging
    - Security event monitoring
    - Anomaly detection
    - Alerting and response
    - Log retention and immutability

  secure_development:
    - Security in SDLC
    - Code review process
    - Static analysis (SAST)
    - Dynamic analysis (DAST)
    - Dependency scanning (SCA)
    - Container security
```

## MITRE ATT&CK Framework

### Mapping Threats to ATT&CK

```yaml
mitre_attack_tactics:
  initial_access:
    - T1566: Phishing
    - T1190: Exploit public-facing application
    - T1078: Valid accounts

  execution:
    - T1059: Command and scripting interpreter
    - T1203: Exploitation for client execution

  persistence:
    - T1098: Account manipulation
    - T1136: Create account
    - T1547: Boot or logon autostart execution

  privilege_escalation:
    - T1068: Exploitation for privilege escalation
    - T1134: Access token manipulation

  defense_evasion:
    - T1070: Indicator removal
    - T1027: Obfuscated files or information

  credential_access:
    - T1110: Brute force
    - T1555: Credentials from password stores

  discovery:
    - T1083: File and directory discovery
    - T1046: Network service scanning

  lateral_movement:
    - T1021: Remote services
    - T1550: Use alternate authentication material

  collection:
    - T1005: Data from local system
    - T1039: Data from network shared drive

  exfiltration:
    - T1041: Exfiltration over C2 channel
    - T1567: Exfiltration over web service

  impact:
    - T1486: Data encrypted for impact
    - T1485: Data destruction
```

## Best Practices

**Threat Modeling**: Start early in design phase. Update regularly as architecture evolves.

**Risk-Based Approach**: Prioritize based on actual risk, not just vulnerability severity.

**Continuous Assessment**: Security is not one-time. Automate scanning and monitoring.

**Red Team Exercises**: Simulate real-world attacks to validate defenses.

**Defense in Depth**: Multiple layers of security controls. Assume breach mentality.
