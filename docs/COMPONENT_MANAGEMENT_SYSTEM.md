# 组件管理系统文档

> **实现日期**: 2025-11-07
> **版本**: 1.0

---

## 📋 系统概述

Claude-Kits 组件管理系统提供全自动的组件扫描、合规性检查和可视化管理功能。

### 核心功能

1. **自动扫描组件目录** - 检测新增和修改的组件
2. **合规性验证和自动修正** - 确保符合 Claude Code 官方规范
3. **组件注册表管理** - JSON格式的组件元数据库
4. **TUI 可视化界面** - 友好的图形化管理界面

---

## 🔧 系统组成

### 1. 组件扫描器 (`components_scanner.py`)

**位置**: `/opt/claude/Claude-Kits/scripts/components_scanner.py`

**功能**:
- 扫描 `components/agents`、`components/commands`、`components/skills` 目录
- 检测新增和修改的组件（基于文件哈希值）
- 验证组件是否符合官方规范
- 自动修正不合规组件
- 更新组件注册表

**使用方法**:
```bash
# 手动运行扫描器
python scripts/components_scanner.py

# 或使用可执行方式
./scripts/components_scanner.py
```

**输出示例**:
```
======================================================================
Claude-Kits 组件扫描和合规性检查工具
======================================================================

扫描结果:
  Agents:   92 个
    - 新增: 5 个
    - 修改: 2 个
  Commands: 63 个
    - 新增: 3 个
    - 修改: 0 个
  Skills:   60 个
    - 新增: 0 个
    - 修改: 1 个

======================================================================
开始合规性检查...
======================================================================

✓ api-designer.md - 合规
❌ custom-agent.md:
   - 缺少 YAML frontmatter
   尝试自动修正...
   ✓ 已修正

✓ 备份注册表到: .backups/components_registry_20251107_131109.json
✓ 注册表已更新: components_registry.json
```

### 2. 组件注册表 (`components_registry.json`)

**位置**: `/opt/claude/Claude-Kits/components_registry.json`

**结构**:
```json
{
  "last_scan": "2025-11-07T13:11:09.123456",
  "components": {
    "agents": {
      "debugger": {
        "file": "debugger.md",
        "path": "components/agents/debugger.md",
        "hash": "abc123...",
        "name": "debugger",
        "description": "Expert debugger agent...",
        "model": "sonnet"
      },
      ...
    },
    "commands": {
      "review": {
        "file": "review.md",
        "path": "components/commands/review.md",
        "hash": "def456...",
        "description": "Code review command"
      },
      ...
    },
    "skills": {
      "code-review-excellence": {
        "dir": "code-review-excellence",
        "path": "components/skills/code-review-excellence",
        "hash": "ghi789...",
        "name": "code-review-excellence",
        "description": "Master effective code review practices..."
      },
      ...
    }
  },
  "metadata": {
    "total_agents": 92,
    "total_commands": 63,
    "total_skills": 60,
    "total_hooks": 0
  }
}
```

### 3. TUI 增强功能 (`claude_tui.py`)

**位置**: `/opt/claude/Claude-Kits/scripts/claude_tui.py`

**新增功能**:

#### 启动时自动扫描
```bash
python scripts/claude_tui.py

# 启动时会自动:
# 1. 显示 Claude-Kits LOGO
# 2. 扫描组件目录
# 3. 加载组件注册表
# 4. 显示组件统计
```

#### View Details 功能
在 **Agents**, **Skills**, **Commands** 菜单中新增 **View Details** 选项：

- 浏览所有可用组件
- 查看组件详细信息（名称、描述、模型、路径等）
- 快速了解组件功能和适用范围

**使用流程**:
```
1. 启动 TUI
2. 选择 "Subagents" 或 "Agent Skills" 或 "Slash Commands"
3. 选择 "View Details"
4. 浏览组件列表
5. 输入编号查看详情
```

**显示效果**:
```
╔══════════════════════════════════════════════════════════╗
║                      debugger                             ║
╚══════════════════════════════════════════════════════════╝

名称          debugger
类型          agents
文件          debugger.md
路径          components/agents/debugger.md
模型          sonnet
描述          Expert in debugging using modern debugging tools,
              observability platforms, and advanced debugging
              techniques for complex distributed systems.
```

---

## 📖 合规性检查规则

### Agents 规范

**必需项**:
- ✅ YAML frontmatter
- ✅ `name` 字段
- ✅ `description` 字段
- ✅ `model` 字段（推荐值: sonnet）

**检查示例**:
```yaml
---
name: debugger
description: Expert debugger agent for complex systems
model: sonnet
---

# Agent content...
```

### Skills 规范

**必需项**:
- ✅ YAML frontmatter（在 SKILL.md 中）
- ✅ `name` 字段
- ✅ `description` 字段（包含触发关键词）
- ✅ SKILL.md 主文件 < 500 行

**目录结构**:
```
skill-name/
├── SKILL.md        # 主文件（必须 < 500 行）
└── resources/      # 详细内容（可选）
    ├── topic-1.md
    └── topic-2.md
```

### Commands 规范

**推荐项**:
- 📝 YAML frontmatter（非必需，但推荐）
- 📝 `description` 字段
- 📝 `allowed-tools` 字段

**示例**:
```yaml
---
description: Code review command for git diff
allowed-tools: Read, Grep, Bash
---

# Command content...
```

---

## 🛠️ 自动修正功能

### 修正范围

扫描器会自动修正以下问题：

1. **缺少 frontmatter** - 自动添加默认 frontmatter
2. **缺少必需字段** - 自动补充默认值
3. **字段不完整** - 补充缺失的字段

### 修正流程

```
检测到问题 → 创建备份(.bak) → 自动修正 → 通知用户
```

### 备份文件

所有修正前都会创建备份：
- **文件备份**: `*.md.bak`
- **注册表备份**: `.backups/components_registry_*.json`

### 修正后的操作

⚠️ **重要**: 自动修正后，请手动检查并更新：
- Agent/Skill 的 `description` 字段
- Agent 的 `name` 字段（如果自动生成的不准确）

---

## 📊 使用场景

### 场景 1: 手工添加新组件

```bash
# 1. 手工复制组件到 components 目录
cp my-custom-agent.md components/agents/

# 2. 运行扫描器检查合规性
python scripts/components_scanner.py

# 3. 启动 TUI 查看新组件
python scripts/claude_tui.py

# 4. 在 TUI 中通过 "View Details" 确认组件信息
```

### 场景 2: 批量复制组件

```bash
# 1. 批量复制
cp reference/agents/plugins/*/agents/*.md components/agents/

# 2. 运行扫描和修正
python scripts/components_scanner.py

# 3. 检查修正报告
# 查看哪些文件被自动修正

# 4. 手动更新自动生成的描述
# 编辑 .md 文件，完善 description 字段
```

### 场景 3: 定期检查组件状态

```bash
# 添加到 crontab 或 CI/CD
0 */6 * * * cd /opt/claude/Claude-Kits && python scripts/components_scanner.py

# 或使用 hook（参考 hooks 文档）
```

### 场景 4: TUI 浏览组件

```bash
# 1. 启动 TUI
python scripts/claude_tui.py

# 2. 选择组件类型
# → Subagents
# → View Details

# 3. 浏览组件列表
# 共 92 个组件
# 1. api-designer - Expert in API design...
# 2. debugger - Expert debugger...
# ...

# 4. 输入编号查看详情
# 选择: 2
# 显示 debugger 的完整信息
```

---

## 🔄 工作流程

### 完整工作流程

```
用户添加组件
    ↓
启动 TUI / 运行扫描器
    ↓
扫描 components 目录
    ↓
检测新增/修改的文件
    ↓
合规性检查
    ↓
自动修正（如需要）
    ↓
更新注册表
    ↓
用户通过 TUI 查看和管理
```

### 数据流

```
components/
├── agents/*.md  ┐
├── commands/*.md├→ Scanner → components_registry.json → TUI Display
└── skills/*/    ┘
```

---

## 🎯 最佳实践

### 1. 组件命名

- **Agents**: 小写连字符 `backend-architect.md`
- **Commands**: 小写连字符 `code-review.md`
- **Skills**: 小写连字符目录 `code-review-excellence/`

### 2. 描述编写

```yaml
# ❌ 不好
description: A debugger

# ✅ 好
description: Expert debugger agent for complex distributed systems,
  using modern debugging tools, observability platforms, and advanced
  debugging techniques. Use for root cause analysis, performance issues,
  and production debugging.
```

### 3. 定期维护

```bash
# 每周运行一次扫描
python scripts/components_scanner.py

# 检查备份目录大小
du -sh .backups/

# 清理旧备份（保留最近30天）
find .backups/ -name "*.json" -mtime +30 -delete
```

### 4. 版本控制

```bash
# 将注册表纳入版本控制
git add components_registry.json
git commit -m "Update: component registry"

# 不要提交备份文件
echo ".backups/" >> .gitignore
echo "*.bak" >> .gitignore
```

---

## 🐛 故障排查

### 问题 1: 扫描器未找到

```bash
# 检查文件是否存在
ls -l scripts/components_scanner.py

# 检查权限
chmod +x scripts/components_scanner.py

# 手动运行测试
python3 scripts/components_scanner.py
```

### 问题 2: TUI 无法加载注册表

```bash
# 检查注册表文件
ls -l components_registry.json

# 手动重新生成
python scripts/components_scanner.py

# 检查 JSON 格式
python3 -c "import json; json.load(open('components_registry.json'))"
```

### 问题 3: 自动修正失败

```bash
# 检查备份文件
ls components/agents/*.bak

# 手动恢复
mv components/agents/my-agent.md.bak components/agents/my-agent.md

# 手动添加 frontmatter
```

### 问题 4: 组件未显示

```bash
# 重新扫描
python scripts/components_scanner.py

# 检查注册表
grep "component-name" components_registry.json

# 检查文件权限
ls -l components/agents/component-name.md
```

---

## 📚 相关文档

- [组件扫描器源码](../scripts/components_scanner.py)
- [TUI 源码](../scripts/claude_tui.py)
- [组件注册表](../components_registry.json)
- [角色清单系统](ROLE_CHECKLISTS_IMPLEMENTATION.md)

---

## 🔮 未来改进

### 计划中的功能

- [ ] **组件依赖检查** - 检测组件间的依赖关系
- [ ] **组件版本管理** - 跟踪组件版本历史
- [ ] **组件导入/导出** - 批量导入导出组件
- [ ] **组件搜索** - 基于关键词的快速搜索
- [ ] **组件评分** - 基于使用频率的推荐
- [ ] **自动化测试** - 组件功能自动测试
- [ ] **Web 界面** - 基于 Web 的组件管理界面

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 扫描速度 | ~100 组件/秒 |
| 注册表大小 | ~100KB (200 组件) |
| 启动时间 | <5秒 |
| 内存占用 | <50MB |

---

**维护**: Claude-Kits Team | **许可**: MIT
