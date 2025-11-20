# Network & Security Architecture

Comprehensive guide to network design, security architecture, and zero-trust implementation for cloud-native infrastructure.


## 📑 Table of Contents

- [Network Topology Design](#network-topology-design)
  - [VPC (Virtual Private Cloud) Architecture](#vpc-virtual-private-cloud-architecture)
  - [Multi-VPC Strategies](#multi-vpc-strategies)
  - [VPN and Direct Connect](#vpn-and-direct-connect)
- [Security Architecture](#security-architecture)
  - [Zero-Trust Architecture](#zero-trust-architecture)
  - [Defense in Depth](#defense-in-depth)
  - [VPC Security](#vpc-security)
  - [Firewall Configuration](#firewall-configuration)
  - [DDoS Protection](#ddos-protection)
- [Identity and Access Management](#identity-and-access-management)
  - [IAM Best Practices](#iam-best-practices)
  - [Service Account Management](#service-account-management)
  - [Secrets Management](#secrets-management)
  - [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
- [Network Policies](#network-policies)
  - [Kubernetes Network Policies](#kubernetes-network-policies)
  - [Service Mesh Security](#service-mesh-security)
  - [Compliance and Governance](#compliance-and-governance)

---
## Network Topology Design

### VPC (Virtual Private Cloud) Architecture

**VPC Design Principles**
- **Network segmentation**: Isolate workloads by environment, tier, or sensitivity
- **CIDR planning**: Choose non-overlapping address ranges for multi-VPC architectures
- **Subnet strategy**: Public, private, and isolated subnets for different purposes
- **High availability**: Subnets across multiple availability zones

**Typical VPC Layout**
```
VPC: 10.0.0.0/16 (65,536 IPs)

Availability Zone A:
  - Public Subnet:    10.0.1.0/24 (256 IPs) - Load balancers, NAT gateways
  - Private Subnet:   10.0.11.0/24 (256 IPs) - Application servers
  - Database Subnet:  10.0.21.0/24 (256 IPs) - Databases, data stores

Availability Zone B:
  - Public Subnet:    10.0.2.0/24
  - Private Subnet:   10.0.12.0/24
  - Database Subnet:  10.0.22.0/24

Availability Zone C:
  - Public Subnet:    10.0.3.0/24
  - Private Subnet:   10.0.13.0/24
  - Database Subnet:  10.0.23.0/24
```

**Subnet Types**
- **Public subnets**: Route to Internet Gateway, public IP addresses, bastion hosts, load balancers
- **Private subnets**: Route to NAT Gateway for outbound only, application tier
- **Isolated subnets**: No internet access, database tier, highly sensitive workloads

**CIDR Planning Best Practices**
- Reserve large CIDR blocks for growth (at least /16 for VPC)
- Align with organizational IP allocation policy
- Avoid overlapping with on-premises networks
- Document IP allocation in central registry
- Consider future VPC peering requirements

### Multi-VPC Strategies

**VPC Peering**
- Direct network connection between VPCs
- Non-transitive (must explicitly peer each VPC pair)
- Low latency, no bandwidth bottleneck
- Use case: Connect production and shared services VPCs

**Transit Gateway**
- Hub-and-spoke topology connecting multiple VPCs and on-premises
- Transitive routing (VPCs can communicate through hub)
- Centralized routing and security policies
- Use case: Enterprise with 10+ VPCs and hybrid cloud

**VPC Sharing (AWS Resource Access Manager)**
- Share subnets across AWS accounts
- Centralized network management
- Account isolation with shared infrastructure
- Use case: Multi-account organization with centralized networking

### VPN and Direct Connect

**Site-to-Site VPN**
- Encrypted IPsec tunnels over internet
- Quick to set up (hours), cost-effective
- Variable latency and throughput (internet dependent)
- Use case: Development, staging, temporary connections

**AWS Direct Connect / Azure ExpressRoute / Google Cloud Interconnect**
- Dedicated physical connection to cloud provider
- Consistent latency, higher throughput (1-100 Gbps)
- Longer setup time (weeks-months), higher cost
- Use case: Production hybrid cloud, high bandwidth requirements, regulatory compliance

**Hybrid Architecture**
- Primary connection: Direct Connect for production traffic
- Backup connection: VPN for failover and redundancy
- Multiple Direct Connect locations for resilience

## Security Architecture

### Zero-Trust Architecture

**Core Principles**
- **Never trust, always verify**: No implicit trust based on network location
- **Least privilege access**: Minimal permissions for users and services
- **Assume breach**: Design as if attackers are already inside network
- **Verify explicitly**: Authenticate and authorize every request
- **Micro-segmentation**: Isolate workloads and limit lateral movement

**Implementation Components**
- **Identity-based access**: Strong authentication (MFA, SSO, certificate-based)
- **Device posture verification**: Check device health before granting access
- **Network segmentation**: Micro-segmentation with security groups and network policies
- **Encryption everywhere**: TLS for all traffic, even internal
- **Continuous monitoring**: Real-time threat detection and response

**Zero-Trust in Kubernetes**
```yaml
# Network policy for zero-trust micro-segmentation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-service-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Only allow traffic from frontend service
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  # Only allow traffic to database and external APIs
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector:
        matchLabels:
          name: external-apis
```

### Defense in Depth

**Layered Security Strategy**
1. **Perimeter security**: Firewall, DDoS protection, WAF at edge
2. **Network security**: VPC, security groups, network ACLs, network policies
3. **Host security**: OS hardening, patch management, endpoint protection
4. **Application security**: Input validation, authentication, authorization
5. **Data security**: Encryption at rest and in transit, access controls
6. **Monitoring**: SIEM, intrusion detection, anomaly detection

**Security Layers**
```
┌─────────────────────────────────────────────────┐
│  Monitoring & Logging (CloudTrail, GuardDuty)  │
├─────────────────────────────────────────────────┤
│  Identity & Access (IAM, RBAC, Service Mesh)   │
├─────────────────────────────────────────────────┤
│  Application (Code scanning, SAST/DAST)        │
├─────────────────────────────────────────────────┤
│  Runtime (Container scanning, Falco, Sysdig)   │
├─────────────────────────────────────────────────┤
│  Network (Security groups, Network policies)   │
├─────────────────────────────────────────────────┤
│  Infrastructure (WAF, DDoS, Firewall)          │
└─────────────────────────────────────────────────┘
```

### VPC Security

**Security Groups (Stateful Firewall)**
- Instance-level firewall controlling inbound and outbound traffic
- Stateful: Return traffic automatically allowed
- Allow rules only (no deny rules)
- Can reference other security groups as source/destination
- Best practice: Default deny all, explicitly allow required traffic

**Network ACLs (Stateless Firewall)**
- Subnet-level firewall
- Stateless: Must explicitly allow return traffic
- Both allow and deny rules
- Evaluated in rule number order
- Use case: Additional defense layer, block specific IPs/ranges

**Security Group Best Practices**
```
# Database security group - only allow from application tier
Inbound:
  - Port 5432, Source: app-tier-sg (PostgreSQL)
  - Port 22, Source: bastion-sg (SSH for maintenance)

Outbound:
  - All traffic (default, can be restricted for sensitive workloads)

# Application security group
Inbound:
  - Port 8080, Source: load-balancer-sg (Application traffic)
  - Port 22, Source: bastion-sg (SSH)

# Load balancer security group
Inbound:
  - Port 443, Source: 0.0.0.0/0 (HTTPS from internet)
  - Port 80, Source: 0.0.0.0/0 (HTTP, redirect to HTTPS)
```

### Firewall Configuration

**Web Application Firewall (WAF)**
- **OWASP Top 10 protection**: SQL injection, XSS, CSRF, etc.
- **Rate limiting**: Prevent DDoS and abuse
- **Geo-blocking**: Block traffic from specific countries
- **Custom rules**: Block based on IP, headers, request patterns
- **Managed rule sets**: AWS Managed Rules, Azure Front Door rules

**WAF Deployment**
- CloudFront/ALB (AWS), Azure Front Door, Cloud Armor (GCP)
- Monitor blocked requests, tune rules to reduce false positives
- Use logging for security analytics and threat intelligence

**Next-Generation Firewall**
- Deep packet inspection (DPI)
- Application awareness (not just port/protocol)
- Intrusion prevention system (IPS)
- SSL/TLS inspection for encrypted traffic
- Use case: Enterprise perimeter, high-security environments

### DDoS Protection

**Layer 3/4 DDoS (Network/Transport)**
- SYN flood, UDP flood, ICMP flood
- Mitigation: Auto-scaling, rate limiting, traffic filtering
- Cloud provider protection: AWS Shield, Azure DDoS Protection, Cloud Armor

**Layer 7 DDoS (Application)**
- HTTP floods targeting application endpoints
- Mitigation: WAF rate limiting, CAPTCHAs, bot detection
- More complex and harder to distinguish from legitimate traffic

**DDoS Protection Tiers**
- **Basic/Standard**: Included with cloud provider, automatic detection and mitigation
- **Advanced/Premium**: Enhanced protection, DDoS response team, cost protection
- Use case: Critical public-facing applications, e-commerce, gaming

## Identity and Access Management

### IAM Best Practices

**Principle of Least Privilege**
- Grant minimum permissions necessary for task
- Start with no permissions, add as needed
- Regular access reviews and permission audits
- Time-limited credentials for temporary access

**IAM Policy Structure**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/data/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

**Role-Based Access Control (RBAC)**
- Define roles based on job function (developer, operator, auditor)
- Assign users to roles, not individual permissions
- Centralized role management
- Easier to audit and maintain

**Kubernetes RBAC**
```yaml
# Role for read-only access to pods and logs
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: jane@example.com
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Service Account Management

**Cloud IAM Roles for Service Accounts**
- **AWS IRSA** (IAM Roles for Service Accounts): Kubernetes service accounts assume IAM roles
- **Azure AAD Pod Identity**: Azure AD identities for Kubernetes pods
- **GCP Workload Identity**: Google Cloud IAM for GKE workloads

**Benefits**
- No static credentials in code or config
- Fine-grained permissions per service
- Automatic credential rotation
- Audit trail of service actions

**IRSA Implementation**
```yaml
# Kubernetes service account with IAM role annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  name: s3-reader
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/s3-reader-role
---
# Pod using the service account
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  serviceAccountName: s3-reader
  containers:
  - name: app
    image: my-app:v1
    # AWS SDK automatically uses IRSA credentials
```

### Secrets Management

**Cloud-Native Secret Stores**
- **AWS Secrets Manager**: Automatic rotation, versioning, fine-grained access
- **Azure Key Vault**: Secrets, keys, certificates, HSM support
- **Google Secret Manager**: Centralized secret storage with replication
- **HashiCorp Vault**: Multi-cloud, dynamic secrets, encryption as a service

**Kubernetes Secrets**
- Base64 encoded (not encrypted by default)
- Encrypted at rest with KMS integration (enable encryption-at-rest)
- Never commit secrets to Git
- Use External Secrets Operator or Sealed Secrets for GitOps

**External Secrets Operator**
```yaml
# Sync secret from AWS Secrets Manager to Kubernetes
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: database-credentials
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: prod/database/password
```

**Secret Rotation**
- Automatic rotation for database credentials, API keys
- Zero-downtime rotation with dual-credential periods
- Monitoring and alerting on rotation failures
- Compliance requirements (rotate every 90 days)

### Multi-Factor Authentication (MFA)

**MFA Enforcement**
- Require MFA for all human access (console, CLI, API)
- Hardware tokens (YubiKey, FIDO2) for highest security
- Software tokens (Google Authenticator, Authy) for convenience
- SMS backup (least secure, avoid if possible)

**Conditional Access**
- Require MFA for sensitive actions (IAM changes, production access)
- Risk-based authentication (unusual location, new device)
- Compliance requirements (PCI-DSS, HIPAA)

## Network Policies

### Kubernetes Network Policies

**Default Deny Policy**
```yaml
# Block all traffic by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

**Namespace Isolation**
```yaml
# Only allow traffic within same namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: namespace-isolation
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}  # Same namespace only
```

**Egress Restrictions**
```yaml
# Restrict egress to specific destinations
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes:
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
  # Allow specific external API
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

### Service Mesh Security

**Mutual TLS (mTLS)**
- Automatic encryption of all service-to-service traffic
- Certificate-based service identity
- Automatic certificate rotation
- No code changes required

**Authorization Policies**
```yaml
# Istio authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend-to-api
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/*"]
```

### Compliance and Governance

**Regulatory Frameworks**
- **PCI-DSS**: Payment card data security
- **HIPAA**: Healthcare data privacy
- **GDPR**: EU data protection regulation
- **SOC 2**: Trust service criteria for service organizations
- **FedRAMP**: US government cloud security

**Compliance Automation**
- **AWS Config / Azure Policy / GCP Organization Policy**: Continuous compliance monitoring
- **Policy as Code**: Open Policy Agent (OPA), Gatekeeper, Kyverno
- **Automated remediation**: Automatically fix non-compliant resources
- **Compliance dashboards**: Real-time compliance posture visibility
