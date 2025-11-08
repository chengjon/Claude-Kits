# Reddit-Case 安装指南

本指南说明如何安全地将 Reddit-Case 组件安装到你的项目中。

## 🛡️ 安全保证

**本安装器遵循严格的安全原则：**

1. ✅ **永不覆盖现有文件** - 如果文件已存在，会询问你如何处理
2. ✅ **所有修改需要授权** - 每个操作都需要你的确认
3. ✅ **完全透明** - 安装前会显示详细的操作列表
4. ✅ **支持 dry-run** - 可以预览而不执行实际操作

---

## 快速开始

### 方法 1: 使用安全安装脚本（推荐）

```bash
# 1. 克隆或导航到 Claude-Kits 仓库
cd /path/to/Claude-Kits

# 2. 安装到你的项目（交互式）
python scripts/install_reddit_case.py /path/to/your/project

# 3. 按照提示进行操作
```

### 方法 2: 预览模式（先查看再安装）

```bash
# 使用 --dry-run 查看将要执行的操作
python scripts/install_reddit_case.py /path/to/your/project --dry-run

# 确认无误后，再执行实际安装
python scripts/install_reddit_case.py /path/to/your/project
```

---

## 详细使用说明

### 命令选项

```bash
python scripts/install_reddit_case.py <目标目录> [选项]
```

**选项：**
- `--dry-run` - 预览模式，不执行实际操作
- `--no-interactive` - 非交互模式（自动跳过所有冲突）

### 安装流程

安装器会按以下步骤执行：

#### 1. 前提条件检查
- 检查目标目录是否存在
- 验证写入权限
- 显示源目录和目标目录

#### 2. 冲突扫描
安装器会扫描以下可能的冲突：
- `.claude/agents/*.md` - Agent 文件
- `.claude/skills/*/` - Skill 目录
- `.claude/hooks/*.sh` - Hook 脚本
- `.claude/commands/*.md` - Command 文件
- `.claude/settings.json` - Hooks 配置
- `.claude/skill-rules.json` - Skills 激活规则
- `.claude/build-checker.json` - 构建检查配置

**如果发现冲突，会详细列出：**
```
⚠️  发现 3 个文件冲突:

1. .claude/settings.json
   类型: file
   现有文件: 1024 bytes
   新文件: 1536 bytes

2. .claude/commands/dev-docs.md
   类型: file
   现有文件: 500 bytes
   新文件: 556 bytes

3. .claude/skills/backend-dev-guidelines/
   类型: directory
```

#### 3. 冲突解决

你可以选择如何处理冲突：

```
冲突解决选项:
1. skip   - 跳过，保留所有现有文件（推荐）
2. rename - 重命名新文件（添加 .reddit-case 后缀）
3. backup - 备份现有文件后安装新文件（添加 .backup 后缀）
4. abort  - 中止安装
```

**选项说明：**
- **skip** (推荐) - 保留你的现有文件，只安装不冲突的组件
- **rename** - 安装新文件为 `file.reddit-case.md`，你可以手动对比和合并
- **backup** - 将你的文件备份为 `file.backup.md`，然后安装新文件
- **abort** - 取消安装

#### 4. 安装计划预览

安装器会显示详细的操作列表：

```
📋 安装计划
============================================================

将执行 28 个操作:
  - 创建目录: 5
  - 复制文件: 18
  - 复制目录: 7
  - 冲突处理: 3

详细操作列表:
------------------------------------------------------------
1. 创建目录: agents
2. 创建目录: skills
3. 创建目录: hooks
4. 复制文件: auth-route-tester.md -> .claude/agents/auth-route-tester.md
5. 复制文件: build-error-resolver.md -> .claude/agents/build-error-resolver.md
...
```

#### 5. 确认执行

```
确认执行以上操作? (y/N):
```

输入 `y` 开始安装，输入 `N` 取消。

#### 6. 安装执行

```
🚀 开始安装...

✅ [1/28] 创建目录: agents
✅ [2/28] 创建目录: skills
✅ [3/28] 创建目录: hooks
✅ [4/28] 复制文件: auth-route-tester.md
...

✅ 安装完成!
```

#### 7. 安装后配置

安装完成后会显示需要自定义的配置：

```
📝 安装后配置提示
============================================================

⚠️  以下配置文件需要根据你的项目自定义:

1. .claude/build-checker.json
   - 更新项目路径
   - 配置构建命令

2. .claude/skill-rules.json
   - 调整文件路径模式以匹配你的项目结构
   - 自定义关键词触发器

3. .claude/skills/*/SKILL.md
   - 更新每个 skill 的 description 以包含项目特定关键词
```

---

## 安装示例

### 示例 1: 全新项目（无冲突）

```bash
$ python scripts/install_reddit_case.py /opt/claude/my-new-project

============================================================
🛡️  Reddit-Case 安全安装器
============================================================

核心原则:
  ✅ 永不覆盖现有文件
  ✅ 所有修改需要用户授权
  ✅ 透明显示所有操作

============================================================

🔍 检查安装前提条件...

✅ 目标目录: /opt/claude/my-new-project
✅ 源目录: /opt/claude/Claude-Kits

🔍 扫描文件冲突...

✅ 没有发现文件冲突

📋 规划安装操作...

============================================================
📋 安装计划
============================================================

将执行 28 个操作:
  - 创建目录: 5
  - 复制文件: 18
  - 复制目录: 7

...

确认执行以上操作? (y/N): y

🚀 开始安装...

✅ [1/28] 创建目录: agents
✅ [2/28] 创建目录: skills
...
✅ [28/28] 复制目录: example-task

✅ 安装完成!

🎉 Reddit-Case 安装完成!
```

### 示例 2: 现有项目（有冲突）

```bash
$ python scripts/install_reddit_case.py /opt/claude/mystocks_spec

============================================================
🛡️  Reddit-Case 安全安装器
============================================================

🔍 检查安装前提条件...

✅ 目标目录: /opt/claude/mystocks_spec
✅ 源目录: /opt/claude/Claude-Kits

🔍 扫描文件冲突...

⚠️  发现 2 个文件冲突:

1. .claude/commands/dev-docs.md
   类型: file
   现有文件: 500 bytes
   新文件: 556 bytes

2. .claude/settings.json
   类型: file
   现有文件: 1024 bytes
   新文件: 1536 bytes

============================================================
冲突解决选项:
============================================================
1. skip   - 跳过，保留所有现有文件（推荐）
2. rename - 重命名新文件（添加 .reddit-case 后缀）
3. backup - 备份现有文件后安装新文件（添加 .backup 后缀）
4. abort  - 中止安装
============================================================

请选择处理方式 (1-4) [1]: 1

📋 规划安装操作...

============================================================
📋 安装计划
============================================================

将执行 26 个操作:
  - 创建目录: 3
  - 复制文件: 16
  - 复制目录: 7
  - 冲突处理: 2

详细操作列表:
------------------------------------------------------------
1. 创建目录: agents
2. 复制文件: auth-route-tester.md -> .claude/agents/auth-route-tester.md
...
25. 冲突处理: dev-docs.md (skip)
26. 冲突处理: settings.json (skip)

确认执行以上操作? (y/N): y

🚀 开始安装...

✅ [1/26] 创建目录: agents
...
✅ [26/26] 冲突处理: settings.json (skip)

✅ 安装完成!

📝 安装后配置提示
============================================================
...
```

### 示例 3: 预览模式（不执行）

```bash
$ python scripts/install_reddit_case.py /opt/claude/my-project --dry-run

============================================================
🛡️  Reddit-Case 安全安装器
============================================================

...

🔍 DRY RUN 模式 - 不会执行任何实际操作

============================================================
📋 安装计划
============================================================

将执行 28 个操作:
  - 创建目录: 5
  - 复制文件: 18
  - 复制目录: 7

详细操作列表:
------------------------------------------------------------
1. 创建目录: agents
2. 创建目录: skills
...

# 所有操作都会显示，但不会实际执行
```

---

## 安装后配置

### 1. 配置构建检查

编辑 `.claude/build-checker.json`:

```json
{
  "repos": {
    "/absolute/path/to/your/project": {
      "buildCommand": "npm run build",  // 改为你的构建命令
      "errorThreshold": 5
    }
  }
}
```

**常见构建命令：**
- TypeScript: `"tsc --noEmit"`
- Next.js: `"next build"`
- Python: `"python3 -m py_compile **/*.py"`
- Vite: `"vite build"`

### 2. 配置 Skills 激活规则

编辑 `.claude/skill-rules.json`:

```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/routes/**/*.ts",      // 改为你的路径
          "src/controllers/**/*.ts"
        ]
      }
    }
  }
}
```

### 3. 自定义 Skills 描述

编辑每个 `.claude/skills/*/SKILL.md` 的 description 字段，添加项目特定关键词。

---

## 卸载

如果需要卸载 Reddit-Case 组件：

```bash
# 删除安装的组件（保留你的现有文件）
rm -rf /path/to/project/.claude/agents/
rm -rf /path/to/project/.claude/skills/
rm -rf /path/to/project/.claude/hooks/
rm /path/to/project/.claude/settings.json
rm /path/to/project/.claude/skill-rules.json
rm /path/to/project/.claude/build-checker.json

# 保留你创建的 commands 和其他自定义内容
```

---

## 故障排除

### 问题 1: 权限错误

```
❌ 没有写入权限: /path/to/project
```

**解决方案：**
```bash
# 检查目录权限
ls -la /path/to/project

# 如果需要，修改权限
chmod u+w /path/to/project
```

### 问题 2: Python 版本

安装器需要 Python 3.6+

```bash
# 检查 Python 版本
python3 --version

# 如果版本过低，升级 Python
```

### 问题 3: 路径问题

确保使用绝对路径：

```bash
# ❌ 错误
python scripts/install_reddit_case.py ../my-project

# ✅ 正确
python scripts/install_reddit_case.py /absolute/path/to/my-project
```

---

## 高级用法

### 批量安装（非交互模式）

```bash
# 自动跳过所有冲突，适合 CI/CD
python scripts/install_reddit_case.py /path/to/project --no-interactive
```

### 自定义安装

如果你只需要特定组件：

```bash
# 手动复制特定组件
cd /path/to/Claude-Kits

# 只复制 agents
cp -r .claude/agents /path/to/project/.claude/

# 只复制特定 skill
cp -r .claude/skills/backend-dev-guidelines /path/to/project/.claude/skills/
```

---

## 安全最佳实践

1. **始终先使用 --dry-run** 查看将要执行的操作
2. **备份重要文件** 在大规模安装前
3. **选择 skip 选项** 对于冲突文件，然后手动合并
4. **版本控制** 将 `.claude/` 目录纳入 git 管理

---

## 获取帮助

```bash
# 查看帮助信息
python scripts/install_reddit_case.py --help
```

如有问题，请参考：
- [Reddit Case Study](docs/REDDIT_CASE_IMPLEMENTATION_SUMMARY.md)
- [Architecture Design](docs/ARCHITECTURE_DESIGN.md)
- [GitHub Issues](https://github.com/your-repo/Claude-Kits/issues)

---

## 许可证

本安装器遵循项目的主许可证。
