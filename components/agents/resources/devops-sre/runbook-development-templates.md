# Runbook Development & Management

Complete templates and best practices for creating effective operational runbooks.


## 📑 Table of Contents

- [Runbook Philosophy](#runbook-philosophy)
  - [Why Runbooks Matter](#why-runbooks-matter)
  - [Runbook vs. Automation](#runbook-vs-automation)
- [Runbook Template](#runbook-template)
- [Runbook Best Practices](#runbook-best-practices)
  - [Structure](#structure)
  - [Writing Style](#writing-style)
  - [Maintenance](#maintenance)
  - [Automation Path](#automation-path)
- [Common Runbook Scenarios](#common-runbook-scenarios)
  - [Service Health Issues](#service-health-issues)
  - [Deployment Problems](#deployment-problems)
  - [Infrastructure Issues](#infrastructure-issues)
  - [Data Issues](#data-issues)
  - [Security Incidents](#security-incidents)

---
## Runbook Philosophy

### Why Runbooks Matter
- **Consistency**: Standardize incident response across team
- **Speed**: Faster resolution with predefined procedures
- **Training**: Onboard new team members effectively
- **Knowledge capture**: Document tribal knowledge
- **Continuous improvement**: Evolve based on incident learnings

### Runbook vs. Automation
- **Runbooks**: Manual procedures for humans to execute
- **Goal**: Convert runbooks into automated remediation
- **Interim**: Runbooks bridge manual→automated transition
- **Complex scenarios**: Some situations require human judgment

## Runbook Template

```markdown
# Runbook: [Service Name] - [Scenario Name]

**Service**: [Service Name]
**Severity**: P0 | P1 | P2 | P3
**Last Updated**: YYYY-MM-DD
**Owner**: [Team Name]

## Overview

Brief description of when to use this runbook and what problem it addresses.

## Prerequisites

- Access to production Kubernetes cluster
- kubectl configured with production context
- Access to monitoring dashboards
- PagerDuty/Opsgenie access
- Slack war room creation permissions

## Symptoms

- [ ] High error rate (> 1%) in API responses
- [ ] Increased latency (p95 > 1 second)
- [ ] Database connection errors
- [ ] Failed health checks
- [ ] User reports of service unavailability

## Impact Assessment

**User Impact**: [Describe how users are affected]
**Business Impact**: [Describe business/revenue impact]
**SLA Impact**: [Describe SLA implications]

## Initial Diagnosis

### Step 1: Check Service Health

```bash
# Check deployment status
kubectl get deployment [service-name] -n production

# Check pod status
kubectl get pods -l app=[service-name] -n production -o wide

# Check recent events
kubectl get events -n production --sort-by='.lastTimestamp' | grep [service-name] | tail -20
```

**Expected**: All pods in Running state, no recent error events
**If not**: Proceed to Step 2

### Step 2: Check Error Logs

```bash
# Get recent error logs
kubectl logs -n production -l app=[service-name] --tail=100 --timestamps=true \
  | grep -i -E 'error|exception|fatal'

# Get logs from specific pod if needed
kubectl logs -n production [pod-name] --tail=200
```

**Look for**: Database errors, timeout errors, null pointer exceptions, authentication failures

### Step 3: Check Resource Usage

```bash
# Check CPU and memory usage
kubectl top pods -n production -l app=[service-name]

# Check node resources
kubectl top nodes
```

**Red flags**: Memory > 90%, CPU throttling, OOMKilled events

### Step 4: Check Dependencies

```bash
# Check database connectivity
kubectl exec -it [pod-name] -n production -- /bin/sh -c \
  "pg_isready -h $DB_HOST || echo 'DB connection failed'"

# Check external API connectivity
kubectl exec -it [pod-name] -n production -- curl -v https://external-api.com/health
```

**Expected**: All dependencies responding normally

## Resolution Steps

### Scenario A: Recent Deployment Causing Issues

**Symptoms**: Error rate increased immediately after deployment

**Steps**:

1. **Verify deployment correlation**:
   ```bash
   kubectl rollout history deployment/[service-name] -n production | head -5
   ```

2. **Initiate rollback**:
   ```bash
   kubectl rollout undo deployment/[service-name] -n production
   ```

3. **Monitor rollback progress**:
   ```bash
   kubectl rollout status deployment/[service-name] -n production
   ```

4. **Verify service recovery**:
   - Check error rate in monitoring dashboard
   - Verify p95 latency returns to baseline
   - Check user reports

5. **Notify stakeholders**: Post status update on status page

**Time estimate**: 5-10 minutes

### Scenario B: Resource Exhaustion

**Symptoms**: High memory usage, OOMKilled events, CPU throttling

**Steps**:

1. **Identify resource bottleneck**:
   ```bash
   kubectl top pods -n production -l app=[service-name]
   kubectl describe pod [pod-name] -n production | grep -A 5 "Limits:"
   ```

2. **Immediate scaling**:
   ```bash
   # Scale up replicas
   kubectl scale deployment [service-name] --replicas=10 -n production
   ```

3. **Monitor recovery**:
   ```bash
   watch kubectl get pods -l app=[service-name] -n production
   ```

4. **Long-term fix**: Update resource limits in deployment manifest

**Time estimate**: 3-5 minutes

### Scenario C: Database Connection Issues

**Symptoms**: Database timeout errors, connection pool exhaustion

**Steps**:

1. **Check database health**:
   ```bash
   # From application pod
   kubectl exec -it [pod-name] -n production -- psql -h $DB_HOST -U $DB_USER -c "SELECT 1;"
   ```

2. **Check connection pool metrics**:
   - Navigate to database monitoring dashboard
   - Check active connections vs max connections
   - Check connection pool wait time

3. **If connection pool exhausted**:
   - Option A: Increase connection pool size (requires deployment)
   - Option B: Reduce application replicas temporarily
   - Option C: Restart application pods to reset connections

4. **Rolling restart**:
   ```bash
   kubectl rollout restart deployment/[service-name] -n production
   ```

**Time estimate**: 5-15 minutes

## Escalation

**Level 1**: On-call engineer (you)
**Level 2**: Senior SRE ([slack-handle], [phone])
**Level 3**: Engineering Manager ([slack-handle], [phone])
**Level 4**: VP Engineering ([slack-handle], [phone])

**Escalate if**:
- Issue not resolved within 30 minutes
- Impact severity increases
- Root cause unclear
- Requires architectural changes

## Communication Template

```
[INCIDENT] [Service Name] - [Brief Description]

Status: Investigating | Identified | Monitoring | Resolved
Severity: P0 | P1 | P2
Impact: [X] users affected, [Y]% error rate
Started: HH:MM UTC
ETA: [Best estimate or "investigating"]

Current actions:
- [Action being taken]

Updates will be posted every 15 minutes.

War room: #incident-[timestamp]
Incident Commander: @[name]
```

## Post-Incident

- [ ] Service fully recovered and stable for 1 hour
- [ ] Status page updated with resolution
- [ ] Incident timeline documented
- [ ] Postmortem scheduled within 48 hours
- [ ] Monitoring alerts reviewed and adjusted
- [ ] Runbook updated with new learnings

## Related Documentation

- Service architecture diagram: [link]
- Deployment process: [link]
- Monitoring dashboards: [link]
- Previous incidents: [link]
- Configuration repository: [link]

## Metrics & SLOs

**Availability SLO**: 99.9% uptime
**Latency SLO**: p95 < 500ms
**Error Rate SLO**: < 1%

**Current error budget**: [Check dashboard]

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-11 | SRE Team | Initial creation |
```

## Runbook Best Practices

### Structure
- **Clear title**: Service name + scenario
- **Prerequisites**: List required access and tools
- **Symptoms**: Checklist of observable issues
- **Impact assessment**: Help triage severity
- **Step-by-step procedures**: Numbered, sequential actions
- **Expected outcomes**: What success looks like at each step
- **Time estimates**: How long each scenario takes
- **Escalation path**: When and how to escalate

### Writing Style
- **Action-oriented**: Use imperative verbs ("Check", "Run", "Verify")
- **Specific**: Exact commands, not vague instructions
- **Copy-paste ready**: Commands that work as-is
- **Decision trees**: "If X, then Y; otherwise Z"
- **Safety notes**: Warnings about destructive operations

### Maintenance
- **Review after incidents**: Update based on learnings
- **Regular testing**: Validate procedures periodically
- **Version control**: Track changes over time
- **Ownership**: Assign team/person responsible
- **Deprecation**: Remove outdated runbooks

### Automation Path
- **Identify patterns**: Repeatable runbooks → automation candidates
- **Start simple**: Automate read-only checks first
- **Add guardrails**: Safety mechanisms for automated actions
- **Gradual transition**: Semi-automated → fully automated
- **Keep runbooks**: Fallback when automation fails

## Common Runbook Scenarios

### Service Health Issues
- High error rates
- Increased latency
- Failed health checks
- Pod crash loops
- Resource exhaustion

### Deployment Problems
- Failed deployments
- Rollback procedures
- Configuration errors
- Image pull failures
- Migration issues

### Infrastructure Issues
- Node failures
- Network partitions
- Storage problems
- DNS resolution failures
- Load balancer issues

### Data Issues
- Database connection problems
- Replication lag
- Query performance
- Data corruption
- Backup/restore procedures

### Security Incidents
- Credential rotation
- Access revocation
- DDoS mitigation
- Certificate expiration
- Security patch deployment
