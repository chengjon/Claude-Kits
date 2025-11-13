# Claude TUI 新工作流指南

> **发布日期**: 2025-11-13
> **版本**: 2.0
> **状态**: ✅ 已发布

## 概述

Claude TUI（文本用户界面）已完成重要改造，实现了更直观、更高效的组件管理工作流。新流程支持从浏览→查看详情→直接安装的无缝体验。

## 🎯 核心改进

### 1. 增强的详情视图

**原流程（旧）**
```
View Details → 显示信息 → 按 Enter 返回
```

**新流程**
```
View Details → 浏览列表 → 选择组件 → 完整信息页面
             └─ [1] 安装到项目 ✨ （新增）
             ├─ [2] 查看更多信息 ✨ （新增）
             └─ [0] 返回列表
```

### 2. 快速安装

**原流程（旧）**
```
Install → 输入组件名 → 进行安装
```

**新流程**
```
Install → 显示组件列表 → 选择组件 → 直接安装 ✨
```

## 📖 详细使用指南

### 方式 1：通过 View Details 安装

这是**推荐的使用方式**，因为你可以先浏览信息后再决定是否安装。

#### 步骤

1. **启动 TUI**
   ```bash
   python scripts/claude_tui.py
   ```

2. **选择组件类型**
   - 选择 `Agent Skills` 或 `Subagents` 或 `Slash Commands`

3. **选择操作**
   - 选择 `View Details`

4. **浏览组件列表**
   ```
   可用的 Skills

   共 84 个组件

   1. [cyan]task-planning-pro[/cyan] - Master task planning with priority...
   2. [cyan]conversational-coding-assistant[/cyan] - Provide expert...
   3. [cyan]ai-observability[/cyan] - Comprehensive AI system observability...
   ...
   ```

5. **选择要查看的组件**
   ```
   输入编号查看详情，或按 Enter 返回
   选择: 1
   ```

6. **查看组件详情**
   ```
   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ task-planning-pro                              ┃
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   名称  │ task-planning-pro
   类型  │ skills
   文件  │ SKILL.md
   路径  │ components/skills/task-planning-pro/SKILL.md
   描述  │ Master task planning with multi-agent coordination,
       │ progress tracking, and enterprise patterns...

   操作选项:
     [1] 安装到项目      ✨
     [2] 查看更多信息    ✨
     [0] 返回列表
   ```

7. **选择安装（[1] 或 [2]）**

   **选项 1：安装到项目**
   ```
   选择: 1
   ```

   **选项 2：查看更多信息**
   ```
   选择: 2

   === 组件源文件预览 ===
   ---
   name: task-planning-pro
   description: Master task planning with multi-agent coordination,
                progress tracking, and enterprise patterns. Build
                scalable testing strategies with advanced CI/CD...
   ---

   # 任务规划专家 (Task Planning Pro)

   > **用途**: 当你需要规划复杂的多步骤任务、追踪进度或管理...
   ```

8. **配置安装参数**
   ```
   安装 task-planning-pro

   输入目标项目路径（留空则使用当前目录）: /path/to/my/project

   选择安装作用域: project

   执行安装...
   ✓ Component installed successfully
   ```

### 方式 2：通过 Install 快速安装

快速方式，适合你已知道要安装哪个组件的场景。

#### 步骤

1. **启动 TUI**
   ```bash
   python scripts/claude_tui.py
   ```

2. **选择组件类型**
   - 选择 `Agent Skills` 或 `Subagents` 或 `Slash Commands`

3. **选择操作**
   - 选择 `Install`

4. **选择要安装的组件**
   ```
   快速安装 Skills

   共 84 个组件

   1. [cyan]task-planning-pro[/cyan] - Master task planning with priority...
   2. [cyan]conversational-coding-assistant[/cyan] - Provide expert...
   ...

   输入编号选择要安装的组件，或按 Enter 返回
   选择: 1
   ```

5. **完成安装**
   - 进入步骤 7-8（与 View Details 方式相同）

## 🔄 工作流对比

### 传统流程 vs 新流程

| 任务 | 传统流程 | 新流程 | 改进 |
|------|---------|--------|------|
| 查看所有组件 | List → 看列表 | View Details → 选择 → 看详情 | ✅ 可看完整信息 |
| 快速安装 | Install → 输入名字 | Install → 选择 → 安装 | ✅ 不用记组件名 |
| 了解组件 | 无法预览 | 查看更多信息 → 看源文件 | ✅ 可预览内容 |
| 从详情安装 | 需要返回 → 重新进入 Install | 直接点击 [1] | ✅ 无缝体验 |

## ⚙️ 配置选项

### 作用域（Scope）

安装时可以选择作用域：

- **project**: 安装到当前项目的 `.claude/` 目录（与团队共享）
- **user**: 安装到用户主目录的 `~/.claude/` 目录（个人使用）

```
选择安装作用域:
  > project
    user
```

### 项目路径

支持绝对路径和相对路径：

```
输入目标项目路径（留空则使用当前目录）: /home/user/my-project
输入目标项目路径（留空则使用当前目录）: ../sibling-project
输入目标项目路径（留空则使用当前目录）:   ← 按 Enter 使用当前目录
```

## 💡 最佳实践

### 1. 浏览时优先使用 View Details

```bash
# ✅ 推荐流程
1. View Details
2. 输入数字选择
3. 查看详情和预览
4. 确认后安装

# ❌ 不推荐
1. Install
2. 输入组件名
   └─ 容易出错，如果名字记错了
```

### 2. 批量安装多个组件

```bash
# 第一个组件
1. View Details → 选择 → [1] 安装

# 第二个组件
2. View Details → 选择 → [1] 安装

# 第三个组件
3. View Details → 选择 → [1] 安装
```

### 3. 查看组件详情后再决定

```bash
1. View Details → 浏览列表
2. 看到感兴趣的 → 选择
3. 查看详情 → [2] 查看更多信息
4. 确认无误 → [1] 安装
```

## 🔍 故障排查

### 问题 1：列表中找不到某个组件

**原因**：组件名称可能有特殊字符或大小写

**解决方案**：
- 使用 `List` 操作查看完整的组件列表
- 检查组件注册表：`components_registry.json`

### 问题 2：安装失败

**常见原因**：
- 项目路径不存在
- 权限不足
- 组件已存在（冲突）

**解决方案**：
- 确保项目路径有效
- 检查文件夹权限
- 如果有冲突，选择备份或重命名

### 问题 3：View Details 中查看信息很慢

**原因**：可能是读取大文件

**解决方案**：
- 跳过预览，直接安装
- 在安装后在项目中查看

## 📚 相关文档

- [TUI 快速开始](TUI_QUICK_START.md)
- [TUI 问题诊断](TUI_DIAGNOSIS_AND_SOLUTIONS.md)
- [组件注册表](../components_registry.json)

## 🎉 总结

新的 TUI 工作流提供了三个核心改进：

1. ✨ **增强的详情视图** - 一页显示完整信息和操作选项
2. ✨ **快速安装** - 从列表直接选择安装，无需记组件名
3. ✨ **无缝体验** - 在详情页面直接安装，不需要返回菜单

**立即尝试**：
```bash
python scripts/claude_tui.py
```

选择 `View Details`，体验新的工作流！
