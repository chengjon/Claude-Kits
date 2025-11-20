# Pinia Store Patterns


## 📑 Table of Contents

- [Normalized State Structure](#normalized-state-structure)
- [State Persistence](#state-persistence)
- [Complex State with Subscriptions](#complex-state-with-subscriptions)
- [Type-Safe Store Pattern](#type-safe-store-pattern)
- [Discriminated Union State](#discriminated-union-state)

---
## Normalized State Structure

```typescript
// stores/products.ts - Normalized state for scalability
export const useProductStore = defineStore('products', () => {
  // Normalized structure
  const byId = ref<Record<string, Product>>({})
  const allIds = ref<string[]>([])

  // Getters
  const all = computed(() =>
    allIds.value.map(id => byId.value[id])
  )

  const byCategory = (categoryId: string) =>
    computed(() =>
      allIds.value
        .map(id => byId.value[id])
        .filter(p => p.categoryId === categoryId)
    )

  // Actions
  async function fetchProducts() {
    const products = await $fetch('/api/products')

    // Normalize
    products.forEach(product => {
      byId.value[product.id] = product
      if (!allIds.value.includes(product.id)) {
        allIds.value.push(product.id)
      }
    })
  }

  function getProduct(id: string) {
    return byId.value[id]
  }

  function updateProduct(id: string, updates: Partial<Product>) {
    if (byId.value[id]) {
      byId.value[id] = { ...byId.value[id], ...updates }
    }
  }

  return {
    byId: readonly(byId),
    all,
    getProduct,
    updateProduct,
    fetchProducts,
    byCategory
  }
})
```

## State Persistence

```typescript
// stores/preferences.ts - Persistent store
export const usePreferencesStore = defineStore(
  'preferences',
  () => {
    const theme = ref<'light' | 'dark'>('light')
    const language = ref<string>('en')
    const sidebarCollapsed = ref(false)

    const save = () => {
      localStorage.setItem('preferences', JSON.stringify({
        theme: theme.value,
        language: language.value,
        sidebarCollapsed: sidebarCollapsed.value
      }))
    }

    const load = () => {
      const stored = localStorage.getItem('preferences')
      if (stored) {
        const prefs = JSON.parse(stored)
        theme.value = prefs.theme
        language.value = prefs.language
        sidebarCollapsed.value = prefs.sidebarCollapsed
      }
    }

    watch(() => ({ theme: theme.value, language: language.value, sidebarCollapsed: sidebarCollapsed.value }),
      () => save(),
      { deep: true }
    )

    return {
      theme,
      language,
      sidebarCollapsed,
      save,
      load
    }
  },
  {
    persist: {
      enabled: true,
      strategies: [
        {
          key: 'preferences',
          storage: localStorage,
          paths: ['theme', 'language', 'sidebarCollapsed']
        }
      ]
    }
  }
)
```

## Complex State with Subscriptions

```typescript
// stores/notifications.ts - Event-driven state
export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])

  const add = (notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    const item = { ...notification, id }

    notifications.value.push(item)

    // Auto-remove after duration
    if (notification.duration) {
      setTimeout(() => {
        remove(id)
      }, notification.duration)
    }

    return id
  }

  const remove = (id: string) => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  // Subscribe to store changes
  const unsubscribe = useNotificationStore.$subscribe((mutation, state) => {
    console.log('Notifications changed:', mutation, state.notifications)
  }, { deep: true })

  return {
    notifications: readonly(notifications),
    add,
    remove,
    unsubscribe
  }
})
```

## Type-Safe Store Pattern

```typescript
// stores/typed-user.ts - Strict type safety
import { defineStore } from 'pinia'
import type { User, UserRole } from '~/types'

interface UserState {
  current: User | null
  isLoading: boolean
  error: Error | null
  lastFetch: number
}

export const useTypedUserStore = defineStore('typed-user', () => {
  const state = reactive<UserState>({
    current: null,
    isLoading: false,
    error: null,
    lastFetch: 0
  })

  // Type-safe getters
  const isAuthenticated = computed(() => state.current !== null)

  const canAccess = (role: UserRole) =>
    computed(() => state.current?.role === role || state.current?.role === 'admin')

  // Type-safe actions with proper return types
  async function fetchUser(id: string): Promise<User | null> {
    state.isLoading = true
    state.error = null

    try {
      const response = await $fetch<User>(`/api/users/${id}`)
      state.current = response
      state.lastFetch = Date.now()
      return response
    } catch (error) {
      state.error = error as Error
      return null
    } finally {
      state.isLoading = false
    }
  }

  return {
    state: readonly(state),
    isAuthenticated,
    canAccess,
    fetchUser
  }
})
```

## Discriminated Union State

```typescript
// stores/async-operation.ts
export type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error }

export const useAsyncStore = defineStore('async', () => {
  const state = ref<AsyncState<Product[]>>({ status: 'idle' })

  const data = computed(() =>
    state.value.status === 'success' ? state.value.data : null
  )

  const isLoading = computed(() => state.value.status === 'loading')

  const error = computed(() =>
    state.value.status === 'error' ? state.value.error : null
  )

  async function load() {
    state.value = { status: 'loading' }

    try {
      const products = await $fetch<Product[]>('/api/products')
      state.value = { status: 'success', data: products }
    } catch (error) {
      state.value = { status: 'error', error: error as Error }
    }
  }

  return {
    state: readonly(state),
    data,
    isLoading,
    error,
    load
  }
})
```
