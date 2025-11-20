# State Management with Pinia

Complete guide to Pinia state management including store patterns, composition API integration, and advanced features.


## 📑 Table of Contents

- [Store Definition](#store-definition)
  - [Basic Store with Composition API](#basic-store-with-composition-api)
  - [Store with Options API](#store-with-options-api)
- [Advanced Patterns](#advanced-patterns)
  - [Store Composition](#store-composition)
  - [Plugin System](#plugin-system)
  - [TypeScript Support](#typescript-support)
- [DevTools Integration](#devtools-integration)
  - [Store Debugging](#store-debugging)
  - [Custom Actions Tracking](#custom-actions-tracking)
- [Server-Side Rendering (SSR) with Pinia](#server-side-rendering-ssr-with-pinia)
  - [Hydration Pattern](#hydration-pattern)
- [Best Practices](#best-practices)
  - [1. Store Design](#1-store-design)
  - [2. Actions](#2-actions)
  - [3. Getters](#3-getters)
  - [4. Performance](#4-performance)
  - [5. Testing](#5-testing)

---
## Store Definition

### Basic Store with Composition API

```typescript
// stores/cart.ts
import { defineStore } from 'pinia'
import type { CartItem } from '~/types'

export const useCartStore = defineStore('cart', () => {
  // State
  const items = ref<CartItem[]>([])
  const isOpen = ref(false)

  // Getters (computed)
  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  const itemCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const isEmpty = computed(() => items.value.length === 0)

  // Actions
  function addItem(item: CartItem) {
    const existing = items.value.find(i => i.id === item.id)
    if (existing) {
      existing.quantity += item.quantity
    } else {
      items.value.push(item)
    }
  }

  function removeItem(id: string) {
    items.value = items.value.filter(item => item.id !== id)
  }

  function updateQuantity(id: string, quantity: number) {
    const item = items.value.find(i => i.id === id)
    if (item) {
      item.quantity = quantity
    }
  }

  function clearCart() {
    items.value = []
  }

  function toggleCart() {
    isOpen.value = !isOpen.value
  }

  // Persist to localStorage
  if (process.client) {
    watch(() => items.value, (newItems) => {
      localStorage.setItem('cart', JSON.stringify(newItems))
    }, { deep: true })

    const stored = localStorage.getItem('cart')
    if (stored) {
      items.value = JSON.parse(stored)
    }
  }

  return {
    // State
    items: readonly(items),
    isOpen,
    // Getters
    total,
    itemCount,
    isEmpty,
    // Actions
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    toggleCart
  }
})
```

### Store with Options API

```typescript
// stores/products.ts
import { defineStore } from 'pinia'
import type { Product } from '~/types'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [] as Product[],
    loading: false,
    error: null as Error | null,
    filters: {
      category: null as string | null,
      minPrice: 0,
      maxPrice: Infinity,
      search: ''
    }
  }),

  getters: {
    filteredProducts: (state) => {
      return state.products.filter(product => {
        const matchesCategory = !state.filters.category ||
          product.category === state.filters.category
        const matchesPrice = product.price >= state.filters.minPrice &&
          product.price <= state.filters.maxPrice
        const matchesSearch = !state.filters.search ||
          product.name.toLowerCase().includes(state.filters.search.toLowerCase())

        return matchesCategory && matchesPrice && matchesSearch
      })
    },

    productById: (state) => (id: string) => {
      return state.products.find(p => p.id === id)
    },

    categories: (state) => {
      return [...new Set(state.products.map(p => p.category))]
    }
  },

  actions: {
    async fetchProducts() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/products')
        this.products = await response.json()
      } catch (error) {
        this.error = error as Error
      } finally {
        this.loading = false
      }
    },

    async fetchProduct(id: string) {
      this.loading = true
      try {
        const response = await fetch(`/api/products/${id}`)
        const product = await response.json()

        // Update or add to products array
        const index = this.products.findIndex(p => p.id === id)
        if (index !== -1) {
          this.products[index] = product
        } else {
          this.products.push(product)
        }

        return product
      } catch (error) {
        this.error = error as Error
        throw error
      } finally {
        this.loading = false
      }
    },

    setFilter(key: keyof typeof this.filters, value: any) {
      this.filters[key] = value
    },

    clearFilters() {
      this.filters = {
        category: null,
        minPrice: 0,
        maxPrice: Infinity,
        search: ''
      }
    }
  }
})
```

## Advanced Patterns

### Store Composition

```typescript
// stores/user.ts
export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => user.value !== null)

  async function login(credentials: LoginCredentials) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
    user.value = await response.json()
  }

  function logout() {
    user.value = null
  }

  return { user: readonly(user), isAuthenticated, login, logout }
})

// stores/cart.ts - Using another store
export const useCartStore = defineStore('cart', () => {
  const userStore = useUserStore()
  const items = ref<CartItem[]>([])

  // Sync cart with server when user logs in
  watch(() => userStore.isAuthenticated, async (isAuth) => {
    if (isAuth) {
      await syncCartWithServer()
    }
  })

  async function syncCartWithServer() {
    if (!userStore.isAuthenticated) return

    const response = await fetch('/api/cart', {
      method: 'POST',
      body: JSON.stringify({ items: items.value })
    })
    items.value = await response.json()
  }

  return { items, syncCartWithServer }
})
```

### Plugin System

```typescript
// plugins/pinia-persistence.ts
import { PiniaPluginContext } from 'pinia'

export function piniaPersistence({ store }: PiniaPluginContext) {
  const storageKey = `pinia-${store.$id}`

  // Restore state from localStorage
  const stored = localStorage.getItem(storageKey)
  if (stored) {
    store.$patch(JSON.parse(stored))
  }

  // Persist state changes
  store.$subscribe((mutation, state) => {
    localStorage.setItem(storageKey, JSON.stringify(state))
  })
}

// main.ts
import { createPinia } from 'pinia'
import { piniaPersistence } from './plugins/pinia-persistence'

const pinia = createPinia()
pinia.use(piniaPersistence)
```

### TypeScript Support

```typescript
// types/store.ts
export interface Product {
  id: string
  name: string
  price: number
  category: string
  image: string
  description: string
}

export interface CartItem extends Product {
  quantity: number
}

export interface User {
  id: string
  email: string
  name: string
  role: 'user' | 'admin'
}

// stores/typed-store.ts
import { defineStore } from 'pinia'

export const useTypedStore = defineStore('typed', () => {
  const products = ref<Product[]>([])
  const cart = ref<CartItem[]>([])
  const user = ref<User | null>(null)

  // Type-safe getters
  const productById = computed(() => (id: string): Product | undefined => {
    return products.value.find(p => p.id === id)
  })

  // Type-safe actions
  async function fetchProducts(): Promise<Product[]> {
    const response = await fetch('/api/products')
    const data = await response.json()
    products.value = data
    return data
  }

  function addToCart(product: Product, quantity: number): void {
    const existing = cart.value.find(item => item.id === product.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      cart.value.push({ ...product, quantity })
    }
  }

  return {
    products: readonly(products) as DeepReadonly<Ref<Product[]>>,
    cart: readonly(cart) as DeepReadonly<Ref<CartItem[]>>,
    user: readonly(user) as DeepReadonly<Ref<User | null>>,
    productById,
    fetchProducts,
    addToCart
  }
})
```

## DevTools Integration

### Store Debugging

```typescript
// stores/debug-store.ts
import { defineStore } from 'pinia'

export const useDebugStore = defineStore('debug', () => {
  const state = ref({
    counter: 0,
    items: [] as string[]
  })

  // Custom action names for devtools
  function increment() {
    state.value.counter++
  }

  function decrement() {
    state.value.counter--
  }

  function addItem(item: string) {
    state.value.items.push(item)
  }

  // Subscribe to store changes
  if (process.env.NODE_ENV === 'development') {
    watch(state, (newState, oldState) => {
      console.log('Store changed:', { newState, oldState })
    }, { deep: true })
  }

  return {
    state: readonly(state),
    increment,
    decrement,
    addItem
  }
})
```

### Custom Actions Tracking

```typescript
// stores/tracked-store.ts
import { defineStore } from 'pinia'

export const useTrackedStore = defineStore('tracked', () => {
  const items = ref<string[]>([])
  const actionHistory = ref<Array<{ action: string; timestamp: number }>>([])

  function trackAction(actionName: string) {
    actionHistory.value.push({
      action: actionName,
      timestamp: Date.now()
    })
  }

  function addItem(item: string) {
    trackAction('addItem')
    items.value.push(item)
  }

  function removeItem(index: number) {
    trackAction('removeItem')
    items.value.splice(index, 1)
  }

  function clearItems() {
    trackAction('clearItems')
    items.value = []
  }

  return {
    items: readonly(items),
    actionHistory: readonly(actionHistory),
    addItem,
    removeItem,
    clearItems
  }
})
```

## Server-Side Rendering (SSR) with Pinia

### Hydration Pattern

```typescript
// stores/ssr-store.ts
export const useSSRStore = defineStore('ssr', () => {
  const data = ref<any>(null)
  const loading = ref(false)

  async function fetchData() {
    // Skip if already loaded (hydration)
    if (data.value) return data.value

    loading.value = true
    try {
      const response = await fetch('/api/data')
      data.value = await response.json()
    } finally {
      loading.value = false
    }
    return data.value
  }

  return {
    data: readonly(data),
    loading: readonly(loading),
    fetchData
  }
})

// Server-side (Nuxt)
export default defineNuxtPlugin(async (nuxtApp) => {
  const store = useSSRStore(nuxtApp.$pinia)

  // Prefetch data on server
  if (process.server) {
    await store.fetchData()
  }
})
```

## Best Practices

### 1. Store Design

- **One store per feature**: Keep stores focused and modular
- **Use Composition API**: More flexible and type-safe
- **Return readonly refs**: Prevent external mutations
- **Group related state**: Keep related data together

### 2. Actions

- **Async actions**: Always use async/await for API calls
- **Error handling**: Catch and store errors in state
- **Loading states**: Track loading for better UX
- **Side effects**: Keep all side effects in actions

### 3. Getters

- **Memoization**: Leverage computed properties for performance
- **Factory getters**: Use `(state) => (id) => ...` pattern for parameters
- **Derived state**: Compute values from state, don't duplicate
- **Type safety**: Always type getter return values

### 4. Performance

- **Shallow refs**: Use `shallowRef` for large objects
- **Selective reactivity**: Only make what's needed reactive
- **Batch updates**: Group multiple state changes
- **Lazy initialization**: Load data only when needed

### 5. Testing

```typescript
// stores/__tests__/cart.spec.ts
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from '../cart'

describe('Cart Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('adds items to cart', () => {
    const cart = useCartStore()

    cart.addItem({ id: '1', name: 'Product', price: 10, quantity: 1 })

    expect(cart.items).toHaveLength(1)
    expect(cart.total).toBe(10)
  })

  it('updates quantity for existing items', () => {
    const cart = useCartStore()

    cart.addItem({ id: '1', name: 'Product', price: 10, quantity: 1 })
    cart.addItem({ id: '1', name: 'Product', price: 10, quantity: 2 })

    expect(cart.items).toHaveLength(1)
    expect(cart.items[0].quantity).toBe(3)
    expect(cart.total).toBe(30)
  })

  it('removes items from cart', () => {
    const cart = useCartStore()

    cart.addItem({ id: '1', name: 'Product', price: 10, quantity: 1 })
    cart.removeItem('1')

    expect(cart.items).toHaveLength(0)
    expect(cart.total).toBe(0)
  })
})
```
