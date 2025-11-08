# Claude TUI 使用说明

## 快速开始（3 步）

```bash
# 1. 启动 TUI（自动使用 tmux）
./scripts/run_tui_with_tmux.sh --log

# 2. 使用 TUI...
# （使用方向键导航菜单，回车选择）

# 3. 断开会话
# 按键：Ctrl+B, 然后按 D
```

## 问题已修复 ✅

- ✅ **菜单功能连接问题**：已修复 stdin 传递
- ✅ **日志查看需求**：提供 tmux + 便捷脚本
- ❌ **PM2 不适合运行 TUI**：请使用 tmux 代替

---

## 核心命令

### 启动 TUI

```bash
# 基本启动（自动创建/连接 tmux 会话）
./scripts/run_tui_with_tmux.sh

# 启用日志记录
./scripts/run_tui_with_tmux.sh --log

# 连接到现有会话
./scripts/run_tui_with_tmux.sh --attach

# 终止会话
./scripts/run_tui_with_tmux.sh --kill
```

---

### 查看日志

```bash
# 列出所有日志
./scripts/view_tui_logs.sh --list

# 实时查看最新日志
./scripts/view_tui_logs.sh --tail

# 交互式查看日志
./scripts/view_tui_logs.sh --view

# 清理 30 天前的日志
./scripts/view_tui_logs.sh --clean 30
```

---

## tmux 必备快捷键

| 按键 | 功能 |
|------|------|
| `Ctrl+B, D` | 断开会话（TUI 继续运行） |
| `Ctrl+B, [` | 滚动模式（查看历史输出） |
| `Ctrl+B, "` | 水平分屏 |
| `Q` | 退出滚动模式 |

---

## 常见场景

### 场景 1：日常使用

```bash
# 启动
./scripts/run_tui_with_tmux.sh

# 工作中需要离开？
# 按 Ctrl+B, D 断开（TUI 继续运行）

# 回来后重连
tmux attach -t claude-tui
```

---

### 场景 2：调试问题

```bash
# 终端 1：启动 TUI 并记录日志
./scripts/run_tui_with_tmux.sh --log

# 终端 2：实时查看日志
./scripts/view_tui_logs.sh --tail
```

---

### 场景 3：远程服务器

```bash
# SSH 连接服务器
ssh user@server

# 启动 TUI
./scripts/run_tui_with_tmux.sh

# 断开 SSH（TUI 继续运行）
exit

# 下次 SSH 登录后重连
ssh user@server
tmux attach -t claude-tui
```

---

## 为什么不用 PM2？

| 需求 | TUI 要求 | PM2 提供 | 兼容性 |
|------|----------|----------|--------|
| 交互式终端 | ✅ 必需 | ❌ 无 TTY | 不兼容 |
| 键盘输入 | ✅ 箭头键 | ❌ 无 stdin | 不兼容 |
| 实时渲染 | ✅ ANSI | ❌ 重定向 | 不兼容 |

**结论**：PM2 设计用于后台服务，不适合 TUI

---

## 帮助和文档

- **快速指南**: `docs/TUI_QUICK_START.md`
- **详细文档**: `docs/TUI_DIAGNOSIS_AND_SOLUTIONS.md`
- **修复报告**: `docs/TUI_FIX_SUMMARY.md`
- **脚本帮助**:
  - `./scripts/run_tui_with_tmux.sh --help`
  - `./scripts/view_tui_logs.sh --help`

---

## 故障排查

### Q: 会话卡住怎么办？

```bash
# 强制终止
tmux kill-session -t claude-tui

# 重新启动
./scripts/run_tui_with_tmux.sh
```

---

### Q: 找不到日志文件？

```bash
# 查看日志目录
./scripts/view_tui_logs.sh --dir

# 查看日志统计
./scripts/view_tui_logs.sh --size
```

---

### Q: 滚动缓冲区太小？

```bash
# 增加到 10000 行
echo "set-option -g history-limit 10000" >> ~/.tmux.conf
tmux source-file ~/.tmux.conf
```

---

## 联系和支持

- **项目文档**: `docs/` 目录
- **问题反馈**: 查看 `docs/TUI_QUICK_START.md` 的故障排查部分
