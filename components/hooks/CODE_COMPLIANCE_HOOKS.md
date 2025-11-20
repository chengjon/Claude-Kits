# Code Compliance Hooks 代码合规性检查 Hooks

**版本**: 2.0.0 - 零硬编码版本
**创建日期**: 2025-11-18
**更新日期**: 2025-11-18 (添加零硬编码支持和导入检查)
**来源**: 基于 MyStocks 项目 Git pre-commit hooks 转换而来

---

## 📦 概述

本套 hooks 提供三个自动化代码合规性检查器，确保项目中的文件符合标准规范：

1. **Python 头部注释验证器** - 验证 Python 文件的标准头部注释 + 导入路径检查
2. **Markdown Frontmatter 验证器** - 验证 Markdown 文件的 YAML frontmatter
3. **中文文件名检查器** - 检测并阻止包含中文字符的文件名

这些 hooks 在 Claude Code 执行 `Edit` 或 `Write` 工具后自动触发，提供实时的合规性反馈。

### ✨ v2.0 新特性

- ✅ **零硬编码**: 所有配置项均可通过环境变量自定义
- ✅ **Python 导入检查**: 自动检测并提醒导入路径可能需要调整
- ✅ **完全可配置**: 必需字段、排除模式、检查模式全部可配置
- ✅ **详细配置指南**: 新增 `CONFIGURATION_GUIDE.md`

---

## 🎯 Hook 详情

### 1. Python 头部注释验证器

**文件**: `post-tool-use-python-header-validator.sh`
**Event**: PostToolUse
**Matcher**: `Edit|Write`
**Timeout**: 5 秒
**输出格式**: 纯文本 (符合 Claude Code 官方规范)

#### 检查内容

验证 Python 文件前 20 行是否包含以下 5 个必需组件：

```python
# -*- coding: utf-8 -*-
# 功能：[功能描述]
# 作者：[作者姓名]
# 日期：YYYY-MM-DD
# 版本：vX.Y.Z
```

#### 环境变量配置

```bash
# 模式设置（默认：warning）
PYTHON_HEADER_VALIDATOR_MODE=blocking   # 阻止模式：不合规时阻止继续
PYTHON_HEADER_VALIDATOR_MODE=warning    # 警告模式：显示警告但允许继续

# 排除文件模式（正则表达式，用 | 分隔）
PYTHON_HEADER_VALIDATOR_EXCLUDE="__init__|test_|conftest"

# 自定义必需字段（避免硬编码，用 | 分隔）
PYTHON_HEADER_REQUIRED_FIELDS="# -*- coding: utf-8 -*-|# 功能：|# 作者：|# 日期：|# 版本："

# 导入路径检查（默认：false）
PYTHON_HEADER_CHECK_IMPORTS=true   # 启用导入语句检查
PYTHON_HEADER_CHECK_IMPORTS=false  # 禁用导入语句检查
```

**默认必需字段** (5个)：
- `# -*- coding: utf-8 -*-`
- `# 功能：`
- `# 作者：`
- `# 日期：`
- `# 版本：`

**自定义示例** (只检查3个字段)：
```bash
export PYTHON_HEADER_REQUIRED_FIELDS="# -*- coding: utf-8 -*-|# 功能：|# 作者："
```

#### 标准 Python 头部模板

```python
# -*- coding: utf-8 -*-
# 功能：用户认证模块，提供登录、注册、权限验证功能
# 作者：John Doe (john@example.com) & Claude
# 日期：2025-11-18
# 版本：v1.2.0
# 依赖：详见 requirements.txt
# 注意事项：需要配置 SECRET_KEY 环境变量
# 版权：© 2025 MyProject

"""
用户认证模块的详细文档字符串
"""
```

---

### 2. Markdown Frontmatter 验证器

**文件**: `post-tool-use-md-frontmatter-validator.sh`
**Event**: PostToolUse
**Matcher**: `Edit|Write`
**Timeout**: 5 秒
**输出格式**: 纯文本 (符合 Claude Code 官方规范)

#### 检查内容

验证 Markdown 文件是否：
1. 第一行为 `---`（YAML frontmatter 起始标记）
2. 包含以下 5 个必需字段：

```yaml
---
创建人: [创建者姓名]
版本: x.y.z
批准日期: YYYY-MM-DD
最后修订: YYYY-MM-DD
本次修订内容: [修改描述]
---
```

#### 环境变量配置

```bash
# 模式设置（默认：warning）
MD_FRONTMATTER_VALIDATOR_MODE=blocking  # 阻止模式
MD_FRONTMATTER_VALIDATOR_MODE=warning   # 警告模式

# 排除文件（正则表达式，用 | 分隔）
MD_FRONTMATTER_VALIDATOR_EXCLUDE="^CLAUDE\.md$|^CHANGELOG\.md$|^README\.md$"

# 自定义必需字段（避免硬编码，用 | 分隔）
MD_FRONTMATTER_REQUIRED_FIELDS="创建人:|版本:|批准日期:|最后修订:|本次修订内容:"
```

**默认必需字段** (5个)：
- `创建人:`
- `版本:`
- `批准日期:`
- `最后修订:`
- `本次修订内容:`

**自定义示例** (英文项目，3个字段)：
```bash
export MD_FRONTMATTER_REQUIRED_FIELDS="author:|version:|date:"
```

#### 标准 Markdown Frontmatter 模板

```markdown
---
创建人: John Doe
版本: 1.0.0
批准日期: 2025-11-18
最后修订: 2025-11-18
本次修订内容: 初始版本，添加用户认证文档
---

# 文档标题

文档内容...
```

---

### 3. 中文文件名检查器

**文件**: `post-tool-use-chinese-filename-checker.sh`
**Event**: PostToolUse
**Matcher**: `Write`
**Timeout**: 3 秒
**输出格式**: 纯文本 (符合 Claude Code 官方规范)

#### 检查内容

检测文件名（basename）是否包含非 ASCII 字符（包括中文、日文、韩文等）。

**为什么要避免中文文件名？**
- 跨平台兼容性问题（Windows/Linux/macOS 编码差异）
- Git 仓库在不同系统间克隆可能出现乱码
- 部分构建工具和脚本无法正确处理

#### 环境变量配置

```bash
# 模式设置（默认：warning）
CHINESE_FILENAME_CHECKER_MODE=blocking  # 阻止模式
CHINESE_FILENAME_CHECKER_MODE=warning   # 警告模式

# 排除目录（正则表达式，用 | 分隔）
CHINESE_FILENAME_CHECKER_EXCLUDE="^temp/|^archive/"
```

#### 推荐的文件命名规范

✅ **推荐**:
- `user_authentication.py`
- `api-config-2025.json`
- `database_schema_v2.sql`
- `README.md`

❌ **避免**:
- `用户认证.py`
- `配置文件-2025.json`
- `数据库架构.sql`

---

## 💡 Python 导入路径检查功能

### 功能说明

启用 `PYTHON_HEADER_CHECK_IMPORTS=true` 后，hook 会自动检测 Python 文件中的导入语句，并在文件移动时提醒可能需要调整导入路径。

### 启用方法

在 `.claude/settings.local.json` 中：

```json
{
  "env": {
    "PYTHON_HEADER_CHECK_IMPORTS": "true"
  }
}
```

### 输出示例

当检测到导入语句时：

```
⚠️  检测到导入语句
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件: src/utils.py

检测到以下导入语句（前5个）:
import os
from typing import Dict, List
from .models import User
from ..config import settings

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

### 适用场景

✅ **建议启用**：
- 正在重构项目结构
- 经常移动 Python 文件
- 团队协作，需要提醒成员注意导入路径

❌ **建议关闭**：
- 稳定的项目结构
- 不频繁移动文件
- 避免过多提示信息

---

## 🚀 快速开始

### 已自动配置

这些 hooks 已经在 `components/hooks/settings.json` 中注册，如果您的项目使用了这个配置文件，hooks 将自动生效。

### 手动安装到项目

如果需要在其他项目中使用这些 hooks：

```bash
# 1. 复制 hook 脚本到项目
cp components/hooks/post-tool-use-python-header-validator.sh /path/to/project/.claude/hooks/
cp components/hooks/post-tool-use-md-frontmatter-validator.sh /path/to/project/.claude/hooks/
cp components/hooks/post-tool-use-chinese-filename-checker.sh /path/to/project/.claude/hooks/

# 2. 设置执行权限
chmod +x /path/to/project/.claude/hooks/post-tool-use-*.sh

# 3. 更新项目的 .claude/settings.json（见下方配置示例）
```

### Settings.json 配置示例

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-python-header-validator.sh"
        }],
        "timeout": 5
      },
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-md-frontmatter-validator.sh"
        }],
        "timeout": 5
      },
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-chinese-filename-checker.sh"
        }],
        "timeout": 3
      }
    ]
  }
}
```

---

## 🔧 自定义配置

### 切换为阻止模式

默认情况下，这些 hooks 使用**警告模式**（显示错误但允许继续）。如需切换为**阻止模式**（不合规时阻止操作），可以通过环境变量配置：

**方法 1: 在 settings.local.json 中配置环境变量**

创建 `.claude/settings.local.json`：

```json
{
  "env": {
    "PYTHON_HEADER_VALIDATOR_MODE": "blocking",
    "MD_FRONTMATTER_VALIDATOR_MODE": "blocking",
    "CHINESE_FILENAME_CHECKER_MODE": "blocking"
  }
}
```

**方法 2: 在 shell 中设置**

```bash
export PYTHON_HEADER_VALIDATOR_MODE=blocking
export MD_FRONTMATTER_VALIDATOR_MODE=blocking
export CHINESE_FILENAME_CHECKER_MODE=blocking
```

### 排除特定文件或目录

```bash
# Python 头部验证器 - 排除测试文件和 __init__.py
export PYTHON_HEADER_VALIDATOR_EXCLUDE="__init__|test_|conftest|setup\.py"

# Markdown 验证器 - 排除 README 和 CHANGELOG
export MD_FRONTMATTER_VALIDATOR_EXCLUDE="^README\.md$|^CHANGELOG\.md$|^CLAUDE\.md$"

# 文件名检查器 - 排除 temp 和 archive 目录
export CHINESE_FILENAME_CHECKER_EXCLUDE="^temp/|^archive/|^\.claude/"
```

---

## 💡 使用场景示例

### 场景 1: Claude 创建新的 Python 文件

```
User: "创建一个新的 user_service.py 文件"
Claude: [使用 Write 工具创建文件，但忘记添加标准头部]
Hook 输出 (stderr):

❌ Python头部注释不合规
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件: user_service.py

缺少以下必需组件:
  • # -*- coding: utf-8 -*-
  • # 功能：
  • # 作者：

📋 标准Python头部模板:
  # -*- coding: utf-8 -*-
  # 功能：[功能描述]
  # 作者：[作者姓名 (email)] & Claude
  ...

💡 建议: 在文件开头添加标准头部注释
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 场景 2: Claude 编辑 Markdown 文档

```
User: "修改 API_GUIDE.md，添加新的接口说明"
Claude: [使用 Edit 工具修改文件]
Hook 输出 (stdout):
✅ Markdown frontmatter合规: API_GUIDE.md
```

### 场景 3: 用户要求创建中文文件名的文件

```
User: "创建一个 配置文件.json"
Claude: [使用 Write 工具创建文件]
Hook 输出 (stderr):

❌ 文件名包含中文或特殊字符
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件名: "配置文件.json"
路径: 配置文件.json

⚠️  为什么要避免中文文件名？
  • 跨平台兼容性问题（Windows/Linux/macOS编码差异）
  • Git仓库在不同系统间克隆可能出现乱码
  • 部分构建工具和脚本无法正确处理

✅ 推荐的文件命名规范:
  • user_authentication.py
  • api-config-2025.json
  • database_schema_v2.sql

💡 建议: 使用英文字母、数字、下划线和连字符
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🐛 调试

### 启用调试模式

```bash
export PYTHON_HEADER_VALIDATOR_DEBUG=true
export MD_FRONTMATTER_VALIDATOR_DEBUG=true
export CHINESE_FILENAME_CHECKER_DEBUG=true
```

调试信息将输出到 stderr，可以查看 hook 的执行细节。

### 手动测试 Hook

```bash
# 测试 Python 头部验证器
echo '{"tool_input":{"file_path":"test.py"}}' | \
  ./post-tool-use-python-header-validator.sh

# 测试 Markdown 验证器
echo '{"tool_input":{"file_path":"test.md"}}' | \
  ./post-tool-use-md-frontmatter-validator.sh

# 测试文件名检查器
echo '{"tool_input":{"file_path":"测试.txt"}}' | \
  ./post-tool-use-chinese-filename-checker.sh
```

---

## 📚 原始来源

这些 hooks 基于 **MyStocks 项目** 的 Git pre-commit hooks 转换而来。原始的 Git hooks 用于在 `git commit` 时进行检查，而这些 Claude Code hooks 在文件创建/编辑时实时检查。

**主要区别**:

| 特性 | Git Pre-commit Hooks | Claude Code Hooks |
|------|---------------------|-------------------|
| 触发时机 | `git commit` | `Edit`/`Write` 工具调用后 |
| 检查对象 | Staged 文件 | 单个被编辑的文件 |
| 输出格式 | 纯文本 | JSON-LD（双语） |
| 跳过机制 | `--no-verify` | 环境变量（warning 模式）|

**原始文档位置**: `/opt/claude/mystocks_nice/temp/hooks/`

---

## ⚙️ 高级配置

### 组合使用多个排除模式

```bash
# 复杂的排除规则
export PYTHON_HEADER_VALIDATOR_EXCLUDE="(__init__|test_|conftest|setup\.py|^scripts/dev/)"
```

### 项目级 vs 用户级配置

**项目级**（团队共享）:
- `.claude/settings.json` - hook 注册配置
- 提交到 Git，所有团队成员共享

**用户级**（个人配置）:
- `.claude/settings.local.json` - 环境变量和个人偏好
- 添加到 `.gitignore`，不提交

---

## 🤝 贡献

如果您改进了这些 hooks 或发现了 bug，欢迎贡献！

1. 修改 `components/hooks/` 中的脚本
2. 更新此文档
3. 测试验证
4. 提交 PR

---

## 📄 许可

这些 hooks 源自 MyStocks 开源项目，可自由用于任何项目。

---

**最后更新**: 2025-11-18
**维护者**: Claude-Kits 项目
**原始作者**: JohnC & Claude (MyStocks Project)
