---
name: documentation-writer
description: Creates and maintains comprehensive technical documentation
tools: Read, Write, Edit, Grep, Glob
model: claude-3-sonnet
temperature: 0.7
---

You are a technical writing expert who creates clear, comprehensive documentation that developers love to read.

## Documentation Principles
- Write for your audience (developers)
- Show, don't just tell (include examples)
- Keep it current (update with code)
- Make it searchable (good structure)
- Test your docs (ensure examples work)

## Documentation Types

### API Documentation
```typescript
/**
 * Creates a new user account with the specified details.
 * 
 * @components/skills/parallel-execution-optimizer/ userData - The user information for account creation
 * @components/skills/parallel-execution-optimizer/ options - Optional configuration for account creation
 * @components/skills/architecture-patterns/ Promise resolving to the created user object
 * 
 * @components/hooks/hook-template/post-tool-use-example.sh
 * ```typescript
 * const user = await createUser({
 *   email: 'user @example.com',
 *   name: 'John Doe',
 *   role: 'admin'
 * }, {
 *   sendWelcomeEmail: true,
 *   requireEmailVerification: false
 * });
 * ```
 * 
 * @components/skills/hybrid-cloud-networking/SKILL.md {ValidationError} If userData is invalid
 * @components/skills/hybrid-cloud-networking/SKILL.md {DuplicateError} If email already exists
 * @components/skills/hybrid-cloud-networking/SKILL.md {NetworkError} If service is unavailable
 * 
 * @components/commands/incident-response.md 2.0.0
 * @components/hooks/optional/session-end-batch-prettier.sh { @components/skills/backend-dev-guidelines/SKILL.md updateUser} for modifying existing users
 * @components/hooks/optional/session-end-batch-prettier.sh { @components/skills/backend-dev-guidelines/SKILL.md deleteUser} for removing users
 */
async function createUser(
  userData: UserData,
  options?: CreateUserOptions
): Promise {
  // Implementation
}
```

### README Template
```markdown
# Project Name

> One-line description of what this project does

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

##  Quick Start

```bash
# Install
npm install package-name

# Basic usage
import { feature } from 'package-name';
const result = feature(options);
```

##  Documentation

- [Getting Started](./docs/getting-started.md)
- [API Reference](./docs/api.md)
- [Examples](./docs/examples.md)
- [Contributing](./CONTRIBUTING.md)

##  Features

- ✅ Feature 1 with benefit
- ✅ Feature 2 with benefit
- ✅ Feature 3 with benefit

##  Installation

### Prerequisites
- Node.js >= 16
- npm >= 8

### Steps
1. Clone the repository
2. Install dependencies
3. Configure environment
4. Run the application

##  Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| API_KEY | Your API key | - | Yes |
| PORT | Server port | 3000 | No |

##  Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

##  License

MIT © [Your Name]
```

## Documentation Checklist
- [ ] README with quick start
- [ ] API documentation
- [ ] Code comments
- [ ] Architecture overview
- [ ] Deployment guide
- [ ] Troubleshooting section
- [ ] FAQ
- [ ] Changelog
- [ ] Contributing guidelines
--- Content from referenced files ---
Content from @components/commands/incident-response.md:
Orchestrate multi-agent incident response with modern SRE practices for rapid resolution and learning:

[Extended thinking: This workflow implements a comprehensive incident command system (ICS) following modern SRE principles. Multiple specialized agents collaborate through defined phases: detection/triage, investigation/mitigation, communication/coordination, and resolution/postmortem. The workflow emphasizes speed without sacrificing accuracy, maintains clear communication channels, and ensures every incident becomes a learning opportunity through blameless postmortems and systematic improvements.]

## Configuration

### Severity Levels
- **P0/SEV-1**: Complete outage, security breach, data loss - immediate all-hands response
- **P1/SEV-2**: Major degradation, significant user impact - rapid response required
- **P2/SEV-3**: Minor degradation, limited impact - standard response
- **P3/SEV-4**: Cosmetic issues, no user impact - scheduled resolution

### Incident Types
- Performance degradation
- Service outage
- Security incident
- Data integrity issue
- Infrastructure failure
- Third-party service disruption

## Phase 1: Detection & Triage

### 1. Incident Detection and Classification
- Use Task tool with subagent_type="incident-responder"
- Prompt: "URGENT: Detect and classify incident: $ARGUMENTS. Analyze alerts from PagerDuty/Opsgenie/monitoring. Determine: 1) Incident severity (P0-P3), 2) Affected services and dependencies, 3) User impact and business risk, 4) Initial incident command structure needed. Check error budgets and SLO violations."
- Output: Severity classification, impact assessment, incident command assignments, SLO status
- Context: Initial alerts, monitoring dashboards, recent changes

### 2. Observability Analysis
- Use Task tool with subagent_type="observability-monitoring::observability-engineer"
- Prompt: "Perform rapid observability sweep for incident: $ARGUMENTS. Query: 1) Distributed tracing (OpenTelemetry/Jaeger), 2) Metrics correlation (Prometheus/Grafana/DataDog), 3) Log aggregation (ELK/Splunk), 4) APM data, 5) Real User Monitoring. Identify anomalies, error patterns, and service degradation points."
- Output: Observability findings, anomaly detection, service health matrix, trace analysis
- Context: Severity level from step 1, affected services

### 3. Initial Mitigation
- Use Task tool with subagent_type="incident-responder"
- Prompt: "Implement immediate mitigation for P$SEVERITY incident: $ARGUMENTS. Actions: 1) Traffic throttling/rerouting if needed, 2) Feature flag disabling for affected features, 3) Circuit breaker activation, 4) Rollback assessment for recent deployments, 5) Scale resources if capacity-related. Prioritize user experience restoration."
- Output: Mitigation actions taken, temporary fixes applied, rollback decisions
- Context: Observability findings, severity classification

## Phase 2: Investigation & Root Cause Analysis

### 4. Deep System Debugging
- Use Task tool with subagent_type="error-debugging::debugger"
- Prompt: "Conduct deep debugging for incident: $ARGUMENTS using observability data. Investigate: 1) Stack traces and error logs, 2) Database query performance and locks, 3) Network latency and timeouts, 4) Memory leaks and CPU spikes, 5) Dependency failures and cascading errors. Apply Five Whys analysis."
- Output: Root cause identification, contributing factors, dependency impact map
- Context: Observability analysis, mitigation status

### 5. Security Assessment
- Use Task tool with subagent_type="security-scanning::security-auditor"
- Prompt: "Assess security implications of incident: $ARGUMENTS. Check: 1) DDoS attack indicators, 2) Authentication/authorization failures, 3) Data exposure risks, 4) Certificate issues, 5) Suspicious access patterns. Review WAF logs, security groups, and audit trails."
- Output: Security assessment, breach analysis, vulnerability identification
- Context: Root cause findings, system logs

### 6. Performance Engineering Analysis
- Use Task tool with subagent_type="application-performance::performance-engineer"
- Prompt: "Analyze performance aspects of incident: $ARGUMENTS. Examine: 1) Resource utilization patterns, 2) Query optimization opportunities, 3) Caching effectiveness, 4) Load balancer health, 5) CDN performance, 6) Autoscaling triggers. Identify bottlenecks and capacity issues."
- Output: Performance bottlenecks, resource recommendations, optimization opportunities
- Context: Debug findings, current mitigation state

## Phase 3: Resolution & Recovery

### 7. Fix Implementation
- Use Task tool with subagent_type="backend-development::backend-architect"
- Prompt: "Design and implement production fix for incident: $ARGUMENTS based on root cause. Requirements: 1) Minimal viable fix for rapid deployment, 2) Risk assessment and rollback capability, 3) Staged rollout plan with monitoring, 4) Validation criteria and health checks. Consider both immediate fix and long-term solution."
- Output: Fix implementation, deployment strategy, validation plan, rollback procedures
- Context: Root cause analysis, performance findings, security assessment

### 8. Deployment and Validation
- Use Task tool with subagent_type="deployment-strategies::deployment-engineer"
- Prompt: "Execute emergency deployment for incident fix: $ARGUMENTS. Process: 1) Blue-green or canary deployment, 2) Progressive rollout with monitoring, 3) Health check validation at each stage, 4) Rollback triggers configured, 5) Real-time monitoring during deployment. Coordinate with incident command."
- Output: Deployment status, validation results, monitoring dashboard, rollback readiness
- Context: Fix implementation, current system state

## Phase 4: Communication & Coordination

### 9. Stakeholder Communication
- Use Task tool with subagent_type="content-marketing::content-marketer"
- Prompt: "Manage incident communication for: $ARGUMENTS. Create: 1) Status page updates (public-facing), 2) Internal engineering updates (technical details), 3) Executive summary (business impact/ETA), 4) Customer support briefing (talking points), 5) Timeline documentation with key decisions. Update every 15-30 minutes based on severity."
- Output: Communication artifacts, status updates, stakeholder briefings, timeline log
- Context: All previous phases, current resolution status

### 10. Customer Impact Assessment
- Use Task tool with subagent_type="incident-responder"
- Prompt: "Assess and document customer impact for incident: $ARGUMENTS. Analyze: 1) Affected user segments and geography, 2) Failed transactions or data loss, 3) SLA violations and contractual implications, 4) Customer support ticket volume, 5) Revenue impact estimation. Prepare proactive customer outreach list."
- Output: Customer impact report, SLA analysis, outreach recommendations
- Context: Resolution progress, communication status

## Phase 5: Postmortem & Prevention

### 11. Blameless Postmortem
- Use Task tool with subagent_type="documentation-generation::docs-architect"
- Prompt: "Conduct blameless postmortem for incident: $ARGUMENTS. Document: 1) Complete incident timeline with decisions, 2) Root cause and contributing factors (systems focus), 3) What went well in response, 4) What could improve, 5) Action items with owners and deadlines, 6) Lessons learned for team education. Follow SRE postmortem best practices."
- Output: Postmortem document, action items list, process improvements, training needs
- Context: Complete incident history, all agent outputs

### 12. Monitoring and Alert Enhancement
- Use Task tool with subagent_type="observability-monitoring::observability-engineer"
- Prompt: "Enhance monitoring to prevent recurrence of: $ARGUMENTS. Implement: 1) New alerts for early detection, 2) SLI/SLO adjustments if needed, 3) Dashboard improvements for visibility, 4) Runbook automation opportunities, 5) Chaos engineering scenarios for testing. Ensure alerts are actionable and reduce noise."
- Output: New monitoring configuration, alert rules, dashboard updates, runbook automation
- Context: Postmortem findings, root cause analysis

### 13. System Hardening
- Use Task tool with subagent_type="backend-development::backend-architect"
- Prompt: "Design system improvements to prevent incident: $ARGUMENTS. Propose: 1) Architecture changes for resilience (circuit breakers, bulkheads), 2) Graceful degradation strategies, 3) Capacity planning adjustments, 4) Technical debt prioritization, 5) Dependency reduction opportunities. Create implementation roadmap."
- Output: Architecture improvements, resilience patterns, technical debt items, roadmap
- Context: Postmortem action items, performance analysis

## Success Criteria

### Immediate Success (During Incident)
- Service restoration within SLA targets
- Accurate severity classification within 5 minutes
- Stakeholder communication every 15-30 minutes
- No cascading failures or incident escalation
- Clear incident command structure maintained

### Long-term Success (Post-Incident)
- Comprehensive postmortem within 48 hours
- All action items assigned with deadlines
- Monitoring improvements deployed within 1 week
- Runbook updates completed
- Team training conducted on lessons learned
- Error budget impact assessed and communicated

## Coordination Protocols

### Incident Command Structure
- **Incident Commander**: Decision authority, coordination
- **Technical Lead**: Technical investigation and resolution
- **Communications Lead**: Stakeholder updates
- **Subject Matter Experts**: Specific system expertise

### Communication Channels
- War room (Slack/Teams channel or Zoom)
- Status page updates (StatusPage, Statusly)
- PagerDuty/Opsgenie for alerting
- Confluence/Notion for documentation

### Handoff Requirements
- Each phase provides clear context to the next
- All findings documented in shared incident doc
- Decision rationale recorded for postmortem
- Timestamp all significant events

Production incident requiring immediate response: $ARGUMENTS
Content from @components/hooks/hook-template/post-tool-use-example.sh:
#!/usr/bin/env bash

# PostToolUse Hook Example - Runs after a tool successfully completes
# This example logs file changes and can provide feedback to Claude

set -e

# Read input from stdin
INPUT=$(cat)

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi

# Parse input JSON
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input')
TOOL_RESPONSE=$(echo "$INPUT" | jq -r '.tool_response')

# Example: Log file edits
if [ "$TOOL_NAME" == "Edit" ] || [ "$TOOL_NAME" == "Write" ]; then
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path')
    echo "[$(date)] $TOOL_NAME: $FILE_PATH" >> ~/.claude/file-changes-log.txt
fi

# Example: Run linter after code changes
if [ "$TOOL_NAME" == "Write" ] && [[ "$FILE_PATH" == *.py ]]; then
    # Optional: Run Python linter (uncomment if you want this)
    # python -m flake8 "$FILE_PATH" 2>&1 || true
    :
fi

# Exit 0 to continue normally
exit 0
Content from @components/hooks/optional/session-end-batch-prettier.sh:
#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Batch Prettier (SessionEnd)
# ============================================================================
#
# Event: SessionEnd
# Matcher: N/A (SessionEnd 不支持 matcher)
# Purpose: 在会话结束时自动格式化所有修改过的文件，确保代码风格一致
#
# Reddit 案例设计理念:
#   "Clean exit" - 在离开前自动整理工作空间：
#   - 格式化所有修改过的代码文件
#   - 确保符合项目的代码风格规范
#   - 减少 PR review 中的格式问题
#
#   使用 gentle reminder 策略：
#   - 如果 Prettier 未安装，友好提示而不阻塞
#   - 如果格式化失败，报告但不影响会话结束
#   - 提供格式化摘要供用户查看
#
# 工作原理:
#   1. 检测 Prettier 是否安装（npx prettier --version）
#   2. 查找修改过的文件（通过 git status 或 file-edit-tracker）
#   3. 对支持的文件类型运行 Prettier
#   4. 输出格式化摘要到 additionalContext
#   5. 非阻塞（exit 0），不影响会话结束
#
# 退出码:
#   0: 成功（格式化完成或跳过）
#   1: 警告（格式化部分失败，但不阻止会话结束）
#
# JSON 输出格式:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "SessionEnd",
#       "additionalContext": "✓ Formatted 12 files with Prettier..."
#     }
#   }
#
# 自定义:
#   - 修改 SUPPORTED_EXTENSIONS 来添加更多文件类型
#   - 修改 PRETTIER_OPTIONS 来调整格式化选项
#   - 修改 MAX_FILES 来限制批量格式化的文件数量
#   - 修改 USE_GIT_STATUS 来改变文件检测方式
#
# 安装方法:
#   1. chmod +x session-end-batch-prettier.sh
#   2. 复制到 .claude/hooks/
#   3. 确保项目安装了 Prettier: npm install -D prettier
#   4. 添加到 settings.json:
#      {
#        "hooks": {
#          "SessionEnd": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-batch-prettier.sh"
#              }],
#              "timeout": 60
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 60 秒（格式化操作，取决于文件数量）
#
# 依赖:
#   - Prettier (npm install -D prettier)
#   - 可选: .prettierrc 配置文件
#   - 可选: .prettierignore 忽略文件
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEBUG_MODE="${BATCH_PRETTIER_DEBUG:-false}"

# 支持的文件扩展名（Prettier 可以格式化的）
SUPPORTED_EXTENSIONS=(
    "js"
    "jsx"
    "ts"
    "tsx"
    "json"
    "css"
    "scss"
    "less"
    "html"
    "vue"
    "md"
    "yaml"
    "yml"
)

# Prettier 选项（可以留空使用项目的 .prettierrc）
PRETTIER_OPTIONS="${PRETTIER_OPTIONS:---write}"

# 最大格式化文件数（防止意外格式化整个项目）
MAX_FILES="${MAX_FILES:-100}"

# 使用 git status 检测修改的文件（推荐）
USE_GIT_STATUS="${USE_GIT_STATUS:-true}"

# file-edit-tracker 日志路径（如果使用 PostToolUse hook）
EDIT_TRACKER_LOG="${EDIT_TRACKER_LOG:-.claude/logs/file-edit-tracker.log}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 检查 Prettier 是否安装 =====
check_prettier_installed() {
    debug_log "Checking if Prettier is installed..."

    if npx prettier --version >/dev/null 2>&1; then
        local version=$(npx prettier --version 2>/dev/null || echo "unknown")
        debug_log "Prettier found: $version"
        return 0
    else
        debug_log "Prettier not found"
        return 1
    fi
}

# ===== 获取项目根目录 =====
get_project_root() {
    if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
        echo "$CLAUDE_PROJECT_DIR"
        return
    fi

    if git rev-parse --show-toplevel 2>/dev/null; then
        return
    fi

    pwd
}

# ===== 从 git status 获取修改的文件 =====
get_modified_files_from_git() {
    local project_root="$1"
    debug_log "Getting modified files from git status..."

    cd "$project_root" || return 1

    # 获取所有修改、添加、未跟踪的文件
    git status --porcelain 2>/dev/null | \
        grep -E '^\s*[MARCU?]' | \
        awk '{print $NF}' || true
}

# ===== 从 file-edit-tracker 日志获取修改的文件 =====
get_modified_files_from_tracker() {
    local project_root="$1"
    local tracker_log="$project_root/$EDIT_TRACKER_LOG"

    debug_log "Getting modified files from edit tracker: $tracker_log"

    if [ ! -f "$tracker_log" ]; then
        debug_log "Edit tracker log not found"
        return 1
    fi

    # 提取今天修改的文件（从 file-edit-tracker.sh 日志）
    local today=$(date +%Y-%m-%d)
    grep "^$today" "$tracker_log" 2>/dev/null | \
        awk '{print $NF}' | \
        sort -u || true
}

# ===== 过滤支持的文件类型 =====
filter_supported_files() {
    local files=("$@")
    local filtered=()

    for file in "${files[@]}"; do
        # 跳过不存在的文件
        [ -f "$file" ] || continue

        # 检查扩展名
        local ext="${file##*.}"
        for supported_ext in "${SUPPORTED_EXTENSIONS[@]}"; do
            if [ "$ext" = "$supported_ext" ]; then
                filtered+=("$file")
                break
            fi
        done
    done

    printf '%s\n' "${filtered[@]}"
}

# ===== 运行 Prettier =====
run_prettier() {
    local files=("$@")
    local success_count=0
    local failure_count=0
    local failed_files=()

    debug_log "Formatting ${#files[@]} files with Prettier..."

    for file in "${files[@]}"; do
        debug_log "Formatting: $file"

        if npx prettier $PRETTIER_OPTIONS "$file" >/dev/null 2>&1; then
            success_count=$((success_count + 1))
        else
            failure_count=$((failure_count + 1))
            failed_files+=("$file")
            debug_log "Failed to format: $file"
        fi
    done

    # 返回结果统计
    echo "$success_count"
    echo "$failure_count"
    printf '%s\n' "${failed_files[@]}"
}

# ===== 主逻辑 =====
debug_log "SessionEnd batch-prettier hook triggered"

# 检查 Prettier 是否安装
if ! check_prettier_installed; then
    # Prettier 未安装，友好提示
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "ℹ️  Prettier not found. To enable automatic code formatting on session end:\n\n  npm install -D prettier\n\nOptional: Add .prettierrc for custom formatting rules."
  }
}
EOF
    exit 0
fi

# 获取项目根目录
PROJECT_ROOT=$(get_project_root)
debug_log "Project root: $PROJECT_ROOT"

# 获取修改的文件列表
MODIFIED_FILES=()

if [ "$USE_GIT_STATUS" = "true" ]; then
    # 优先使用 git status
    mapfile -t MODIFIED_FILES < <(get_modified_files_from_git "$PROJECT_ROOT")
fi

# 如果 git 方法失败或没有找到文件，尝试 edit tracker
if [ ${#MODIFIED_FILES[@]} -eq 0 ]; then
    mapfile -t MODIFIED_FILES < <(get_modified_files_from_tracker "$PROJECT_ROOT")
fi

# 如果没有找到任何修改的文件
if [ ${#MODIFIED_FILES[@]} -eq 0 ]; then
    debug_log "No modified files found"

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "ℹ️  No modified files found for formatting."
  }
}
EOF
    exit 0
fi

debug_log "Found ${#MODIFIED_FILES[@]} modified files"

# 过滤支持的文件类型
cd "$PROJECT_ROOT" || exit 0
mapfile -t FORMATTABLE_FILES < <(filter_supported_files "${MODIFIED_FILES[@]}")

if [ ${#FORMATTABLE_FILES[@]} -eq 0 ]; then
    debug_log "No formattable files found"

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "ℹ️  No formattable files found (checked ${#MODIFIED_FILES[@]} modified files)."
  }
}
EOF
    exit 0
fi

debug_log "Found ${#FORMATTABLE_FILES[@]} formattable files"

# 检查是否超过最大文件数限制
if [ ${#FORMATTABLE_FILES[@]} -gt $MAX_FILES ]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "⚠️  Found ${#FORMATTABLE_FILES[@]} files to format, which exceeds the limit ($MAX_FILES).\n\nSkipping automatic formatting. To format manually:\n\n  npx prettier --write ."
  }
}
EOF
    exit 1
fi

# 运行 Prettier
PRETTIER_OUTPUT=$(run_prettier "${FORMATTABLE_FILES[@]}")
SUCCESS_COUNT=$(echo "$PRETTIER_OUTPUT" | head -n 1)
FAILURE_COUNT=$(echo "$PRETTIER_OUTPUT" | head -n 2 | tail -n 1)

# 生成输出消息
if [ "$FAILURE_COUNT" -eq 0 ]; then
    # 全部成功
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "✓ Formatted $SUCCESS_COUNT files with Prettier\n\nAll modified code files have been formatted according to project style guidelines."
  }
}
EOF
    exit 0
else
    # 部分失败
    FAILED_FILES=$(echo "$PRETTIER_OUTPUT" | tail -n +3)

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionEnd",
    "additionalContext": "⚠️  Formatted $SUCCESS_COUNT files, but $FAILURE_COUNT files failed:\n\n$FAILED_FILES\n\nCheck Prettier configuration or file syntax errors."
  }
}
EOF
    exit 1
fi
Content from @components/skills/backend-dev-guidelines/SKILL.md:
---
name: backend-dev-guidelines
description: Brief description of what this Skill does and when to use it. Include keywords for discovery.
---

# Backend Dev Guidelines

## Instructions
Provide clear, step-by-step guidance for Claude.

## Examples
Show concrete examples of using this Skill.
Content from @components/skills/hybrid-cloud-networking/SKILL.md:
---
name: hybrid-cloud-networking
description: Configure secure, high-performance connectivity between on-premises infrastructure and cloud platforms using VPN and dedicated connections. Use when building hybrid cloud architectures, connecting data centers to cloud, or implementing secure cross-premises networking.
---

# Hybrid Cloud Networking

Configure secure, high-performance connectivity between on-premises and cloud environments using VPN, Direct Connect, and ExpressRoute.

## Purpose

Establish secure, reliable network connectivity between on-premises data centers and cloud providers (AWS, Azure, GCP).

## When to Use

- Connect on-premises to cloud
- Extend datacenter to cloud
- Implement hybrid active-active setups
- Meet compliance requirements
- Migrate to cloud gradually

## Connection Options

### AWS Connectivity

#### 1. Site-to-Site VPN
- IPSec VPN over internet
- Up to 1.25 Gbps per tunnel
- Cost-effective for moderate bandwidth
- Higher latency, internet-dependent

```hcl
resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-vpn-gateway"
  }
}

resource "aws_customer_gateway" "main" {
  bgp_asn    = 65000
  ip_address = "203.0.113.1"
  type       = "ipsec.1"
}

resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.main.id
  type                = "ipsec.1"
  static_routes_only  = false
}
```

#### 2. AWS Direct Connect
- Dedicated network connection
- 1 Gbps to 100 Gbps
- Lower latency, consistent bandwidth
- More expensive, setup time required

**Reference:** See `references/direct-connect.md`

### Azure Connectivity

#### 1. Site-to-Site VPN
```hcl
resource "azurerm_virtual_network_gateway" "vpn" {
  name                = "vpn-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  type     = "Vpn"
  vpn_type = "RouteBased"
  sku      = "VpnGw1"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }
}
```

#### 2. Azure ExpressRoute
- Private connection via connectivity provider
- Up to 100 Gbps
- Low latency, high reliability
- Premium for global connectivity

### GCP Connectivity

#### 1. Cloud VPN
- IPSec VPN (Classic or HA VPN)
- HA VPN: 99.99% SLA
- Up to 3 Gbps per tunnel

#### 2. Cloud Interconnect
- Dedicated (10 Gbps, 100 Gbps)
- Partner (50 Mbps to 50 Gbps)
- Lower latency than VPN

## Hybrid Network Patterns

### Pattern 1: Hub-and-Spoke
```
On-Premises Datacenter
         ↓
    VPN/Direct Connect
         ↓
    Transit Gateway (AWS) / vWAN (Azure)
         ↓
    ├─ Production VPC/VNet
    ├─ Staging VPC/VNet
    └─ Development VPC/VNet
```

### Pattern 2: Multi-Region Hybrid
```
On-Premises
    ├─ Direct Connect → us-east-1
    └─ Direct Connect → us-west-2
            ↓
        Cross-Region Peering
```

### Pattern 3: Multi-Cloud Hybrid
```
On-Premises Datacenter
    ├─ Direct Connect → AWS
    ├─ ExpressRoute → Azure
    └─ Interconnect → GCP
```

## Routing Configuration

### BGP Configuration
```
On-Premises Router:
- AS Number: 65000
- Advertise: 10.0.0.0/8

Cloud Router:
- AS Number: 64512 (AWS), 65515 (Azure)
- Advertise: Cloud VPC/VNet CIDRs
```

### Route Propagation
- Enable route propagation on route tables
- Use BGP for dynamic routing
- Implement route filtering
- Monitor route advertisements

## Security Best Practices

1. **Use private connectivity** (Direct Connect/ExpressRoute)
2. **Implement encryption** for VPN tunnels
3. **Use VPC endpoints** to avoid internet routing
4. **Configure network ACLs** and security groups
5. **Enable VPC Flow Logs** for monitoring
6. **Implement DDoS protection**
7. **Use PrivateLink/Private Endpoints**
8. **Monitor connections** with CloudWatch/Monitor
9. **Implement redundancy** (dual tunnels)
10. **Regular security audits**

## High Availability

### Dual VPN Tunnels
```hcl
resource "aws_vpn_connection" "primary" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.primary.id
  type                = "ipsec.1"
}

resource "aws_vpn_connection" "secondary" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.secondary.id
  type                = "ipsec.1"
}
```

### Active-Active Configuration
- Multiple connections from different locations
- BGP for automatic failover
- Equal-cost multi-path (ECMP) routing
- Monitor health of all connections

## Monitoring and Troubleshooting

### Key Metrics
- Tunnel status (up/down)
- Bytes in/out
- Packet loss
- Latency
- BGP session status

### Troubleshooting
```bash
# AWS VPN
aws ec2 describe-vpn-connections
aws ec2 get-vpn-connection-telemetry

# Azure VPN
az network vpn-connection show
az network vpn-connection show-device-config-script
```

## Cost Optimization

1. **Right-size connections** based on traffic
2. **Use VPN for low-bandwidth** workloads
3. **Consolidate traffic** through fewer connections
4. **Minimize data transfer** costs
5. **Use Direct Connect** for high bandwidth
6. **Implement caching** to reduce traffic

## Reference Files

- `references/vpn-setup.md` - VPN configuration guide
- `references/direct-connect.md` - Direct Connect setup

## Related Skills

- `multi-cloud-architecture` - For architecture decisions
- `terraform-module-library` - For IaC implementation
--- End of content ---
