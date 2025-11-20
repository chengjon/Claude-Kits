# Composables, Middleware & Plugins

Complete guide to Nuxt 3's composables system, route middleware, and plugin architecture.


## 📑 Table of Contents

- [Composables](#composables)
  - [Shopping Cart Composable](#shopping-cart-composable)
  - [Data Fetching Composable](#data-fetching-composable)
  - [Authentication Composable](#authentication-composable)
  - [Form Validation Composable](#form-validation-composable)
- [Route Middleware](#route-middleware)
  - [Authentication Middleware](#authentication-middleware)
  - [Admin Access Middleware](#admin-access-middleware)
  - [Role-Based Middleware](#role-based-middleware)
  - [Loading State Middleware](#loading-state-middleware)
  - [Analytics Middleware](#analytics-middleware)
- [Plugins](#plugins)
  - [Error Tracking Plugin](#error-tracking-plugin)
  - [API Plugin](#api-plugin)
  - [Toast Notification Plugin](#toast-notification-plugin)
  - [Local Storage Plugin](#local-storage-plugin)
- [Best Practices](#best-practices)
  - [Composables](#composables)
  - [Middleware](#middleware)
  - [Plugins](#plugins)
- [Common Patterns](#common-patterns)
  - [Auto-Fetching Composable](#auto-fetching-composable)
  - [Debounced Search Composable](#debounced-search-composable)

---
## Composables

### Shopping Cart Composable

```typescript
// composables/useCart.ts
export const useCart = () => {
  const items = useState<CartItem[]>('cart.items', () => [])

  const itemCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const total = computed(() =>
    items.value.reduce((sum, item) =>
      sum + (item.product.price * item.quantity), 0
    )
  )

  async function addItem(item: CartItem) {
    const existingIndex = items.value.findIndex(
      i => i.product.id === item.product.id
    )

    if (existingIndex > -1) {
      items.value[existingIndex].quantity += item.quantity
    } else {
      items.value.push(item)
    }

    // Persist to server
    if (useAuth().isAuthenticated.value) {
      await $fetch('/api/cart', {
        method: 'POST',
        body: { items: items.value }
      })
    }
  }

  function removeItem(productId: string) {
    items.value = items.value.filter(
      item => item.product.id !== productId
    )
  }

  function clearCart() {
    items.value = []
  }

  // Sync with server on auth change
  watch(() => useAuth().isAuthenticated, async (isAuth) => {
    if (isAuth) {
      const { data } = await $fetch('/api/cart')
      if (data?.items) {
        items.value = data.items
      }
    }
  })

  return {
    items: readonly(items),
    itemCount: readonly(itemCount),
    total: readonly(total),
    addItem,
    removeItem,
    clearCart
  }
}
```

### Data Fetching Composable

```typescript
// composables/useApi.ts
export const useApi = () => {
  const config = useRuntimeConfig()

  const api = $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ request, options }) {
      // Add auth header
      const { token } = useAuth()
      if (token.value) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token.value}`
        }
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        // Handle unauthorized
        return navigateTo('/login')
      }
    }
  })

  return {
    get: (url: string, options?: any) => api(url, { ...options, method: 'GET' }),
    post: (url: string, body?: any, options?: any) => api(url, { ...options, method: 'POST', body }),
    put: (url: string, body?: any, options?: any) => api(url, { ...options, method: 'PUT', body }),
    delete: (url: string, options?: any) => api(url, { ...options, method: 'DELETE' }),
  }
}
```

### Authentication Composable

```typescript
// composables/useAuth.ts
export const useAuth = () => {
  const user = useState<User | null>('auth.user', () => null)
  const token = useState<string | null>('auth.token', () => null)

  const isAuthenticated = computed(() => !!user.value)

  async function login(credentials: { email: string; password: string }) {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: credentials
    })

    user.value = response.user
    token.value = response.token
  }

  async function logout() {
    await $fetch('/api/auth/logout', { method: 'POST' })
    user.value = null
    token.value = null
    await navigateTo('/login')
  }

  async function fetchUser() {
    try {
      const response = await $fetch('/api/auth/me')
      user.value = response.user
    } catch (error) {
      user.value = null
      token.value = null
    }
  }

  function hasPermission(permission: string): boolean {
    return user.value?.permissions?.includes(permission) ?? false
  }

  function hasRole(role: string): boolean {
    return user.value?.roles?.includes(role) ?? false
  }

  return {
    user: readonly(user),
    token: readonly(token),
    isAuthenticated: readonly(isAuthenticated),
    login,
    logout,
    fetchUser,
    hasPermission,
    hasRole
  }
}
```

### Form Validation Composable

```typescript
// composables/useFormValidation.ts
import { z } from 'zod'

export const useFormValidation = <T extends z.ZodSchema>(schema: T) => {
  const errors = ref<Record<string, string[]>>({})
  const touched = ref<Record<string, boolean>>({})
  const isValid = ref(false)

  function validate(data: z.infer<T>) {
    const result = schema.safeParse(data)

    if (result.success) {
      errors.value = {}
      isValid.value = true
      return { success: true, data: result.data }
    }

    errors.value = result.error.flatten().fieldErrors as Record<string, string[]>
    isValid.value = false
    return { success: false, errors: errors.value }
  }

  function validateField(field: string, value: any) {
    const fieldSchema = schema.shape[field]
    if (!fieldSchema) return

    const result = fieldSchema.safeParse(value)
    touched.value[field] = true

    if (result.success) {
      delete errors.value[field]
    } else {
      errors.value[field] = result.error.errors.map(e => e.message)
    }
  }

  function clearErrors() {
    errors.value = {}
    touched.value = {}
    isValid.value = false
  }

  function getFieldError(field: string): string | null {
    return errors.value[field]?.[0] ?? null
  }

  return {
    errors: readonly(errors),
    touched: readonly(touched),
    isValid: readonly(isValid),
    validate,
    validateField,
    clearErrors,
    getFieldError
  }
}
```

## Route Middleware

### Authentication Middleware

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()

  // Protected routes
  const protectedRoutes = ['/dashboard', '/profile', '/admin']
  const isProtectedRoute = protectedRoutes.some(route =>
    to.path.startsWith(route)
  )

  if (isProtectedRoute && !isAuthenticated.value) {
    return navigateTo(`/login?redirect=${to.path}`)
  }
})
```

### Admin Access Middleware

```typescript
// middleware/admin.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { user, hasPermission } = useAuth()

  if (!user.value || !hasPermission('admin.access')) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied'
    })
  }
})
```

### Role-Based Middleware

```typescript
// middleware/role.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { user, hasRole } = useAuth()
  const requiredRole = to.meta.role as string

  if (!requiredRole) return

  if (!user.value || !hasRole(requiredRole)) {
    return navigateTo('/unauthorized')
  }
})

// Usage in page:
// pages/admin/users.vue
definePageMeta({
  middleware: 'role',
  role: 'admin'
})
```

### Loading State Middleware

```typescript
// middleware/loading.global.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const loading = useState('app.loading', () => false)

  if (process.client) {
    loading.value = true

    // Clear loading state after navigation
    const stopLoading = () => {
      loading.value = false
    }

    to.meta.loadingHandler = stopLoading
  }
})
```

### Analytics Middleware

```typescript
// middleware/analytics.global.ts
export default defineNuxtRouteMiddleware((to, from) => {
  if (process.client && window.gtag) {
    window.gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: to.fullPath,
      page_title: to.meta.title || to.name
    })
  }
})
```

## Plugins

### Error Tracking Plugin

```typescript
// plugins/error-tracking.client.ts
export default defineNuxtPlugin((nuxtApp) => {
  // Only in production
  if (process.env.NODE_ENV !== 'production') return

  // Initialize error tracking (e.g., Sentry)
  const { $sentry } = nuxtApp

  // Vue errors
  nuxtApp.vueApp.config.errorHandler = (error, instance, info) => {
    console.error('Vue error:', error)
    $sentry.captureException(error, {
      extra: { info }
    })
  }

  // Unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason)
    $sentry.captureException(event.reason)
  })
})
```

### API Plugin

```typescript
// plugins/api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const api = $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ request, options }) {
      const { token } = useAuth()
      if (token.value) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token.value}`
        }
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        navigateTo('/login')
      }
    }
  })

  return {
    provide: {
      api
    }
  }
})

// Usage in components:
const { $api } = useNuxtApp()
const data = await $api('/products')
```

### Toast Notification Plugin

```typescript
// plugins/toast.ts
import { reactive } from 'vue'

interface Toast {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
}

export default defineNuxtPlugin(() => {
  const toasts = reactive<Toast[]>([])

  function showToast(toast: Omit<Toast, 'id'>) {
    const id = Math.random().toString(36).substring(7)
    const newToast = { ...toast, id }

    toasts.push(newToast)

    if (toast.duration !== 0) {
      setTimeout(() => {
        removeToast(id)
      }, toast.duration || 3000)
    }
  }

  function removeToast(id: string) {
    const index = toasts.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.splice(index, 1)
    }
  }

  return {
    provide: {
      toast: {
        success: (message: string, duration?: number) =>
          showToast({ type: 'success', message, duration }),
        error: (message: string, duration?: number) =>
          showToast({ type: 'error', message, duration }),
        info: (message: string, duration?: number) =>
          showToast({ type: 'info', message, duration }),
        warning: (message: string, duration?: number) =>
          showToast({ type: 'warning', message, duration }),
        remove: removeToast,
        toasts: readonly(toasts)
      }
    }
  }
})
```

### Local Storage Plugin

```typescript
// plugins/local-storage.client.ts
export default defineNuxtPlugin(() => {
  const get = <T>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue ?? null
    } catch {
      return defaultValue ?? null
    }
  }

  const set = <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
    }
  }

  const remove = (key: string): void => {
    localStorage.removeItem(key)
  }

  const clear = (): void => {
    localStorage.clear()
  }

  return {
    provide: {
      storage: {
        get,
        set,
        remove,
        clear
      }
    }
  }
})
```

## Best Practices

### Composables
1. **Naming Convention**: Always prefix with `use` (e.g., `useAuth`, `useCart`)
2. **State Management**: Use `useState` for shared state across components
3. **Reactivity**: Return readonly refs for computed values
4. **SSR Compatibility**: Ensure composables work on both server and client
5. **Type Safety**: Use TypeScript for better type inference

### Middleware
1. **Global Middleware**: Use `.global.ts` suffix for automatic application
2. **Order Matters**: Global middleware runs before route-specific middleware
3. **Navigation Guards**: Use `navigateTo()` or return values to control navigation
4. **Meta Properties**: Use route meta for configuration (roles, permissions)
5. **Performance**: Keep middleware lightweight

### Plugins
1. **Lifecycle**: Use `.client.ts` or `.server.ts` for specific environments
2. **Provide Pattern**: Use `provide` to make utilities available globally
3. **Dependencies**: Handle plugin dependencies properly
4. **Error Handling**: Always handle errors gracefully
5. **Type Safety**: Define proper TypeScript types for provided values

## Common Patterns

### Auto-Fetching Composable

```typescript
// composables/useAsyncData.ts
export const useAsyncData = <T>(
  key: string,
  fetcher: () => Promise<T>,
  options?: { immediate?: boolean; watch?: Ref[] }
) => {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function refresh() {
    loading.value = true
    error.value = null

    try {
      data.value = await fetcher()
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  if (options?.immediate !== false) {
    refresh()
  }

  if (options?.watch) {
    watch(options.watch, refresh)
  }

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    refresh
  }
}
```

### Debounced Search Composable

```typescript
// composables/useSearch.ts
export const useSearch = <T>(
  searchFn: (query: string) => Promise<T[]>,
  options: { debounce?: number } = {}
) => {
  const query = ref('')
  const results = ref<T[]>([])
  const loading = ref(false)

  const debouncedSearch = useDebounceFn(async () => {
    if (!query.value.trim()) {
      results.value = []
      return
    }

    loading.value = true
    try {
      results.value = await searchFn(query.value)
    } finally {
      loading.value = false
    }
  }, options.debounce || 300)

  watch(query, debouncedSearch)

  return {
    query,
    results: readonly(results),
    loading: readonly(loading)
  }
}
```
