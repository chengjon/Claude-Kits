# Code Compliance Hooks 配置指南

**版本**: 2.0.0
**更新日期**: 2025-11-18

---

## 🎯 核心原则：零硬编码

所有 hooks 遵循**零硬编码**原则，所有配置项均可通过环境变量自定义，确保最大灵活性。

---

## 📋 环境变量配置

### Python Header Validator

#### 基本配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `PYTHON_HEADER_VALIDATOR_MODE` | `warning` | 模式：`warning` (警告) 或 `blocking` (阻止) |
| `PYTHON_HEADER_VALIDATOR_EXCLUDE` | `__pycache__\|\.pyc$` | 排除的文件模式（正则表达式，用 \| 分隔） |
| `PYTHON_HEADER_REQUIRED_FIELDS` | 见下方 | 必需的头部字段（用 \| 分隔） |
| `PYTHON_HEADER_CHECK_IMPORTS` | `false` | 是否检查导入语句：`true` 或 `false` |
| `PYTHON_HEADER_VALIDATOR_DEBUG` | `false` | 调试模式：`true` 或 `false` |

#### 默认必需字段

```bash
"# -*- coding: utf-8 -*-|# 功能：|# 作者：|# 日期：|# 版本："
```

**包含 5 个字段**：
1. `# -*- coding: utf-8 -*-`
2. `# 功能：`
3. `# 作者：`
4. `# 日期：`
5. `# 版本：`

#### 自定义示例

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "blocking",
    "PYTHON_HEADER_REQUIRED_FIELDS": "# -*- coding: utf-8 -*-|# Author:|# Date:",
    "PYTHON_HEADER_CHECK_IMPORTS": "true",
    "PYTHON_HEADER_VALIDATOR_EXCLUDE": "__init__|test_|setup\.py"
  }
}
```

---

### Markdown Frontmatter Validator

#### 基本配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `MD_FRONTMATTER_VALIDATOR_MODE` | `warning` | 模式：`warning` (警告) 或 `blocking` (阻止) |
| `MD_FRONTMATTER_VALIDATOR_EXCLUDE` | 见下方 | 排除的文件（正则表达式，用 \| 分隔） |
| `MD_FRONTMATTER_REQUIRED_FIELDS` | 见下方 | 必需的 frontmatter 字段（用 \| 分隔） |
| `MD_FRONTMATTER_VALIDATOR_DEBUG` | `false` | 调试模式：`true` 或 `false` |

#### 默认排除文件

```bash
"^CLAUDE\.md$|^CHANGELOG\.md$|^README\.md$"
```

#### 默认必需字段

```bash
"创建人:|版本:|批准日期:|最后修订:|本次修订内容:"
```

**包含 5 个字段**：
1. `创建人:`
2. `版本:`
3. `批准日期:`
4. `最后修订:`
5. `本次修订内容:`

#### 自定义示例

```json
{
  "env": {
    "MD_FRONTMATTER_VALIDATOR_MODE": "warning",
    "MD_FRONTMATTER_REQUIRED_FIELDS": "author:|version:|date:",
    "MD_FRONTMATTER_VALIDATOR_EXCLUDE": "^README|^CHANGELOG|^CONTRIBUTING"
  }
}
```

---

### Chinese Filename Checker

#### 基本配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `CHINESE_FILENAME_CHECKER_MODE` | `warning` | 模式：`warning` (警告) 或 `blocking` (阻止) |
| `CHINESE_FILENAME_CHECKER_EXCLUDE` | `^temp/\|^archive/` | 排除的目录（正则表达式，用 \| 分隔） |
| `CHINESE_FILENAME_CHECKER_DEBUG` | `false` | 调试模式：`true` 或 `false` |

#### 自定义示例

```json
{
  "env": {
    "CHINESE_FILENAME_CHECKER_MODE": "blocking",
    "CHINESE_FILENAME_CHECKER_EXCLUDE": "^temp/|^archive/|^\.claude/"
  }
}
```

---

## 🔧 配置文件位置

### 方式 1: 项目级配置（推荐）

创建 `.claude/settings.local.json`（不提交到 Git）：

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "blocking",
    "PYTHON_HEADER_REQUIRED_FIELDS": "# -*- coding: utf-8 -*-|# 功能：|# 作者：",
    "PYTHON_HEADER_CHECK_IMPORTS": "true",

    "MD_FRONTMATTER_VALIDATOR_MODE": "warning",
    "MD_FRONTMATTER_REQUIRED_FIELDS": "创建人:|版本:|批准日期:",

    "CHINESE_FILENAME_CHECKER_MODE": "blocking"
  }
}
```

### 方式 2: 用户级配置

修改 `~/.claude/settings.json`：

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "warning",
    "PYTHON_HEADER_CHECK_IMPORTS": "false"
  }
}
```

### 方式 3: Shell 环境变量

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export PYTHON_HEADER_VALIDATOR_MODE=blocking
export PYTHON_HEADER_CHECK_IMPORTS=true
export MD_FRONTMATTER_VALIDATOR_MODE=warning
export CHINESE_FILENAME_CHECKER_MODE=blocking
```

---

## 📝 Python 导入路径检查功能

### 启用导入检查

```json
{
  "env": {
    "PYTHON_HEADER_CHECK_IMPORTS": "true"
  }
}
```

### 功能说明

启用后，当检测到 Python 文件包含导入语句时，会显示以下提醒：

```
⚠️  检测到导入语句
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件: src/utils.py

检测到以下导入语句（前5个）:
import os
from typing import Dict, List
from .models import User

💡 重要提醒:
  如果此文件是从其他位置移动过来的，请检查：
  • 相对导入路径是否需要调整
  • 模块导入路径是否仍然正确
  • 是否需要更新 __init__.py
  • 是否需要更新 PYTHONPATH

  示例：
    - 从 'src/utils.py' 移到 'lib/utils.py'
    - 导入语句可能需要从 'from . import' 改为 'from lib import'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 使用场景

**适合启用的情况**：
- 正在重构项目结构
- 经常移动 Python 文件
- 团队协作，需要提醒成员注意导入路径

**建议关闭的情况**：
- 稳定的项目结构
- 不频繁移动文件
- 避免过多提示信息

---

## 🎨 完整配置示例

### 示例 1: 严格模式（阻止不合规）

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "blocking",
    "PYTHON_HEADER_REQUIRED_FIELDS": "# -*- coding: utf-8 -*-|# 功能：|# 作者：|# 日期：|# 版本：",
    "PYTHON_HEADER_CHECK_IMPORTS": "true",
    "PYTHON_HEADER_VALIDATOR_EXCLUDE": "__init__|test_|conftest",

    "MD_FRONTMATTER_VALIDATOR_MODE": "blocking",
    "MD_FRONTMATTER_REQUIRED_FIELDS": "创建人:|版本:|批准日期:|最后修订:|本次修订内容:",
    "MD_FRONTMATTER_VALIDATOR_EXCLUDE": "^CLAUDE\.md$|^CHANGELOG\.md$|^README\.md$",

    "CHINESE_FILENAME_CHECKER_MODE": "blocking",
    "CHINESE_FILENAME_CHECKER_EXCLUDE": "^temp/|^archive/"
  }
}
```

### 示例 2: 宽松模式（仅警告）

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "warning",
    "PYTHON_HEADER_REQUIRED_FIELDS": "# -*- coding: utf-8 -*-|# 功能：",
    "PYTHON_HEADER_CHECK_IMPORTS": "false",

    "MD_FRONTMATTER_VALIDATOR_MODE": "warning",
    "MD_FRONTMATTER_REQUIRED_FIELDS": "创建人:|版本:",

    "CHINESE_FILENAME_CHECKER_MODE": "warning"
  }
}
```

### 示例 3: 英文项目配置

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "blocking",
    "PYTHON_HEADER_REQUIRED_FIELDS": "# -*- coding: utf-8 -*-|# Purpose:|# Author:|# Date:|# Version:",
    "PYTHON_HEADER_CHECK_IMPORTS": "true",

    "MD_FRONTMATTER_VALIDATOR_MODE": "blocking",
    "MD_FRONTMATTER_REQUIRED_FIELDS": "author:|version:|date:",

    "CHINESE_FILENAME_CHECKER_MODE": "blocking"
  }
}
```

---

## 🔍 调试模式

启用调试模式查看详细执行信息：

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_DEBUG": "true",
    "MD_FRONTMATTER_VALIDATOR_DEBUG": "true",
    "CHINESE_FILENAME_CHECKER_DEBUG": "true"
  }
}
```

调试信息示例：

```
[DEBUG] Received input: {"tool_input":{"file_path":"test.py"}...}
[DEBUG] File path: test.py
[DEBUG] Not in exclude pattern
[DEBUG] Python header validation passed
```

---

## 💡 最佳实践

### 1. 项目初期

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "warning",
    "MD_FRONTMATTER_VALIDATOR_MODE": "warning",
    "CHINESE_FILENAME_CHECKER_MODE": "warning"
  }
}
```

先使用警告模式，让团队适应规范。

### 2. 项目成熟期

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "blocking",
    "MD_FRONTMATTER_VALIDATOR_MODE": "blocking",
    "CHINESE_FILENAME_CHECKER_MODE": "blocking"
  }
}
```

切换到阻止模式，强制执行规范。

### 3. 重构期

```json
{
  "env": {
    "PYTHON_HEADER_CHECK_IMPORTS": "true"
  }
}
```

启用导入检查，避免移动文件后的导入错误。

---

## 🆘 常见问题

### Q1: 如何临时禁用某个检查？

**方法 1**: 设置排除模式

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_EXCLUDE": ".*"
  }
}
```

**方法 2**: 注释掉 settings.json 中的 hook 注册

### Q2: 如何只检查特定字段？

通过 `REQUIRED_FIELDS` 环境变量自定义：

```json
{
  "env": {
    "PYTHON_HEADER_REQUIRED_FIELDS": "# -*- coding: utf-8 -*-|# 功能："
  }
}
```

只检查编码和功能字段。

### Q3: 配置不生效？

1. 检查 JSON 语法是否正确
2. 重启 Claude Code 会话
3. 启用调试模式查看日志
4. 确认环境变量名称拼写正确

---

## 🔗 相关文档

- **详细使用指南**: `CODE_COMPLIANCE_HOOKS.md`
- **Hook 脚本源码**: `post-tool-use-*.sh`
- **Claude Code 官方文档**: `/opt/mydoc/Anthropic/Claude-code/hooks.md`

---

**维护者**: Claude-Kits 项目
**最后更新**: 2025-11-18
**版本**: 2.0.0 - 零硬编码版本
