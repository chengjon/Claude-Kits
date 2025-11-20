# Scalable Component Architecture

Complete guide to Vue component design patterns, architecture, and enterprise patterns.


## 📑 Table of Contents

- [Component with Script Setup](#component-with-script-setup)
  - [Modern Component Structure](#modern-component-structure)
  - [Props and Emits Best Practices](#props-and-emits-best-practices)
- [Renderless Components (Logic Components)](#renderless-components-logic-components)
  - [Async Component Pattern](#async-component-pattern)
  - [Form Field Wrapper](#form-field-wrapper)
- [Slots and Dynamic Components](#slots-and-dynamic-components)
  - [Named Slots](#named-slots)
  - [Scoped Slots](#scoped-slots)
  - [Dynamic Components](#dynamic-components)
- [Enterprise Patterns](#enterprise-patterns)
  - [Micro-Frontend Architecture](#micro-frontend-architecture)
  - [Feature Module Pattern](#feature-module-pattern)
  - [Design System Integration](#design-system-integration)
  - [Plugin Architecture](#plugin-architecture)
- [Component Composition](#component-composition)
  - [Higher-Order Components](#higher-order-components)
  - [Component Mixins (Composition API)](#component-mixins-composition-api)
- [Best Practices](#best-practices)
  - [1. Component Design](#1-component-design)
  - [2. Props and Events](#2-props-and-events)
  - [3. Slots](#3-slots)
  - [4. Performance](#4-performance)

---
## Component with Script Setup

### Modern Component Structure

```vue
<script setup lang="ts">
import { ref, computed, defineProps, defineEmits } from 'vue'
import type { Product } from '~/types'

const props = defineProps<{
  product: Product
  isSelected?: boolean
}>()

const emit = defineEmits<{
  select: [product: Product]
  quantity: [amount: number]
}>()

const quantity = ref(1)
const isAdding = ref(false)

const totalPrice = computed(() =>
  props.product.price * quantity.value
)

async function handleAddToCart() {
  isAdding.value = true
  try {
    await addToCartAPI(props.product, quantity.value)
    emit('select', props.product)
    emit('quantity', quantity.value)
  } finally {
    isAdding.value = false
  }
}
</script>

<template>
  <div :class="{ 'border-blue-500': isSelected }" class="border rounded p-4">
    <h3 class="font-bold">{{ product.name }}</h3>
    <p class="text-gray-600 text-sm">{{ product.description }}</p>

    <div class="mt-4 flex items-center gap-2">
      <button
        @click="quantity > 1 && quantity--"
        :disabled="quantity <= 1"
      >
        -
      </button>
      <input v-model.number="quantity" type="number" min="1" class="w-12" />
      <button @click="quantity++">+</button>
    </div>

    <div class="mt-4 flex justify-between items-center">
      <span class="font-bold">${{ totalPrice }}</span>
      <button
        @click="handleAddToCart"
        :disabled="isAdding"
        class="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {{ isAdding ? 'Adding...' : 'Add to Cart' }}
      </button>
    </div>
  </div>
</template>
```

### Props and Emits Best Practices

```typescript
// Define props with TypeScript
interface Props {
  modelValue: string
  placeholder?: string
  disabled?: boolean
  maxLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Enter text...',
  disabled: false,
  maxLength: 255
})

// Define emits with TypeScript
interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'submit', value: string): void
  (e: 'focus'): void
  (e: 'blur'): void
}

const emit = defineEmits<Emits>()

// Usage
function handleInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  emit('update:modelValue', value)
}

function handleSubmit() {
  emit('submit', props.modelValue)
}
```

## Renderless Components (Logic Components)

### Async Component Pattern

```vue
<!-- components/AsyncRenderer.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  promise: Promise<any>
}>()

const slots = defineSlots<{
  default: (props: { data: any; loading: boolean; error: Error | null }) => any
  error: (props: { error: Error }) => any
  pending: () => any
}>()

const data = ref(null)
const loading = ref(true)
const error = ref<Error | null>(null)

onMounted(async () => {
  try {
    data.value = await props.promise
  } catch (e) {
    error.value = e as Error
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <template v-if="loading">
    <slot name="pending" />
  </template>
  <template v-else-if="error">
    <slot name="error" :error="error" />
  </template>
  <template v-else>
    <slot :data="data" :loading="loading" :error="error" />
  </template>
</template>

<!-- Usage -->
<AsyncRenderer :promise="fetchProducts()">
  <template #pending>
    <div>Loading products...</div>
  </template>

  <template #error="{ error }">
    <div class="text-red-600">Error: {{ error.message }}</div>
  </template>

  <template #default="{ data }">
    <ProductList :products="data" />
  </template>
</AsyncRenderer>
```

### Form Field Wrapper

```vue
<!-- components/FormField.vue -->
<script setup lang="ts">
const props = defineProps<{
  label: string
  error?: string
  required?: boolean
  hint?: string
}>()

const slots = defineSlots<{
  default: () => any
}>()
</script>

<template>
  <div class="mb-4">
    <label class="block text-sm font-medium mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <slot />

    <p v-if="hint && !error" class="text-gray-500 text-xs mt-1">
      {{ hint }}
    </p>

    <p v-if="error" class="text-red-600 text-xs mt-1">
      {{ error }}
    </p>
  </div>
</template>

<!-- Usage -->
<FormField
  label="Email"
  :error="errors.email"
  hint="We'll never share your email"
  required
>
  <input
    v-model="form.email"
    type="email"
    class="w-full border rounded px-3 py-2"
  />
</FormField>
```

## Slots and Dynamic Components

### Named Slots

```vue
<!-- components/Card.vue -->
<script setup lang="ts">
const slots = defineSlots<{
  header?: () => any
  default: () => any
  footer?: () => any
}>()
</script>

<template>
  <div class="card">
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>

    <div class="card-body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<!-- Usage -->
<Card>
  <template #header>
    <h2>Card Title</h2>
  </template>

  <p>Card content goes here</p>

  <template #footer>
    <button>Action</button>
  </template>
</Card>
```

### Scoped Slots

```vue
<!-- components/DataTable.vue -->
<script setup lang="ts">
const props = defineProps<{
  items: any[]
  columns: string[]
}>()

const slots = defineSlots<{
  default: (props: { item: any; index: number }) => any
  empty?: () => any
}>()
</script>

<template>
  <table>
    <thead>
      <tr>
        <th v-for="col in columns" :key="col">{{ col }}</th>
      </tr>
    </thead>
    <tbody>
      <template v-if="items.length > 0">
        <tr v-for="(item, index) in items" :key="index">
          <slot :item="item" :index="index" />
        </tr>
      </template>
      <template v-else>
        <tr>
          <td :colspan="columns.length">
            <slot name="empty">
              <div class="text-center text-gray-500">No data</div>
            </slot>
          </td>
        </tr>
      </template>
    </tbody>
  </table>
</template>

<!-- Usage -->
<DataTable :items="products" :columns="['Name', 'Price', 'Actions']">
  <template #default="{ item, index }">
    <td>{{ item.name }}</td>
    <td>${{ item.price }}</td>
    <td>
      <button @click="edit(item)">Edit</button>
    </td>
  </template>

  <template #empty>
    <div>No products found</div>
  </template>
</DataTable>
```

### Dynamic Components

```vue
<script setup lang="ts">
import { shallowRef } from 'vue'
import ComponentA from './ComponentA.vue'
import ComponentB from './ComponentB.vue'
import ComponentC from './ComponentC.vue'

const currentComponent = shallowRef(ComponentA)

const components = {
  a: ComponentA,
  b: ComponentB,
  c: ComponentC
}

function switchComponent(name: 'a' | 'b' | 'c') {
  currentComponent.value = components[name]
}
</script>

<template>
  <div>
    <button @click="switchComponent('a')">Component A</button>
    <button @click="switchComponent('b')">Component B</button>
    <button @click="switchComponent('c')">Component C</button>

    <KeepAlive>
      <component :is="currentComponent" />
    </KeepAlive>
  </div>
</template>
```

## Enterprise Patterns

### Micro-Frontend Architecture

```typescript
// Micro-frontend loader
export function loadMicroFrontend(name: string, container: string) {
  return defineAsyncComponent({
    loader: async () => {
      const module = await import(`@micro-frontends/${name}`)
      return module.default
    },
    loadingComponent: LoadingSpinner,
    errorComponent: ErrorDisplay,
    delay: 200,
    timeout: 10000
  })
}

// Usage in parent app
const ProductCatalog = loadMicroFrontend('product-catalog', '#product-catalog-container')
const ShoppingCart = loadMicroFrontend('shopping-cart', '#cart-container')

// Parent component
<template>
  <div id="app">
    <Suspense>
      <template #default>
        <ProductCatalog />
      </template>
      <template #fallback>
        <LoadingSpinner />
      </template>
    </Suspense>

    <Suspense>
      <template #default>
        <ShoppingCart />
      </template>
      <template #fallback>
        <LoadingSpinner />
      </template>
    </Suspense>
  </div>
</template>
```

### Feature Module Pattern

```typescript
// features/products/index.ts
import { RouteRecordRaw } from 'vue-router'
import { Store } from 'pinia'

export interface FeatureModule {
  routes: RouteRecordRaw[]
  store?: Store
  components?: Record<string, any>
}

export const productsModule: FeatureModule = {
  routes: [
    {
      path: '/products',
      component: () => import('./pages/ProductList.vue'),
      children: [
        {
          path: ':id',
          component: () => import('./pages/ProductDetail.vue')
        }
      ]
    }
  ],
  store: useProductsStore,
  components: {
    ProductCard: () => import('./components/ProductCard.vue'),
    ProductFilter: () => import('./components/ProductFilter.vue')
  }
}

// app.ts - Register feature modules
import { productsModule } from './features/products'
import { cartModule } from './features/cart'

const featureModules = [productsModule, cartModule]

featureModules.forEach(module => {
  router.addRoute(module.routes)
  // Register components globally if needed
  if (module.components) {
    Object.entries(module.components).forEach(([name, component]) => {
      app.component(name, component)
    })
  }
})
```

### Design System Integration

```typescript
// Design system composable
export function useDesignSystem() {
  const theme = useTheme()
  const tokens = computed(() => ({
    colors: theme.value.colors,
    spacing: theme.value.spacing,
    typography: theme.value.typography
  }))

  function getColor(name: string) {
    return tokens.value.colors[name] || '#000000'
  }

  function getSpacing(size: 'xs' | 'sm' | 'md' | 'lg' | 'xl') {
    return tokens.value.spacing[size]
  }

  function getTypography(variant: 'h1' | 'h2' | 'body' | 'caption') {
    return tokens.value.typography[variant]
  }

  return {
    tokens,
    getColor,
    getSpacing,
    getTypography
  }
}

// Component using design system
<script setup lang="ts">
const { getColor, getSpacing } = useDesignSystem()

const buttonStyle = computed(() => ({
  backgroundColor: getColor('primary'),
  padding: `${getSpacing('sm')} ${getSpacing('md')}`,
  borderRadius: getSpacing('xs')
}))
</script>

<template>
  <button :style="buttonStyle">
    <slot />
  </button>
</template>
```

### Plugin Architecture

```typescript
// Plugin system
export interface VuePlugin {
  install(app: App, options?: any): void
}

// Example plugin - Analytics
export const analyticsPlugin: VuePlugin = {
  install(app, options) {
    const analytics = createAnalytics(options)

    app.config.globalProperties.$analytics = analytics
    app.provide('analytics', analytics)

    // Track page views
    if (app.config.globalProperties.$router) {
      app.config.globalProperties.$router.afterEach((to) => {
        analytics.pageView(to.path)
      })
    }
  }
}

// Example plugin - Toast notifications
export const toastPlugin: VuePlugin = {
  install(app, options) {
    const toast = {
      success: (message: string) => {
        // Implementation
      },
      error: (message: string) => {
        // Implementation
      },
      info: (message: string) => {
        // Implementation
      }
    }

    app.config.globalProperties.$toast = toast
    app.provide('toast', toast)
  }
}

// Usage
const app = createApp(App)
app.use(analyticsPlugin, { apiKey: 'xxx' })
app.use(toastPlugin)
```

## Component Composition

### Higher-Order Components

```typescript
// withLoading.ts
export function withLoading<T extends Record<string, any>>(
  Component: Component<T>
) {
  return defineComponent({
    name: `WithLoading${Component.name}`,
    props: {
      loading: Boolean,
      ...Component.props
    },
    setup(props, { slots }) {
      return () => {
        if (props.loading) {
          return h('div', 'Loading...')
        }
        return h(Component, props, slots)
      }
    }
  })
}

// Usage
const ProductListWithLoading = withLoading(ProductList)
```

### Component Mixins (Composition API)

```typescript
// composables/useValidation.ts
export function useValidation() {
  const errors = ref<Record<string, string>>({})

  function validate(rules: Record<string, (value: any) => boolean | string>) {
    errors.value = {}
    let isValid = true

    Object.entries(rules).forEach(([field, rule]) => {
      const result = rule(field)
      if (result !== true) {
        errors.value[field] = typeof result === 'string' ? result : 'Invalid'
        isValid = false
      }
    })

    return isValid
  }

  function clearErrors() {
    errors.value = {}
  }

  return {
    errors: readonly(errors),
    validate,
    clearErrors
  }
}

// Usage in component
const { errors, validate } = useValidation()

function handleSubmit() {
  const isValid = validate({
    email: (value) => /\S+@\S+\.\S+/.test(value) || 'Invalid email',
    password: (value) => value.length >= 8 || 'Password too short'
  })

  if (isValid) {
    // Submit form
  }
}
```

## Best Practices

### 1. Component Design

- **Single Responsibility**: Each component should do one thing well
- **Keep components < 200 LOC**: Extract complex logic to composables
- **Use TypeScript**: Proper typing for props, emits, and slots
- **Validate props**: Use prop validators for complex types
- **Document components**: Add JSDoc comments for public APIs

### 2. Props and Events

- **Use kebab-case for event names**: `@user-updated` not `@userUpdated`
- **Emit from child, handle in parent**: Unidirectional data flow
- **Avoid prop mutations**: Emit events instead
- **Use `v-model` for two-way binding**: Cleaner than manual binding
- **Provide default values**: Use `withDefaults` for optional props

### 3. Slots

- **Provide fallback content**: Use default slot content
- **Use scoped slots for data**: Pass data to parent via slot props
- **Name slots semantically**: `header`, `footer`, `actions` etc.
- **Check slot existence**: Use `$slots.slotName` before rendering

### 4. Performance

- **Use `shallowRef` for large objects**: Reduce reactivity overhead
- **Lazy load components**: Use `defineAsyncComponent`
- **Use `v-once` for static content**: Render only once
- **Use `v-memo` for expensive renders**: Memoize template rendering
- **Avoid deep watchers**: Watch specific properties instead
