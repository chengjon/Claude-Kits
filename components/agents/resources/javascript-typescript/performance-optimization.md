# Performance Optimization Patterns

## Debounce

Limit function calls by waiting for a delay after the last call.

```javascript
function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;

  return function(...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

// Usage: search input
const handleSearch = debounce((query: string) => {
  fetchSearchResults(query);
}, 300);
```

## Throttle

Execute at most once per period.

```javascript
function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Usage: scroll event
const handleScroll = throttle(() => {
  console.log('Scroll position:', window.scrollY);
}, 100);
```

## Memoization

Cache function results to avoid expensive recalculations.

```javascript
function memoize<T extends (...args: any[]) => any>(fn: T): T {
  const cache = new Map();

  return function(...args: Parameters<T>): ReturnType<T> {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn(...args);
    cache.set(key, result);
    return result;
  } as T;
}

// Usage: expensive calculation
const fibonacci = memoize((n: number): number => {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
});
```

## Module System Optimization

```javascript
// ESM (modern, recommended)
// math.js
export const add = (a, b) => a + b;
export const multiply = (a, b) => a * b;
export default class Calculator {
  constructor() {
    this.history = [];
  }
}

// app.js
import Calculator, { add, multiply } from './math.js';
import * as MathUtils from './math.js';

// Dynamic imports (code splitting)
async function loadFeature() {
  const { default: FeatureModule } = await import('./feature.js');
  return new FeatureModule();
}
```

## Build Tool Integration

### Vite Configuration

```javascript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: 'es2020',
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash', 'date-fns']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom']
  }
});
```

### Webpack Optimization

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10
        }
      }
    },
    runtimeChunk: 'single'
  }
};
```

## Best Practices

**Memory Management**:
- Clear intervals and timeouts
- Remove event listeners
- Nullify large objects when done
- Use WeakMap/WeakSet for cache

**Loop Optimization**:
- Cache array length in loops
- Use for-of for readability
- Prefer map/filter/reduce for clarity
- Use for loop for performance-critical code

**Function Performance**:
- Avoid creating functions in loops
- Use arrow functions for lexical this
- Memoize expensive pure functions
- Debounce/throttle event handlers
