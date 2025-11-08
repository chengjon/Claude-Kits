# 无头模式

> 以编程方式运行 Claude Code，无需交互式 UI

## 概述

无头模式允许您从命令行脚本和自动化工具以编程方式运行 Claude Code，无需任何交互式 UI。

## 基本用法

Claude Code 的主要命令行界面是 `claude` 命令。使用 `--print`（或 `-p`）标志以非交互模式运行并打印最终结果：

```bash  theme={null}
claude -p "暂存我的更改并为它们编写一组提交" \
  --allowedTools "Bash,Read" \
  --permission-mode acceptEdits
```

## 配置选项

无头模式利用 Claude Code 中所有可用的 CLI 选项。以下是自动化和脚本编写的关键选项：

| 标志                         | 描述                                        | 示例                                                                                                                        |
| :------------------------- | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| `--print`, `-p`            | 以非交互模式运行                                  | `claude -p "查询"`                                                                                                          |
| `--output-format`          | 指定输出格式（`text`、`json`、`stream-json`）       | `claude -p --output-format json`                                                                                          |
| `--resume`, `-r`           | 通过会话 ID 恢复对话                              | `claude --resume abc123`                                                                                                  |
| `--continue`, `-c`         | 继续最近的对话                                   | `claude --continue`                                                                                                       |
| `--verbose`                | 启用详细日志记录                                  | `claude --verbose`                                                                                                        |
| `--append-system-prompt`   | 附加到系统提示（仅与 `--print` 一起使用）                | `claude --append-system-prompt "自定义指令"`                                                                                   |
| `--allowedTools`           | 以空格分隔的允许工具列表，或 <br /><br /> 以逗号分隔的允许工具字符串 | `claude --allowedTools mcp__slack mcp__filesystem`<br /><br />`claude --allowedTools "Bash(npm install),mcp__filesystem"` |
| `--disallowedTools`        | 以空格分隔的禁用工具列表，或 <br /><br /> 以逗号分隔的禁用工具字符串 | `claude --disallowedTools mcp__splunk mcp__github`<br /><br />`claude --disallowedTools "Bash(git commit),mcp__github"`   |
| `--mcp-config`             | 从 JSON 文件加载 MCP 服务器                       | `claude --mcp-config servers.json`                                                                                        |
| `--permission-prompt-tool` | 用于处理权限提示的 MCP 工具（仅与 `--print` 一起使用）       | `claude --permission-prompt-tool mcp__auth__prompt`                                                                       |

有关 CLI 选项和功能的完整列表，请参阅 [CLI 参考](/zh-CN/docs/claude-code/cli-reference) 文档。

## 多轮对话

对于多轮对话，您可以恢复对话或从最近的会话继续：

```bash  theme={null}
# 继续最近的对话
claude --continue "现在重构这个以获得更好的性能"

# 通过会话 ID 恢复特定对话
claude --resume 550e8400-e29b-41d4-a716-446655440000 "更新测试"

# 以非交互模式恢复
claude --resume 550e8400-e29b-41d4-a716-446655440000 "修复所有 linting 问题" --no-interactive
```

## 输出格式

### 文本输出（默认）

```bash  theme={null}
claude -p "解释文件 src/components/Header.tsx"
# 输出：这是一个显示...的 React 组件
```

### JSON 输出

返回包含元数据的结构化数据：

```bash  theme={null}
claude -p "数据层是如何工作的？" --output-format json
```

响应格式：

```json  theme={null}
{
  "type": "result",
  "subtype": "success",
  "total_cost_usd": 0.003,
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 800,
  "num_turns": 6,
  "result": "响应文本在这里...",
  "session_id": "abc123"
}
```

### 流式 JSON 输出

在接收到每条消息时流式传输：

```bash  theme={null}
claude -p "构建一个应用程序" --output-format stream-json
```

每个对话都以初始的 `init` 系统消息开始，然后是用户和助手消息列表，最后是带有统计信息的最终 `result` 系统消息。每条消息都作为单独的 JSON 对象发出。

## 输入格式

### 文本输入（默认）

```bash  theme={null}
# 直接参数
claude -p "解释这段代码"

# 从 stdin
echo "解释这段代码" | claude -p
```

### 流式 JSON 输入

通过 `stdin` 提供的消息流，其中每条消息代表一个用户轮次。这允许在不重新启动 `claude` 二进制文件的情况下进行多轮对话，并允许在模型处理请求时向其提供指导。

每条消息都是一个 JSON '用户消息' 对象，遵循与输出消息模式相同的格式。消息使用 [jsonl](https://jsonlines.org/) 格式进行格式化，其中输入的每一行都是一个完整的 JSON 对象。流式 JSON 输入需要 `-p` 和 `--output-format stream-json`。

```bash  theme={null}
echo '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"解释这段代码"}]}}' | claude -p --output-format=stream-json --input-format=stream-json --verbose
```

## 代理集成示例

### SRE 事件响应机器人

```bash  theme={null}
#!/bin/bash

# 自动化事件响应代理
investigate_incident() {
    local incident_description="$1"
    local severity="${2:-medium}"

    claude -p "事件：$incident_description（严重性：$severity）" \
      --append-system-prompt "您是 SRE 专家。诊断问题，评估影响，并提供即时行动项目。" \
      --output-format json \
      --allowedTools "Bash,Read,WebSearch,mcp__datadog" \
      --mcp-config monitoring-tools.json
}

# 用法
investigate_incident "支付 API 返回 500 错误" "high"
```

### 自动化安全审查

```bash  theme={null}
# 拉取请求的安全审计代理
audit_pr() {
    local pr_number="$1"

    gh pr diff "$pr_number" | claude -p \
      --append-system-prompt "您是安全工程师。审查此 PR 的漏洞、不安全模式和合规问题。" \
      --output-format json \
      --allowedTools "Read,Grep,WebSearch"
}

# 用法并保存到文件
audit_pr 123 > security-report.json
```

### 多轮法律助手

```bash  theme={null}
# 具有会话持久性的法律文档审查
session_id=$(claude -p "开始法律审查会话" --output-format json | jq -r '.session_id')

# 分多个步骤审查合同
claude -p --resume "$session_id" "审查 contract.pdf 的责任条款"
claude -p --resume "$session_id" "检查 GDPR 要求的合规性"
claude -p --resume "$session_id" "生成风险的执行摘要"
```

## 最佳实践

* **使用 JSON 输出格式** 进行响应的程序化解析：

  ```bash  theme={null}
  # 使用 jq 解析 JSON 响应
  result=$(claude -p "生成代码" --output-format json)
  code=$(echo "$result" | jq -r '.result')
  cost=$(echo "$result" | jq -r '.cost_usd')
  ```

* **优雅地处理错误** - 检查退出代码和 stderr：

  ```bash  theme={null}
  if ! claude -p "$prompt" 2>error.log; then
      echo "发生错误：" >&2
      cat error.log >&2
      exit 1
  fi
  ```

* **使用会话管理** 在多轮对话中维护上下文

* **考虑超时** 对于长时间运行的操作：

  ```bash  theme={null}
  timeout 300 claude -p "$complex_prompt" || echo "5 分钟后超时"
  ```

* **尊重速率限制** 在进行多个请求时，通过在调用之间添加延迟

## 相关资源

* [CLI 用法和控制](/zh-CN/docs/claude-code/cli-reference) - 完整的 CLI 文档
* [常见工作流程](/zh-CN/docs/claude-code/common-workflows) - 常见用例的分步指南
