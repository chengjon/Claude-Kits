# Nuxt 3 Advanced Patterns

## Server API Routes

```typescript
// server/api/products/[id].get.ts
export default defineEventHandler(async (event) => {
  const { id } = getRouterParams(event)
  const db = useDatabase()

  const product = await db.product.findUnique({ where: { id } })

  if (!product) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Product not found'
    })
  }

  return product
})

// server/api/cart.post.ts - Protected route
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event)
  const body = await readBody(event)

  const cart = await useDatabase().cart.update({
    where: { userId: user.id },
    data: { items: body.items }
  })

  return cart
})
```

## Middleware and Plugins

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated.value) {
    return navigateTo('/login', {
      query: { redirect: to.fullPath }
    })
  }
})

// plugins/analytics.client.ts
export default defineNuxtPlugin((nuxtApp) => {
  const analytics = createAnalytics({
    apiKey: useRuntimeConfig().public.analyticsKey
  })

  nuxtApp.hook('page:finish', () => {
    analytics.pageView(window.location.pathname)
  })

  return {
    provide: {
      analytics
    }
  }
})
```

## Data Fetching Patterns

```typescript
// useFetch - SSR-friendly, cached
const { data, pending, error, refresh } = await useFetch('/api/data')

// useAsyncData - Custom async logic
const { data } = await useAsyncData('products', async () => {
  const [products, categories] = await Promise.all([
    $fetch('/api/products'),
    $fetch('/api/categories')
  ])
  return { products, categories }
})

// useLazyFetch - Client-side only
const { data } = useLazyFetch('/api/data', {
  server: false
})

// $fetch - Programmatic fetch
async function loadData() {
  const data = await $fetch('/api/data')
  return data
}
```

## SSR Page with Data Fetching

```vue
<!-- pages/products/[id].vue -->
<template>
  <div>
    <Head>
      <Title>{{ product.name }}</Title>
      <Meta name="description" :content="product.description" />
    </Head>

    <NuxtLayout>
      <div class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <NuxtImg
            :src="product.image"
            :alt="product.name"
            class="w-full rounded-lg"
            loading="lazy"
          />

          <div>
            <h1 class="text-3xl font-bold mb-4">{{ product.name }}</h1>
            <p class="text-gray-600 mb-6">{{ product.description }}</p>
            <span class="text-2xl font-bold">${{ product.price }}</span>

            <button
              @click="addToCart"
              :disabled="loading"
              class="mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg"
            >
              {{ loading ? 'Adding...' : 'Add to Cart' }}
            </button>
          </div>
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { addItem } = useCart()
const loading = ref(false)

// SSR-friendly data fetching
const { data: product } = await useFetch<Product>(
  `/api/products/${route.params.id}`,
  { key: `product-${route.params.id}` }
)

useSeoMeta({
  title: product.value?.name,
  description: product.value?.description,
})

async function addToCart() {
  loading.value = true
  try {
    await addItem({ product: product.value, quantity: 1 })
  } finally {
    loading.value = false
  }
}
</script>
```
