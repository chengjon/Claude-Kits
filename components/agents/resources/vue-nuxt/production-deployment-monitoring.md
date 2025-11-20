# Production Deployment & Monitoring

Complete guide to production deployment, monitoring, multi-environment configuration, and Docker containerization for Nuxt 3.


## 📑 Table of Contents

- [Production Monitoring](#production-monitoring)
  - [Sentry Integration](#sentry-integration)
  - [Datadog APM Integration](#datadog-apm-integration)
  - [Performance Monitoring](#performance-monitoring)
  - [Custom Health Checks](#custom-health-checks)
- [Multi-Environment Configuration](#multi-environment-configuration)
  - [Environment Variables](#environment-variables)
  - [Environment Files](#environment-files)
- [Docker Containerization](#docker-containerization)
  - [Multi-Stage Production Dockerfile](#multi-stage-production-dockerfile)
  - [Docker Compose for Production](#docker-compose-for-production)
  - [Nginx Configuration](#nginx-configuration)
- [CI/CD Pipeline](#cicd-pipeline)
  - [GitHub Actions Deployment](#github-actions-deployment)
- [Best Practices](#best-practices)
  - [1. Monitoring](#1-monitoring)
  - [2. Security](#2-security)
  - [3. Deployment](#3-deployment)
  - [4. Docker](#4-docker)
  - [5. CI/CD](#5-cicd)

---
## Production Monitoring

### Sentry Integration

```typescript
// plugins/sentry.client.ts
import * as Sentry from '@sentry/vue'

export default defineNuxtPlugin((nuxtApp) => {
  const router = useRouter()
  const config = useRuntimeConfig()

  if (process.env.NODE_ENV === 'production') {
    Sentry.init({
      app: nuxtApp.vueApp,
      dsn: config.public.sentryDsn,
      integrations: [
        new Sentry.BrowserTracing({
          routingInstrumentation: Sentry.vueRouterInstrumentation(router),
        }),
        new Sentry.Replay({
          maskAllText: false,
          blockAllMedia: false,
        }),
      ],
      tracesSampleRate: 0.2,
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
      environment: process.env.NODE_ENV,
    })
  }

  return {
    provide: {
      sentry: Sentry
    }
  }
})

// server/middleware/error-tracking.ts
import * as Sentry from '@sentry/node'

export default defineEventHandler((event) => {
  event.context.sentry = Sentry

  event.node.res.on('finish', () => {
    if (event.node.res.statusCode >= 500) {
      Sentry.captureMessage(`Server error: ${event.node.req.url}`, 'error')
    }
  })
})
```

### Datadog APM Integration

```typescript
// server/plugins/datadog.ts
import tracer from 'dd-trace'

export default defineNitroPlugin((nitroApp) => {
  if (process.env.NODE_ENV === 'production') {
    tracer.init({
      service: 'nuxt-app',
      env: process.env.DD_ENV || 'production',
      version: process.env.DD_VERSION || '1.0.0',
      logInjection: true,
      runtimeMetrics: true,
      profiling: true
    })
  }
})

// Custom instrumentation
export default defineEventHandler(async (event) => {
  const span = tracer.startSpan('api.products.get')

  try {
    const products = await fetchProducts()
    span.setTag('products.count', products.length)
    return products
  } catch (error) {
    span.setTag('error', true)
    span.setTag('error.message', error.message)
    throw error
  } finally {
    span.finish()
  }
})
```

### Performance Monitoring

```typescript
// composables/usePerformanceMonitoring.ts
export const usePerformanceMonitoring = () => {
  const trackPageView = (path: string) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', 'GA_MEASUREMENT_ID', {
        page_path: path
      })
    }
  }

  const trackWebVitals = () => {
    if (typeof window !== 'undefined') {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        getCLS((metric) => {
          reportToAnalytics('CLS', metric.value)
        })
        getFID((metric) => {
          reportToAnalytics('FID', metric.value)
        })
        getFCP((metric) => {
          reportToAnalytics('FCP', metric.value)
        })
        getLCP((metric) => {
          reportToAnalytics('LCP', metric.value)
        })
        getTTFB((metric) => {
          reportToAnalytics('TTFB', metric.value)
        })
      })
    }
  }

  const reportToAnalytics = (metric: string, value: number) => {
    if (window.gtag) {
      window.gtag('event', metric, {
        value: Math.round(value),
        event_category: 'Web Vitals',
        non_interaction: true
      })
    }
  }

  return {
    trackPageView,
    trackWebVitals
  }
}

// app.vue
const router = useRouter()
const { trackPageView, trackWebVitals } = usePerformanceMonitoring()

router.afterEach((to) => {
  trackPageView(to.fullPath)
})

onMounted(() => {
  trackWebVitals()
})
```

### Custom Health Checks

```typescript
// server/api/health.get.ts
export default defineEventHandler(async (event) => {
  const checks = {
    database: false,
    redis: false,
    external_api: false
  }

  // Database check
  try {
    await prisma.$queryRaw`SELECT 1`
    checks.database = true
  } catch (error) {
    console.error('Database health check failed:', error)
  }

  // Redis check
  try {
    const redis = await getRedisClient()
    await redis.ping()
    checks.redis = true
  } catch (error) {
    console.error('Redis health check failed:', error)
  }

  // External API check
  try {
    await $fetch('https://api.example.com/health', { timeout: 5000 })
    checks.external_api = true
  } catch (error) {
    console.error('External API health check failed:', error)
  }

  const isHealthy = Object.values(checks).every(check => check)

  setResponseStatus(event, isHealthy ? 200 : 503)

  return {
    status: isHealthy ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    checks
  }
})
```

## Multi-Environment Configuration

### Environment Variables

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    // Private (server-only)
    databaseUrl: process.env.DATABASE_URL,
    redisUrl: process.env.REDIS_URL,
    jwtSecret: process.env.JWT_SECRET,
    revalidateSecret: process.env.REVALIDATE_SECRET,
    stripeSecretKey: process.env.STRIPE_SECRET_KEY,

    // Public (client + server)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE,
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL,
      sentryDsn: process.env.NUXT_PUBLIC_SENTRY_DSN,
      stripePublicKey: process.env.NUXT_PUBLIC_STRIPE_PUBLIC_KEY,
      environment: process.env.NODE_ENV,
    }
  },

  nitro: {
    preset: 'node-server',

    // Production optimizations
    ...(process.env.NODE_ENV === 'production' && {
      compressPublicAssets: true,
      minify: true,
    }),

    // Storage layers
    storage: {
      redis: {
        driver: 'redis',
        url: process.env.REDIS_URL
      },
      db: {
        driver: 'fs',
        base: './.data/db'
      }
    }
  }
})
```

### Environment Files

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@prod-db:5432/app
REDIS_URL=redis://prod-redis:6379
JWT_SECRET=super-secret-production-key
NUXT_PUBLIC_API_BASE=https://api.production.com
NUXT_PUBLIC_SITE_URL=https://production.com
NUXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
NODE_ENV=production

# .env.staging
DATABASE_URL=postgresql://user:pass@staging-db:5432/app
REDIS_URL=redis://staging-redis:6379
JWT_SECRET=super-secret-staging-key
NUXT_PUBLIC_API_BASE=https://api.staging.com
NUXT_PUBLIC_SITE_URL=https://staging.com
NODE_ENV=staging

# .env.development
DATABASE_URL=postgresql://user:pass@localhost:5432/app_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret
NUXT_PUBLIC_API_BASE=http://localhost:3000/api
NUXT_PUBLIC_SITE_URL=http://localhost:3000
NODE_ENV=development
```

## Docker Containerization

### Multi-Stage Production Dockerfile

```dockerfile
# Dockerfile.production
FROM node:20-alpine AS base

# Dependencies stage
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Build stage
FROM base AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/.output ./.output

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nuxtjs
RUN chown -R nuxtjs:nodejs /app

USER nuxtjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", ".output/server/index.mjs"]
```

### Docker Compose for Production

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_cache:/var/cache/nginx
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  nginx_cache:

networks:
  app-network:
    driver: bridge
```

### Nginx Configuration

```nginx
# nginx.conf
events {
  worker_connections 4096;
}

http {
  upstream nuxt_app {
    least_conn;
    server app:3000 max_fails=3 fail_timeout=30s;
  }

  # Cache configuration
  proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=nuxt_cache:10m max_size=1g inactive=60m use_temp_path=off;

  # Rate limiting
  limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

  # Gzip compression
  gzip on;
  gzip_vary on;
  gzip_min_length 1000;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

  server {
    listen 80;
    server_name example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
  }

  server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
      proxy_pass http://nuxt_app;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection 'upgrade';
      proxy_set_header Host $host;
      proxy_cache_bypass $http_upgrade;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;

      # Timeouts
      proxy_connect_timeout 60s;
      proxy_send_timeout 60s;
      proxy_read_timeout 60s;
    }

    location /_nuxt/ {
      proxy_pass http://nuxt_app;
      proxy_cache nuxt_cache;
      proxy_cache_valid 200 30d;
      proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
      add_header Cache-Control "public, immutable";
      add_header X-Cache-Status $upstream_cache_status;
    }

    location /api/ {
      limit_req zone=api_limit burst=20 nodelay;
      proxy_pass http://nuxt_app;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
}
```

## CI/CD Pipeline

### GitHub Actions Deployment

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run test
      - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: nuxt-app
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -f Dockerfile.production .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster prod-cluster --service nuxt-app --force-new-deployment

      - name: Notify deployment
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Best Practices

### 1. Monitoring
- **Health checks**: Implement comprehensive health endpoints
- **Error tracking**: Use Sentry or similar services
- **Performance monitoring**: Track Web Vitals and custom metrics
- **Logging**: Centralized logging with structured data

### 2. Security
- **Environment variables**: Never commit secrets
- **HTTPS only**: Enforce TLS in production
- **Security headers**: Implement CSP, HSTS, etc.
- **Rate limiting**: Protect against abuse

### 3. Deployment
- **Zero-downtime**: Use rolling deployments
- **Rollback strategy**: Keep previous versions
- **Database migrations**: Automate and test
- **Smoke tests**: Verify critical paths after deployment

### 4. Docker
- **Multi-stage builds**: Minimize image size
- **Non-root user**: Run as unprivileged user
- **Health checks**: Built into containers
- **Resource limits**: Set memory and CPU limits

### 5. CI/CD
- **Automated testing**: Run tests before deploy
- **Environment parity**: Dev/staging/prod consistency
- **Deployment notifications**: Alert team of changes
- **Rollback automation**: Quick revert on failures
