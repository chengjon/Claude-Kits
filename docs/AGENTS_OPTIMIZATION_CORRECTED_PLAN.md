# Agents优化修正计划 - 遵守500行规则和Delegation Pattern

**日期**: 2025-11-19
**状态**: 规划阶段
**模式**: 基于Phase 4的成功方法论

---

## 📌 核心原则回顾（来自项目文档）

### 1. 500行规则（强制）
- ✅ **主文件限制**: 所有SKILL.md/Agent.md必须 ≤ 500行
- ✅ **可接受范围**: ≤ 620行（slight tolerance）
- ❌ **需要拆分**: ≥ 761行
- ✅ **资源分离**: 详细内容放在resources/下的子文件（每个也≤500行）

### 2. Delegation Pattern（关键！）
用来替代简单的删除和合并，实现agents之间的专业化协作。

**示例格式**：
```yaml
name: agent-a
description: Handles X responsibility. Use for [use cases].
  Delegates to agent-b for [specific scenarios].

agent_a:
  delegates_to: agent-b
  when:
    - Scenario 1
    - Scenario 2
```

### 3. 三个优化模式
- **Pattern 1**: Implementation vs Validation（用于QA类）
- **Pattern 2**: Full-Stack vs Specialization（用于Framework类）
- **Pattern 3**: Strategy vs Operations（用于运维类）

---

## 🎯 当前优化进度

### ✅ 已完成
- [x] Phase 1: 文档agents整合 (5 → 2)
  - deleted: documentation-engineer, documentation-specialist, documentation-writer, documentation-pro
  - kept: documentation-architect-pro, api-documentation-pro
  - agents count: 254 → 249

- [x] Phase 2: 测试agents整合 (8 → 3)
  - deleted: test-writer, test-creator, test-generator-pro, test-results-analyzer, spec-validator, spec-tester, test-engineer, accessibility-tester, penetration-tester
  - kept: test-strategy-pro, test-implementation-pro, test-writer-fixer, api-tester-pro
  - agents count: 249 → 240

- [x] 模型升级: 6个agents升级到sonnet
  - advanced-debugger, documentation-writer, performance-optimizer, security-scanner, tech-lead-orchestrator, test-generator-pro

- [x] 冗余删除: 2个agents
  - security-auditor (与security-auditor-pro重复)
  - backend-security-coder (与backend-security-pro重复)

**当前agents总数**: 240个

---

## ⚠️ 关键发现：超大Agents问题

### 超大agents列表（需要按优先级处理）
```
🔴 优先级1（>1000行）:
  - devops-sre-pro: 1,387行 ⚠️ 需要拆分
  - vue-nuxt-expert: 1,265行

🟡 优先级2（800-1000行）:
  - vue-fullstack-pro: 907行
  - infrastructure-architect-pro: 885行

🟠 优先级3（700-800行）:
  - react-component-pro: 822行
  - security-infrastructure-pro: 704行
```

---

## 📝 Phase 3修正方案：DevOps Agents优化

### 问题：devops-sre-pro 有1,387行，违反500行规则

### 解决方案：使用拆分法（参考Phase 4成功案例）

**目标**:
- devops-sre-pro (1,387) → 拆分成两个agents
- 保持清晰的delegation pattern
- 遵守≤500行规则

**方案选项**（等待用户选择）：

#### 选项A：按职责拆分（推荐）
```
devops-infrastructure-core (IaC, CI/CD, Containers)
  ↔ delegates ↔
devops-reliability-pro (Incident, SRE, Reliability)
  ↔ delegates ↔
deployment-engineer (GitOps, Progressive Delivery)
```

预期结果：
- devops-infrastructure-core: ~450行 ✅
- devops-reliability-pro: ~400行 ✅ (从devops-sre-pro中提取)
- deployment-engineer: ~400行 ✅ (升级到sonnet)
- 删除重复agents: devops-engineer, devops-pro, devops-automator, devops-incident-responder, devops-reliability, devops-troubleshooter, sre-engineer, sre-pro

#### 选项B：压缩法（如不想拆分）
- 从devops-sre-pro中移除冗长的examples
- 保留关键patterns和best practices
- 使用指向resources/的链接存放详细内容
- 目标：1,387 → ≤500行

---

## 📋 Phase 4规划：其他超大Agents

### 4.1 Vue/Nuxt相关agents
```
vue-nuxt-expert (1,265行) ⚠️
  → Option: 拆分或压缩，保留nuxt-pro的清晰定位

vue-fullstack-pro (907行)
  → Option: 压缩到≤500行，或拆分为vue-core + vue-advanced
```

### 4.2 React相关agents
```
react-component-pro (822行)
  → Option: 压缩到≤500行
  → 使用resources/存放详细的component patterns
```

### 4.3 架构相关agents
```
infrastructure-architect-pro (885行)
  → Option: 拆分为 infrastructure-design + infrastructure-implementation

security-infrastructure-pro (704行)
  → Option: 保留或压缩到≤500行
```

---

## 📌 后续工作流程

### 步骤1：确认Phase 3方案
需要用户选择：
- [ ] 选项A：拆分devops-sre-pro（推荐）
- [ ] 选项B：压缩devops-sre-pro

### 步骤2：执行Phase 3（一旦确认）
1. 根据选择拆分或压缩devops-sre-pro
2. 更新相关agents的description（添加delegation pattern）
3. 删除功能重复的agents
4. 验证所有agents ≤500行

### 步骤3：识别Phase 4需要处理的agents
根据当前状态，制定具体的拆分/压缩方案

### 步骤4：添加description增强
对所有agents的description添加：
- ✅ "NOT FOR" 部分（何时不用此agent）
- ✅ "RELATED AGENTS" 链接（相关agents）
- ✅ "SCOPE" 说明（小/中/大项目？）
- ✅ Delegation pattern（当X时使用Y）

### 步骤5：更新registry
运行 `python scripts/components_scanner.py` 更新components_registry.json

---

## 🎓 关键学习要点

### ✅ 正确的方法论
1. **不是简单删除** - 使用delegation pattern建立agents间的协作
2. **不是盲目合并** - 使用专业化的拆分替代
3. **遵守500行规则** - 这是项目的强制要求
4. **清晰的职责边界** - 每个agent有明确的不重复职责

### ❌ 要避免的做法
1. ❌ 简单删除agents而不转移其功能
2. ❌ 创建超过500行的agents
3. ❌ 合并不相关的功能
4. ❌ 忽视description中的delegation关系

---

## 📊 最终目标

**当前**: 240个agents
**目标**:
- 所有agents ≤500行（或可接受的≤620行）
- 清晰的delegation patterns建立
- 减少到170-190个agents（15-20%的总体减少）
- 100%功能覆盖，零功能丧失

---

## 🚀 下一步行动

等待用户确认Phase 3的方案选择，然后进行具体的拆分/压缩工作。

