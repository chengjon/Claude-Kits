# Security Incident Response & Forensics

Comprehensive incident response procedures, forensic investigation techniques, threat hunting methodologies, and automated response playbooks.


## 📑 Table of Contents

- [Security Incident Response Plan](#security-incident-response-plan)
  - [Phase 1: Detection & Alerting (T+0)](#phase-1-detection-alerting-t0)
  - [Phase 2: Containment (T+15 minutes)](#phase-2-containment-t15-minutes)
  - [Phase 3: Investigation (T+1 hour)](#phase-3-investigation-t1-hour)
  - [Phase 4: Eradication (T+6 hours)](#phase-4-eradication-t6-hours)
  - [Phase 5: Recovery (T+24 hours)](#phase-5-recovery-t24-hours)
  - [Phase 6: Post-Incident (T+7 days)](#phase-6-post-incident-t7-days)
- [Automated Response Playbooks](#automated-response-playbooks)
  - [SOAR Integration for Automated Incident Response](#soar-integration-for-automated-incident-response)
- [Forensics Investigation](#forensics-investigation)
  - [Evidence Collection](#evidence-collection)
  - [Timeline Analysis](#timeline-analysis)
- [Threat Hunting](#threat-hunting)
  - [Proactive Threat Hunting Queries](#proactive-threat-hunting-queries)
  - [Threat Intelligence Integration](#threat-intelligence-integration)
- [Security Monitoring & Alerting](#security-monitoring-alerting)
  - [Detection Rules (Sigma Format)](#detection-rules-sigma-format)
  - [SIEM Alert Correlation](#siem-alert-correlation)
- [Forensics Tools](#forensics-tools)
- [Best Practices](#best-practices)

---
## Security Incident Response Plan

### Phase 1: Detection & Alerting (T+0)

**Time**: Continuous monitoring

**Triggers**:
- Alert from SIEM (anomalous login, failed auth, suspicious traffic)
- Alert from IDS/IPS (attack pattern detected)
- Alert from endpoint detection (malware detected)
- User report

**Actions**:
- Confirm incident status
- Assign incident commander
- Create incident channel (Slack/Teams)
- Begin incident logging

### Phase 2: Containment (T+15 minutes)

**Goal**: Stop ongoing attack and prevent spread

**Actions**:
- Isolate affected systems (network isolation)
- Disable compromised credentials
- Block malicious IPs/domains
- Kill suspicious processes
- Preserve forensic evidence (memory dumps, logs)

**Escalation**:
- Critical: Notify CISO immediately
- High: Notify Security Leadership
- Medium: Notify Team Lead
- Low: Log for review

### Phase 3: Investigation (T+1 hour)

**Forensic Analysis**:
- Timeline reconstruction
- Identify entry point
- Map lateral movement
- Identify exfiltrated data

**Threat Intelligence**:
- Compare with threat feeds
- Identify attacker TTPs
- Correlate with other incidents

### Phase 4: Eradication (T+6 hours)

**Remediation**:
- Patch vulnerabilities
- Remove malware
- Reset compromised credentials
- Update firewall rules

**Validation**:
- Verify malware removal
- Confirm access controls
- Test recovery procedures

### Phase 5: Recovery (T+24 hours)

**Restoration**:
- Restore from clean backups
- Bring systems online
- Monitor for reinfection
- Verify functionality

### Phase 6: Post-Incident (T+7 days)

**Analysis**:
- Document lessons learned
- Update security controls
- Improve detection rules
- Train team on findings

**Communication**:
- Notify affected users
- Prepare for regulatory reporting
- Update incident documentation

**SLAs**:
- Critical: Contain within 1 hour, resolve within 24 hours
- High: Contain within 4 hours, resolve within 72 hours
- Medium: Contain within 8 hours, resolve within 1 week
- Low: Review within 1 week

## Automated Response Playbooks

### SOAR Integration for Automated Incident Response

```typescript
// SOAR integration for automated incident response
interface IncidentResponsePlaybook {
  // Malware detection → Automated response
  malwareDetected: {
    triggers: ['AV detection', 'Behavioral analysis', 'Threat intel match'],
    automatedActions: [
      'Isolate endpoint from network',
      'Kill process and child processes',
      'Capture memory dump for analysis',
      'Disable user account',
      'Create forensic snapshot',
      'Alert security team',
    ],
    manualReview: 'Security analyst within 15 minutes',
  };

  // Credential compromise → Automated response
  credentialCompromise: {
    triggers: ['Multiple failed logins', 'Credential found in breach database'],
    automatedActions: [
      'Force password reset',
      'Revoke active sessions',
      'Require MFA re-enrollment',
      'Review account activity',
      'Block suspicious IPs',
    ],
  };

  // Data exfiltration → Automated response
  dataExfiltration: {
    triggers: ['Unusual data access patterns', 'Large data transfers to external IP'],
    automatedActions: [
      'Block destination IP',
      'Kill session',
      'Preserve audit logs',
      'Snapshot filesystem',
      'Alert data protection team',
    ],
  };
}
```

## Forensics Investigation

### Evidence Collection

```bash
# Memory dump acquisition (Linux)
sudo lime-forensics /dev/mem > memory.dump

# Disk imaging
sudo dd if=/dev/sda of=/mnt/evidence/disk.img bs=4M status=progress

# Preserve volatile data
ps aux > running_processes.txt
netstat -anp > network_connections.txt
lsof > open_files.txt

# Log collection
tar -czf logs_$(date +%Y%m%d_%H%M%S).tar.gz /var/log/
```

### Timeline Analysis

```bash
# Generate timeline from filesystem metadata
fls -r -m / /dev/sda1 > filesystem_timeline.body
mactime -b filesystem_timeline.body -d > timeline.csv

# Parse web server logs
cat access.log | awk '{print $1, $4, $7}' | sort -k2

# Correlate events across multiple sources
log2timeline.py --storage-file timeline.plaso /mnt/evidence/
psort.py -o dynamic timeline.plaso
```

## Threat Hunting

### Proactive Threat Hunting Queries

```sql
-- Hunt for unusual process creation
SELECT
  datetime,
  hostname,
  username,
  process_name,
  command_line
FROM process_events
WHERE process_name NOT IN (SELECT name FROM known_good_processes)
  AND parent_process_name IN ('cmd.exe', 'powershell.exe', 'wscript.exe')
ORDER BY datetime DESC;

-- Hunt for lateral movement
SELECT
  src_ip,
  dst_ip,
  COUNT(*) as connection_count
FROM network_connections
WHERE dst_port IN (445, 3389, 5985, 5986)
GROUP BY src_ip, dst_ip
HAVING connection_count > 10;

-- Hunt for credential dumping
SELECT
  datetime,
  hostname,
  process_name,
  command_line
FROM process_events
WHERE command_line LIKE '%lsass%'
   OR command_line LIKE '%mimikatz%'
   OR command_line LIKE '%procdump%';
```

### Threat Intelligence Integration

```python
# MISP threat intelligence integration
import pymisp

misp = pymisp.PyMISP('https://misp.local', api_key, ssl=True)

# Search for IOCs
iocs = misp.search(value='192.168.1.100', type_attribute='ip-dst')

# Enrich incident with threat intelligence
for ioc in iocs:
    print(f"IOC: {ioc['value']}, Tags: {ioc['Tag']}")
    print(f"Related Events: {len(ioc['Event'])}")
```

## Security Monitoring & Alerting

### Detection Rules (Sigma Format)

```yaml
# Suspicious PowerShell execution
title: Suspicious PowerShell Command Line
status: experimental
description: Detects suspicious PowerShell command line patterns
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    Image|endswith: '\powershell.exe'
    CommandLine|contains:
      - '-encodedcommand'
      - '-enc'
      - 'bypass'
      - 'hidden'
      - 'noprofile'
  condition: selection
level: high
tags:
  - attack.execution
  - attack.t1059.001
```

### SIEM Alert Correlation

```python
# Splunk query for multi-stage attack detection
"""
index=security sourcetype=wineventlog:security
| transaction maxspan=1h EventCode startswith=4624 endswith=4648
| where EventCode=4624 AND EventCode=4648
| stats count by src_ip, dst_ip, user
| where count > 5
"""
```

## Forensics Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| Volatility | Memory analysis | RAM dump forensics |
| Autopsy | Disk analysis | Filesystem investigation |
| Wireshark | Network forensics | PCAP analysis |
| YARA | Malware detection | Pattern matching |
| Sleuth Kit | File recovery | Deleted file recovery |
| log2timeline | Timeline analysis | Event correlation |

## Best Practices

**Preserve Evidence**: Always work on copies, maintain chain of custody, document every action.

**Automate Response**: Use SOAR for repeatable tasks, but keep human oversight for critical decisions.

**Practice Regularly**: Conduct tabletop exercises, red team simulations, and incident response drills.

**Learn and Improve**: Every incident is a learning opportunity. Update playbooks, detection rules, and training.

**Communicate Clearly**: Keep stakeholders informed, document decisions, provide post-incident reports.
