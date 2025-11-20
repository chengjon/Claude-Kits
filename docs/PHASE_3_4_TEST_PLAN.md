# Phase 3 & 4 优化功能测试计划

**日期**: 2025-11-19
**版本**: v1.0
**状态**: 待执行

---

## 🎯 测试目标

验证6个分层优化后的agents：
1. **功能完整性** - 所有功能都能正常访问和使用
2. **资源文件导航** - 📖 链接清晰，可以引导Claude读取详细内容
3. **Delegation pattern** - 多个agents之间的协作是否顺畅
4. **性能** - 主文件加载快速，按需加载详细内容
5. **用户体验** - 从用户角度验证实际使用场景

---

## 📋 测试用例设计

### Test Suite 1: DevOps SRE场景

#### TC-1.1: 生产事件响应 (Incident Response)
**触发agent**: devops-sre-pro

**测试场景**:
```
用户请求: "我们的生产环境API错误率突然从0.1%飙升到5%，需要立即响应。
请帮我制定应急响应计划并提供系统诊断脚本。"
```

**预期行为**:
1. ✅ Agent正确激活 (devops-sre-pro)
2. ✅ 提供immediate response步骤
3. ✅ 提到 📖 resources/devops-sre/incident-response-playbook.md
4. ✅ 主动读取该资源文件获取详细诊断脚本
5. ✅ 提供完整的kubectl诊断命令和observability-driven investigation

**验证点**:
- [ ] Agent能否识别这是事件响应场景
- [ ] 是否提供了5分钟内快速响应步骤
- [ ] 是否读取了incident-response-playbook.md
- [ ] 提供的诊断脚本是否完整可用
- [ ] 是否建立了incident command structure

#### TC-1.2: SLO违规和错误预算管理
**触发agent**: devops-sre-pro

**测试场景**:
```
用户请求: "我们需要为新服务定义SLO并实现错误预算追踪系统。
服务要求99.9%可用性，P95延迟<500ms。"
```

**预期行为**:
1. ✅ Agent识别SLO/error budget场景
2. ✅ 提到 📖 resources/devops-sre/sli-slo-error-budget-management.md
3. ✅ 提供Python错误预算追踪实现
4. ✅ 包含burn rate计算和policy enforcement

**验证点**:
- [ ] 是否提供SLO定义框架
- [ ] 是否读取了sli-slo-error-budget-management.md
- [ ] Python代码是否完整可执行
- [ ] 是否包含error budget policy

#### TC-1.3: DevOps Delegation Pattern测试
**触发agent**: devops-sre-pro → devops-infrastructure-core

**测试场景**:
```
用户请求: "我们遇到生产事件，需要回滚部署。
但发现Terraform状态被锁定，无法执行基础设施变更。"
```

**预期行为**:
1. ✅ devops-sre-pro处理事件响应部分
2. ✅ 识别需要IaC专业知识
3. ✅ 明确表示 "对于Terraform状态锁定问题，应使用devops-infrastructure-core"
4. ✅ 或建议："这涉及基础设施自动化，让我协调devops-infrastructure-core来处理"

**验证点**:
- [ ] 是否识别职责边界
- [ ] 是否提到delegation
- [ ] 两个agents能否协同工作

---

### Test Suite 2: Vue/Nuxt开发场景

#### TC-2.1: Nuxt 3 SSR项目搭建
**触发agent**: vue-nuxt-expert

**测试场景**:
```
用户请求: "我需要创建一个Nuxt 3项目，支持SSR，集成Prisma数据库，
并配置Redis缓存。请提供完整的项目结构和配置。"
```

**预期行为**:
1. ✅ Agent激活vue-nuxt-expert
2. ✅ 提供基础项目配置（主文件中的quick start）
3. ✅ 提到 📖 resources/vue-nuxt/nitro-server-api-development.md (Prisma集成)
4. ✅ 提到 📖 resources/vue-nuxt/caching-performance-optimization.md (Redis缓存)
5. ✅ 读取相关资源文件提供详细实现

**验证点**:
- [ ] 是否提供nuxt.config.ts配置
- [ ] 是否读取nitro-server-api-development.md获取Prisma集成代码
- [ ] 是否读取caching-performance-optimization.md获取Redis配置
- [ ] 代码是否完整可运行

#### TC-2.2: Nuxt 3 边缘部署优化
**触发agent**: vue-nuxt-expert

**测试场景**:
```
用户请求: "我的Nuxt应用需要部署到Cloudflare Workers，
请优化代码以适应edge runtime限制。"
```

**预期行为**:
1. ✅ 识别edge deployment场景
2. ✅ 提到 📖 resources/vue-nuxt/edge-deployment-optimization.md
3. ✅ 读取该文件获取Cloudflare Workers配置
4. ✅ 提供edge-compatible代码示例

**验证点**:
- [ ] 是否读取edge-deployment-optimization.md
- [ ] 是否提供Cloudflare Workers配置
- [ ] 是否说明edge runtime限制

#### TC-2.3: Vue Composition API高级模式
**触发agent**: vue-fullstack-pro

**测试场景**:
```
用户请求: "需要创建一个复杂的购物车composable，
支持本地存储持久化、实时价格更新、库存检查。"
```

**预期行为**:
1. ✅ Agent激活vue-fullstack-pro
2. ✅ 提到 📖 resources/vue-fullstack/composition-api-patterns.md
3. ✅ 读取该文件获取useCart composable示例
4. ✅ 提供完整的reactive、computed、watch实现

**验证点**:
- [ ] 是否读取composition-api-patterns.md
- [ ] 是否提供完整的composable实现
- [ ] 代码是否包含持久化、实时更新逻辑

---

### Test Suite 3: React组件开发场景

#### TC-3.1: 设计系统集成 (shadcn/ui)
**触发agent**: react-component-pro

**测试场景**:
```
用户请求: "我需要使用shadcn/ui构建一个可访问的Modal组件，
符合WCAG 2.1 AA标准，支持键盘导航。"
```

**预期行为**:
1. ✅ Agent激活react-component-pro
2. ✅ 提到 📖 resources/react-components/design-systems-accessibility.md
3. ✅ 读取该文件获取WCAG合规Modal示例
4. ✅ 提供shadcn/ui集成代码

**验证点**:
- [ ] 是否读取design-systems-accessibility.md
- [ ] 是否提供WCAG合规代码
- [ ] 是否包含ARIA属性和键盘导航

#### TC-3.2: Storybook文档化
**触发agent**: react-component-pro

**测试场景**:
```
用户请求: "为我的Button组件创建Storybook stories，
包括所有变体、交互测试和a11y检查。"
```

**预期行为**:
1. ✅ 识别Storybook场景
2. ✅ 提到 📖 resources/react-components/storybook-documentation.md
3. ✅ 读取该文件获取story模板
4. ✅ 提供完整的stories、play function、a11y addon配置

**验证点**:
- [ ] 是否读取storybook-documentation.md
- [ ] 是否提供完整的story配置
- [ ] 是否包含交互测试和a11y检查

---

### Test Suite 4: 基础设施架构场景

#### TC-4.1: 多云架构设计
**触发agent**: infrastructure-architect-pro

**测试场景**:
```
用户请求: "需要设计一个multi-cloud架构，主要在AWS运行，
Azure作为DR，GCP用于AI/ML工作负载。"
```

**预期行为**:
1. ✅ Agent激活infrastructure-architect-pro
2. ✅ 提到 📖 resources/infrastructure/cloud-architecture-patterns.md
3. ✅ 读取该文件获取multi-cloud patterns
4. ✅ 提供架构决策框架和平台选择rationale

**验证点**:
- [ ] 是否读取cloud-architecture-patterns.md
- [ ] 是否提供multi-cloud架构图/描述
- [ ] 是否说明各云平台的使用场景

#### TC-4.2: 灾难恢复计划
**触发agent**: infrastructure-architect-pro

**测试场景**:
```
用户请求: "设计RTO=1小时、RPO=5分钟的灾难恢复方案，
包括自动化failover和数据备份策略。"
```

**预期行为**:
1. ✅ 识别HA/DR场景
2. ✅ 提到 📖 resources/infrastructure/high-availability-disaster-recovery.md
3. ✅ 读取该文件获取DR策略
4. ✅ 提供符合RTO/RPO要求的方案

**验证点**:
- [ ] 是否读取high-availability-disaster-recovery.md
- [ ] 是否计算RTO/RPO可行性
- [ ] 是否提供具体的failover机制

#### TC-4.3: Terraform最佳实践
**触发agent**: infrastructure-architect-pro

**测试场景**:
```
用户请求: "我们的Terraform代码库有3000行，状态文件管理混乱。
请提供重构方案和module设计最佳实践。"
```

**预期行为**:
1. ✅ 识别IaC/Terraform场景
2. ✅ 提到 📖 resources/infrastructure/infrastructure-as-code-terraform.md
3. ✅ 读取该文件获取module patterns和state management
4. ✅ 提供重构roadmap

**验证点**:
- [ ] 是否读取infrastructure-as-code-terraform.md
- [ ] 是否提供module设计模式
- [ ] 是否包含state management策略

---

### Test Suite 5: 安全基础设施场景

#### TC-5.1: DevSecOps Pipeline构建
**触发agent**: security-infrastructure-pro

**测试场景**:
```
用户请求: "构建一个完整的DevSecOps流水线，集成SAST、DAST、
容器扫描和secret检测。"
```

**预期行为**:
1. ✅ Agent激活security-infrastructure-pro
2. ✅ 提到 📖 resources/security-infrastructure/devsecops-pipeline-security.md
3. ✅ 读取该文件获取完整pipeline配置
4. ✅ 提供GitHub Actions/GitLab CI配置

**验证点**:
- [ ] 是否读取devsecops-pipeline-security.md
- [ ] 是否提供SAST/DAST/SCA集成
- [ ] pipeline配置是否完整可用

#### TC-5.2: 安全事件响应
**触发agent**: security-infrastructure-pro

**测试场景**:
```
用户请求: "检测到可疑的AWS IAM活动，需要立即进行安全调查和取证。"
```

**预期行为**:
1. ✅ 识别安全事件场景
2. ✅ 提到 📖 resources/security-infrastructure/incident-response-forensics.md
3. ✅ 读取该文件获取incident response playbook
4. ✅ 提供forensics investigation步骤

**验证点**:
- [ ] 是否读取incident-response-forensics.md
- [ ] 是否提供6-phase响应流程
- [ ] 是否包含evidence collection

#### TC-5.3: STRIDE威胁建模
**触发agent**: security-infrastructure-pro

**测试场景**:
```
用户请求: "为我们的支付系统进行STRIDE威胁建模，
识别潜在的安全风险。"
```

**预期行为**:
1. ✅ 识别威胁建模场景
2. ✅ 提到 📖 resources/security-infrastructure/threat-modeling-assessment.md
3. ✅ 读取该文件获取STRIDE方法论
4. ✅ 应用STRIDE到支付系统

**验证点**:
- [ ] 是否读取threat-modeling-assessment.md
- [ ] 是否应用STRIDE (Spoofing, Tampering, Repudiation, etc.)
- [ ] 是否提供风险缓解措施

---

### Test Suite 6: 性能和用户体验

#### TC-6.1: 加载性能测试
**测试方法**: 使用Read工具读取主文件和资源文件，对比token消耗

**测试场景**:
```
场景A: 只读取主文件 (devops-sre-pro.md - 220行)
场景B: 读取主文件 + 1个资源文件 (incident-response-playbook.md)
场景C: 优化前读取完整文件 (1,387行)
```

**预期结果**:
- [ ] 场景A token消耗 < 场景B < 场景C
- [ ] 场景A响应速度最快
- [ ] 按需加载资源文件有效

#### TC-6.2: 导航清晰度测试
**测试方法**: 用户视角评估

**评估点**:
- [ ] 主文件中的 📖 emoji是否醒目
- [ ] 资源文件链接描述是否清晰
- [ ] 用户能否快速找到需要的详细内容
- [ ] Claude是否主动读取相关资源

#### TC-6.3: 功能完整性检查
**测试方法**: 对比优化前后的功能列表

**验证点**:
- [ ] 所有code examples是否完整保留
- [ ] 所有best practices是否保留
- [ ] 没有内容丢失
- [ ] 新增的navigation links是否有效

---

## 🔄 测试执行流程

### Phase 1: 自动化验证 (5分钟)
1. 验证所有主文件 ≤ 500行
2. 验证所有资源文件存在
3. 验证YAML frontmatter格式
4. 验证文件路径链接

### Phase 2: 功能测试 (30分钟)
执行以下核心测试用例：
- TC-1.1: 生产事件响应
- TC-2.1: Nuxt 3 SSR项目
- TC-3.1: React设计系统集成
- TC-4.1: 多云架构设计
- TC-5.1: DevSecOps Pipeline

### Phase 3: Delegation测试 (15分钟)
- TC-1.3: DevOps delegation
- 验证agents之间的协作

### Phase 4: 性能测试 (10分钟)
- TC-6.1: 加载性能对比
- TC-6.2: 导航清晰度

### Phase 5: 用户体验验证 (10分钟)
- TC-6.3: 功能完整性
- 整体使用体验反馈

---

## ✅ 测试通过标准

### 必须通过 (P0)
- [ ] 所有agents能正确激活
- [ ] 资源文件能被正常读取
- [ ] 没有功能丢失
- [ ] Delegation pattern工作正常
- [ ] 500行规则100%合规

### 应该通过 (P1)
- [ ] 📖 导航链接清晰有效
- [ ] Claude主动读取相关资源
- [ ] 代码示例完整可用
- [ ] 性能有明显提升

### 建议通过 (P2)
- [ ] 用户体验评分 ≥ 8/10
- [ ] 文档组织清晰度 ≥ 8/10
- [ ] 可维护性提升明显

---

## 📊 测试报告模板

```markdown
# 测试执行报告

**执行日期**: YYYY-MM-DD
**执行人**: [Name]
**测试环境**: Claude Code CLI / Web

## 测试结果汇总

| Test Suite | 总数 | 通过 | 失败 | 通过率 |
|-----------|------|------|------|--------|
| DevOps SRE | 3 | - | - | -% |
| Vue/Nuxt | 3 | - | - | -% |
| React | 2 | - | - | -% |
| Infrastructure | 3 | - | - | -% |
| Security | 3 | - | - | -% |
| Performance | 3 | - | - | -% |
| **总计** | **17** | **-** | **-** | **-%** |

## 详细测试记录

### TC-1.1: 生产事件响应
- **状态**: ✅ PASS / ❌ FAIL
- **执行时间**: XX秒
- **实际行为**: [描述]
- **问题**: [如有]
- **截图**: [如有]

[... 其他测试用例 ...]

## 发现的问题

### 问题 #1: [标题]
- **严重程度**: Critical / High / Medium / Low
- **Test Case**: TC-X.X
- **描述**: [详细描述]
- **复现步骤**: [步骤]
- **建议修复**: [建议]

## 总体评估

### 优点
- [列出优点]

### 改进建议
- [列出建议]

### 结论
[总体结论和建议]
```

---

## 🚀 准备执行测试

现在测试计划已准备好，可以开始执行了。建议从Phase 2的核心功能测试开始。
