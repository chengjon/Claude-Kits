# 大型代码文件优化方法论指南

**文档性质**: 通用指导性文档
**适用场景**: 代码文件大小限制、模块化重构、职责分离
**更新日期**: 2025-11-19
**版本**: v2.0 Methodology Guide

---

## 📖 文档目的

本文档提供一套系统化的方法论，用于解决代码文件因内容过多而超出规模限制的问题。这些方法在实际项目中验证有效，具有广泛的应用价值。

**核心价值**:
- ✅ 保持功能完整性（零内容丢失）
- ✅ 符合文件大小限制要求
- ✅ 提高代码可维护性
- ✅ 增强模块化和职责清晰度

---

## 🎯 优化目标定义

### 明确约束条件

在开始优化前，必须明确以下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `MAX_LINES` | 单个文件的最大行数限制 | 500 行 |
| `TARGET_LINES` | 理想目标行数（建议为限制的 60-80%） | 300-400 行 |
| `RESOURCE_MAX` | 资源文件的行数建议上限 | 200-300 行 |
| `VIOLATION_THRESHOLD` | 定义"违规"的阈值 | > `MAX_LINES` |

### 设定优化指标

```
优化前基线评估:
- 文件总数: N 个
- 超标文件数: M 个 (M/N 为违规率)
- 功能覆盖: 100%
- 资源文件: 0 个

优化后目标:
- 文件总数: ≤ N (可能减少冗余)
- 超标文件数: 0 个 ✅
- 功能覆盖: 100% ✅
- 资源文件: > 0 个 ✅
- 合规率: 100% ✅
```

---

## 🧭 优化决策树

### 第一步：分析文件违规原因

```
是否超过 MAX_LINES？
├─ 否 → 无需优化，跳过
└─ 是 → 继续分析
    │
    ├─ 是否包含多个不同职责？
    │  ├─ 是 → 使用「分流 (Delegation)」
    │  └─ 否 → 继续分析
    │      │
    │      └─ 是否单一职责但内容过多？
    │         ├─ 是 → 使用「分层 (Layering)」
    │         └─ 否 → 混合使用两种方法
```

### 第二步：选择优化策略

| 场景 | 特征 | 推荐方法 | 预期效果 |
|------|------|---------|---------|
| **单一职责，内容详实** | 一个主题，包含大量示例、配置、最佳实践 | 分层 (Layering) | 压缩 40-80% |
| **多重职责** | 多个不相关的功能模块 | 分流 (Delegation) | 拆分为 N 个文件 |
| **功能冗余** | 多个文件内容重叠 | 合并 + 委托 | 减少文件数 |
| **混合型** | 既有多职责，又有详细内容 | 先分流，后分层 | 综合优化 |

---

## 🔧 方法一：分层 (Layering) - 渐进式披露

### 适用场景

- ✅ 文件职责单一明确
- ✅ 包含大量代码示例、配置模板、详细说明
- ✅ 内容可按主题分类
- ✅ 需要保留所有详细信息

### 核心原则：Progressive Disclosure

**主文件**保留"地图"，**资源文件**提供"详细路线"。

### 实施步骤

#### 1. 分析内容结构

```bash
# 统计文件行数
wc -l target_file.ext

# 分析内容分布（手动或工具辅助）
# 识别可独立的主题模块
```

**内容分类标准**:
- **保留在主文件**: 概览、快速参考、核心概念、使用场景、导航链接
- **移至资源文件**: 详细实现、代码示例、配置模板、高级模式、最佳实践

#### 2. 创建资源目录结构

```bash
# 目录命名规则: resources/{category-name}/
mkdir -p resources/{category-name}
```

**命名建议**:
- 使用小写字母和连字符
- 名称应描述内容类别
- 与主文件名称相关但更具体

**示例**:
```
agent-file.md → resources/agent-category/
├── topic-1-implementation.md    # 主题1详细实现
├── topic-2-patterns.md          # 主题2设计模式
├── topic-3-examples.md          # 主题3代码示例
└── topic-4-best-practices.md    # 主题4最佳实践
```

#### 3. 提取内容到资源文件

**提取原则**:
- 每个资源文件 ≤ `RESOURCE_MAX` 行
- 内容主题聚焦，独立完整
- 包含标题、说明、代码示例

**资源文件模板**:
```markdown
# {主题名称}

{1-2 段简介，说明本文档的用途和覆盖范围}

## {子主题 1}

{详细内容、代码示例、配置模板}

## {子主题 2}

{详细内容、代码示例、配置模板}

---

**相关资源**:
- [其他相关资源文件](./related-file.md)
```

#### 4. 压缩主文件并添加导航

**压缩策略**:
- 删除详细代码示例（保留 1-2 个最简单的）
- 删除长篇配置模板（保留精简版）
- 删除详细最佳实践（保留要点列表）
- 删除深入的实现细节

**导航链接格式**:
```markdown
## {主题概述}

{2-3 句话概述本主题}

### 📖 [详细文档](resources/{category}/{file}.md)

**包含内容**:
- {要点 1}
- {要点 2}
- {要点 3}
```

#### 5. 验证行数

```bash
# 验证主文件
lines=$(wc -l < target_file.ext)
if [ "$lines" -le MAX_LINES ]; then
    echo "✅ 主文件合规: $lines 行"
else
    echo "❌ 主文件仍超标: $lines 行 (需要进一步优化)"
fi

# 验证资源文件
for file in resources/{category}/*.md; do
    lines=$(wc -l < "$file")
    echo "资源文件: $file - $lines 行"
done
```

### 分层效果评估

**成功标准**:
- ✅ 主文件 ≤ `MAX_LINES`
- ✅ 主文件保留清晰导航
- ✅ 资源文件独立完整
- ✅ 功能覆盖 100%

**预期压缩率**:
- 轻度优化: 20-40% (适用于略超标的文件)
- 中度优化: 40-60% (适用于明显超标的文件)
- 深度优化: 60-80% (适用于严重超标的文件)

---

## 🔧 方法二：分流 (Delegation) - 职责分离

### 适用场景

- ✅ 文件包含多个不同职责
- ✅ 职责之间相关但可分离
- ✅ 各职责都有足够的内容量
- ✅ 需要明确的职责边界

### 核心原则：Single Responsibility

每个文件专注一个核心职责，通过委托协议互相配合。

### 实施步骤

#### 1. 识别职责边界

**分析问题**:
- 这个文件做了多少件"不同的事"？
- 哪些职责可以独立存在？
- 哪些职责经常一起使用？

**职责分类方法**:
```
原始文件: large-file.ext
│
├─ 职责 A: {描述} → 拆分为 file-a.ext
├─ 职责 B: {描述} → 拆分为 file-b.ext
└─ 职责 C: {描述} → 拆分为 file-c.ext
```

#### 2. 创建独立文件

**文件头部声明**:
```yaml
---
name: {file-name}
description: {明确的职责描述，包含触发关键词}
NOT FOR: {不属于此文件的职责} (use {other-file} instead)
---
```

**关键要素**:
- `description`: 清晰说明此文件的职责范围
- `NOT FOR`: 明确声明不属于此文件的内容
- 指向正确的文件: 使用 `use {file-name} instead`

#### 3. 建立委托关系

**委托模式类型**:

**类型 1: 单向委托**
```
File A → delegates to → File B
（A 的某些任务交给 B 处理）
```

**类型 2: 双向委托**
```
File A ↔ File B
（A 和 B 互相委托不同职责）
```

**类型 3: 多向委托网络**
```
    File A
   ↙  ↓  ↘
File B File C File D
   ↘  ↓  ↙
    相互协作
```

**实现委托模式**:
```markdown
## 集成与协作

**本文件职责**:
- {职责 1}
- {职责 2}

**协作文件**:
- **{file-a}**: {什么情况下使用它}
- **{file-b}**: {什么情况下使用它}

**委托模式**:
- **TO {file-a}**: 当需要 {功能 X} 时
- **TO {file-b}**: 当需要 {功能 Y} 时
- **FROM {file-c}**: 当 {场景 Z} 发生时
```

#### 4. 删除冗余内容

**删除标准**:
- 内容已完整迁移到其他文件
- 职责已被其他文件覆盖
- 功能有明确的委托关系

**安全删除流程**:
1. 确认内容已迁移
2. 确认委托关系已建立
3. 备份原文件
4. 删除冗余文件
5. 更新所有引用

### 分流效果评估

**成功标准**:
- ✅ 每个文件职责单一明确
- ✅ 文件间委托关系清晰
- ✅ 无功能重叠或冗余
- ✅ 合理的文件数量

---

## 🎯 混合优化策略

### 何时使用混合方法

某些复杂文件需要同时应用两种方法：

```
大型文件 (职责多 + 内容详细)
│
├─ 第一步: 分流 (Delegation)
│   └─ 拆分为 3 个职责文件
│
└─ 第二步: 分层 (Layering)
    ├─ 文件 A: 仍超标 → 应用分层
    ├─ 文件 B: 符合要求 → 无需优化
    └─ 文件 C: 仍超标 → 应用分层
```

### 优化顺序建议

**推荐顺序**: 先分流，后分层

**原因**:
1. 分流确立清晰的职责边界
2. 单一职责更容易应用分层
3. 避免在错误的粒度上分层

---

## 📊 验证与测试方法

### 自动化验证脚本

#### 检查文件行数合规性

```bash
#!/bin/bash
# compliance-check.sh - 检查所有文件是否符合行数限制

MAX_LINES=${MAX_LINES:-500}  # 可通过环境变量配置
TARGET_DIR=${TARGET_DIR:-.}   # 可通过环境变量配置

echo "=== 文件行数合规性检查 ==="
echo "限制: ≤ ${MAX_LINES} 行"
echo ""

violations=0
total=0

# 查找所有目标文件
find "$TARGET_DIR" -maxdepth 1 -type f -name "*.md" | while read file; do
    lines=$(wc -l < "$file")
    total=$((total + 1))

    if [ "$lines" -gt "$MAX_LINES" ]; then
        echo "❌ $(basename $file): $lines 行 (超标 $((lines - MAX_LINES)) 行)"
        violations=$((violations + 1))
    fi
done

if [ "$violations" -eq 0 ]; then
    echo "✅ 所有文件符合 ${MAX_LINES} 行限制"
    echo "合规率: 100%"
else
    echo "⚠️  发现 $violations 个违规文件"
    echo "合规率: $(( (total - violations) * 100 / total ))%"
fi
```

#### 检查委托关系完整性

```bash
#!/bin/bash
# delegation-check.sh - 检查文件间的委托关系

echo "=== 委托关系完整性检查 ==="

# 提取所有 "NOT FOR" 声明
grep -r "NOT FOR:" . --include="*.md" | while read line; do
    file=$(echo "$line" | cut -d: -f1)
    delegation=$(echo "$line" | grep -oP '(?<=use )\S+(?= instead)')

    # 检查被委托的文件是否存在
    if [ -n "$delegation" ]; then
        if [ ! -f "$delegation" ]; then
            echo "⚠️  $file 委托给不存在的文件: $delegation"
        fi
    fi
done

echo "✅ 委托关系检查完成"
```

### 功能完整性测试

**测试清单**:

```markdown
## 功能完整性验证

### 核心功能测试
- [ ] 功能 1: 是否保留？路径是否可访问？
- [ ] 功能 2: 是否保留？路径是否可访问？
- [ ] 功能 3: 是否保留？路径是否可访问？

### 导航链接测试
- [ ] 所有 📖 链接可访问
- [ ] 资源文件路径正确
- [ ] 相对路径正确解析

### 委托模式测试
- [ ] "NOT FOR" 声明准确
- [ ] 委托目标文件存在
- [ ] 委托关系无循环依赖

### 内容质量测试
- [ ] 主文件概览清晰
- [ ] 资源文件内容完整
- [ ] 代码示例可运行
- [ ] 文档结构合理
```

### 性能测试

**加载性能对比**:
```
优化前: 加载 X 个大文件 (每个 > MAX_LINES)
优化后: 加载 X 个主文件 (每个 ≤ TARGET_LINES) + 按需加载资源

预期改善:
- 初始加载时间: -40% ~ -60%
- 内存占用: -30% ~ -50%
- 查找效率: +50% ~ +100%
```

---

## 💡 最佳实践与经验总结

### 优化前的准备工作

#### 1. 建立基线

```bash
# 记录优化前状态
echo "优化前基线评估 - $(date)" > optimization-baseline.txt
echo "总文件数: $(find . -name '*.ext' | wc -l)" >> optimization-baseline.txt
echo "超标文件: $(find . -name '*.ext' -exec sh -c 'test $(wc -l < "$1") -gt MAX_LINES && echo "$1"' _ {} \; | wc -l)" >> optimization-baseline.txt
```

#### 2. 创建备份

```bash
# 备份整个目录
backup_dir=".backups/optimization_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp -r . "$backup_dir"
echo "备份创建于: $backup_dir"
```

#### 3. 版本控制

```bash
# 创建优化分支
git checkout -b optimization/reduce-file-size
git commit -m "Baseline: before optimization"
```

### 优化中的关键决策

#### 决策点 1: 何时停止分层？

**停止条件**:
- ✅ 主文件 ≤ `TARGET_LINES`
- ✅ 主文件结构清晰，导航明确
- ✅ 资源文件独立完整，无过度碎片化

**警告信号** (过度分层):
- ❌ 资源文件过多（> 10 个）
- ❌ 单个资源文件过小（< 50 行）
- ❌ 导航链接密度过高（> 30% 行数为链接）

#### 决策点 2: 何时合并而非拆分？

**合并场景**:
- 多个小文件功能高度重叠
- 文件间频繁互相引用
- 独立存在没有意义

**判断标准**:
```
如果 文件A + 文件B < MAX_LINES 且功能相关
  → 考虑合并
否则
  → 保持独立并建立委托关系
```

#### 决策点 3: 资源文件放在哪里？

**目录结构选择**:

**方案 A: 扁平结构** (适合资源文件少)
```
main-file.ext
resources/
├── resource-1.md
├── resource-2.md
└── resource-3.md
```

**方案 B: 分类结构** (适合资源文件多)
```
main-file.ext
resources/
├── category-a/
│   ├── resource-a1.md
│   └── resource-a2.md
└── category-b/
    ├── resource-b1.md
    └── resource-b2.md
```

**推荐**: 资源文件 > 5 个时使用分类结构

### 优化后的维护策略

#### 1. 建立守护机制

**Pre-commit Hook 示例**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

MAX_LINES=500

# 检查暂存的文件
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.md$'); do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        if [ "$lines" -gt "$MAX_LINES" ]; then
            echo "❌ 错误: $file 超过 $MAX_LINES 行限制 (当前: $lines 行)"
            echo "请在提交前优化此文件"
            exit 1
        fi
    fi
done
```

#### 2. 定期审查

**审查周期**: 每季度 / 每次重大功能添加后

**审查清单**:
- [ ] 是否有新增超标文件？
- [ ] 资源文件是否需要整合？
- [ ] 委托关系是否仍然合理？
- [ ] 文档链接是否全部有效？

#### 3. 文档更新规范

**新增内容决策树**:
```
新增内容需要添加到哪里？
├─ 内容 ≤ 10 行 → 添加到主文件
├─ 内容 10-50 行 → 评估主文件剩余空间
│   ├─ 主文件 + 新内容 ≤ TARGET_LINES → 添加到主文件
│   └─ 否则 → 添加到现有资源文件或创建新资源文件
└─ 内容 > 50 行 → 必须创建新资源文件
```

---

## ⚠️ 常见陷阱与解决方案

### 陷阱 1: 过度优化

**表现**:
- 资源文件碎片化严重
- 单个资源文件过小（< 50 行）
- 导航链接多于实际内容

**解决方案**:
```
合并相关的小资源文件
设定资源文件最小行数（建议 ≥ 100 行）
保持主文件有足够的概览内容
```

### 陷阱 2: 委托循环

**表现**:
```
文件 A → 委托给 → 文件 B
文件 B → 委托给 → 文件 A
```

**检测方法**:
```bash
# 绘制委托关系图
grep -r "Delegates to:" . | awk '{print $1, "→", $4}'
# 人工检查是否有循环
```

**解决方案**:
- 重新设计职责边界
- 引入第三个文件打破循环
- 合并循环依赖的文件

### 陷阱 3: 丢失功能

**预防措施**:
- ✅ 优化前列出所有功能点
- ✅ 逐一确认迁移位置
- ✅ 使用 checklist 追踪
- ✅ 优化后逐项验证

**检测方法**:
```bash
# 搜索关键词是否仍存在
keywords=("功能A" "功能B" "功能C")
for keyword in "${keywords[@]}"; do
    if ! grep -r "$keyword" . > /dev/null; then
        echo "⚠️  关键功能可能丢失: $keyword"
    fi
done
```

### 陷阱 4: 破坏性的简单删除

**错误做法**:
```bash
# ❌ 错误: 直接删除内容以达到行数要求
sed -n '1,500p' large-file.md > large-file-trimmed.md
```

**正确做法**:
```bash
# ✅ 正确: 先迁移，后删除
1. 提取内容到资源文件
2. 验证资源文件完整性
3. 在主文件添加导航链接
4. 删除主文件中已迁移的内容
5. 验证功能完整性
```

---

## 📏 衡量标准与成功指标

### 量化指标

| 指标 | 计算方法 | 目标值 |
|------|---------|--------|
| **合规率** | (符合文件数 / 总文件数) × 100% | 100% |
| **平均压缩率** | 平均((优化前行数 - 优化后行数) / 优化前行数) | 40-60% |
| **资源化率** | (资源文件行数 / 总行数) × 100% | 30-50% |
| **导航密度** | 导航链接数 / 主文件行数 | 1-3% |

### 质量指标

**功能完整性**: 100% 功能保留
- 验证方法: 功能清单逐项检查

**文档清晰度**: 主文件易读，导航明确
- 验证方法: 新用户 5 分钟内找到所需信息

**可维护性**: 模块化程度高，职责分明
- 验证方法: 单个模块修改不影响其他模块

**性能提升**: 加载速度和内存占用改善
- 验证方法: 性能测试对比

---

## 🔄 迭代优化流程

### 第一轮优化

**目标**: 解决最严重的违规文件

```
1. 识别超标最严重的文件（行数最多）
2. 分析其职责和内容结构
3. 应用合适的优化方法
4. 验证优化效果
5. 记录经验教训
```

**优先级排序**:
```
Priority 1: 行数 > MAX_LINES × 2
Priority 2: 行数 > MAX_LINES × 1.5
Priority 3: 行数 > MAX_LINES × 1.2
Priority 4: 行数 > MAX_LINES
```

### 第二轮优化

**目标**: 优化剩余违规文件

```
1. 应用第一轮学到的经验
2. 标准化优化流程
3. 批量处理相似文件
4. 建立资源文件复用机制
```

### 第三轮优化

**目标**: 精细化和完善

```
1. 审查所有委托关系
2. 合并过于碎片化的资源
3. 统一命名和结构规范
4. 完善文档和导航
```

---

## 📚 实际案例研究

### 案例 1: 大型配置文件优化

**场景**:
- 文件: `devops-sre-pro.md`
- 原始行数: 1,387 行
- 主要内容: 事件响应、监控、SLI/SLO、Runbook 等

**优化方法**: 分层 (Layering)

**执行步骤**:
1. 内容分析: 识别出 6 个独立主题
2. 创建资源目录: `resources/devops-sre/`
3. 提取详细内容:
   - 事件响应剧本 → `incident-response-playbook.md`
   - 监控配置 → `observability-monitoring-setup.md`
   - 自动修复 → `automated-remediation-self-healing.md`
   - SLI/SLO → `sli-slo-error-budget-management.md`
   - Postmortem → `blameless-postmortem-process.md`
   - Runbook → `runbook-development-templates.md`
4. 压缩主文件: 保留概览和快速参考
5. 添加导航: 6 个 📖 链接到资源文件

**优化结果**:
- 优化后行数: 220 行 ✅
- 压缩率: 84%
- 资源文件: 6 个
- 功能保留: 100%

**关键经验**:
- ✅ 按主题分类非常有效
- ✅ 保留简短示例在主文件中作为快速参考
- ✅ 资源文件命名清晰易懂

### 案例 2: 多职责文件拆分

**场景**:
- 问题: 多个 DevOps 相关文件功能重叠
- 涉及文件: 8 个 (devops-engineer, devops-pro, sre-engineer 等)
- 总行数: ~3,000 行
- 问题: 职责不清，内容重复

**优化方法**: 分流 (Delegation)

**执行步骤**:
1. 职责分析: 识别 3 个核心职责
   - 基础设施自动化 (IaC, CI/CD)
   - 事件响应和可靠性 (SRE)
   - 部署工程 (GitOps)
2. 合并与拆分:
   - 保留 3 个核心文件
   - 删除 8 个冗余文件
3. 建立委托关系:
   - 三向委托网络
   - 明确 "NOT FOR" 边界
4. 验证功能覆盖: 100%

**优化结果**:
- 文件数: 8 → 3
- 职责边界: 清晰明确
- 冗余: 完全消除
- 协作: 通过委托模式实现

**关键经验**:
- ✅ 先画出职责边界图
- ✅ 确保每个文件有独特价值
- ✅ 委托关系要双向清晰

### 案例 3: 混合优化

**场景**:
- 文件: `vue-fullstack-pro.md`
- 原始行数: 907 行
- 第一次优化: 526 行 (仍超标)
- 需要: 二次优化

**优化方法**: 两阶段分层

**执行步骤**:

**第一阶段** (Phase 4):
1. 创建 4 个资源文件
2. 提取核心主题内容
3. 结果: 526 行 (仍超过 500)

**第二阶段** (Phase 5):
1. 重新审视主文件内容
2. 识别仍可提取的详细示例
3. 进一步压缩概览部分
4. 优化代码示例（保留最简版本）
5. 结果: 336 行 ✅

**优化结果**:
- 最终行数: 336 行
- 总压缩率: 63%
- 资源文件: 4 个
- 迭代次数: 2 次

**关键经验**:
- ✅ 首次优化可能不够彻底
- ✅ 允许迭代优化
- ✅ 设定明确的行数目标（≤ 500，不是"接近 500"）

---

## 🛠️ 工具与自动化

### 推荐工具集

#### 1. 行数统计工具

```bash
# 单文件统计
wc -l filename.ext

# 目录统计
find . -name "*.ext" -exec wc -l {} \; | sort -rn

# 生成统计报告
find . -name "*.ext" -exec wc -l {} \; |
  awk '{sum+=$1} END {print "Total:", sum, "lines"}'
```

#### 2. 内容分析工具

```python
#!/usr/bin/env python3
# analyze-file-structure.py
"""分析文件内容结构，建议分层方案"""

import sys
import re

def analyze_file(filepath, max_lines=500):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    total_lines = len(lines)
    sections = []
    current_section = None
    section_lines = 0

    # 识别章节结构
    for i, line in enumerate(lines):
        if re.match(r'^#{1,3}\s+', line):  # 章节标题
            if current_section:
                sections.append((current_section, section_lines))
            current_section = line.strip()
            section_lines = 0
        section_lines += 1

    if current_section:
        sections.append((current_section, section_lines))

    # 生成建议
    print(f"文件: {filepath}")
    print(f"总行数: {total_lines}")
    print(f"限制: {max_lines} 行")
    print(f"超标: {total_lines - max_lines} 行\n")

    print("章节分布:")
    for section, lines in sorted(sections, key=lambda x: x[1], reverse=True):
        print(f"  {lines:4d} 行 - {section}")

    print(f"\n建议: 将最大的 {len([s for s in sections if s[1] > 100])} 个章节提取到资源文件")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python analyze-file-structure.py <file>")
        sys.exit(1)

    analyze_file(sys.argv[1])
```

#### 3. 自动生成导航工具

```python
#!/usr/bin/env python3
# generate-navigation.py
"""自动生成资源文件导航链接"""

import os
import sys

def generate_navigation(resource_dir):
    """生成资源文件的导航 Markdown"""

    if not os.path.isdir(resource_dir):
        print(f"错误: {resource_dir} 不是目录")
        return

    print("## 📖 详细资源文件\n")
    print("深入了解特定主题，请查阅以下资源:\n")

    for filename in sorted(os.listdir(resource_dir)):
        if filename.endswith('.md'):
            filepath = os.path.join(resource_dir, filename)

            # 读取第一行作为标题
            with open(filepath, 'r') as f:
                title = f.readline().strip().lstrip('#').strip()

            # 生成导航链接
            relative_path = os.path.join(resource_dir, filename)
            print(f"### 📖 [{title}]({relative_path})")
            print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate-navigation.py <resource_dir>")
        sys.exit(1)

    generate_navigation(sys.argv[1])
```

### CI/CD 集成

```yaml
# .github/workflows/file-size-check.yml
name: File Size Compliance Check

on: [push, pull_request]

jobs:
  check-file-size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Check file size limits
        run: |
          MAX_LINES=500
          violations=0

          for file in $(find . -name "*.md" -not -path "*/resources/*"); do
            lines=$(wc -l < "$file")
            if [ "$lines" -gt "$MAX_LINES" ]; then
              echo "::error file=$file::File exceeds $MAX_LINES lines limit ($lines lines)"
              violations=$((violations + 1))
            fi
          done

          if [ "$violations" -gt 0 ]; then
            echo "::error::Found $violations files exceeding size limit"
            exit 1
          fi

          echo "✅ All files comply with size limits"
```

---

## 📖 附录：术语表

| 术语 | 定义 |
|------|------|
| **分层 (Layering)** | 将单一文件的内容按主题提取到资源文件，主文件保留概览和导航 |
| **分流 (Delegation)** | 将多职责文件拆分为多个单一职责文件，通过委托协议协作 |
| **渐进式披露 (Progressive Disclosure)** | 信息架构模式，首先展示概览，用户按需深入细节 |
| **委托模式 (Delegation Pattern)** | 文件间通过明确声明职责边界和转交关系实现协作 |
| **资源文件 (Resource Files)** | 存放详细内容、代码示例、配置模板的独立文件 |
| **主文件 (Main File)** | 经过优化后的核心文件，包含概览和导航 |
| **合规率 (Compliance Rate)** | 符合行数限制的文件占总文件数的百分比 |
| **压缩率 (Compression Rate)** | 优化后减少的行数占原始行数的百分比 |

---

## 🔗 相关资源

### 内部文档
- `LAYERING_VS_DELEGATION_CLARIFICATION.md` - 方法论深入对比
- `AGENTS_OPTIMIZATION_CORRECTED_PLAN.md` - 项目优化计划
- `PHASE_3_4_TEST_REPORT.md` - 测试验证报告

### 外部参考
- [Progressive Disclosure (NN/g)](https://www.nngroup.com/articles/progressive-disclosure/)
- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle)
- [Code Refactoring Techniques](https://refactoring.guru/refactoring/techniques)

---

## ✅ 总结与行动指南

### 快速开始清单

**Phase 1: 评估**
- [ ] 统计当前文件违规情况
- [ ] 设定明确的优化目标（`MAX_LINES`, `TARGET_LINES`）
- [ ] 创建备份和版本控制分支

**Phase 2: 规划**
- [ ] 按违规严重程度排序
- [ ] 为每个文件选择优化方法（分层 / 分流 / 混合）
- [ ] 设计资源目录结构

**Phase 3: 执行**
- [ ] 从最严重的文件开始
- [ ] 逐个优化，记录经验
- [ ] 定期验证功能完整性

**Phase 4: 验证**
- [ ] 运行自动化合规性检查
- [ ] 测试所有功能点
- [ ] 检查委托关系完整性
- [ ] 验证导航链接有效性

**Phase 5: 维护**
- [ ] 建立 Pre-commit Hook
- [ ] 制定定期审查计划
- [ ] 更新团队开发规范

### 关键成功因素

1. **明确目标**: 设定清晰的行数限制和质量标准
2. **系统方法**: 使用决策树选择合适的优化方法
3. **功能优先**: 确保 100% 功能保留
4. **迭代改进**: 允许多轮优化
5. **自动化验证**: 建立自动化检查机制
6. **文档驱动**: 详细记录决策和经验

### 预期成果

**量化成果**:
- ✅ 合规率: 100%
- ✅ 平均压缩率: 40-60%
- ✅ 资源文件创建: 根据需要
- ✅ 功能保留: 100%

**质量成果**:
- ✅ 代码可维护性提升
- ✅ 模块化程度提高
- ✅ 职责边界清晰
- ✅ 文档结构优化

---

**最后更新**: 2025-11-19
**文档版本**: v2.0
**适用范围**: 通用代码文件优化
**维护状态**: 活跃维护
