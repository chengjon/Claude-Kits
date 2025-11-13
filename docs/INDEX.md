# 📚 文档导航索引

> 快速访问 Claude-Kits 所有文档

---

## 🚀 快速开始

### 新用户必读
1. **[README.md](../README.md)** - 项目概览和快速开始指南
2. **[QUICK_INSTALL_GUIDE.md](../QUICK_INSTALL_GUIDE.md)** - 详细安装指南
3. **[CLAUDE.md](../CLAUDE.md)** - Claude Code AI 工作指南

### 组件浏览
4. **[COMPONENTS_TREE.md](COMPONENTS_TREE.md)** - 完整组件文件树（433 个文件）
5. **[COMPONENT_COVERAGE_ANALYSIS.md](COMPONENT_COVERAGE_ANALYSIS.md)** - 组件覆盖面科学分析

---

## 📦 组件管理

### 组件系统
6. **[COMPONENT_MANAGEMENT_SYSTEM.md](COMPONENT_MANAGEMENT_SYSTEM.md)** - 组件管理系统设计
7. **[MODEL_SELECTION_GUIDE.md](MODEL_SELECTION_GUIDE.md)** - 模型选择指南（Opus/Sonnet/Haiku）

### 统计和分析
- **总计**: 386 个组件
  - 233 个 Agents (14 个类别)
  - 71 个 Skills (12 个类别)
  - 63 个 Commands (11 个类别)
  - 19 个 Hooks

---

## 🏗️ 架构设计

### 核心架构
8. **[ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)** - 详细架构设计和 SOP
9. **[THREE_TIER_ARCHITECTURE.md](THREE_TIER_ARCHITECTURE.md)** - 三层架构设计（user/plugin/project）
10. **[UNIVERSAL_INSTALLER_DESIGN.md](UNIVERSAL_INSTALLER_DESIGN.md)** - 通用安装器设计

---

## 📝 实施报告

### 最新进展
11. **[SESSION_COMPLETION_SUMMARY.md](SESSION_COMPLETION_SUMMARY.md)** - 会话完成摘要（含最新清理工作）
12. **[BAK_FILES_CLEANUP_REPORT.md](BAK_FILES_CLEANUP_REPORT.md)** - .bak 文件清理报告
13. **[DOCUMENTATION_UPDATE_LOG.md](DOCUMENTATION_UPDATE_LOG.md)** - 文档更新记录

### 功能实施
14. **[IMPLEMENTATION_COMPLETION_REPORT.md](IMPLEMENTATION_COMPLETION_REPORT.md)** - 实施完成报告
15. **[INSTALLATION_SYSTEM_IMPLEMENTATION.md](INSTALLATION_SYSTEM_IMPLEMENTATION.md)** - 安装系统实施
16. **[CUSTOM_ROLE_BUILDER_IMPLEMENTATION.md](CUSTOM_ROLE_BUILDER_IMPLEMENTATION.md)** - 自定义 Role 构建器
17. **[ROLE_CHECKLISTS_IMPLEMENTATION.md](ROLE_CHECKLISTS_IMPLEMENTATION.md)** - Role Checklist 实施
18. **[CASE_IMPLEMENTATION_SUMMARY.md](CASE_IMPLEMENTATION_SUMMARY.md)** - Reddit Case 实施总结

---

## 🔍 质量审计

### 合规性检查
19. **[COMPLIANCE_AUDIT_REPORT.md](COMPLIANCE_AUDIT_REPORT.md)** - 合规性审计报告
20. **[OFFICIAL_COMPLIANCE_AUDIT_REPORT.md](OFFICIAL_COMPLIANCE_AUDIT_REPORT.md)** - 官方合规性审计
21. **[CODE_REVIEW_FINDINGS.md](CODE_REVIEW_FINDINGS.md)** - 代码审查发现

---

## 📊 参考项目

### 迁移和分析
22. **[REFERENCE_PROJECTS_ANALYSIS.md](REFERENCE_PROJECTS_ANALYSIS.md)** - 参考项目分析（8 个项目）
23. **[MIGRATION_REPORT.md](MIGRATION_REPORT.md)** - 组件迁移报告
24. **[AGENTS2_IMPORT_REPORT.md](AGENTS2_IMPORT_REPORT.md)** - Agents2 导入报告

---

## 🖥️ TUI 系统

### 交互界面
25. **[TUI_QUICK_START.md](TUI_QUICK_START.md)** - TUI 快速开始指南
26. **[TUI_FIX_SUMMARY.md](TUI_FIX_SUMMARY.md)** - TUI 修复总结
27. **[TUI_DIAGNOSIS_AND_SOLUTIONS.md](TUI_DIAGNOSIS_AND_SOLUTIONS.md)** - TUI 诊断和解决方案

---

## 🔧 工具和脚本

### 管理脚本位置
- `scripts/claude_manager.py` - 统一 CLI 管理器
- `scripts/claude_tui.py` - 交互式 TUI
- `scripts/skills_manager.py` - Skills 管理
- `scripts/subagents_manager.py` - Agents 管理
- `scripts/commands_manager.py` - Commands 管理
- `scripts/hooks_manager.py` - Hooks 管理
- `scripts/roles_manager.py` - Roles 管理
- `scripts/custom_role_builder.py` - 自定义 Role 构建器
- `scripts/components_scanner.py` - 组件扫描器
- `scripts/generate_components_tree.py` - 文件树生成器
- `scripts/analyze_component_coverage.py` - 覆盖面分析器

### 安装脚本
- `scripts/install_reddit_case.py` - Reddit Case 安装器
- `scripts/universal_installer.py` - 通用安装器

---

## 📋 常见任务快速链接

### 安装组件
```bash
# 查看所有 Roles
python scripts/roles_manager.py list

# 安装 Reddit Case
python scripts/roles_manager.py install reddit-case --path /path/to/project

# 安装单个 Skill
python scripts/skills_manager.py install task-planning-pro --path /path/to/project
```

参考: [QUICK_INSTALL_GUIDE.md](../QUICK_INSTALL_GUIDE.md)

### 浏览组件
```bash
# 扫描并更新组件注册表
python scripts/components_scanner.py

# 生成组件文件树
python scripts/generate_components_tree.py

# 分析组件覆盖面
python scripts/analyze_component_coverage.py
```

参考: [COMPONENT_MANAGEMENT_SYSTEM.md](COMPONENT_MANAGEMENT_SYSTEM.md)

### 创建自定义 Role
```bash
# 使用 TUI 图形界面（推荐）
python scripts/claude_tui.py
# 导航到: Role Checklists → Create Custom

# 或使用命令行工具
python scripts/custom_role_builder.py
```

参考: [CUSTOM_ROLE_BUILDER_IMPLEMENTATION.md](CUSTOM_ROLE_BUILDER_IMPLEMENTATION.md)

---

## 📊 关键统计数据

### 组件数量（2025-11-11）
- **总计**: 386 个组件
- **Agents**: 233 个（14 个类别）
  - Backend Development: 110 个
  - Frontend Development: 31 个
  - Data & AI: 19 个
- **Skills**: 71 个（12 个类别）
  - Development Patterns: 24 个
  - Testing & Quality: 10 个
- **Commands**: 63 个（11 个类别）
- **Hooks**: 19 个

### 技术栈覆盖（Top 10）
1. AI: 54 个组件
2. Cloud: 21 个组件
3. Testing: 13 个组件
4. Docker: 11 个组件
5. React/Monitoring: 各 10 个组件

参考: [COMPONENT_COVERAGE_ANALYSIS.md](COMPONENT_COVERAGE_ANALYSIS.md)

---

## 🔄 文档维护

### 最近更新
- **2025-11-11**: .bak 文件清理，文档全面中文化
- **文档数量**: 27 个 Markdown 文件
- **组件文件**: 433 个（排除备份）

### 更新文档
```bash
# 更新所有组件文档
python scripts/components_scanner.py
python scripts/generate_components_tree.py
python scripts/analyze_component_coverage.py
```

参考: [DOCUMENTATION_UPDATE_LOG.md](DOCUMENTATION_UPDATE_LOG.md)

---

## 🎯 按用户角色推荐

### 新用户
1. README.md - 了解项目
2. QUICK_INSTALL_GUIDE.md - 快速上手
3. COMPONENTS_TREE.md - 浏览组件

### 开发者
1. ARCHITECTURE_DESIGN.md - 理解架构
2. COMPONENT_MANAGEMENT_SYSTEM.md - 组件系统
3. CLAUDE.md - AI 协作指南

### 系统管理员
1. INSTALLATION_SYSTEM_IMPLEMENTATION.md - 安装系统
2. THREE_TIER_ARCHITECTURE.md - 架构设计
3. COMPLIANCE_AUDIT_REPORT.md - 质量审计

### 贡献者
1. CODE_REVIEW_FINDINGS.md - 代码标准
2. REFERENCE_PROJECTS_ANALYSIS.md - 参考实践
3. MIGRATION_REPORT.md - 迁移指南

---

## 📖 阅读顺序建议

### 初学者路径
1. README.md
2. QUICK_INSTALL_GUIDE.md
3. COMPONENTS_TREE.md
4. COMPONENT_COVERAGE_ANALYSIS.md
5. TUI_QUICK_START.md

### 深入学习路径
1. ARCHITECTURE_DESIGN.md
2. THREE_TIER_ARCHITECTURE.md
3. COMPONENT_MANAGEMENT_SYSTEM.md
4. UNIVERSAL_INSTALLER_DESIGN.md
5. CUSTOM_ROLE_BUILDER_IMPLEMENTATION.md

### 实施参考路径
1. CASE_IMPLEMENTATION_SUMMARY.md
2. IMPLEMENTATION_COMPLETION_REPORT.md
3. REFERENCE_PROJECTS_ANALYSIS.md
4. SESSION_COMPLETION_SUMMARY.md

---

## 🔗 外部资源

### Claude Code 官方文档
- 位置: `reference/Claude-code/`
- 内容: Claude Code 官方参考文档

### 参考项目
- 位置: `reference/`
- 包含: 8 个参考项目和实践案例

---

**版本**: v1.0.0
**最后更新**: 2025-11-11
**维护状态**: ✅ 活跃维护
