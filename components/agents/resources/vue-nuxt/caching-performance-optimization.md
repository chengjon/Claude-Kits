# Caching & Performance Optimization

Advanced caching strategies, performance optimization techniques, and best practices for Nuxt 3 applications.


## 📑 Table of Contents

- [Advanced Caching Strategies](#advanced-caching-strategies)
  - [Redis Caching Layer](#redis-caching-layer)
  - [Multi-Layer Caching Strategy](#multi-layer-caching-strategy)
  - [Cache Invalidation Patterns](#cache-invalidation-patterns)
- [Performance Optimization](#performance-optimization)
  - [Image Optimization](#image-optimization)
  - [Component Lazy Loading](#component-lazy-loading)
  - [Code Splitting](#code-splitting)
  - [Database Query Optimization](#database-query-optimization)
  - [N+1 Query Prevention](#n1-query-prevention)
- [Client-Side Performance](#client-side-performance)
  - [Virtual Scrolling](#virtual-scrolling)
  - [Debouncing & Throttling](#debouncing-throttling)
  - [Web Workers for Heavy Computation](#web-workers-for-heavy-computation)
- [Monitoring Performance](#monitoring-performance)
  - [Web Vitals Tracking](#web-vitals-tracking)
- [Best Practices](#best-practices)
  - [1. Caching Strategy](#1-caching-strategy)
  - [2. Database Optimization](#2-database-optimization)
  - [3. Asset Optimization](#3-asset-optimization)
  - [4. Runtime Performance](#4-runtime-performance)
  - [5. Monitoring](#5-monitoring)

---
## Advanced Caching Strategies

### Redis Caching Layer

```typescript
// server/utils/cache.ts
import { createClient } from 'redis'

let redisClient: ReturnType<typeof createClient> | null = null

export async function getRedisClient() {
  if (!redisClient) {
    redisClient = createClient({
      url: useRuntimeConfig().redisUrl
    })
    await redisClient.connect()
  }
  return redisClient
}

export async function cacheGet<T>(key: string): Promise<T | null> {
  const client = await getRedisClient()
  const cached = await client.get(key)
  return cached ? JSON.parse(cached) : null
}

export async function cacheSet(key: string, value: any, ttl: number = 300) {
  const client = await getRedisClient()
  await client.setEx(key, ttl, JSON.stringify(value))
}

export async function cacheDelete(key: string) {
  const client = await getRedisClient()
  await client.del(key)
}

// server/api/products/[id].get.ts with caching
export default defineEventHandler(async (event) => {
  const { id } = getRouterParams(event)
  const cacheKey = `product:${id}`

  // Try cache first
  const cached = await cacheGet(cacheKey)
  if (cached) {
    setHeader(event, 'X-Cache', 'HIT')
    return cached
  }

  // Fetch from database
  const product = await prisma.product.findUnique({ where: { id } })

  if (!product) {
    throw createError({ statusCode: 404, message: 'Product not found' })
  }

  // Cache for 5 minutes
  await cacheSet(cacheKey, product, 300)
  setHeader(event, 'X-Cache', 'MISS')

  return product
})
```

### Multi-Layer Caching Strategy

```typescript
// server/utils/multi-cache.ts
interface CacheOptions {
  memory?: boolean
  redis?: boolean
  ttl?: number
}

const memoryCache = new Map<string, { data: any; expiresAt: number }>()

export async function getFromCache<T>(
  key: string,
  options: CacheOptions = {}
): Promise<T | null> {
  // Layer 1: Memory cache
  if (options.memory !== false) {
    const cached = memoryCache.get(key)
    if (cached && cached.expiresAt > Date.now()) {
      return cached.data
    }
    memoryCache.delete(key)
  }

  // Layer 2: Redis cache
  if (options.redis !== false) {
    return await cacheGet(key)
  }

  return null
}

export async function setInCache(
  key: string,
  value: any,
  options: CacheOptions = {}
) {
  const ttl = options.ttl || 300

  // Store in memory cache
  if (options.memory !== false) {
    memoryCache.set(key, {
      data: value,
      expiresAt: Date.now() + ttl * 1000
    })
  }

  // Store in Redis cache
  if (options.redis !== false) {
    await cacheSet(key, value, ttl)
  }
}

// Usage example
export default defineEventHandler(async (event) => {
  const cacheKey = 'expensive-query'

  const cached = await getFromCache(cacheKey, {
    memory: true,
    redis: true,
    ttl: 600
  })

  if (cached) return cached

  const data = await performExpensiveQuery()

  await setInCache(cacheKey, data, {
    memory: true,
    redis: true,
    ttl: 600
  })

  return data
})
```

### Cache Invalidation Patterns

```typescript
// server/utils/cache-invalidation.ts
export async function invalidateProductCache(productId: string) {
  const keysToInvalidate = [
    `product:${productId}`,
    `products:all`,
    `products:featured`,
    `product:${productId}:related`
  ]

  await Promise.all(keysToInvalidate.map(key => cacheDelete(key)))
}

export async function invalidateCategoryCache(categoryId: string) {
  await cacheDelete(`category:${categoryId}`)
  await cacheDelete(`categories:all`)
  // Invalidate all products in this category
  await cacheDelete(`products:category:${categoryId}`)
}

// server/api/products/[id].put.ts
export default defineEventHandler(async (event) => {
  const { id } = getRouterParams(event)
  const body = await readBody(event)

  const product = await prisma.product.update({
    where: { id },
    data: body
  })

  // Invalidate all related caches
  await invalidateProductCache(id)
  if (body.categoryId) {
    await invalidateCategoryCache(body.categoryId)
  }

  return product
})
```

## Performance Optimization

### Image Optimization

```vue
<template>
  <NuxtImg
    :src="imageSrc"
    :alt="imageAlt"
    loading="lazy"
    :width="800"
    :height="600"
    sizes="sm:100vw md:50vw lg:400px"
    :modifiers="{ quality: 80, format: 'webp' }"
    placeholder
    @load="handleImageLoad"
  />
</template>

<script setup lang="ts">
// nuxt.config.ts
export default defineNuxtConfig({
  image: {
    provider: 'cloudinary', // or 'ipx', 'imgix', etc.
    cloudinary: {
      baseURL: 'https://res.cloudinary.com/your-cloud/image/upload/'
    },
    presets: {
      avatar: {
        modifiers: {
          format: 'webp',
          width: 150,
          height: 150,
          quality: 80
        }
      },
      thumbnail: {
        modifiers: {
          format: 'webp',
          width: 300,
          height: 300,
          quality: 75
        }
      }
    }
  }
})
</script>
```

### Component Lazy Loading

```vue
<template>
  <div>
    <!-- Lazy load heavy component -->
    <LazyHeavyComponent v-if="showComponent" />
    <button @click="showComponent = true">Load Component</button>

    <!-- Lazy load on intersection -->
    <LazyImageGallery v-intersection="handleIntersection" />

    <!-- Named lazy import -->
    <ClientOnly>
      <template #fallback>
        <div>Loading...</div>
      </template>
      <LazyComplexChart :data="chartData" />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
const showComponent = ref(false)

function handleIntersection(entries: IntersectionObserverEntry[]) {
  // Load component when visible
}
</script>
```

### Code Splitting

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-vue': ['vue', 'vue-router'],
            'vendor-ui': ['@headlessui/vue', '@heroicons/vue'],
            'vendor-utils': ['lodash-es', 'date-fns']
          }
        }
      }
    }
  },

  // Route-based code splitting
  experimental: {
    splitPageChunks: true
  }
})

// Dynamic imports in components
const HeavyLibrary = defineAsyncComponent(() =>
  import('~/components/HeavyLibrary.vue')
)
```

### Database Query Optimization

```typescript
// server/api/products/index.get.ts
import { z } from 'zod'

const querySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
  category: z.string().optional(),
  sort: z.enum(['price-asc', 'price-desc', 'newest']).default('newest')
})

export default defineEventHandler(async (event) => {
  const query = await getValidatedQuery(event, querySchema.parse)

  const cacheKey = `products:${JSON.stringify(query)}`
  const cached = await cacheGet(cacheKey)

  if (cached) {
    return cached
  }

  const where = query.category
    ? { categoryId: query.category }
    : {}

  const orderBy = {
    'price-asc': { price: 'asc' },
    'price-desc': { price: 'desc' },
    'newest': { createdAt: 'desc' }
  }[query.sort]

  // Optimized query with select
  const [products, total] = await Promise.all([
    prisma.product.findMany({
      where,
      orderBy,
      skip: (query.page - 1) * query.limit,
      take: query.limit,
      select: {
        id: true,
        name: true,
        price: true,
        image: true,
        category: {
          select: {
            name: true
          }
        }
      }
    }),
    prisma.product.count({ where })
  ])

  const result = {
    products,
    pagination: {
      page: query.page,
      limit: query.limit,
      total,
      pages: Math.ceil(total / query.limit)
    }
  }

  // Cache for 5 minutes
  await cacheSet(cacheKey, result, 300)

  return result
})
```

### N+1 Query Prevention

```typescript
// BAD: N+1 queries
const posts = await prisma.post.findMany()
const postsWithAuthors = await Promise.all(
  posts.map(async (post) => ({
    ...post,
    author: await prisma.user.findUnique({ where: { id: post.authorId } })
  }))
)

// GOOD: Single query with include
const posts = await prisma.post.findMany({
  include: {
    author: {
      select: {
        name: true,
        email: true,
        avatar: true
      }
    }
  }
})

// GOOD: Drizzle with join
const posts = await db
  .select()
  .from(postsTable)
  .leftJoin(usersTable, eq(postsTable.authorId, usersTable.id))
```

## Client-Side Performance

### Virtual Scrolling

```vue
<template>
  <div class="virtual-list" ref="containerRef" @scroll="handleScroll">
    <div :style="{ height: `${totalHeight}px` }">
      <div
        v-for="item in visibleItems"
        :key="item.id"
        :style="{ transform: `translateY(${item.offset}px)` }"
        class="virtual-item"
      >
        <slot :item="item.data" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  items: any[]
  itemHeight: number
  buffer?: number
}

const props = withDefaults(defineProps<Props>(), {
  buffer: 5
})

const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)
const containerHeight = ref(0)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleItems = computed(() => {
  const start = Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.buffer)
  const end = Math.min(
    props.items.length,
    Math.ceil((scrollTop.value + containerHeight.value) / props.itemHeight) + props.buffer
  )

  return props.items.slice(start, end).map((item, index) => ({
    data: item,
    offset: (start + index) * props.itemHeight,
    id: item.id || start + index
  }))
})

function handleScroll() {
  scrollTop.value = containerRef.value?.scrollTop || 0
}

onMounted(() => {
  containerHeight.value = containerRef.value?.clientHeight || 0
})
</script>
```

### Debouncing & Throttling

```typescript
// composables/useDebounce.ts
export const useDebounce = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
) => {
  let timeoutId: NodeJS.Timeout

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

// composables/useThrottle.ts
export const useThrottle = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
) => {
  let lastCall = 0

  return (...args: Parameters<T>) => {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      fn(...args)
    }
  }
}

// Usage
const handleSearch = useDebounce((query: string) => {
  // Perform search
}, 300)

const handleScroll = useThrottle(() => {
  // Handle scroll
}, 100)
```

### Web Workers for Heavy Computation

```typescript
// composables/useWebWorker.ts
export const useWebWorker = <T = any, R = any>(
  workerFn: (data: T) => R
) => {
  const result = ref<R>()
  const error = ref<Error>()
  const loading = ref(false)

  const execute = async (data: T) => {
    loading.value = true
    error.value = undefined

    try {
      const blob = new Blob(
        [`(${workerFn.toString()})(self.postMessage)`],
        { type: 'application/javascript' }
      )

      const worker = new Worker(URL.createObjectURL(blob))

      return new Promise<R>((resolve, reject) => {
        worker.onmessage = (e) => {
          result.value = e.data
          loading.value = false
          worker.terminate()
          resolve(e.data)
        }

        worker.onerror = (e) => {
          error.value = new Error(e.message)
          loading.value = false
          worker.terminate()
          reject(error.value)
        }

        worker.postMessage(data)
      })
    } catch (e) {
      error.value = e as Error
      loading.value = false
      throw e
    }
  }

  return {
    result: readonly(result),
    error: readonly(error),
    loading: readonly(loading),
    execute
  }
}
```

## Monitoring Performance

### Web Vitals Tracking

```typescript
// composables/useWebVitals.ts
export const useWebVitals = () => {
  const metrics = ref<Record<string, number>>({})

  const trackWebVitals = () => {
    if (typeof window === 'undefined') return

    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS((metric) => {
        metrics.value.CLS = metric.value
        reportMetric(metric)
      })
      getFID((metric) => {
        metrics.value.FID = metric.value
        reportMetric(metric)
      })
      getFCP((metric) => {
        metrics.value.FCP = metric.value
        reportMetric(metric)
      })
      getLCP((metric) => {
        metrics.value.LCP = metric.value
        reportMetric(metric)
      })
      getTTFB((metric) => {
        metrics.value.TTFB = metric.value
        reportMetric(metric)
      })
    })
  }

  const reportMetric = (metric: any) => {
    // Send to analytics
    if (window.gtag) {
      window.gtag('event', metric.name, {
        value: Math.round(metric.value),
        metric_id: metric.id,
        metric_value: metric.value,
        metric_delta: metric.delta
      })
    }
  }

  return {
    metrics: readonly(metrics),
    trackWebVitals
  }
}
```

## Best Practices

### 1. Caching Strategy
- **Multi-layer caching**: Memory → Redis → Database
- **Cache invalidation**: Clear related caches on updates
- **TTL management**: Balance freshness vs performance
- **Cache warming**: Pre-populate frequently accessed data

### 2. Database Optimization
- **Select only needed fields**: Use `select` or projection
- **Avoid N+1 queries**: Use joins or includes
- **Connection pooling**: Reuse database connections
- **Indexing**: Index frequently queried fields

### 3. Asset Optimization
- **Image optimization**: Use NuxtImg with appropriate formats
- **Code splitting**: Split by route and vendor
- **Lazy loading**: Load components on demand
- **Tree shaking**: Remove unused code

### 4. Runtime Performance
- **Virtual scrolling**: For long lists
- **Debounce/throttle**: For frequent events
- **Web workers**: For heavy computations
- **Memoization**: Cache computed values

### 5. Monitoring
- **Web Vitals**: Track CLS, FID, LCP, FCP, TTFB
- **Custom metrics**: Monitor business-critical operations
- **Error tracking**: Log and alert on errors
- **Performance budgets**: Set and enforce limits
