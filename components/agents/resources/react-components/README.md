# React Component Pro 资源文件集

本目录包含 React 组件开发专业知识的详细资源文件，配合 `react-component-pro.md` 主文件使用。

## 📁 资源文件概览

| 文件 | 主题 | 用途 |
|------|------|------|
| `component-design-patterns.md` | 组件设计模式 | HOC、Render Props、Compound Components、Hooks 模式 |
| `design-systems-accessibility.md` | 设计系统与无障碍 | Design Tokens、WCAG 合规、ARIA 模式、主题系统 |
| `storybook-documentation.md` | Storybook 文档化 | Stories、Controls、Docs、测试、CI/CD 集成 |

**总资源**: 3 个文件，~1,881 行详细内容

## 🎯 核心主题

### 高级组件模式
📖 `component-design-patterns.md` - 可复用组件设计、性能优化、TypeScript 类型安全

### 设计系统构建
📖 `design-systems-accessibility.md` - Token 系统、主题化、WCAG AAA 无障碍

### 组件文档化
📖 `storybook-documentation.md` - Storybook 7+、交互测试、自动化文档

## 💡 快速开始

```tsx
// Compound Component 模式
const Tabs = ({ children }) => {
  const [activeTab, setActiveTab] = useState(0)
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  )
}
Tabs.List = TabsList
Tabs.Panel = TabsPanel

// 使用
<Tabs>
  <Tabs.List>
    <Tab>Tab 1</Tab>
    <Tab>Tab 2</Tab>
  </Tabs.List>
  <Tabs.Panel>Content 1</Tabs.Panel>
  <Tabs.Panel>Content 2</Tabs.Panel>
</Tabs>
```

---

**相关资源**:
- 主文件: [`react-component-pro.md`](../../react-component-pro.md)
- 相关: `react-fullstack/`, `ui-visual/`
