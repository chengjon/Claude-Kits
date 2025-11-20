# Vue Fullstack Pro 资源文件集

本目录包含 Vue 3 全栈开发的详细资源文件，配合 `vue-fullstack-pro.md` 主文件使用。

## 📁 资源文件概览

| 文件 | 主题 | 用途 |
|------|------|------|
| `composition-api-patterns.md` | Composition API 模式 | ref/reactive、computed、watch、生命周期、最佳实践 |
| `component-architecture.md` | 组件架构 | 设计模式、插槽、动态组件、微前端、设计系统 |
| `state-management-pinia.md` | Pinia 状态管理 | Store 定义、Actions/Getters、持久化、TypeScript |
| `performance-ecosystem-integration.md` | 性能优化与生态集成 | Bundle 优化、懒加载、Vue Router、VueUse、Vitest |

**总资源**: 4 个文件，~2,367 行详细内容

## 🎯 核心主题

### Composition API 精通
📖 `composition-api-patterns.md` - 响应式系统、Composables 设计、性能优化

### 可扩展组件设计
📖 `component-architecture.md` - 企业级组件模式、设计系统集成、插件架构

### 全局状态管理
📖 `state-management-pinia.md` - Pinia Store、模块化、SSR Hydration

### 性能与生态
📖 `performance-ecosystem-integration.md` - 优化策略、Router 高级用法、测试集成

## 💡 快速开始

```typescript
// Composable 模式
export const useUser = () => {
  const user = ref(null)
  const fetchUser = async () => {
    user.value = await $fetch('/api/user')
  }
  return { user, fetchUser }
}

// Pinia Store
export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price, 0)
  )
  return { items, total }
})
```

---

**相关资源**:
- 主文件: [`vue-fullstack-pro.md`](../../vue-fullstack-pro.md)
- 相关: `vue-nuxt/`, `vue-state/`
