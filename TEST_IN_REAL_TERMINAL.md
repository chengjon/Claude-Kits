# 在真正的终端中测试 TUI

**重要：此文件中的命令必须在真正的终端（Terminal）中运行，不能在 Claude Code 中运行！**

---

## 为什么需要真正的终端？

- ❌ **Claude Code 环境**：没有 TTY（伪终端），tmux 和 TUI 无法运行
- ✅ **真正的终端**：有 TTY，tmux 和 TUI 可以正常工作

**错误信息示例（在 Claude Code 中运行）：**
```
open terminal failed: not a terminal
```

---

## 测试步骤

### 1. 打开你的系统终端

根据你的操作系统：

- **Linux/WSL**: 打开 Terminal（Ctrl+Alt+T）
- **macOS**: 打开 Terminal.app 或 iTerm2
- **Windows**: 打开 Windows Terminal 或 PowerShell

### 2. 导航到项目目录

```bash
cd /opt/claude/Claude-Kits
```

### 3. 检查依赖

```bash
# 检查 tmux 是否安装
which tmux
tmux -V

# 检查 Python 和依赖
python3 --version
python3 -c "import rich; print('rich 已安装')"
```

**如果 tmux 未安装：**

```bash
# Ubuntu/Debian
sudo apt install tmux

# CentOS/RHEL
sudo yum install tmux

# macOS
brew install tmux
```

### 4. 测试 1: 直接运行 TUI（不使用 tmux）

```bash
# 最简单的测试
python3 scripts/claude_tui.py
```

**预期结果：**
- 显示 Claude-Kits Logo
- 显示主菜单
- 可以使用方向键导航
- 按 'q' 或选择 "Exit" 退出

**如果成功：**
- ✅ TUI 本身工作正常
- ✅ Python 和依赖正常
- ✅ 修复后的 stdin 传递正常

---

### 5. 测试 2: 使用脚本查看帮助

```bash
# 测试启动脚本
./scripts/run_tui_with_tmux.sh --help

# 测试日志脚本
./scripts/view_tui_logs.sh --help
```

**预期结果：**
- 显示完整的帮助信息
- 没有错误

---

### 6. 测试 3: 启动 tmux 会话

```bash
# 基本启动（不记录日志）
./scripts/run_tui_with_tmux.sh
```

**预期结果：**
- 显示 "创建 tmux 会话: claude-tui"
- 进入 TUI 界面
- 可以正常使用

**tmux 操作：**
- 断开会话：`Ctrl+B`, 然后按 `D`
- 重新连接：`tmux attach -t claude-tui`
- 终止会话：`./scripts/run_tui_with_tmux.sh --kill`

---

### 7. 测试 4: 启用日志记录

```bash
# 启动并记录日志
./scripts/run_tui_with_tmux.sh --log
```

**预期结果：**
- 创建 tmux 会话
- 启用 `script` 命令记录日志
- 日志保存在 `~/.claude-tui-logs/session-*.log`

**在另一个终端查看日志：**
```bash
# 打开第二个终端窗口
cd /opt/claude/Claude-Kits

# 实时查看日志
./scripts/view_tui_logs.sh --tail
```

---

### 8. 测试 5: 日志管理

```bash
# 列出所有日志
./scripts/view_tui_logs.sh --list

# 查看日志统计
./scripts/view_tui_logs.sh --size

# 查看最新日志
./scripts/view_tui_logs.sh --view 1
```

---

### 9. 测试 6: 菜单功能（修复验证）

在 TUI 中测试以下操作：

1. **选择 "Agent Skills" → "List"**
   - 输入 scope: `project`
   - 应该能正常显示 skills 列表
   - ✅ 验证 stdin 修复有效

2. **选择 "Agent Skills" → "Install"**
   - 输入 skill 名称（例如：`test-skill`）
   - 输入 scope: `project`
   - 应该能正常接收输入
   - ✅ 验证交互式输入正常

3. **选择 "Hooks" → "List"**
   - 输入 scope: `project`
   - 应该能正常显示 hooks 配置

---

### 10. 测试 7: tmux 高级功能

```bash
# 创建会话并分屏
./scripts/run_tui_with_tmux.sh --log

# 在 tmux 中：
# 1. 按 Ctrl+B, " (水平分屏)
# 2. 按 Ctrl+B, ↓ (切换到下方面板)
# 3. 运行: ./scripts/view_tui_logs.sh --tail
# 4. 现在可以同时看到 TUI 和日志！
```

---

## 常见问题排查

### Q1: 显示 "open terminal failed: not a terminal"

**原因：** 你在非 TTY 环境中运行（如 Claude Code）

**解决：** 在真正的终端中运行

---

### Q2: 显示 "tmux: command not found"

**原因：** tmux 未安装

**解决：**
```bash
# Ubuntu/Debian
sudo apt install tmux

# macOS
brew install tmux
```

---

### Q3: 显示 "rich library not found"

**原因：** Python rich 库未安装

**解决：**
```bash
pip3 install rich
```

---

### Q4: TUI 显示但菜单无响应

**原因：** 终端不支持方向键或配置问题

**解决：**
- 使用数字快捷键（1-8）代替方向键
- 或使用 `w`/`s` 键导航
- 检查终端类型：`echo $TERM`

---

### Q5: tmux 会话卡住

**解决：**
```bash
# 强制终止
tmux kill-session -t claude-tui

# 重新启动
./scripts/run_tui_with_tmux.sh
```

---

## 成功标志

如果所有测试通过，你应该能够：

- ✅ TUI 正常启动和显示
- ✅ 方向键或数字键导航菜单
- ✅ 选择菜单项后能正常执行
- ✅ 底层脚本能接收用户输入（stdin 修复有效）
- ✅ tmux 会话正常创建和重连
- ✅ 日志正常记录和查看
- ✅ 分屏功能正常工作

---

## 下一步

测试通过后，你可以：

1. **日常使用：**
   ```bash
   ./scripts/run_tui_with_tmux.sh
   ```

2. **调试时启用日志：**
   ```bash
   ./scripts/run_tui_with_tmux.sh --log
   ```

3. **远程服务器使用：**
   ```bash
   ssh user@server
   cd /opt/claude/Claude-Kits
   ./scripts/run_tui_with_tmux.sh
   # 断开 SSH，TUI 继续运行
   # 下次 SSH 登录后：tmux attach -t claude-tui
   ```

---

## 总结

**记住：**
- ❌ 不要在 Claude Code 中运行 TUI
- ✅ 在真正的终端中运行
- ✅ tmux 让 TUI 会话持久化
- ✅ 修复后的 stdin 让菜单功能正常工作

**完整工作流：**
```bash
# 终端 1：运行 TUI
./scripts/run_tui_with_tmux.sh --log

# 终端 2：查看日志（可选）
./scripts/view_tui_logs.sh --tail

# 需要离开？
# 按 Ctrl+B, D 断开（TUI 继续运行）

# 回来后重连
tmux attach -t claude-tui
```

---

**祝测试顺利！** 🎉
