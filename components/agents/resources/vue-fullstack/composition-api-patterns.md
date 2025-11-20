# Vue 3 Composition API Mastery

Complete guide to Vue 3's Composition API including reactivity system, advanced patterns, and composables.


## 📑 Table of Contents

- [Reactivity System](#reactivity-system)
  - [Ref vs Reactive](#ref-vs-reactive)
  - [Advanced Reactivity Patterns](#advanced-reactivity-patterns)
  - [Lifecycle Hooks](#lifecycle-hooks)
- [Composables Pattern](#composables-pattern)
  - [Basic Composable - useFetch](#basic-composable---usefetch)
  - [Complex Composable - useCart](#complex-composable---usecart)
  - [Advanced Composable - useAsync](#advanced-composable---useasync)
  - [Composable - useInfiniteScroll](#composable---useinfinitescroll)
- [Provide/Inject Pattern](#provideinject-pattern)
  - [Theme Provider](#theme-provider)
- [Best Practices](#best-practices)
  - [1. Composition API Guidelines](#1-composition-api-guidelines)
  - [2. Composable Design](#2-composable-design)
  - [3. Performance Optimization](#3-performance-optimization)
  - [4. Common Pitfalls](#4-common-pitfalls)

---
## Reactivity System

### Ref vs Reactive

```typescript
import { ref, reactive, computed, watch, onMounted } from 'vue'

// Simple values -> ref
const count = ref(0)
const name = ref('John')

// Complex objects -> reactive (rarely needed with Composition API)
const user = reactive({
  id: 1,
  email: 'john@example.com',
  profile: { bio: '', avatar: '' }
})

// Computed properties (memoized)
const doubled = computed(() => count.value * 2)

const userSummary = computed(() =>
  `${user.id}: ${user.email}`
)

// Watchers - watch specific sources
watch(
  () => count.value,
  (newVal, oldVal) => {
    console.log(`count changed from ${oldVal} to ${newVal}`)
  }
)

// watchEffect - auto-track dependencies
watch(
  () => user.email,
  (newEmail) => {
    // Validate email
    validateEmail(newEmail)
  },
  { debounce: 500 }
)
```

### Advanced Reactivity Patterns

```typescript
// Shallow reactivity for performance
import { shallowRef, shallowReactive } from 'vue'

// Large object - only top level reactive
const state = shallowRef({
  nested: { deep: { value: 1 } }
})

// Force update when deep properties change
function updateNested() {
  state.value = { ...state.value }
}

// Custom reactivity
import { reactive, effect } from 'vue'

const effectScope = {
  counter: 0,
  increment() { this.counter++ }
}

const target = reactive(effectScope)

// Effect to track dependencies
effect(() => {
  console.log('Count is:', target.counter)
})

// Provide/Inject for cross-tree communication
const countKey = Symbol('count')

// Parent component
const count = ref(0)
provide(countKey, count)

// Child component (any nesting level)
const count = inject(countKey)
```

### Lifecycle Hooks

```typescript
import {
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
  onActivated,
  onDeactivated
} from 'vue'

// Setup function runs before component is created
// No access to `this`

onBeforeMount(() => {
  console.log('About to mount')
})

onMounted(() => {
  console.log('Component mounted')
  // DOM is available
  // Good for API calls, event listeners, third-party integrations
})

onBeforeUpdate(() => {
  console.log('Before DOM updates')
})

onUpdated(() => {
  console.log('Component updated')
  // Avoid state changes here (infinite loop risk)
})

onBeforeUnmount(() => {
  console.log('Before component unmounts')
  // Cleanup: remove listeners, timers
})

onUnmounted(() => {
  console.log('Component unmounted')
})

// For <keep-alive> components
onActivated(() => {
  console.log('Component activated')
})

onDeactivated(() => {
  console.log('Component deactivated')
})
```

## Composables Pattern

### Basic Composable - useFetch

```typescript
// composables/useFetch.ts
export function useFetch<T>(url: string) {
  const data = ref<T | null>(null)
  const loading = ref(true)
  const error = ref<Error | null>(null)

  const execute = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(url)
      data.value = await res.json()
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  onMounted(execute)

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    refetch: execute
  }
}

// Usage in component
const { data: products, loading, refetch } = useFetch<Product[]>('/api/products')
```

### Complex Composable - useCart

```typescript
// composables/useCart.ts
export function useCart() {
  const items = ref<CartItem[]>([])
  const isOpen = ref(false)

  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  const itemCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  function addItem(product: Product, quantity: number) {
    const existing = items.value.find(i => i.id === product.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({ ...product, quantity })
    }
  }

  function removeItem(productId: string) {
    items.value = items.value.filter(i => i.id !== productId)
  }

  function updateQuantity(productId: string, quantity: number) {
    const item = items.value.find(i => i.id === productId)
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

  return {
    items: readonly(items),
    total,
    itemCount,
    isOpen,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    toggleCart,
  }
}
```

### Advanced Composable - useAsync

```typescript
// composables/useAsync.ts
export function useAsync<T>(
  asyncFn: () => Promise<T>,
  options: {
    immediate?: boolean
    onSuccess?: (data: T) => void
    onError?: (error: Error) => void
  } = {}
) {
  const { immediate = true, onSuccess, onError } = options

  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const execute = async () => {
    loading.value = true
    error.value = null
    try {
      const result = await asyncFn()
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
      throw e
    } finally {
      loading.value = false
    }
  }

  if (immediate) {
    onMounted(execute)
  }

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    execute
  }
}

// Usage
const { data, loading, execute } = useAsync(
  () => fetch('/api/data').then(r => r.json()),
  {
    immediate: false,
    onSuccess: (data) => console.log('Success:', data),
    onError: (error) => console.error('Error:', error)
  }
)
```

### Composable - useInfiniteScroll

```typescript
// composables/useInfiniteScroll.ts
export function useInfiniteScroll<T>(
  fetchFn: (page: number) => Promise<T[]>
) {
  const items = ref<T[]>([])
  const page = ref(1)
  const loading = ref(false)
  const hasMore = ref(true)
  const error = ref<Error | null>(null)

  const loadMore = async () => {
    if (loading.value || !hasMore.value) return

    loading.value = true
    error.value = null
    try {
      const newItems = await fetchFn(page.value)
      if (newItems.length === 0) {
        hasMore.value = false
      } else {
        items.value.push(...newItems)
        page.value++
      }
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    items.value = []
    page.value = 1
    hasMore.value = true
    error.value = null
  }

  onMounted(loadMore)

  return {
    items: readonly(items),
    loading: readonly(loading),
    hasMore: readonly(hasMore),
    error: readonly(error),
    loadMore,
    reset
  }
}

// Usage
const { items, loading, hasMore, loadMore } = useInfiniteScroll(
  (page) => fetch(`/api/products?page=${page}`).then(r => r.json())
)
```

## Provide/Inject Pattern

### Theme Provider

```typescript
// composables/useTheme.ts
import { InjectionKey } from 'vue'

export interface Theme {
  colors: {
    primary: string
    secondary: string
    background: string
    text: string
  }
  spacing: {
    xs: string
    sm: string
    md: string
    lg: string
    xl: string
  }
}

export const ThemeKey: InjectionKey<Theme> = Symbol('theme')

// Provider (App.vue)
const theme: Theme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#10b981',
    background: '#ffffff',
    text: '#1f2937'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem'
  }
}

provide(ThemeKey, theme)

// Consumer (any child component)
const theme = inject(ThemeKey)
if (!theme) {
  throw new Error('Theme not provided')
}
```

## Best Practices

### 1. Composition API Guidelines

- **Use `ref` for primitives**: Numbers, strings, booleans
- **Use `reactive` for objects**: Only when you need to maintain reactivity after destructuring
- **Prefer `ref` over `reactive`**: More consistent, works with all value types
- **Use `computed` for derived state**: Memoized, only recalculates when dependencies change
- **Use `watch` for side effects**: API calls, localStorage updates, analytics

### 2. Composable Design

- **Single responsibility**: Each composable should do one thing well
- **Return readonly refs**: Prevent external mutations
- **Use TypeScript**: Proper typing for better DX
- **Handle cleanup**: Use `onUnmounted` for event listeners, timers
- **Make it testable**: Pure functions, mockable dependencies

### 3. Performance Optimization

- **Use `shallowRef` for large objects**: Only top-level reactivity
- **Debounce watchers**: Avoid excessive updates
- **Lazy initialization**: Create refs only when needed
- **Cleanup properly**: Remove listeners, clear timers in `onUnmounted`

### 4. Common Pitfalls

- **Forgetting `.value`**: Always access ref values with `.value`
- **Mutating reactive objects**: Use spread operator or `Object.assign` for immutable updates
- **Infinite watch loops**: Avoid changing watched values inside watch callback
- **Memory leaks**: Always cleanup in `onUnmounted`
