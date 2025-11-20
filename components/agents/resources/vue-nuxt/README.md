# Vue Nuxt Expert 资源文件集

本目录包含 Nuxt.js 框架高级开发的详细资源文件，配合 `vue-nuxt-expert.md` 主文件使用。

## 📁 资源文件概览

| 文件 | 主题 | 用途 |
|------|------|------|
| `ssr-ssg-rendering-modes.md` | SSR/SSG/ISR 渲染模式 | 静态生成、增量静态再生、混合渲染策略 |
| `nitro-server-api-development.md` | Nitro 服务器与 API 开发 | Server Routes、中间件、数据库集成、缓存 |
| `composables-middleware-plugins.md` | Composables/中间件/插件 | 可复用逻辑、路由守卫、应用生命周期 |
| `caching-performance-optimization.md` | 缓存与性能优化 | 多层缓存、CDN、代码分割、懒加载 |
| `production-deployment-monitoring.md` | 生产部署与监控 | Docker 部署、PM2、Sentry、性能监控 |
| `edge-deployment-optimization.md` | Edge 部署优化 | Edge Functions、全球分发、边缘缓存 |

**总资源**: 6 个文件，~3,238 行详细内容

## 🎯 使用场景

### 选择渲染策略
📖 阅读: `ssr-ssg-rendering-modes.md`
- SSG: 预渲染静态页面（博客、文档）
- SSR: 服务端渲染（动态内容、个性化）
- ISR: 增量静态再生（大量页面、定期更新）
- 混合: 按路由配置不同策略

### 构建 API 服务
📖 阅读: `nitro-server-api-development.md`
- RESTful API endpoints 设计
- 数据库连接（Prisma、Drizzle）
- 身份验证和授权
- API 缓存策略

### 编写可复用逻辑
📖 阅读: `composables-middleware-plugins.md`
- Composables: 数据获取、状态管理、工具函数
- Middleware: 路由守卫、权限验证
- Plugins: 第三方集成、全局配置

### 优化性能
📖 阅读: `caching-performance-optimization.md`
- HTTP 缓存策略
- Redis 数据缓存
- 图片优化（NuxtImg）
- 代码分割和懒加载

### 部署到生产
📖 阅读: `production-deployment-monitoring.md`
- Docker 容器化
- Vercel/Netlify 部署
- 环境变量管理
- 错误监控（Sentry）

### Edge 部署
📖 阅读: `edge-deployment-optimization.md`
- Cloudflare Workers
- Vercel Edge Functions
- 全球 CDN 配置
- 边缘缓存优化

## 💡 快速开始

### 场景 1: 构建博客网站（SSG）
```typescript
// 1. 阅读 ssr-ssg-rendering-modes.md - SSG 部分
// 2. 配置预渲染
export default defineNuxtConfig({
  nitro: {
    prerender: {
      routes: ['/'],
      crawlLinks: true
    }
  }
})

// 3. 使用 useAsyncData 获取内容
const { data: posts } = await useAsyncData('posts', () =>
  $fetch('/api/posts')
)
```

### 场景 2: 开发全栈应用（SSR + API）
```typescript
// 1. 阅读 nitro-server-api-development.md
// 2. 创建 API endpoint
// server/api/users.get.ts
export default defineEventHandler(async (event) => {
  const users = await prisma.user.findMany()
  return users
})

// 3. 页面中调用
const { data: users } = await useFetch('/api/users')
```

### 场景 3: 性能优化现有项目
```bash
1. 阅读 caching-performance-optimization.md
2. 实施 HTTP 缓存策略
3. 添加 Redis 缓存层
4. 配置图片优化
5. 代码分割和懒加载
6. 使用 production-deployment-monitoring.md 监控效果
```

## 🔗 与主文件的关系

**主文件**: `components/agents/vue-nuxt-expert.md` (378 行)
- Nuxt 3 快速开始
- 核心概念概览
- 📖 导航到本目录资源

**资源文件**: 本目录 (6 个文件)
- 深入的实现指南
- 完整代码示例
- 生产级最佳实践

## 🎓 学习路径

**初级** (刚开始 Nuxt):
1. 主文件 - 快速开始
2. `ssr-ssg-rendering-modes.md` - 理解渲染模式
3. `composables-middleware-plugins.md` - 学习 Nuxt 特性

**中级** (3-6 个月):
4. `nitro-server-api-development.md` - 构建全栈应用
5. `caching-performance-optimization.md` - 性能优化

**高级** (6+ 个月):
6. `production-deployment-monitoring.md` - 生产部署
7. `edge-deployment-optimization.md` - Edge 架构

## 🔧 技术栈

- **框架**: Nuxt 3 + Nitro
- **渲染**: SSR、SSG、ISR、Hybrid
- **数据**: Prisma、Drizzle ORM
- **缓存**: Redis、HTTP Cache
- **部署**: Docker、Vercel、Cloudflare
- **监控**: Sentry、DataDog

---

**相关资源**:
- 主文件: [`vue-nuxt-expert.md`](../../vue-nuxt-expert.md)
- 相关资源: `vue-fullstack/`, `vue-state/`
- 官方文档: [nuxt.com](https://nuxt.com)

**最后更新**: 2025-11-19
