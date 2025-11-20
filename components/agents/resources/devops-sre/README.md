# DevOps & SRE 资源文件集

本目录包含 DevOps 和 Site Reliability Engineering (SRE) 专业领域的详细资源文件，配合 `devops-sre-pro.md` 主文件使用。

## 📁 资源文件概览

| 文件 | 主题 | 行数 | 用途 |
|------|------|------|------|
| `incident-response-playbook.md` | 事件响应剧本 | ~272 | 生产事件快速响应、系统诊断、故障排查 |
| `observability-monitoring-setup.md` | 可观测性和监控 | ~179 | Prometheus/Grafana 配置、告警规则、监控最佳实践 |
| `automated-remediation-self-healing.md` | 自动修复和自愈 | ~231 | 自动化事件响应、自愈系统设计、Chaos Engineering |
| `sli-slo-error-budget-management.md` | SLI/SLO/错误预算 | ~170 | SRE 指标定义、错误预算计算、可靠性决策框架 |
| `blameless-postmortem-process.md` | 无责事后分析 | ~234 | Postmortem 模板、复盘流程、持续改进机制 |
| `runbook-development-templates.md` | Runbook 开发 | ~334 | 运维手册模板、标准化响应流程、文档最佳实践 |

**总资源**: 6 个文件，~1,420 行详细内容

## 🎯 使用场景

### 生产事件响应 (P0-P4)
📖 阅读: `incident-response-playbook.md`
- 立即响应协议（前 5 分钟）
- 系统诊断脚本（9 步调查）
- 分布式追踪分析（OpenTelemetry）
- 网络故障排查工具包

### 监控和告警设置
📖 阅读: `observability-monitoring-setup.md`
- Prometheus + Grafana 完整配置
- SRE 专用告警规则（错误率、延迟、容量）
- 告警降噪和优先级设计
- Dashboard 设计最佳实践

### 建立自愈系统
📖 阅读: `automated-remediation-self-healing.md`
- 自动修复框架（Python 实现）
- 6 种常见修复动作（回滚、扩容、重启等）
- 安全机制（爆炸半径控制、验证步骤）
- Chaos Engineering 测试方法

### 定义 SLI/SLO/SLA
📖 阅读: `sli-slo-error-budget-management.md`
- SRE 基础概念和定义
- 错误预算跟踪实现（Python）
- 错误预算策略框架
- 可靠性与速度的权衡决策

### 事件复盘和学习
📖 阅读: `blameless-postmortem-process.md`
- Postmortem 完整模板
- 无责文化建立原则
- 根因分析方法（Five Whys）
- 行动项管理和追踪

### 编写运维手册
📖 阅读: `runbook-development-templates.md`
- Runbook 标准模板
- 常见场景（部署失败、资源耗尽、数据库问题）
- 升级流程和沟通模板
- Runbook → 自动化的演进路径

## 🔗 与主文件的关系

**主文件**: `components/agents/devops-sre-pro.md` (220 行)
- 提供概览和快速参考
- 核心概念和使用场景
- 📖 导航链接到本目录资源

**资源文件**: 本目录 (6 个文件)
- 详细实现指南
- 完整的代码示例和配置模板
- 深入的最佳实践和模式

## 💡 快速开始

### 场景 1: 生产环境出现故障
```bash
1. 打开 incident-response-playbook.md
2. 执行"立即响应协议"（前 5 分钟）
3. 运行系统诊断脚本
4. 使用分布式追踪定位问题
5. 完成后参考 blameless-postmortem-process.md 进行复盘
```

### 场景 2: 搭建新服务的监控
```bash
1. 打开 observability-monitoring-setup.md
2. 复制 Prometheus 配置模板
3. 根据服务特点定制告警规则
4. 参考 sli-slo-error-budget-management.md 定义 SLI/SLO
5. 创建 Grafana Dashboard
```

### 场景 3: 实现自动化响应
```bash
1. 打开 automated-remediation-self-healing.md
2. 研究自动修复框架设计
3. 选择适用的修复动作
4. 实现安全机制
5. 使用 Chaos Engineering 测试
6. 将经验记录到 runbook-development-templates.md
```

## 🎓 学习路径

**初级 SRE** (0-6 个月):
1. `incident-response-playbook.md` - 学习事件响应基础
2. `runbook-development-templates.md` - 编写第一个 Runbook
3. `observability-monitoring-setup.md` - 配置基础监控

**中级 SRE** (6-18 个月):
4. `sli-slo-error-budget-management.md` - 理解 SRE 指标体系
5. `blameless-postmortem-process.md` - 主持事件复盘
6. `automated-remediation-self-healing.md` - 开始自动化

**高级 SRE** (18+ 个月):
- 设计复杂的自愈系统
- 建立团队 SRE 文化
- Chaos Engineering 实践
- 容量规划和成本优化

## 🔧 工具和框架

**监控和可观测性**:
- Prometheus + Grafana
- OpenTelemetry
- Jaeger / Zipkin
- ELK Stack / Loki

**自动化和编排**:
- Kubernetes
- ArgoCD / Flux
- Ansible / Terraform
- Python + Bash

**Chaos Engineering**:
- Chaos Monkey
- Gremlin
- LitmusChaos

## 📊 资源文件质量指标

- ✅ 代码示例完整可运行
- ✅ 配置模板即拷即用
- ✅ 包含实际生产案例
- ✅ 遵循 SRE 行业最佳实践
- ✅ 定期更新和维护

## 🤝 贡献和反馈

本资源集持续维护和更新。如有建议或发现问题，请：
1. 提出 Issue 或 Pull Request
2. 分享实际使用经验和案例
3. 建议新增主题或优化现有内容

---

**相关资源**:
- 主文件: [`devops-sre-pro.md`](../../devops-sre-pro.md)
- 相关 Agent: `devops-infrastructure-core.md`, `deployment-engineer.md`
- 方法论文档: [`COMPLETE_OPTIMIZATION_REPORT.md`](../../../../docs/COMPLETE_OPTIMIZATION_REPORT.md)

**最后更新**: 2025-11-19
