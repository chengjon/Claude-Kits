# Performance Optimization & Vue Ecosystem Integration

Complete guide to Vue performance optimization, bundle optimization, and ecosystem integration.

## 📑 Table of Contents

- [Performance Optimization](#performance-optimization)
  - [Code Splitting & Lazy Loading](#code-splitting--lazy-loading)
  - [Virtual Scrolling for Large Lists](#virtual-scrolling-for-large-lists)
  - [Memoization and v-memo](#memoization-and-v-memo)
  - [Bundle Optimization](#bundle-optimization)
  - [Image Optimization](#image-optimization)
- [Vue Router 4 Advanced Patterns](#vue-router-4-advanced-patterns)
  - [Advanced Routing Configuration](#advanced-routing-configuration)
  - [Route Guards and Middleware](#route-guards-and-middleware)
- [VueUse Utilities Integration](#vueuse-utilities-integration)
  - [Essential Composables](#essential-composables)
  - [Custom VueUse Composables](#custom-vueuse-composables)
- [Form Libraries Integration](#form-libraries-integration)
  - [VeeValidate Integration](#veevalidate-integration)
  - [FormKit Integration](#formkit-integration)
- [UI Framework Integration](#ui-framework-integration)
  - [Vuetify Integration](#vuetify-integration)
  - [Quasar Integration](#quasar-integration)
- [Testing with Vitest](#testing-with-vitest)
  - [Component Testing](#component-testing)
  - [Composables Testing](#composables-testing)
- [Best Practices](#best-practices)
  - [Performance](#1-performance)
  - [Routing](#2-routing)
  - [Ecosystem Integration](#3-ecosystem-integration)
  - [Testing](#4-testing)

---

## Performance Optimization

### Code Splitting & Lazy Loading

```typescript
// Auto import composables
export const autoImport = {
  from: 'composables',
  imports: ['useFetch', 'useCart', 'useAuth']
}

// Lazy load components
const HeavyComponent = defineAsyncComponent(() =>
  import('~/components/Heavy.vue')
)

// With loading and error states
const AsyncComponent = defineAsyncComponent({
  loader: () => import('~/components/Heavy.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 10000
})

// Route-based code splitting
const routes = [
  {
    path: '/products',
    component: () => import('~/pages/products/index.vue')
  },
  {
    path: '/admin',
    component: () => import('~/pages/admin/index.vue')
  }
]
```

### Virtual Scrolling for Large Lists

```vue
<script setup lang="ts">
import { useVirtualList } from '@vueuse/core'

const allItems = ref(Array.from({ length: 10000 }, (_, i) => ({
  id: i,
  name: `Item ${i}`,
  description: `Description for item ${i}`
})))

const { list, containerProps, wrapperProps } = useVirtualList(
  allItems,
  {
    itemHeight: 60,
    overscan: 10
  }
)
</script>

<template>
  <div v-bind="containerProps" class="h-96 overflow-auto">
    <div v-bind="wrapperProps">
      <div
        v-for="{ data, index } in list"
        :key="index"
        class="py-2 px-4 border-b"
      >
        <h3>{{ data.name }}</h3>
        <p class="text-sm text-gray-600">{{ data.description }}</p>
      </div>
    </div>
  </div>
</template>
```

### Memoization and v-memo

```vue
<script setup lang="ts">
const items = ref([
  { id: 1, name: 'Item 1', price: 10 },
  { id: 2, name: 'Item 2', price: 20 },
  { id: 3, name: 'Item 3', price: 30 }
])

const selectedId = ref(1)
</script>

<template>
  <!-- v-memo - only re-render when dependencies change -->
  <div
    v-for="item in items"
    :key="item.id"
    v-memo="[item.id === selectedId]"
    class="item"
  >
    <h3>{{ item.name }}</h3>
    <span>${{ item.price }}</span>
  </div>

  <!-- v-once - render only once, never update -->
  <div v-once>
    <h1>Static Header</h1>
    <p>This content never changes</p>
  </div>
</template>
```

### Bundle Optimization

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['@headlessui/vue', '@heroicons/vue'],

          // Feature-based chunks
          'admin': ['./src/features/admin'],
          'products': ['./src/features/products']
        }
      }
    },
    // Tree-shaking optimization
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  }
})

// nuxt.config.ts
export default defineNuxtConfig({
  build: {
    analyze: true, // Bundle analyzer
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendor',
            priority: 10
          }
        }
      }
    }
  },

  // Tree-shaking
  experimental: {
    treeshakeClientOnly: true
  }
})
```

### Image Optimization

```vue
<template>
  <!-- Nuxt Image -->
  <NuxtImg
    src="/images/product.jpg"
    alt="Product"
    width="800"
    height="600"
    loading="lazy"
    format="webp"
    quality="80"
  />

  <!-- Picture element with multiple formats -->
  <NuxtPicture
    src="/images/hero.jpg"
    :img-attrs="{ class: 'w-full' }"
    :formats="['webp', 'avif']"
    sizes="sm:100vw md:50vw lg:400px"
  />

  <!-- Lazy loading with intersection observer -->
  <img
    v-lazy="imageUrl"
    alt="Product"
    class="lazy-image"
  />
</template>

<script setup lang="ts">
// Custom lazy loading composable
export function useLazyImage(src: Ref<string>) {
  const imageRef = ref<HTMLImageElement>()
  const loaded = ref(false)

  onMounted(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && imageRef.value) {
          imageRef.value.src = src.value
          loaded.value = true
          observer.disconnect()
        }
      })
    })

    if (imageRef.value) {
      observer.observe(imageRef.value)
    }
  })

  return { imageRef, loaded }
}
</script>
```

## Vue Router 4 Advanced Patterns

### Advanced Routing Configuration

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/products',
      component: () => import('~/pages/products/index.vue'),
      children: [
        {
          path: ':id',
          component: () => import('~/pages/products/[id].vue'),
          meta: { requiresAuth: true }
        }
      ]
    },
    {
      path: '/admin',
      component: () => import('~/layouts/admin.vue'),
      beforeEnter: (to, from) => {
        const { isAdmin } = useAuth()
        if (!isAdmin.value) {
          return { name: 'home' }
        }
      },
      children: [
        {
          path: 'dashboard',
          component: () => import('~/pages/admin/dashboard.vue')
        },
        {
          path: 'users',
          component: () => import('~/pages/admin/users.vue')
        }
      ]
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  }
})

// Global navigation guards
router.beforeEach(async (to, from) => {
  const { isAuthenticated } = useAuth()

  // Authentication check
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // Progress bar
  const progressBar = useProgressBar()
  progressBar.start()
})

router.afterEach(() => {
  const progressBar = useProgressBar()
  progressBar.done()
})

export default router
```

### Route Guards and Middleware

```typescript
// middleware/auth.ts
export function authGuard(to: RouteLocationNormalized) {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated.value) {
    return {
      name: 'login',
      query: { redirect: to.fullPath }
    }
  }
}

// middleware/admin.ts
export function adminGuard(to: RouteLocationNormalized) {
  const { isAdmin } = useAuth()

  if (!isAdmin.value) {
    return { name: 'forbidden' }
  }
}

// Route with middleware
const routes = [
  {
    path: '/admin/dashboard',
    component: () => import('~/pages/admin/dashboard.vue'),
    beforeEnter: [authGuard, adminGuard]
  }
]
```

## VueUse Utilities Integration

### Essential Composables

```typescript
import {
  useLocalStorage,
  useDark,
  useToggle,
  useMouse,
  useWindowSize,
  useEventListener,
  useDebounce,
  useThrottle,
  useAsyncState
} from '@vueuse/core'

// Reactive localStorage
const state = useLocalStorage('app-state', {
  theme: 'light',
  sidebar: 'open'
})

// Dark mode toggle
const isDark = useDark()
const toggleDark = useToggle(isDark)

// Mouse position
const { x, y } = useMouse()

// Window size
const { width, height } = useWindowSize()

// Event listener (auto cleanup)
useEventListener(window, 'resize', () => {
  console.log('Window resized')
})

// Debounced value
const input = ref('')
const debouncedInput = useDebounce(input, 500)

// Throttled function
const handleScroll = useThrottle(() => {
  console.log('Scrolled')
}, 200)

// Async state management
const { state, isReady, isLoading, error } = useAsyncState(
  fetch('/api/data').then(r => r.json()),
  null
)
```

### Custom VueUse Composables

```typescript
// composables/useInfiniteScroll.ts
import { useIntersectionObserver } from '@vueuse/core'

export function useInfiniteScroll(
  callback: () => void,
  options: { distance?: number } = {}
) {
  const { distance = 100 } = options
  const target = ref<HTMLElement>()

  const { stop } = useIntersectionObserver(
    target,
    ([{ isIntersecting }]) => {
      if (isIntersecting) {
        callback()
      }
    },
    {
      rootMargin: `${distance}px`
    }
  )

  return {
    target,
    stop
  }
}

// Usage
const { target, stop } = useInfiniteScroll(() => {
  loadMore()
})
```

## Form Libraries Integration

### VeeValidate Integration

```vue
<script setup lang="ts">
import { useForm, useField } from 'vee-validate'
import * as yup from 'yup'

const schema = yup.object({
  email: yup.string().email().required(),
  password: yup.string().min(8).required(),
  confirmPassword: yup.string()
    .oneOf([yup.ref('password')], 'Passwords must match')
    .required()
})

const { handleSubmit, errors, isSubmitting } = useForm({
  validationSchema: schema
})

const { value: email } = useField('email')
const { value: password } = useField('password')
const { value: confirmPassword } = useField('confirmPassword')

const onSubmit = handleSubmit(async (values) => {
  await registerUser(values)
})
</script>

<template>
  <form @submit="onSubmit">
    <div>
      <label>Email</label>
      <input v-model="email" type="email" />
      <span class="error">{{ errors.email }}</span>
    </div>

    <div>
      <label>Password</label>
      <input v-model="password" type="password" />
      <span class="error">{{ errors.password }}</span>
    </div>

    <div>
      <label>Confirm Password</label>
      <input v-model="confirmPassword" type="password" />
      <span class="error">{{ errors.confirmPassword }}</span>
    </div>

    <button :disabled="isSubmitting" type="submit">
      {{ isSubmitting ? 'Submitting...' : 'Register' }}
    </button>
  </form>
</template>
```

### FormKit Integration

```vue
<script setup lang="ts">
import { FormKit } from '@formkit/vue'

const submitForm = async (data: any) => {
  console.log('Form data:', data)
  await registerUser(data)
}
</script>

<template>
  <FormKit
    type="form"
    @submit="submitForm"
    :actions="false"
  >
    <FormKit
      type="email"
      name="email"
      label="Email"
      validation="required|email"
    />

    <FormKit
      type="password"
      name="password"
      label="Password"
      validation="required|length:8"
    />

    <FormKit
      type="password"
      name="password_confirm"
      label="Confirm Password"
      validation="required|confirm"
    />

    <FormKit type="submit">Register</FormKit>
  </FormKit>
</template>
```

## UI Framework Integration

### Vuetify Integration

```typescript
// plugins/vuetify.ts
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
          accent: '#82B1FF'
        }
      }
    }
  }
})

export default vuetify

// main.ts
import vuetify from './plugins/vuetify'

app.use(vuetify)
```

### Quasar Integration

```typescript
// quasar.config.js
module.exports = {
  framework: {
    plugins: ['Notify', 'Dialog', 'Loading'],
    config: {
      brand: {
        primary: '#1976D2',
        secondary: '#26A69A'
      }
    }
  },
  boot: ['axios', 'i18n']
}

// Usage
import { useQuasar } from 'quasar'

const $q = useQuasar()

$q.notify({
  message: 'Success!',
  color: 'positive'
})

$q.dialog({
  title: 'Confirm',
  message: 'Are you sure?'
}).onOk(() => {
  // Handle confirmation
})
```

## Testing with Vitest

### Component Testing

```typescript
// components/__tests__/ProductCard.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductCard from '../ProductCard.vue'

describe('ProductCard', () => {
  const product = {
    id: '1',
    name: 'Test Product',
    price: 99.99,
    image: '/test.jpg',
    description: 'Test description'
  }

  it('renders product information', () => {
    const wrapper = mount(ProductCard, {
      props: { product }
    })

    expect(wrapper.text()).toContain('Test Product')
    expect(wrapper.text()).toContain('99.99')
  })

  it('emits add-to-cart event', async () => {
    const wrapper = mount(ProductCard, {
      props: { product }
    })

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('add-to-cart')).toBeTruthy()
    expect(wrapper.emitted('add-to-cart')?.[0]).toEqual([product])
  })

  it('updates quantity', async () => {
    const wrapper = mount(ProductCard, {
      props: { product }
    })

    const input = wrapper.find('input[type="number"]')
    await input.setValue(5)

    expect(wrapper.vm.quantity).toBe(5)
  })
})
```

### Composables Testing

```typescript
// composables/__tests__/useCart.spec.ts
import { describe, it, expect } from 'vitest'
import { useCart } from '../useCart'

describe('useCart', () => {
  it('adds items to cart', () => {
    const { items, addItem, total } = useCart()

    addItem({ id: '1', name: 'Product', price: 10 }, 2)

    expect(items.value).toHaveLength(1)
    expect(total.value).toBe(20)
  })

  it('updates quantity for existing items', () => {
    const { items, addItem } = useCart()

    addItem({ id: '1', name: 'Product', price: 10 }, 1)
    addItem({ id: '1', name: 'Product', price: 10 }, 2)

    expect(items.value).toHaveLength(1)
    expect(items.value[0].quantity).toBe(3)
  })

  it('removes items from cart', () => {
    const { items, addItem, removeItem } = useCart()

    addItem({ id: '1', name: 'Product', price: 10 }, 1)
    removeItem('1')

    expect(items.value).toHaveLength(0)
  })

  it('calculates total correctly', () => {
    const { total, addItem } = useCart()

    addItem({ id: '1', name: 'Product 1', price: 10 }, 2)
    addItem({ id: '2', name: 'Product 2', price: 15 }, 1)

    expect(total.value).toBe(35)
  })
})
```

## Best Practices

### 1. Performance

- **Lazy load heavy components**: Use `defineAsyncComponent`
- **Virtual scrolling for lists**: Use VueUse or custom implementation
- **Memoize expensive computations**: Use `computed` and `v-memo`
- **Optimize bundle size**: Code splitting and tree-shaking
- **Image optimization**: Use modern formats (WebP, AVIF)

### 2. Routing

- **Use route-level code splitting**: Lazy load route components
- **Implement proper guards**: Authentication, authorization checks
- **Handle navigation errors**: Proper error handling and fallbacks
- **Optimize scroll behavior**: Save and restore scroll positions

### 3. Ecosystem Integration

- **Use VueUse for common patterns**: Don't reinvent the wheel
- **Integrate form libraries**: VeeValidate or FormKit for complex forms
- **Choose UI frameworks wisely**: Match project requirements
- **Test thoroughly**: Unit tests for composables, component tests

### 4. Testing

- **Write unit tests for composables**: Test business logic in isolation
- **Component tests for UI**: Test user interactions and rendering
- **Mock external dependencies**: API calls, router, stores
- **Aim for >85% coverage**: Balance between coverage and maintainability
