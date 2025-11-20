# Cloud Security & Compliance

Comprehensive cloud security architecture, compliance frameworks, security posture management, and audit logging across AWS, Azure, and GCP.


## 📑 Table of Contents

- [AWS Security Architecture](#aws-security-architecture)
  - [Identity & Access Management (IAM)](#identity-access-management-iam)
  - [Network Security](#network-security)
  - [Data Protection](#data-protection)
  - [Logging & Monitoring](#logging-monitoring)
- [Compliance Frameworks](#compliance-frameworks)
  - [SOC 2 Type II Controls](#soc-2-type-ii-controls)
  - [HIPAA Security Rule](#hipaa-security-rule)
  - [GDPR Data Protection](#gdpr-data-protection)
  - [PCI-DSS v4.0](#pci-dss-v40)
- [CIS Benchmarks Implementation](#cis-benchmarks-implementation)
  - [CIS AWS Foundations Benchmark](#cis-aws-foundations-benchmark)
  - [CIS Kubernetes Benchmark](#cis-kubernetes-benchmark)
- [Cloud Security Posture Management (CSPM)](#cloud-security-posture-management-cspm)
  - [Multi-Cloud Security Assessment](#multi-cloud-security-assessment)
- [Compliance Automation](#compliance-automation)
  - [Automated Evidence Collection](#automated-evidence-collection)
- [Best Practices](#best-practices)

---
## AWS Security Architecture

### Identity & Access Management (IAM)

```typescript
interface AWSIAMSecurity {
  rootAccountProtection: {
    mfaRequired: true,
    noAccessKeys: true,
    lockdownWithCloudTrail: true,
  };

  assumeRolePatterns: {
    trustedServices: ['ec2.amazonaws.com', 'ecs-tasks.amazonaws.com'],
    sessionDuration: '15m',
    externalIdRequired: true,
  };

  permissionBoundaries: {
    description: 'Prevent privilege escalation',
    maxPermissions: 'Limited to service scope',
    denyList: ['iam:*', 'kms:Decrypt', 'ec2:TerminateInstances'],
  };
}
```

### Network Security

```typescript
interface AWSNetworkSecurity {
  vpc: {
    flowLogs: 'to CloudWatch and S3',
    publicSubnets: {
      natGateway: 'for outbound egress only',
      networkAcl: 'restrict inbound to HTTP/HTTPS',
    },
    privateSubnets: {
      noDirectInternetAccess: true,
      vpcEndpoints: 'for AWS service access',
    },
  };

  securityGroups: {
    defaultDeny: 'implicit deny all inbound',
    egressRestriction: 'restrict outbound to required services',
    principle: 'least privilege',
  };

  networkAcl: {
    statefulness: 'Track established connections',
    ephemeralPorts: '1024-65535',
  };
}
```

### Data Protection

```typescript
interface AWSDataProtection {
  atRest: {
    s3: {
      encryption: 'S3-SSE with KMS CMK',
      versioning: 'enabled',
      mfa_delete: true,
      public_access: 'blocked at bucket level',
      logging: 'to separate logging bucket',
    },
    rds: {
      encryption: 'KMS CMK',
      autoBackup: '30 days',
      backupEncryption: 'enabled',
      iamDatabaseAuth: 'enabled',
    },
    dynamodb: {
      encryption: 'SSE with KMS',
      ttl: 'enabled for sensitive data',
      pointInTimeRecovery: 'enabled',
    },
  };

  inTransit: {
    tls: '1.3 minimum',
    certificateValidation: true,
    publicCertificates: 'via ACM',
    internalCertificates: 'private PKI with Vault',
  };

  keyManagement: {
    kms: {
      customerMasterKey: 'CMK for each service',
      keyRotation: 'annual automatic rotation',
      keyPolicy: 'least privilege access',
      auditLogging: 'CloudTrail + CloudWatch',
    },
    secretsManager: {
      rotation: 'automatic every 30 days',
      versions: '10 retained for rollback',
      auditLog: 'enabled',
    },
  };
}
```

### Logging & Monitoring

```typescript
interface AWSLoggingMonitoring {
  cloudTrail: {
    multiRegion: true,
    logFileValidation: true,
    cloudWatchLogs: 'all API calls',
    s3: {
      encryption: 'KMS CMK',
      versioningAndMfaDelete: true,
      lifecyclePolicy: '90 day archive to Glacier',
    },
  };

  cloudWatch: {
    metrics: 'custom metrics for security',
    alarms: 'on suspicious activity',
    logGroups: 'separate per application',
    retention: '90 days minimum',
  };

  guardDuty: {
    enabled: true,
    s3ProtectionEnabled: true,
    eksRuntimeMonitoring: true,
    automatedResponse: 'via EventBridge',
  };

  securityHub: {
    enabled: true,
    standards: ['PCI-DSS', 'CIS AWS', 'GDPR'],
    automatedRemediation: true,
  };
}
```

## Compliance Frameworks

### SOC 2 Type II Controls

```yaml
soc2_controls:
  cc1_control_environment:
    - Documented security policies
    - Security awareness training
    - Background checks
    - Separation of duties

  cc2_communication:
    - Security incident reporting
    - Policy communication
    - Stakeholder communication

  cc3_risk_assessment:
    - Annual risk assessment
    - Threat modeling
    - Vulnerability management
    - Third-party risk assessment

  cc4_monitoring:
    - SIEM implementation
    - Log aggregation
    - Continuous monitoring
    - Alerting and response

  cc5_control_activities:
    - Access controls (MFA, RBAC)
    - Change management
    - Data classification
    - Encryption standards

  cc6_logical_access:
    - Identity management
    - Authentication (SSO, MFA)
    - Authorization (RBAC)
    - Privileged access management

  cc7_system_operations:
    - Capacity planning
    - Backup and recovery
    - Disaster recovery
    - Business continuity

  cc8_change_management:
    - Change approval process
    - Testing requirements
    - Rollback procedures
    - Documentation

  cc9_risk_mitigation:
    - Firewall management
    - Intrusion detection
    - Vulnerability scanning
    - Patch management
```

### HIPAA Security Rule

```yaml
hipaa_security_rule:
  administrative_safeguards:
    - Security management process
    - Risk analysis and management
    - Workforce security
    - Information access management
    - Security awareness training
    - Contingency planning
    - Business associate agreements

  physical_safeguards:
    - Facility access controls
    - Workstation use policies
    - Device and media controls
    - Disposal procedures

  technical_safeguards:
    - Access controls (unique user IDs)
    - Audit controls (logging)
    - Integrity controls (checksums)
    - Transmission security (encryption)
    - Authentication (MFA)
```

### GDPR Data Protection

```yaml
gdpr_compliance:
  data_protection_principles:
    - Lawfulness, fairness, transparency
    - Purpose limitation
    - Data minimization
    - Accuracy
    - Storage limitation
    - Integrity and confidentiality
    - Accountability

  data_subject_rights:
    - Right to access
    - Right to rectification
    - Right to erasure
    - Right to restrict processing
    - Right to data portability
    - Right to object
    - Rights related to automated decision-making

  technical_measures:
    - Encryption of personal data
    - Pseudonymization
    - Access controls
    - Data breach notification (72 hours)
    - Data protection impact assessment
    - Privacy by design and default
```

### PCI-DSS v4.0

```yaml
pci_dss_requirements:
  build_maintain_secure_network:
    - Install and maintain network security controls
    - Apply secure configurations to all system components

  protect_account_data:
    - Protect stored account data
    - Protect cardholder data with strong cryptography

  maintain_vulnerability_management:
    - Protect systems with anti-malware
    - Develop and maintain secure systems

  implement_access_control:
    - Restrict access to system components
    - Identify users and authenticate access
    - Restrict physical access

  monitor_test_networks:
    - Log and monitor all access to system components
    - Test security systems and processes regularly

  maintain_information_security_policy:
    - Support organizational security with policies
```

## CIS Benchmarks Implementation

### CIS AWS Foundations Benchmark

```bash
# Automated CIS benchmark scanning with Prowler
prowler -M csv,html,json

# Key controls to implement:
# 1.1 - Root account MFA
# 2.1 - CloudTrail enabled in all regions
# 3.1 - S3 bucket logging enabled
# 4.1 - Deny all default security group rules
# 5.1 - IAM password policy enforcement
```

### CIS Kubernetes Benchmark

```bash
# kube-bench for Kubernetes CIS benchmark
kube-bench run --targets master,node,policies

# Key controls:
# 1.2.1 - API server authentication
# 1.2.6 - Disable AlwaysAdmit
# 3.2.1 - Audit logging
# 5.1.1 - RBAC enabled
# 5.7.1 - Network policies
```

## Cloud Security Posture Management (CSPM)

### Multi-Cloud Security Assessment

```python
# CSPM automation with ScoutSuite
from scoutsuite import Scout

# Scan AWS environment
scout = Scout(provider='aws')
scout.run(services=['iam', 's3', 'ec2', 'rds'])

# Generate report
scout.export_report('html', 'aws-security-report.html')

# Key findings to track:
# - Unencrypted resources
# - Publicly accessible resources
# - Overly permissive IAM policies
# - Missing security controls
# - Compliance violations
```

## Compliance Automation

### Automated Evidence Collection

```yaml
# AWS Config rules for continuous compliance
config_rules:
  - rule_name: s3-bucket-encryption
    source: AWS_MANAGED
    compliance: required

  - rule_name: rds-encryption-enabled
    source: AWS_MANAGED
    compliance: required

  - rule_name: iam-password-policy
    source: AWS_MANAGED
    parameters:
      RequireUppercaseCharacters: true
      RequireLowercaseCharacters: true
      RequireSymbols: true
      RequireNumbers: true
      MinimumPasswordLength: 14
    compliance: required
```

## Best Practices

**Defense in Depth**: Multiple layers of security controls. Don't rely on single control.

**Least Privilege**: Grant minimum necessary permissions. Review and revoke regularly.

**Encryption Everywhere**: At rest and in transit. Use strong algorithms and key management.

**Continuous Compliance**: Automate evidence collection and monitoring. Don't wait for audits.

**Audit Everything**: Comprehensive logging with tamper-proof storage and retention.
