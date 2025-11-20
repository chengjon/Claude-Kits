# Edge Deployment & Optimization

Complete guide to edge runtime deployment, CDN optimization, and global distribution strategies for Nuxt 3.


## 📑 Table of Contents

- [Edge Deployment Platforms](#edge-deployment-platforms)
  - [Cloudflare Workers](#cloudflare-workers)
  - [Cloudflare KV Storage](#cloudflare-kv-storage)
  - [Vercel Edge Functions](#vercel-edge-functions)
  - [Netlify Edge Functions](#netlify-edge-functions)
- [Edge Runtime Optimization](#edge-runtime-optimization)
  - [Edge-Compatible Code](#edge-compatible-code)
  - [Conditional Server Code](#conditional-server-code)
  - [Edge Caching Strategies](#edge-caching-strategies)
- [CDN Optimization](#cdn-optimization)
  - [Asset Optimization](#asset-optimization)
  - [CDN Cache Headers](#cdn-cache-headers)
  - [Smart CDN Purging](#smart-cdn-purging)
- [Geo-Location & Personalization](#geo-location-personalization)
  - [Geo-Based Routing](#geo-based-routing)
  - [Localized Content at Edge](#localized-content-at-edge)
- [Performance Optimization](#performance-optimization)
  - [Streaming SSR at Edge](#streaming-ssr-at-edge)
  - [Edge Middleware for A/B Testing](#edge-middleware-for-ab-testing)
  - [Edge Function Timeouts](#edge-function-timeouts)
- [Global Distribution Strategies](#global-distribution-strategies)
  - [Multi-Region Deployment](#multi-region-deployment)
  - [Smart Routing](#smart-routing)
- [Best Practices](#best-practices)
  - [1. Edge Compatibility](#1-edge-compatibility)
  - [2. Caching Strategy](#2-caching-strategy)
  - [3. Global Distribution](#3-global-distribution)
  - [4. Performance](#4-performance)
  - [5. Monitoring](#5-monitoring)

---
## Edge Deployment Platforms

### Cloudflare Workers

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  nitro: {
    preset: 'cloudflare',

    cloudflare: {
      pages: {
        routes: {
          include: ['/*'],
          exclude: ['/static/*']
        }
      }
    }
  },

  // Edge-compatible configuration
  experimental: {
    payloadExtraction: false
  }
})

// wrangler.toml
name = "nuxt-app"
main = ".output/server/index.mjs"
compatibility_date = "2024-01-01"

[site]
bucket = ".output/public"

[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id"

[[r2_buckets]]
binding = "ASSETS"
bucket_name = "nuxt-assets"

[vars]
NUXT_PUBLIC_API_BASE = "https://api.example.com"
```

### Cloudflare KV Storage

```typescript
// server/api/config.get.ts
export default defineEventHandler(async (event) => {
  // Access Cloudflare KV
  const kv = process.env.CACHE

  // Get cached config
  const cached = await kv.get('app-config', { type: 'json' })

  if (cached) {
    return cached
  }

  // Fetch and cache
  const config = await fetchAppConfig()
  await kv.put('app-config', JSON.stringify(config), {
    expirationTtl: 3600 // 1 hour
  })

  return config
})
```

### Vercel Edge Functions

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  nitro: {
    preset: 'vercel-edge',

    vercel: {
      regions: ['iad1', 'sfo1', 'cdg1'], // Multi-region deployment
      isr: {
        expiration: 60, // ISR cache time
      }
    }
  }
})

// Edge middleware example
// server/middleware/edge-geo.ts
export default defineEventHandler((event) => {
  const geo = event.context.vercel?.geo || {}

  // Add geo information to context
  event.context.geo = {
    country: geo.country,
    city: geo.city,
    region: geo.region,
    latitude: geo.latitude,
    longitude: geo.longitude
  }
})
```

### Netlify Edge Functions

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  nitro: {
    preset: 'netlify-edge',

    netlify: {
      images: {
        remote_images: ['https://example.com/.*']
      }
    }
  }
})

// netlify.toml
[build]
  command = "npm run build"
  publish = ".output/public"

[[edge_functions]]
  path = "/*"
  function = "server"

[[headers]]
  for = "/_nuxt/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

## Edge Runtime Optimization

### Edge-Compatible Code

```typescript
// ❌ NOT edge-compatible (uses Node.js APIs)
import fs from 'fs'
import { execSync } from 'child_process'

// ✅ Edge-compatible
const data = await fetch('https://api.example.com/data')
const json = await data.json()

// ✅ Use Web APIs
const encoder = new TextEncoder()
const decoder = new TextDecoder()

// ✅ Use edge-compatible storage
const cached = await useStorage('kv').getItem('key')
```

### Conditional Server Code

```typescript
// server/api/heavy-task.ts
export default defineEventHandler(async (event) => {
  // Check if running on edge
  const isEdge = process.env.NITRO_PRESET?.includes('edge')

  if (isEdge) {
    // Lightweight edge version
    return await fetchFromExternalAPI()
  } else {
    // Full-featured version with Node.js APIs
    return await performHeavyComputation()
  }
})
```

### Edge Caching Strategies

```typescript
// server/utils/edge-cache.ts
export async function edgeCacheGet<T>(
  key: string,
  options?: { namespace?: string }
): Promise<T | null> {
  const storage = useStorage(options?.namespace || 'cache')
  return await storage.getItem(key)
}

export async function edgeCacheSet<T>(
  key: string,
  value: T,
  options?: { ttl?: number; namespace?: string }
): Promise<void> {
  const storage = useStorage(options?.namespace || 'cache')
  await storage.setItem(key, value, { ttl: options?.ttl })
}

// server/api/products/[id].get.ts
export default defineEventHandler(async (event) => {
  const { id } = getRouterParams(event)
  const cacheKey = `product:${id}`

  // Try edge cache
  const cached = await edgeCacheGet(cacheKey)
  if (cached) {
    setHeader(event, 'X-Edge-Cache', 'HIT')
    return cached
  }

  // Fetch data
  const product = await fetchProduct(id)

  // Cache at edge
  await edgeCacheSet(cacheKey, product, { ttl: 300 })
  setHeader(event, 'X-Edge-Cache', 'MISS')

  return product
})
```

## CDN Optimization

### Asset Optimization

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // Image optimization
  image: {
    cloudinary: {
      baseURL: 'https://res.cloudinary.com/your-cloud/image/upload/'
    }
  },

  // Route rules for caching
  routeRules: {
    '/_nuxt/**': {
      headers: {
        'cache-control': 'public, max-age=31536000, immutable'
      }
    },
    '/images/**': {
      headers: {
        'cache-control': 'public, max-age=86400' // 1 day
      }
    }
  },

  // Nitro asset compression
  nitro: {
    compressPublicAssets: {
      gzip: true,
      brotli: true
    }
  }
})
```

### CDN Cache Headers

```typescript
// server/middleware/cache-headers.ts
export default defineEventHandler((event) => {
  const path = event.node.req.url || ''

  // Static assets - long cache
  if (path.startsWith('/_nuxt/') || path.match(/\.(js|css|png|jpg|jpeg|gif|svg|woff2?)$/)) {
    setHeader(event, 'Cache-Control', 'public, max-age=31536000, immutable')
    return
  }

  // API routes - short cache
  if (path.startsWith('/api/')) {
    setHeader(event, 'Cache-Control', 'public, max-age=60, s-maxage=300, stale-while-revalidate=600')
    return
  }

  // HTML pages - moderate cache with revalidation
  setHeader(event, 'Cache-Control', 'public, max-age=0, s-maxage=3600, must-revalidate')
})
```

### Smart CDN Purging

```typescript
// server/api/cdn/purge.post.ts
import { z } from 'zod'

const purgeSchema = z.object({
  paths: z.array(z.string()),
  secret: z.string()
})

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, purgeSchema.parse)

  // Verify secret
  if (body.secret !== useRuntimeConfig().cdnPurgeSecret) {
    throw createError({ statusCode: 401, message: 'Invalid secret' })
  }

  // Purge Cloudflare cache
  const zoneId = useRuntimeConfig().cloudflareZoneId
  const apiToken = useRuntimeConfig().cloudflareApiToken

  await $fetch(`https://api.cloudflare.com/client/v4/zones/${zoneId}/purge_cache`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiToken}`,
      'Content-Type': 'application/json'
    },
    body: {
      files: body.paths.map(path => `https://example.com${path}`)
    }
  })

  return { purged: body.paths }
})
```

## Geo-Location & Personalization

### Geo-Based Routing

```typescript
// server/middleware/geo-routing.ts
export default defineEventHandler((event) => {
  const country = getHeader(event, 'cf-ipcountry') ||
                  event.context.vercel?.geo?.country ||
                  'US'

  event.context.geo = { country }

  // Redirect based on country
  const path = event.node.req.url || ''
  if (!path.startsWith('/api/') && !path.startsWith('/_nuxt/')) {
    if (country === 'CN' && !path.startsWith('/cn')) {
      return sendRedirect(event, `/cn${path}`)
    }
  }
})
```

### Localized Content at Edge

```typescript
// server/api/content.get.ts
export default defineEventHandler(async (event) => {
  const country = event.context.geo?.country || 'US'
  const cacheKey = `content:${country}`

  // Check edge cache
  const cached = await edgeCacheGet(cacheKey)
  if (cached) return cached

  // Fetch localized content
  const content = await fetchLocalizedContent(country)

  // Cache at edge (1 hour)
  await edgeCacheSet(cacheKey, content, { ttl: 3600 })

  return content
})
```

## Performance Optimization

### Streaming SSR at Edge

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  experimental: {
    renderJsonPayloads: false // Disable for edge
  },

  nitro: {
    experimental: {
      streaming: true // Enable streaming
    }
  }
})
```

### Edge Middleware for A/B Testing

```typescript
// server/middleware/ab-testing.ts
export default defineEventHandler((event) => {
  const variant = Math.random() < 0.5 ? 'A' : 'B'

  // Set cookie for consistent experience
  if (!getCookie(event, 'ab-variant')) {
    setCookie(event, 'ab-variant', variant, {
      maxAge: 60 * 60 * 24 * 30, // 30 days
      sameSite: 'lax'
    })
  }

  event.context.abVariant = getCookie(event, 'ab-variant') || variant
})

// Use in pages
const event = useRequestEvent()
const variant = event?.context.abVariant || 'A'
```

### Edge Function Timeouts

```typescript
// Cloudflare Workers have 50ms CPU time limit
// Optimize for quick responses

export default defineEventHandler(async (event) => {
  // Use Promise.race for timeout protection
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), 25000)
  )

  const operation = async () => {
    // Fast edge operation
    return await fetchFromCache() || await fetchFromAPI()
  }

  try {
    return await Promise.race([operation(), timeout])
  } catch (error) {
    // Fallback to cached data or default
    return await getFallbackData()
  }
})
```

## Global Distribution Strategies

### Multi-Region Deployment

```typescript
// Deploy to multiple regions for low latency

// Vercel configuration
{
  "regions": ["iad1", "sfo1", "cdg1", "hnd1", "syd1"]
}

// Cloudflare automatically distributes to all edge locations

// AWS CloudFront + Lambda@Edge
{
  "ViewerRequest": {
    "FunctionArn": "arn:aws:lambda:us-east-1:xxx:function:edge-function:1"
  }
}
```

### Smart Routing

```typescript
// server/middleware/smart-routing.ts
export default defineEventHandler(async (event) => {
  const path = event.node.req.url || ''
  const geo = event.context.geo

  // Route to nearest region
  if (path.startsWith('/api/')) {
    const region = determineNearestRegion(geo)
    const apiUrl = getRegionalApiUrl(region)

    // Proxy to regional API
    if (region !== 'current') {
      const response = await fetch(`${apiUrl}${path}`)
      return await response.json()
    }
  }
})

function determineNearestRegion(geo: any): string {
  const regions = {
    'US': 'us-east',
    'EU': 'eu-west',
    'APAC': 'ap-southeast'
  }

  return regions[geo.continent] || 'us-east'
}
```

## Best Practices

### 1. Edge Compatibility
- **Use Web APIs**: Avoid Node.js-specific APIs
- **Lightweight bundles**: Minimize code size
- **Fast execution**: Optimize for CPU time limits
- **Stateless design**: Don't rely on local state

### 2. Caching Strategy
- **Multi-layer caching**: Edge → CDN → Origin
- **Smart invalidation**: Purge selectively
- **Cache warming**: Pre-populate popular content
- **Stale-while-revalidate**: Serve stale during updates

### 3. Global Distribution
- **Multi-region deployment**: Reduce latency globally
- **Geo-based routing**: Serve from nearest location
- **Content localization**: Edge-side personalization
- **Failover handling**: Graceful degradation

### 4. Performance
- **Streaming SSR**: Send HTML as it's generated
- **Code splitting**: Load only what's needed
- **Asset optimization**: Compress and minify
- **Resource hints**: Preload/prefetch critical resources

### 5. Monitoring
- **Edge analytics**: Track edge function performance
- **Error rates**: Monitor edge failures
- **Cache hit rates**: Optimize caching effectiveness
- **Geographic metrics**: Analyze by region
