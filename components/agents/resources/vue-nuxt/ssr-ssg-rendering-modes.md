# SSR/SSG Rendering Modes

This guide covers Static Site Generation, Incremental Static Regeneration, and deployment strategies for Nuxt 3 applications.


## 📑 Table of Contents

- [Static Site Generation (SSG)](#static-site-generation-ssg)
  - [Dynamic Routes Pre-rendering](#dynamic-routes-pre-rendering)
  - [Hybrid Rendering Strategies](#hybrid-rendering-strategies)
- [Incremental Static Regeneration (ISR)](#incremental-static-regeneration-isr)
  - [On-Demand Revalidation](#on-demand-revalidation)
  - [Time-based Revalidation](#time-based-revalidation)
  - [Webhook-Triggered Revalidation](#webhook-triggered-revalidation)
- [Rendering Mode Selection Guide](#rendering-mode-selection-guide)
  - [When to Use SSR](#when-to-use-ssr)
  - [When to Use SSG](#when-to-use-ssg)
  - [When to Use ISR](#when-to-use-isr)
  - [When to Use SPA](#when-to-use-spa)
- [Performance Optimization](#performance-optimization)
  - [Selective Hydration](#selective-hydration)
  - [Payload Extraction](#payload-extraction)
- [Deployment Configurations](#deployment-configurations)
  - [Docker Static Build](#docker-static-build)
  - [Docker SSR Build](#docker-ssr-build)
  - [Nginx Configuration](#nginx-configuration)
- [Best Practices](#best-practices)
  - [1. Route-Level Rendering Control](#1-route-level-rendering-control)
  - [2. Data Fetching Strategy](#2-data-fetching-strategy)
  - [3. Build Performance](#3-build-performance)
  - [4. SEO Optimization](#4-seo-optimization)
  - [5. Monitoring](#5-monitoring)

---
## Static Site Generation (SSG)

### Dynamic Routes Pre-rendering

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  nitro: {
    prerender: {
      routes: ['/sitemap.xml'],
      crawlLinks: true,
    }
  },

  hooks: {
    'nitro:config'(nitroConfig) {
      if (nitroConfig.dev) return

      // Generate dynamic routes
      nitroConfig.prerender.routes.push(
        ...generateProductRoutes(),
        ...generateCategoryRoutes()
      )
    }
  }
})

async function generateProductRoutes() {
  const products = await fetchProducts()
  return products.map(p => `/products/${p.slug}`)
}

async function generateCategoryRoutes() {
  const categories = await fetchCategories()
  return categories.map(c => `/category/${c.slug}`)
}
```

### Hybrid Rendering Strategies

```typescript
// nuxt.config.ts - Mix SSR, SSG, and SPA
export default defineNuxtConfig({
  routeRules: {
    // Static pages - pre-rendered at build time
    '/': { prerender: true },
    '/about': { prerender: true },
    '/contact': { prerender: true },

    // ISR - regenerate periodically
    '/blog/**': { isr: 1800 }, // 30 minutes
    '/products/**': { isr: 600 }, // 10 minutes

    // SSR - server-side rendered on demand
    '/dashboard/**': { ssr: true },
    '/profile/**': { ssr: true },

    // SPA - client-side only
    '/admin/**': { ssr: false },

    // API routes with caching
    '/api/**': {
      cors: true,
      cache: { maxAge: 60 },
      headers: {
        'cache-control': 'public, max-age=60'
      }
    }
  }
})
```

## Incremental Static Regeneration (ISR)

### On-Demand Revalidation

```typescript
// server/api/revalidate.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { secret, path } = body

  // Verify secret
  if (secret !== useRuntimeConfig().revalidateSecret) {
    throw createError({ statusCode: 401, message: 'Invalid secret' })
  }

  // Revalidate path
  await revalidatePath(path)

  return { revalidated: true, path }
})
```

### Time-based Revalidation

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    '/': { isr: 3600 }, // Regenerate every hour
    '/blog/**': { isr: 1800 }, // 30 minutes
    '/products/**': { isr: 600 }, // 10 minutes
  }
})
```

### Webhook-Triggered Revalidation

```typescript
// server/api/webhooks/content-update.post.ts
import { z } from 'zod'

const webhookSchema = z.object({
  type: z.enum(['product', 'blog', 'page']),
  action: z.enum(['create', 'update', 'delete']),
  slug: z.string(),
  secret: z.string()
})

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, webhookSchema.parse)

  // Verify webhook secret
  if (body.secret !== useRuntimeConfig().webhookSecret) {
    throw createError({ statusCode: 401, message: 'Invalid webhook secret' })
  }

  // Determine paths to revalidate
  const pathsToRevalidate: string[] = []

  switch (body.type) {
    case 'product':
      pathsToRevalidate.push(`/products/${body.slug}`)
      pathsToRevalidate.push('/products') // List page
      break
    case 'blog':
      pathsToRevalidate.push(`/blog/${body.slug}`)
      pathsToRevalidate.push('/blog')
      break
    case 'page':
      pathsToRevalidate.push(`/${body.slug}`)
      break
  }

  // Revalidate paths
  for (const path of pathsToRevalidate) {
    await revalidatePath(path)
  }

  return {
    success: true,
    revalidated: pathsToRevalidate
  }
})
```

## Rendering Mode Selection Guide

### When to Use SSR
- Dynamic content that changes frequently
- User-specific content (dashboards, profiles)
- Real-time data requirements
- Authentication-dependent pages
- High SEO requirements with personalization

### When to Use SSG
- Static content (landing pages, docs)
- Content that rarely changes
- Maximum performance requirements
- Minimal server costs
- Content-driven sites (blogs, portfolios)

### When to Use ISR
- E-commerce product pages
- Blog posts that get updated
- Content that changes periodically
- Balance between SSR and SSG benefits
- Reduced build times for large sites

### When to Use SPA
- Admin dashboards
- Complex interactive applications
- Client-side heavy apps
- Apps behind authentication
- Real-time collaborative tools

## Performance Optimization

### Selective Hydration

```vue
<!-- pages/blog/[slug].vue -->
<template>
  <div>
    <!-- SSR rendered, no hydration needed -->
    <article>
      <h1>{{ post.title }}</h1>
      <div v-html="post.content"></div>
    </article>

    <!-- Client-side only interactive components -->
    <ClientOnly>
      <CommentsSection :post-id="post.id" />
      <ShareButtons :url="shareUrl" />
    </ClientOnly>
  </div>
</template>
```

### Payload Extraction

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  experimental: {
    payloadExtraction: true,
    renderJsonPayloads: true,
  }
})
```

## Deployment Configurations

### Docker Static Build

```dockerfile
# Dockerfile for SSG
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run generate

FROM nginx:alpine

COPY --from=builder /app/.output/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker SSR Build

```dockerfile
# Dockerfile for SSR
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM base AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/.output ./.output

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nuxtjs
RUN chown -R nuxtjs:nodejs /app

USER nuxtjs

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
```

### Nginx Configuration

```nginx
# nginx.conf for SSR
events {
  worker_connections 1024;
}

http {
  upstream nuxt_app {
    server app:3000;
  }

  server {
    listen 80;
    server_name example.com;

    location / {
      proxy_pass http://nuxt_app;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection 'upgrade';
      proxy_set_header Host $host;
      proxy_cache_bypass $http_upgrade;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /_nuxt/ {
      proxy_pass http://nuxt_app;
      proxy_cache_valid 200 30d;
      add_header Cache-Control "public, immutable";
    }
  }
}
```

## Best Practices

### 1. Route-Level Rendering Control
- Use `routeRules` for granular control
- Combine different strategies per route
- Cache API responses appropriately

### 2. Data Fetching Strategy
- Use `useFetch` for SSR-compatible fetching
- Implement proper caching for expensive queries
- Consider data freshness requirements

### 3. Build Performance
- Limit pre-rendered routes for SSG
- Use ISR for large content catalogs
- Implement incremental builds

### 4. SEO Optimization
- Ensure critical content is server-rendered
- Use proper meta tags and structured data
- Implement dynamic sitemaps

### 5. Monitoring
- Track rendering times
- Monitor cache hit rates
- Set up performance budgets
