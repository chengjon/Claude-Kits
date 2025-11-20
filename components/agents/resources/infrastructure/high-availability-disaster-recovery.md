# High Availability & Disaster Recovery

Comprehensive strategies for designing resilient systems with high availability, disaster recovery, and business continuity.


## 📑 Table of Contents

- [High Availability Patterns](#high-availability-patterns)
  - [Multi-AZ (Availability Zone) Deployment](#multi-az-availability-zone-deployment)
  - [Multi-Region Strategies](#multi-region-strategies)
  - [Load Balancing Strategies](#load-balancing-strategies)
- [Disaster Recovery Planning](#disaster-recovery-planning)
  - [RTO and RPO Requirements](#rto-and-rpo-requirements)
  - [Disaster Recovery Testing](#disaster-recovery-testing)
  - [Failover Mechanisms](#failover-mechanisms)
- [Backup Strategies](#backup-strategies)
  - [Backup Types](#backup-types)
  - [Backup Best Practices](#backup-best-practices)
  - [Cloud-Native Backup Solutions](#cloud-native-backup-solutions)
- [Chaos Engineering](#chaos-engineering)
  - [Principles of Chaos Engineering](#principles-of-chaos-engineering)
  - [Failure Scenarios](#failure-scenarios)
  - [Chaos Engineering Tools](#chaos-engineering-tools)
  - [Chaos Engineering Best Practices](#chaos-engineering-best-practices)

---
## High Availability Patterns

### Multi-AZ (Availability Zone) Deployment

**Availability Zone Architecture**
- **Independent infrastructure**: Separate power, cooling, networking within same region
- **Low latency**: Typically <2ms between AZs in same region
- **Synchronous replication**: Maintain data consistency across zones
- **Automatic failover**: Load balancers detect and route around failures

**Best Practices**
- Deploy instances across at least 3 AZs for maximum resilience
- Use managed services with built-in multi-AZ (RDS Multi-AZ, ElastiCache)
- Configure load balancers for cross-zone load balancing
- Test failover scenarios regularly with chaos engineering

**Kubernetes Multi-AZ**
```yaml
# Zone-aware scheduling
apiVersion: v1
kind: Pod
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - critical-service
        topologyKey: topology.kubernetes.io/zone
```

**Cost vs Resilience Trade-offs**
- Single AZ: Lowest cost, vulnerable to zone failures
- Multi-AZ (2 zones): 2x cost, survives single zone failure
- Multi-AZ (3+ zones): 3x+ cost, highest resilience, recommended for production

### Multi-Region Strategies

**Active-Active (Multi-Master)**
- Traffic distributed across multiple regions simultaneously
- All regions handle read and write operations
- Requires conflict resolution for data synchronization
- Highest availability but most complex to implement

**Use Cases**
- Global applications with users worldwide
- Zero-downtime requirements (99.99%+ SLA)
- Performance optimization through geographic distribution
- Compliance requirements for data residency

**Implementation Considerations**
- **Database replication**: Multi-region databases (DynamoDB Global Tables, Cosmos DB, Spanner)
- **Data consistency**: Eventual consistency, conflict resolution strategies
- **Traffic routing**: GeoDNS, anycast, global load balancers (AWS Global Accelerator, Azure Front Door)
- **Cost**: 2x-3x infrastructure cost plus data transfer charges

**Active-Passive (Hot Standby)**
- Primary region handles all traffic
- Secondary region ready but idle, synchronously replicated
- Automatic or manual failover to secondary region
- Lower cost than active-active, higher complexity than cold standby

**Use Cases**
- Disaster recovery for critical applications
- Regional compliance requirements
- Cost-conscious high availability

**Implementation**
- **Database**: Read replicas in secondary region, promoted on failover
- **Traffic routing**: Health check-based DNS failover (Route 53, Traffic Manager)
- **Data synchronization**: Near real-time replication
- **RTO target**: Minutes to hours depending on automation level

**Warm Standby**
- Minimal infrastructure running in secondary region
- Scaled up during failover event
- Balance between cost and recovery time
- Common for non-critical applications

**Cold Standby**
- Data backups in secondary region, no running infrastructure
- Infrastructure created from IaC during disaster
- Lowest cost, highest recovery time (hours to days)
- Suitable for non-critical systems with lenient RTO requirements

### Load Balancing Strategies

**Layer 4 (Network) Load Balancing**
- TCP/UDP traffic distribution
- Fast (low latency), simple routing decisions
- No content inspection, limited routing rules
- Use case: Database connections, non-HTTP protocols

**Layer 7 (Application) Load Balancing**
- HTTP/HTTPS traffic with content-based routing
- Path-based, host-based, header-based routing
- SSL termination, Web Application Firewall integration
- Use case: Microservices, API gateways, web applications

**Global Load Balancing**
- **GeoDNS**: Route based on user geographic location
- **Anycast**: Same IP announced from multiple locations, routing via BGP
- **Global accelerators**: AWS Global Accelerator, Azure Front Door, Cloudflare
- **Health-based routing**: Automatic failover to healthy regions

**Session Persistence**
- **Sticky sessions**: Route same user to same instance (can cause imbalance)
- **Session replication**: Share session state across instances
- **External session store**: Redis, Memcached for shared session data
- **Stateless design**: Encode session in JWT, no server-side storage (preferred)

## Disaster Recovery Planning

### RTO and RPO Requirements

**Recovery Time Objective (RTO)**
- Maximum acceptable downtime after disaster
- Drives infrastructure design and failover automation
- Examples:
  - Tier 1 (Critical): RTO <1 hour, active-active or hot standby
  - Tier 2 (Important): RTO <4 hours, warm standby
  - Tier 3 (Standard): RTO <24 hours, cold standby or backup restoration

**Recovery Point Objective (RPO)**
- Maximum acceptable data loss measured in time
- Drives backup frequency and replication strategy
- Examples:
  - Tier 1 (Critical): RPO <1 minute, synchronous replication
  - Tier 2 (Important): RPO <15 minutes, frequent snapshots
  - Tier 3 (Standard): RPO <24 hours, daily backups

**Cost vs Requirements**
```
┌─────────────────────────────────────────────────┐
│ RTO/RPO   │ Strategy       │ Relative Cost    │
├───────────┼────────────────┼──────────────────┤
│ Minutes   │ Active-Active  │ 300-500%         │
│ Hours     │ Hot Standby    │ 150-200%         │
│ Hours     │ Warm Standby   │ 120-150%         │
│ Days      │ Cold Standby   │ 105-120%         │
│ Weeks     │ Backup Only    │ 100% (baseline)  │
└─────────────────────────────────────────────────┘
```

### Disaster Recovery Testing

**Testing Types**
- **Walkthrough**: Review procedures with team, identify gaps
- **Tabletop exercise**: Simulate scenario, discuss responses without executing
- **Parallel test**: Activate DR environment, validate without impacting production
- **Full failover test**: Complete failover to DR, most realistic but highest risk

**Testing Frequency**
- Critical systems: Quarterly full tests, monthly tabletop
- Important systems: Semi-annual full tests, quarterly tabletop
- Standard systems: Annual full tests, semi-annual tabletop

**GameDay Events**
- Scheduled chaos engineering exercises
- Simulate realistic failure scenarios (region outage, database failure, network partition)
- Involve entire team in response
- Document lessons learned and update runbooks

### Failover Mechanisms

**Automated Failover**
- Health check monitoring (endpoint, database connection, business logic)
- Automatic traffic redirection (DNS, load balancer)
- Database promotion (read replica to primary)
- Notification to on-call team
- Reduced RTO but requires careful testing to avoid false positives

**Manual Failover**
- Human validation before failover decision
- Lower risk of false positives
- Higher RTO due to decision time
- Appropriate for less critical systems or complex scenarios

**Failover Procedures**
1. **Detection**: Monitoring alerts on service degradation
2. **Validation**: Confirm widespread failure, not transient issue
3. **Decision**: Go/no-go decision based on severity
4. **Execution**: Run failover automation or manual steps
5. **Verification**: Confirm services operational in DR site
6. **Communication**: Notify stakeholders of DR activation
7. **Investigation**: Root cause analysis of primary site failure
8. **Failback**: Plan and execute return to primary site

## Backup Strategies

### Backup Types

**Full Backup**
- Complete copy of all data
- Slowest to create, fastest to restore
- High storage cost
- Typically performed weekly or monthly

**Incremental Backup**
- Only data changed since last backup (full or incremental)
- Fastest to create, slower to restore (need full + all incrementals)
- Lowest storage cost
- Typically performed hourly or daily

**Differential Backup**
- All data changed since last full backup
- Medium creation time, medium restore time (need full + latest differential)
- Medium storage cost
- Typically performed daily

**Snapshot**
- Point-in-time copy using copy-on-write
- Very fast creation (seconds), instant restoration
- Supported by cloud storage (EBS snapshots, Azure Managed Disks)
- Use case: Database backups, volume backups, disaster recovery

### Backup Best Practices

**3-2-1 Backup Rule**
- **3** copies of data (production + 2 backups)
- **2** different storage media (disk, tape, cloud)
- **1** copy offsite (different region or provider)

**Backup Automation**
- Scheduled backups with cloud-native tools (AWS Backup, Azure Backup)
- Automated testing of restore procedures
- Retention policies (daily for 7 days, weekly for 4 weeks, monthly for 12 months)
- Lifecycle policies for cost optimization (move old backups to glacier/archive)

**Backup Encryption**
- Encrypt backups at rest and in transit
- Separate encryption keys from backup storage
- Test encrypted backup restoration regularly
- Compliance requirements (HIPAA, PCI-DSS, GDPR)

**Backup Monitoring**
- Verify backup completion and integrity
- Alert on failed backups
- Track backup size trends (unexpected growth may indicate issues)
- Regularly test restoration (monthly for critical systems)

### Cloud-Native Backup Solutions

**Kubernetes Backup - Velero**
```yaml
# Velero backup schedule
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  template:
    includedNamespaces:
    - production
    - staging
    storageLocation: aws-s3-backup
    volumeSnapshotLocations:
    - aws-ebs
    ttl: 720h  # 30 days retention
```

**AWS Backup**
- Centralized backup across AWS services (EC2, RDS, EBS, EFS, DynamoDB)
- Backup plans with schedules and retention rules
- Cross-region and cross-account backup copy
- Compliance reporting and backup audit

**Azure Backup**
- Azure VMs, SQL databases, file shares, Blob storage
- Application-consistent backups
- Long-term retention with archive tier
- Soft delete for ransomware protection

**Database Backup Strategies**
- **Continuous backup**: Point-in-time restore (RDS automated backups, Azure SQL)
- **Snapshot backup**: Consistent point-in-time copy
- **Logical backup**: Export data (pg_dump, mysqldump) for portability
- **Transaction log backup**: Capture changes for point-in-time recovery

## Chaos Engineering

### Principles of Chaos Engineering

**Purpose**
- Discover weaknesses before they manifest in production
- Build confidence in system resilience
- Verify monitoring and alerting effectiveness
- Improve incident response capabilities

**Methodology**
1. **Define steady state**: Normal system behavior metrics
2. **Hypothesis**: System will maintain steady state during disruption
3. **Introduce variables**: Inject realistic failures
4. **Measure**: Compare actual vs expected behavior
5. **Learn**: Document findings, improve system

### Failure Scenarios

**Infrastructure Failures**
- Server shutdown (terminate EC2 instance, kill pod)
- Availability zone outage (network partition, power loss)
- Region failure (complete region unavailable)
- Resource exhaustion (CPU, memory, disk space)

**Network Failures**
- Latency injection (add delay to requests)
- Packet loss (drop percentage of network packets)
- Network partition (split brain scenarios)
- DNS failures (unresolvable hostnames)

**Application Failures**
- Exception injection (random errors in code path)
- Dependency failures (downstream service unavailable)
- Resource limits (connection pool exhaustion)
- Traffic spikes (sudden load increase)

### Chaos Engineering Tools

**Chaos Monkey (Netflix)**
- Randomly terminates instances in production
- Validates auto-scaling and recovery mechanisms
- Ensures no single instance is irreplaceable

**Litmus Chaos**
- Kubernetes-native chaos engineering platform
- Pre-built chaos experiments (pod delete, network latency, node drain)
- GitOps integration for declarative chaos workflows

**AWS Fault Injection Simulator**
- Managed chaos engineering service
- Safe failure injection for EC2, EKS, RDS, DynamoDB
- Progressive experiments with rollback on degradation

**Gremlin**
- Commercial chaos engineering platform
- Comprehensive failure scenarios
- Safety controls and guardrails
- Team collaboration and experiment sharing

### Chaos Engineering Best Practices

**Start Small**
- Begin in non-production environments
- Simple experiments (terminate single instance)
- Gradually increase complexity and scope

**Blast Radius Limit**
- Limit impact to small percentage of traffic
- Use canary regions or test namespaces
- Automatic halt on unexpected behavior

**Business Hours**
- Run experiments during working hours
- Team available to observe and respond
- Avoid holidays and high-traffic periods

**Monitoring and Observability**
- Comprehensive metrics collection
- Distributed tracing for failure correlation
- Alerting validation during experiments
