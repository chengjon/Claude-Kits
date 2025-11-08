# Claude TUI 快速使用指南

## 问题已修复 ✅

**修复内容：** `claude_tui.py` 中的 stdin 传递问题已解决

**变更位置：** `scripts/claude_tui.py:200`

```python
# 修复前（❌ 会导致交互式输入失败）
result = subprocess.run(cmd, capture_output=True, text=True)

# 修复后（✅ 允许交互式输入正常工作）
result = subprocess.run(cmd, text=True)
```

**修复效果：**
- ✅ 菜单与功能正常连接
- ✅ 底层脚本的交互式输入（`Prompt.ask()`, `input()`）正常工作
- ✅ 用户可以正常确认操作、输入参数

---

## 核心问题解答

### 1. PM2 能运行 TUI 吗？

**答案：❌ 不能**

| 原因 | 说明 |
|------|------|
| **无交互式终端** | PM2 以 daemon 模式运行，没有 TTY |
| **stdin 被关闭** | 无法接收键盘输入（箭头键、回车） |
| **stdout 被重定向** | 输出写入日志文件，无法实时渲染终端 |

**PM2 适用场景：**
- Web 服务器（Express, Flask）
- API 服务（REST, GraphQL）
- 后台任务队列

**TUI 适用场景：**
- 需要用户实时交互的前台程序
- 需要直接连接终端的应用

---

### 2. 日志查看的最佳方案

#### 🏆 推荐：tmux（最佳方案）

**优点：**
- ✅ 会话持久化（SSH 断开也不影响）
- ✅ 可随时重连查看
- ✅ 支持滚动查看历史（默认 2000 行）
- ✅ 支持分屏（同时查看 TUI 和日志）
- ✅ 无需修改代码

**快速使用：**

```bash
# 启动 TUI（使用便捷脚本）
./scripts/run_tui_with_tmux.sh

# 或手动启动
tmux new-session -s claude-tui
python3 scripts/claude_tui.py
# 断开：Ctrl+B, D

# 重新连接
tmux attach -t claude-tui

# 启用日志记录
./scripts/run_tui_with_tmux.sh --log
```

---

## 便捷脚本使用指南

### `run_tui_with_tmux.sh` - TUI 启动脚本

**基本使用：**

```bash
# 启动 TUI（自动创建/连接 tmux 会话）
./scripts/run_tui_with_tmux.sh

# 启用日志记录
./scripts/run_tui_with_tmux.sh --log

# 连接到现有会话
./scripts/run_tui_with_tmux.sh --attach

# 终止会话
./scripts/run_tui_with_tmux.sh --kill

# 列出所有会话
./scripts/run_tui_with_tmux.sh --list

# 查看帮助
./scripts/run_tui_with_tmux.sh --help
```

**日志文件位置：**
- 默认路径：`~/.claude-tui-logs/session-YYYYMMDD-HHMMSS.log`

---

### `view_tui_logs.sh` - 日志查看脚本

**基本使用：**

```bash
# 列出所有日志文件
./scripts/view_tui_logs.sh --list

# 实时查看最新日志（类似 tail -f）
./scripts/view_tui_logs.sh --tail

# 交互式选择查看日志
./scripts/view_tui_logs.sh --view

# 查看第 3 个日志文件
./scripts/view_tui_logs.sh --view 3

# 清理 30 天前的日志
./scripts/view_tui_logs.sh --clean 30

# 查看日志目录大小统计
./scripts/view_tui_logs.sh --size

# 使用 lnav 查看所有日志（需要安装 lnav）
./scripts/view_tui_logs.sh --lnav

# 查看日志目录路径
./scripts/view_tui_logs.sh --dir
```

---

## tmux 快捷键速查

| 操作 | 快捷键 | 说明 |
|------|--------|------|
| **前缀键** | `Ctrl+B` | 所有命令前先按此键 |
| 断开会话 | `Ctrl+B, D` | Detach，TUI 继续运行 |
| 滚动模式 | `Ctrl+B, [` | 查看历史输出，按 Q 退出 |
| 向上滚动 | 滚动模式下 `↑` / `PgUp` | 查看之前的输出 |
| 向下滚动 | 滚动模式下 `↓` / `PgDn` | 查看之后的输出 |
| 搜索 | 滚动模式下 `/` | 向下搜索 |
| 反向搜索 | 滚动模式下 `?` | 向上搜索 |
| 水平分屏 | `Ctrl+B, "` | 横向分割窗口 |
| 垂直分屏 | `Ctrl+B, %` | 纵向分割窗口 |
| 切换面板 | `Ctrl+B, ↑/↓/←/→` | 在分屏间切换 |
| 关闭面板 | `Ctrl+B, X` | 确认后关闭 |
| 列出会话 | `Ctrl+B, S` | 交互式选择会话 |
| 重命名会话 | `Ctrl+B, $` | 修改会话名称 |
| 命令模式 | `Ctrl+B, :` | 输入 tmux 命令 |

---

## 常见使用场景

### 场景 1：日常开发使用

```bash
# 启动 TUI
./scripts/run_tui_with_tmux.sh

# 使用 TUI...

# 需要离开？断开会话（按 Ctrl+B, D）
# TUI 继续在后台运行

# 回来后重连
tmux attach -t claude-tui
```

---

### 场景 2：调试问题（需要日志）

```bash
# 启动 TUI 并启用日志记录
./scripts/run_tui_with_tmux.sh --log

# 在另一个终端实时查看日志
./scripts/view_tui_logs.sh --tail

# 或查看历史日志
./scripts/view_tui_logs.sh --list
./scripts/view_tui_logs.sh --view
```

---

### 场景 3：远程服务器使用

```bash
# 在服务器上启动 TUI
ssh user@server
./scripts/run_tui_with_tmux.sh

# 本地 SSH 断开，TUI 继续运行

# 下次登录时重连
ssh user@server
tmux attach -t claude-tui
```

---

### 场景 4：分屏查看（TUI + 日志）

```bash
# 启动 TUI
./scripts/run_tui_with_tmux.sh

# 在 tmux 中水平分屏（按 Ctrl+B, "）
# 上半部分：运行 TUI
# 下半部分：查看日志

# 切换到下半部分（按 Ctrl+B, ↓）
./scripts/view_tui_logs.sh --tail

# 现在可以同时看到 TUI 和日志！
```

---

### 场景 5：清理旧日志

```bash
# 查看日志目录大小
./scripts/view_tui_logs.sh --size

# 清理 30 天前的日志
./scripts/view_tui_logs.sh --clean 30

# 或清理 7 天前的日志
./scripts/view_tui_logs.sh --clean 7
```

---

## 高级用法

### 自定义日志目录

```bash
# 设置环境变量
export CLAUDE_TUI_LOG_DIR="/var/log/claude-tui"

# 创建目录
mkdir -p "$CLAUDE_TUI_LOG_DIR"

# 启动 TUI（日志将保存到自定义目录）
./scripts/run_tui_with_tmux.sh --log

# 查看日志
./scripts/view_tui_logs.sh --list
```

---

### 使用 lnav 高级日志查看器

**安装 lnav：**

```bash
# Ubuntu/Debian
sudo apt install lnav

# macOS
brew install lnav

# CentOS/RHEL（需要 EPEL）
sudo yum install epel-release
sudo yum install lnav
```

**使用 lnav：**

```bash
# 自动启用彩色、过滤、搜索
./scripts/view_tui_logs.sh --lnav

# lnav 快捷键：
#   /       - 搜索
#   n/N     - 下一个/上一个搜索结果
#   t       - 切换时间戳格式
#   i/I     - 按时间间隔统计
#   q       - 退出
#   ?       - 帮助
```

---

### 自动清理旧日志（cron 任务）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每周日凌晨 2 点清理 30 天前的日志）
0 2 * * 0 /opt/claude/Claude-Kits/scripts/view_tui_logs.sh --clean 30 > /dev/null 2>&1
```

---

## 故障排查

### 问题 1：tmux 会话卡住或无响应

**解决方案：**

```bash
# 强制终止会话
tmux kill-session -t claude-tui

# 重新启动
./scripts/run_tui_with_tmux.sh
```

---

### 问题 2：无法连接到会话（会话不存在）

**检查会话：**

```bash
# 列出所有会话
tmux list-sessions

# 或使用脚本
./scripts/run_tui_with_tmux.sh --list
```

**解决方案：**

```bash
# 创建新会话
./scripts/run_tui_with_tmux.sh --new
```

---

### 问题 3：日志文件太大

**查看大小：**

```bash
./scripts/view_tui_logs.sh --size
```

**清理旧日志：**

```bash
# 清理 7 天前的日志
./scripts/view_tui_logs.sh --clean 7

# 或手动删除
rm ~/.claude-tui-logs/session-2024*.log
```

---

### 问题 4：tmux 滚动缓冲区太小

**增加滚动缓冲区：**

```bash
# 编辑 ~/.tmux.conf
cat >> ~/.tmux.conf << EOF
# 增加滚动缓冲区到 10000 行
set-option -g history-limit 10000

# 启用鼠标支持（可选）
set -g mouse on
EOF

# 重新加载配置
tmux source-file ~/.tmux.conf
```

---

## 对比：PM2 vs tmux

| 特性 | PM2 | tmux | 说明 |
|------|-----|------|------|
| **运行 TUI** | ❌ 不支持 | ✅ 完美支持 | tmux 提供完整的 TTY |
| **会话持久化** | ✅ 支持 | ✅ 支持 | 两者都支持 |
| **滚动查看历史** | ❌ 不支持 | ✅ 支持 | tmux 可滚动查看 |
| **日志管理** | ✅ 强大 | ⚠️ 需配合 script | PM2 有更好的日志轮转 |
| **适用场景** | 后台服务 | 交互式程序 | 不同的设计目标 |
| **学习曲线** | 低 | 中 | tmux 需要学习快捷键 |

**结论：**
- **TUI 程序** → 使用 **tmux**
- **后台服务** → 使用 **PM2**

---

## 总结

### ✅ 已解决的问题

1. ✅ **菜单连接问题**：修复了 `claude_tui.py` 的 stdin 传递
2. ✅ **日志查看需求**：提供 tmux + 便捷脚本解决方案
3. ✅ **PM2 适用性**：明确 PM2 不适合 TUI，推荐 tmux

### 📦 提供的工具

1. **修复后的 TUI**：`scripts/claude_tui.py`（已修复 stdin 问题）
2. **启动脚本**：`scripts/run_tui_with_tmux.sh`（一键启动 tmux 会话）
3. **日志查看脚本**：`scripts/view_tui_logs.sh`（方便管理日志）
4. **完整文档**：`docs/TUI_DIAGNOSIS_AND_SOLUTIONS.md`（详细技术分析）

### 🚀 快速开始

```bash
# 1. 启动 TUI（自动使用 tmux）
./scripts/run_tui_with_tmux.sh --log

# 2. 使用 TUI...

# 3. 断开会话（按 Ctrl+B, D）

# 4. 在另一个终端查看日志
./scripts/view_tui_logs.sh --tail

# 5. 重连会话
tmux attach -t claude-tui
```

---

## 参考资源

- **tmux 官方文档**: https://github.com/tmux/tmux/wiki
- **tmux 快捷键速查**: https://tmuxcheatsheet.com/
- **lnav 官方网站**: https://lnav.org/
- **本项目文档**:
  - `docs/TUI_DIAGNOSIS_AND_SOLUTIONS.md` - 详细技术分析
  - `scripts/run_tui_with_tmux.sh --help` - 启动脚本帮助
  - `scripts/view_tui_logs.sh --help` - 日志脚本帮助
