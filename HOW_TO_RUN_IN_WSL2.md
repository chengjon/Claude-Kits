# 如何在 WSL2 中运行 Claude TUI

## ⚠️ 重要说明

**问题：** 在 WSL2 中运行 `./scripts/run_tui_with_tmux.sh --log` 没有反应

**原因：** 你是通过 **Claude Code 的 Bash 工具**运行命令，这是**非交互式环境**（没有 TTY），无法运行 tmux 和 TUI。

**解决：** 必须在 **WSL2 终端中手动输入**命令，而不是让 Claude 代为执行。

---

## 🔍 问题诊断

### 错误的操作流程（❌）

```
你的 WSL2 终端
    ↓
运行 Claude Code
    ↓
Claude 执行 Bash 命令  ← 这里是非 TTY 环境
    ↓
tmux/TUI 失败（错误: "open terminal failed: not a terminal"）
```

### 正确的操作流程（✅）

```
你的 WSL2 终端
    ↓
你直接用键盘输入命令  ← 这里是 TTY 环境
    ↓
tmux/TUI 成功运行
```

---

## ✅ 正确的操作步骤

### 步骤 1：打开 WSL2 终端

在 Windows 中打开你的 WSL2 终端：

**方法 1：Windows Terminal（推荐）**
- 打开 Windows Terminal
- 点击下拉菜单，选择你的 WSL2 发行版（如 Ubuntu）

**方法 2：直接启动**
- 按 `Win+R`
- 输入 `wsl`
- 按 Enter

**方法 3：从 VS Code**
- 打开 VS Code
- 按 `Ctrl+` \` 打开终端
- 确保终端类型是 WSL（不是 PowerShell）

---

### 步骤 2：导航到项目目录

在 WSL2 终端中**用键盘输入**以下命令：

```bash
cd /opt/claude/Claude-Kits
```

按 Enter 执行。

---

### 步骤 3：运行诊断脚本（验证环境）

**用键盘输入**：

```bash
./scripts/test_tty.sh
```

按 Enter 执行。

**预期输出（正确环境）：**

```
=========================================
TTY 环境诊断
=========================================

✅ stdin (0) 连接到 TTY
✅ stdout (1) 连接到 TTY
✅ stderr (2) 连接到 TTY

终端信息：
  TTY 设备: /dev/pts/0
  TERM 类型: xterm-256color
  是否交互式 shell: 是

tmux 可用性：
  tmux 版本: tmux 3.4
  ✅ 可以运行 tmux（有 TTY）

TUI 可用性：
  ✅ 可以运行 TUI（有 TTY）

建议运行：
  ./scripts/run_tui_with_tmux.sh --log

=========================================
```

**如果看到 ❌（错误环境）：**

```
❌ stdin (0) 未连接到 TTY（非交互式环境）
❌ stdout (1) 未连接到 TTY
❌ stderr (2) 未连接到 TTY
```

说明你仍然在通过 Claude Code 或其他非交互式方式运行。请确保：
1. 打开**真正的** WSL2 终端窗口
2. **用键盘手动输入**命令（不要复制粘贴 Claude 的输出）
3. 不要通过 Claude Code 的 Bash 工具运行

---

### 步骤 4：测试 TUI（简单版本，不使用 tmux）

先测试 TUI 本身是否工作。**用键盘输入**：

```bash
./scripts/simple_test_tui.sh
```

按 Enter 执行。

**预期结果：**
1. 显示 "✅ TTY 检查通过"
2. 显示依赖检查结果
3. 提示 "按 Enter 继续..."
4. 启动 TUI 界面（显示 Claude-Kits Logo 和菜单）

**TUI 操作：**
- 使用方向键 `↑` `↓` 或数字键 `1-8` 导航
- 按 `Enter` 选择
- 按 `q` 或选择 "Exit" 退出

---

### 步骤 5：使用 tmux 运行 TUI（完整版本）

如果步骤 4 成功，继续**用键盘输入**：

```bash
./scripts/run_tui_with_tmux.sh --log
```

按 Enter 执行。

**预期结果：**
1. 显示 "ℹ 创建 tmux 会话: claude-tui"
2. 显示 "ℹ 日志文件: /root/.claude-tui-logs/session-*.log"
3. 进入 TUI 界面

**tmux 操作：**
- **断开会话**：按 `Ctrl+B`，然后按 `D`（TUI 继续在后台运行）
- **重新连接**：在 WSL2 终端中输入 `tmux attach -t claude-tui`
- **终止会话**：在 WSL2 终端中输入 `./scripts/run_tui_with_tmux.sh --kill`

---

### 步骤 6：查看日志（可选）

在**另一个 WSL2 终端窗口**中**用键盘输入**：

```bash
cd /opt/claude/Claude-Kits
./scripts/view_tui_logs.sh --tail
```

这样可以实时查看 TUI 的日志输出。

---

## 🐛 常见问题

### Q1: 我确实在 WSL2 终端中输入了命令，还是显示"没有 TTY"

**可能原因：**
- 你在 VS Code 的终端中，但终端类型不是 WSL
- 你通过 SSH 连接到 WSL2（可能没有 TTY 分配）

**解决方法：**
1. 打开 Windows Terminal
2. 确保选择的是 WSL2 配置文件
3. 重新运行 `./scripts/test_tty.sh` 验证

---

### Q2: tmux 命令找不到

**解决：**

```bash
sudo apt update
sudo apt install tmux
```

---

### Q3: 显示 "rich library not found"

**解决：**

```bash
pip3 install rich
```

或

```bash
sudo apt install python3-pip
pip3 install rich
```

---

### Q4: TUI 显示但方向键不工作

**解决方法：**
- 使用数字键 `1-8` 代替方向键
- 或使用 `w`/`s` 键导航

---

### Q5: 运行后立即退出，没有显示任何内容

**可能原因：**
- 依赖缺失
- Python 脚本有错误

**调试方法：**

```bash
# 直接运行 TUI，查看错误信息
python3 scripts/claude_tui.py
```

---

## 📝 快速参考

### 完整测试流程（复制到 WSL2 终端中）

```bash
# 1. 进入项目目录
cd /opt/claude/Claude-Kits

# 2. 验证环境
./scripts/test_tty.sh

# 3. 测试 TUI（简单版）
./scripts/simple_test_tui.sh

# 4. 使用 tmux 运行（完整版）
./scripts/run_tui_with_tmux.sh --log

# 5. 断开会话：Ctrl+B, D

# 6. 重新连接
tmux attach -t claude-tui

# 7. 查看日志（在另一个终端）
./scripts/view_tui_logs.sh --tail
```

---

## 🎯 成功标志

如果一切正常，你应该能够：

1. ✅ `test_tty.sh` 显示所有 ✅ 符号
2. ✅ `simple_test_tui.sh` 成功启动 TUI
3. ✅ TUI 显示 Logo 和菜单
4. ✅ 方向键或数字键可以导航
5. ✅ 选择菜单项可以正常执行
6. ✅ `run_tui_with_tmux.sh` 创建 tmux 会话
7. ✅ `Ctrl+B, D` 可以断开会话
8. ✅ `tmux attach` 可以重新连接
9. ✅ 日志脚本可以查看日志

---

## 💡 理解 TTY 的概念

**TTY（TeleTYpewriter）：**
- 交互式终端的抽象
- 提供键盘输入和屏幕输出
- 支持特殊键（箭头键、Ctrl+C 等）
- 支持光标控制和颜色

**有 TTY 的环境：**
- ✅ Windows Terminal 中的 WSL2
- ✅ 直接运行的 `bash` shell
- ✅ SSH 连接（使用 `-t` 选项）

**没有 TTY 的环境：**
- ❌ Claude Code 的 Bash 工具
- ❌ 管道命令（`echo "command" | bash`）
- ❌ 后台进程（`command &`）
- ❌ cron 任务

---

## 🔧 如果你想在没有 TTY 的环境中测试

虽然 TUI 和 tmux **必须**在 TTY 环境中运行，但你可以测试其他功能：

```bash
# 测试底层管理脚本（不需要 TTY）
python3 scripts/skills_manager.py list --scope project

# 测试 hooks 管理器
python3 scripts/hooks_manager.py list-templates

# 测试组件扫描器
python3 scripts/components_scanner.py
```

---

## 📚 总结

**关键点：**
1. **必须在真正的 WSL2 终端中手动输入命令**
2. **不要通过 Claude Code 的 Bash 工具运行**
3. **先用 `test_tty.sh` 验证环境**
4. **用 `simple_test_tui.sh` 测试 TUI 本身**
5. **确认成功后再使用 tmux 版本**

**记住这个规则：**
```
如果你是"复制 Claude 的输出并粘贴到某处执行"
  → ❌ 可能不会工作

如果你是"在 WSL2 终端中用键盘手动输入命令"
  → ✅ 应该可以工作
```

---

**祝你成功！** 🎉

如果按照以上步骤操作后仍有问题，请运行：

```bash
./scripts/test_tty.sh > /tmp/tty_diagnostic.txt
cat /tmp/tty_diagnostic.txt
```

然后将输出内容提供给我，我可以进一步诊断。
