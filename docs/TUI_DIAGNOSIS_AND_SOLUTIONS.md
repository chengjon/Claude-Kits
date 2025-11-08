# Claude TUI 诊断与解决方案

## 问题总结

用户遇到三个问题：
1. 能否在 PM2 中运行 `claude_tui.py`？
2. TUI 菜单与功能"连接不上"的问题
3. 想要方便查看日志的更好方案

---

## 问题 1：PM2 运行 TUI 的可行性

### ❌ 结论：不适合在 PM2 中运行

**原因分析：**

| 需求项 | TUI 要求 | PM2 提供 | 兼容性 |
|--------|----------|----------|--------|
| 交互式终端 | ✅ 必需 | ❌ 无 TTY | 不兼容 |
| 键盘输入 | ✅ 箭头键、回车 | ❌ 无 stdin | 不兼容 |
| 实时输出 | ✅ 终端渲染 | ❌ 重定向到日志 | 不兼容 |
| 后台运行 | ❌ 不需要 | ✅ 核心功能 | 需求不匹配 |

**PM2 设计用途：**
- Web 服务器（Express, Flask, Django）
- API 服务（REST, GraphQL）
- 后台任务队列（Celery, Bull）
- 数据库服务、消息队列

**TUI 设计用途：**
- 需要用户实时交互的界面程序
- 需要在前台运行，直接连接终端

---

## 问题 2：TUI "菜单连接不上" 的根本原因

### 诊断结果：subprocess stdin 传递问题

**问题代码位置：** `scripts/claude_tui.py:199`

```python
def run_manager_script(script_name, args):
    # ...
    result = subprocess.run(cmd, capture_output=True, text=True)  # ❌ 问题在这里
    # ...
```

**根本原因：**

1. **`capture_output=True`**：捕获 stdout/stderr，但不传递 stdin
2. **底层脚本交互需求**：
   - `skills_manager.py` 等脚本使用 `Prompt.ask()` 需要用户确认
   - `hooks_manager.py` 的 `confirm_action()` 等待 `input()`
   - 当 stdin 被关闭时，这些调用会：
     - 立即返回空字符串（最佳情况）
     - 抛出 `EOFError` 异常（常见情况）
     - 无限挂起（最坏情况）

3. **状态流转断裂**：
   ```
   TUI 菜单 → 调用 run_manager_script() → subprocess.run()
                                              ↓
                                        stdin 关闭
                                              ↓
                                        底层脚本 input() 失败
                                              ↓
                                        用户看到错误或无响应
   ```

### 解决方案：修复 stdin 传递

#### 方案 2A：传递 stdin（推荐）

```python
def run_manager_script(script_name, args):
    """运行指定的管理脚本（修复版）"""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        console.print(f"[red]Error: Management script {script_name} not found[/red]")
        input("Press Enter to continue...")
        return False

    cmd = [sys.executable, str(script_path)] + args

    try:
        clear_screen()
        console.print(Panel(f"Running: {' '.join(cmd)}", title="Executing Command", border_style="blue"))

        # ✅ 修复：允许底层脚本访问 stdin
        result = subprocess.run(cmd, text=True)  # 不捕获输出，直接显示到终端

        if result.returncode == 0:
            console.print("\n[green]✓ Command executed successfully.[/green]")
        else:
            console.print(f"\n[red]✗ Command failed with return code {result.returncode}.[/red]")

        input("\nPress Enter to return to menu...")
        return result.returncode == 0

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        input("Press Enter to continue...")
        return False
```

**优点：**
- ✅ 完全解决 stdin 传递问题
- ✅ 底层脚本可以正常交互
- ✅ 输出实时显示，用户体验更好
- ✅ 简化代码逻辑

**缺点：**
- ❌ 无法在 TUI 中美化底层脚本的输出（但底层脚本本身已经用 `rich` 美化）

#### 方案 2B：切换到纯 CLI 模式（备选）

如果需要完全控制输出格式，可以让底层脚本支持 `--json` 输出：

```python
def run_manager_script(script_name, args):
    # 添加 --json 参数获取结构化输出
    cmd = [sys.executable, str(script_path)] + args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 解析 JSON 并美化显示
    data = json.loads(result.stdout)
    display_formatted_result(data)
```

**优点：**
- ✅ TUI 完全控制输出格式
- ✅ 可以捕获和处理错误

**缺点：**
- ❌ 需要修改所有底层脚本
- ❌ 工作量大

---

## 问题 3：日志查看的更好方案

### 方案对比

| 方案 | 适用场景 | 优点 | 缺点 | 推荐度 |
|------|----------|------|------|--------|
| **PM2** | ❌ 不适合 TUI | 日志管理、自动重启 | 无法运行 TUI | ⭐ |
| **tmux/screen** | ✅ TUI 持久化 | 会话持久、可重连、滚动缓冲 | 需要学习快捷键 | ⭐⭐⭐⭐⭐ |
| **script 命令** | ✅ 会话记录 | 自动记录所有输出 | 无法实时查看 | ⭐⭐⭐⭐ |
| **文件日志 + tail** | ✅ 长期存档 | 持久化、可搜索 | 需要修改代码 | ⭐⭐⭐ |
| **lnav/multitail** | ✅ 高级日志查看 | 彩色、过滤、搜索 | 需要安装额外工具 | ⭐⭐⭐⭐ |

---

### 推荐方案详解

#### ⭐⭐⭐⭐⭐ 方案 1：tmux（最佳推荐）

**安装：**
```bash
# Ubuntu/Debian
sudo apt install tmux

# CentOS/RHEL
sudo yum install tmux

# macOS
brew install tmux
```

**使用方法：**

```bash
# 1. 创建一个名为 "claude-tui" 的 tmux 会话
tmux new-session -s claude-tui

# 2. 在会话中运行 TUI
python3 scripts/claude_tui.py

# 3. 断开会话（TUI 继续运行）
# 按键：Ctrl+B, 然后按 D

# 4. 重新连接会话
tmux attach -t claude-tui

# 5. 查看所有会话
tmux list-sessions

# 6. 滚动查看历史输出
# 按键：Ctrl+B, 然后按 [ 进入滚动模式，使用 ↑/↓/PgUp/PgDn，按 Q 退出

# 7. 结束会话
tmux kill-session -t claude-tui
```

**高级功能：**

```bash
# 创建会话并自动记录日志
tmux new-session -s claude-tui \
  "script -f -c 'python3 scripts/claude_tui.py' ~/claude-tui-$(date +%Y%m%d-%H%M%S).log"

# 分屏查看（水平分割）
# 按键：Ctrl+B, 然后按 "
# 切换面板：Ctrl+B, 然后按方向键
```

**优点：**
- ✅ 会话持久化（SSH 断开也不影响）
- ✅ 可随时重连查看
- ✅ 支持滚动查看历史（默认 2000 行，可配置）
- ✅ 支持分屏（同时查看 TUI 和日志）
- ✅ 支持会话共享（多用户协作）

---

#### ⭐⭐⭐⭐ 方案 2：script 命令记录会话

**使用方法：**

```bash
# 1. 启动会话记录
script -f ~/claude-tui-session.log

# 2. 运行 TUI
python3 scripts/claude_tui.py

# 3. 退出时自动保存日志
exit

# 4. 在另一个终端实时查看日志
tail -f ~/claude-tui-session.log

# 5. 回放会话（带时间戳）
scriptreplay -t ~/claude-tui-session.timing -s ~/claude-tui-session.log
```

**自动化脚本：**

```bash
#!/bin/bash
# scripts/run_tui_with_logging.sh

LOG_DIR="$HOME/.claude-tui-logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/session-$TIMESTAMP.log"
TIMING_FILE="$LOG_DIR/session-$TIMESTAMP.timing"

echo "Starting Claude TUI with logging..."
echo "Log file: $LOG_FILE"

script -f -t"$TIMING_FILE" -c "python3 $(dirname $0)/claude_tui.py" "$LOG_FILE"
```

**优点：**
- ✅ 完整记录所有输入输出（包括 ANSI 颜色）
- ✅ 可回放会话
- ✅ 无需学习新工具（Linux 自带）

**缺点：**
- ❌ 日志文件可能很大
- ❌ 包含控制字符，不便直接阅读

---

#### ⭐⭐⭐⭐ 方案 3：增加文件日志功能

**修改 TUI 添加日志支持：**

```python
# scripts/claude_tui.py 顶部添加

import logging
from datetime import datetime

# 配置日志
LOG_DIR = Path.home() / ".claude-tui-logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"tui-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# 在关键位置添加日志
def run_manager_script(script_name, args):
    logger.info(f"Executing: {script_name} {' '.join(args)}")
    # ...
    logger.info(f"Result: returncode={result.returncode}")

def handle_skills_actions(action):
    logger.info(f"Skills action: {action}")
    # ...
```

**实时查看日志：**

```bash
# 终端 1：运行 TUI
python3 scripts/claude_tui.py

# 终端 2：实时查看日志
tail -f ~/.claude-tui-logs/tui-*.log

# 或使用 lnav（更强大）
lnav ~/.claude-tui-logs/tui-*.log
```

---

#### ⭐⭐⭐⭐ 方案 4：使用 lnav 高级日志查看器

**安装 lnav：**

```bash
# Ubuntu 20.04+
sudo apt install lnav

# macOS
brew install lnav

# 或从源码编译
# https://github.com/tstack/lnav
```

**使用方法：**

```bash
# 实时查看日志（自动彩色、过滤、搜索）
lnav ~/.claude-tui-logs/

# 功能：
# - 自动识别日志格式
# - 彩色语法高亮
# - 正则搜索（/ 键）
# - 时间戳导航
# - SQL 查询日志
```

---

## 综合推荐方案

### 场景 1：日常开发使用

```bash
# 使用 tmux 运行 TUI，随时可重连
tmux new-session -s claude-tui "python3 scripts/claude_tui.py"

# 需要查看时重连
tmux attach -t claude-tui
```

### 场景 2：调试问题

```bash
# 使用 script 记录完整会话
script -f ~/debug-session.log
python3 scripts/claude_tui.py
exit

# 分析日志
less ~/debug-session.log
# 或使用 cat 去除控制字符
cat ~/debug-session.log | sed 's/\x1b\[[0-9;]*m//g' > debug-clean.log
```

### 场景 3：长期存档

```bash
# 修改 TUI 添加文件日志
# 定期清理旧日志
find ~/.claude-tui-logs -name "*.log" -mtime +30 -delete
```

### 场景 4：服务器远程使用

```bash
# 在服务器上使用 tmux
ssh user@server
tmux new-session -s claude-tui
python3 scripts/claude_tui.py

# 本地断开，服务器继续运行
# 下次登录时重连
ssh user@server
tmux attach -t claude-tui
```

---

## 总结

| 需求 | 推荐方案 | 命令 |
|------|----------|------|
| **持久化 TUI 会话** | tmux | `tmux new -s claude-tui` |
| **调试问题** | script | `script -f debug.log` |
| **长期日志存档** | 文件日志 + lnav | 修改代码添加 logging |
| **实时监控** | tmux 分屏 | `Ctrl+B "` 分屏 |
| **远程使用** | tmux over SSH | `ssh + tmux attach` |

**不要使用 PM2** 运行 TUI，它会导致：
- ❌ 键盘输入无法传递
- ❌ 终端渲染失败
- ❌ 程序无法正常运行

---

## 快速修复指南

### 立即修复 "菜单连接不上" 问题

1. 编辑 `scripts/claude_tui.py`
2. 找到 `run_manager_script()` 函数（line 182）
3. 将 line 199 修改为：

```python
# 修改前（❌ 会导致 stdin 问题）
result = subprocess.run(cmd, capture_output=True, text=True)

# 修改后（✅ 允许交互式输入）
result = subprocess.run(cmd, text=True)
```

4. 测试：
```bash
python3 scripts/claude_tui.py
# 选择 "Agent Skills" → "List" → 输入参数
# 应该能正常工作
```

### 立即启用日志查看

```bash
# 方案 A：tmux（推荐）
tmux new-session -s claude-tui "python3 scripts/claude_tui.py"
# 断开：Ctrl+B, D
# 重连：tmux attach -t claude-tui

# 方案 B：script 记录
script -f ~/claude-tui.log
python3 scripts/claude_tui.py
# 在另一个终端：tail -f ~/claude-tui.log
```

---

## 附录：tmux 快捷键速查

| 操作 | 快捷键 | 说明 |
|------|--------|------|
| **前缀键** | `Ctrl+B` | 所有命令前先按此键 |
| 断开会话 | `Ctrl+B, D` | Detach，TUI 继续运行 |
| 滚动模式 | `Ctrl+B, [` | 按 Q 退出滚动模式 |
| 水平分屏 | `Ctrl+B, "` | 横向分割窗口 |
| 垂直分屏 | `Ctrl+B, %` | 纵向分割窗口 |
| 切换面板 | `Ctrl+B, ↑/↓/←/→` | 在分屏间切换 |
| 关闭面板 | `Ctrl+B, X` | 确认后关闭 |
| 列出会话 | `Ctrl+B, S` | 交互式选择会话 |

---

## 参考资源

- tmux 官方文档: https://github.com/tmux/tmux/wiki
- tmux 入门教程: https://tmuxcheatsheet.com/
- lnav 文档: https://lnav.org/
- script 手册: `man script`
