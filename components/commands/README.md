# Commands 组件库

> **最后更新**: 2025-11-07 | **组件数量**: 8

本目录包含所有可用的斜杠命令（Slash Commands），用于快速执行特定任务。

---

## 📋 组件列表

### 代码质量类

| Command | 功能描述 | 引用来源 |
|---------|---------|---------|
| **/review** | 对最近的代码更改进行全面代码审查，检查安全、性能、最佳实践 | 本项目原创 |
| **/refactor-clean** | 代码重构和清理，识别重复代码、消除技术债务、改善代码结构 | [code-refactoring](../../reference/agents/plugins/code-refactoring/commands/refactor-clean.md) |
| **/tech-debt** | 识别和跟踪技术债务，生成债务清单和修复优先级 | [code-refactoring](../../reference/agents/plugins/code-refactoring/commands/tech-debt.md) |

### 测试与调试类

| Command | 功能描述 | 引用来源 |
|---------|---------|---------|
| **/test-generate** | 自动生成单元测试，支持多种测试框架和语言 | [unit-testing](../../reference/agents/plugins/unit-testing/commands/test-generate.md) |
| **/smart-debug** | AI 辅助的智能调试，进行根因分析和故障排查 | [debugging-toolkit](../../reference/agents/plugins/debugging-toolkit/commands/smart-debug.md) |

### 文档类

| Command | 功能描述 | 引用来源 |
|---------|---------|---------|
| **/docs** | 生成全面的代码文档、README、API 文档 | 本项目原创 |

### 安全类

| Command | 功能描述 | 引用来源 |
|---------|---------|---------|
| **/security-sast** | 静态应用安全测试（SAST），扫描代码漏洞 | [security-scanning](../../reference/agents/plugins/security-scanning/commands/security-sast.md) |

### 模板（参考）

| Command | 功能描述 | 引用来源 |
|---------|---------|---------|
| **/command-template** | 创建新命令的模板文件，包含 frontmatter 示例 | 本项目原创 |

---

## 🎯 使用场景

### 日常开发
```bash
/review                    # 代码审查
/docs                      # 生成文档
/test-generate src/app.js  # 生成测试
```

### 调试与优化
```bash
/smart-debug "error message"   # 智能调试
/refactor-clean                # 代码重构
/tech-debt analyze             # 技术债务分析
```

### 安全审计
```bash
/security-sast scan            # 安全扫描
```

---

## 📖 使用方法

### 安装 Command

```bash
# 安装到项目级别
python scripts/commands_manager.py install <command-name> --scope project

# 安装到用户级别
python scripts/commands_manager.py install <command-name> --scope user
```

### 使用 Command

```bash
# 启动 Claude Code
claude

# 直接使用斜杠命令
> /review
> /smart-debug "Timeout error in payment processing"
> /test-generate src/utils/validator.js
> /security-sast scan --path src/
```

### 查看已安装 Commands

```bash
python scripts/commands_manager.py list
```

### 查看帮助

```bash
# 在 Claude Code 中
> /help
```

---

## 🔧 Command 特点

### 与 Agents 的区别

| 特性 | Commands | Agents |
|------|----------|--------|
| **调用方式** | 斜杠命令 `/command` | 自然语言激活 |
| **响应速度** | 快速 | 可能需要多步 |
| **适用场景** | 单一明确任务 | 复杂多步骤任务 |
| **参数传递** | 支持参数 | 通过对话 |

### Command 优势

- ✅ 快速执行，无需长对话
- ✅ 明确的输入输出
- ✅ 支持参数和选项
- ✅ 可脚本化和自动化

---

## 📝 YAML Frontmatter

Commands 支持可选的 YAML frontmatter 配置：

```yaml
---
description: Command description for help text
allowed-tools: Read, Write, Bash, Edit
argument-hint: [file] [options]
model: sonnet
---
```

### Frontmatter 字段说明

| 字段 | 说明 | 必需 |
|------|------|------|
| `description` | 命令描述，显示在帮助中 | 推荐 |
| `allowed-tools` | 限制可用工具 | 可选 |
| `argument-hint` | 参数提示 | 可选 |
| `model` | 指定模型（sonnet/opus/haiku） | 可选 |

---

## 🚀 创建自定义 Command

1. 复制 `command-template.md` 为新文件
2. 编写命令逻辑和提示词
3. 添加 YAML frontmatter
4. 安装并测试

示例：

```bash
cp command-template.md my-command.md
# 编辑 my-command.md
python scripts/commands_manager.py install my-command --scope project
```

---

## 🔗 相关文档

- [组件目录总览](../../COMPONENTS_CATALOG.md)
- [Commands 官方文档](https://docs.claude.com/claude-code/slash-commands)
- [Claude 工作指南](../../CLAUDE.md)

---

## 📊 命令统计

| 类别 | 数量 |
|------|------|
| 代码质量 | 3 |
| 测试调试 | 2 |
| 文档生成 | 1 |
| 安全扫描 | 1 |
| 模板参考 | 1 |
| **总计** | **8** |

---

**维护**: Claude-Kits Team | **许可**: MIT
