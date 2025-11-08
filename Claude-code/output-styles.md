# 输出样式

> 将 Claude Code 适配用于软件工程之外的用途

输出样式允许您将 Claude Code 用作任何类型的代理，同时保持其核心功能，如运行本地脚本、读写文件和跟踪 TODO。

## 内置输出样式

Claude Code 的**默认**输出样式是现有的系统提示，旨在帮助您高效完成软件工程任务。

还有两种额外的内置输出样式，专注于教您代码库和 Claude 的工作原理：

* **解释性**：在帮助您完成软件工程任务的过程中提供教育性的"见解"。帮助您理解实现选择和代码库模式。

* **学习**：协作式的边做边学模式，Claude 不仅会在编码时分享"见解"，还会要求您自己贡献小的、战略性的代码片段。Claude Code 会在您的代码中添加 `TODO(human)` 标记供您实现。

## 输出样式的工作原理

输出样式直接修改 Claude Code 的系统提示。

* 非默认输出样式排除了通常内置在 Claude Code 中的特定于代码生成和高效输出的指令（如简洁回应和通过测试验证代码）。
* 相反，这些输出样式在系统提示中添加了自己的自定义指令。

## 更改您的输出样式

您可以：

* 运行 `/output-style` 来访问菜单并选择您的输出样式（这也可以从 `/config` 菜单访问）

* 运行 `/output-style [样式]`，如 `/output-style explanatory`，直接切换到某种样式

这些更改适用于[本地项目级别](/zh-CN/docs/claude-code/settings)，并保存在 `.claude/settings.local.json` 中。

## 创建自定义输出样式

要在 Claude 的帮助下设置新的输出样式，运行
`/output-style:new I want an output style that ...`

默认情况下，通过 `/output-style:new` 创建的输出样式作为 markdown 文件保存在用户级别的 `~/.claude/output-styles` 中，可以跨项目使用。它们具有以下结构：

```markdown  theme={null}
---
name: My Custom Style
description:
  A brief description of what this style does, to be displayed to the user
---

# Custom Style Instructions

You are an interactive CLI tool that helps users with software engineering
tasks. [Your custom instructions here...]

## Specific Behaviors

[Define how the assistant should behave in this style...]
```

您也可以创建自己的输出样式 Markdown 文件，并将它们保存在用户级别（`~/.claude/output-styles`）或项目级别（`.claude/output-styles`）。

## 与相关功能的比较

### 输出样式 vs. CLAUDE.md vs. --append-system-prompt

输出样式完全"关闭"了 Claude Code 默认系统提示中特定于软件工程的部分。CLAUDE.md 和 `--append-system-prompt` 都不会编辑 Claude Code 的默认系统提示。CLAUDE.md 将内容作为用户消息添加在 Claude Code 默认系统提示\_之后\_。`--append-system-prompt` 将内容附加到系统提示。

### 输出样式 vs. [代理](/zh-CN/docs/claude-code/sub-agents)

输出样式直接影响主代理循环，只影响系统提示。代理被调用来处理特定任务，可以包括额外的设置，如要使用的模型、它们可用的工具以及何时使用代理的一些上下文。

### 输出样式 vs. [自定义斜杠命令](/zh-CN/docs/claude-code/slash-commands)

您可以将输出样式视为"存储的系统提示"，将自定义斜杠命令视为"存储的提示"。
