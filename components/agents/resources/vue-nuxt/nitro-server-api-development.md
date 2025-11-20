# Nitro Server & API Development

Complete guide to Nuxt 3's Nitro server engine, API routes, database integration, and authentication.


## 📑 Table of Contents

- [Server Routes Fundamentals](#server-routes-fundamentals)
  - [Basic API Endpoint](#basic-api-endpoint)
  - [Protected API Route](#protected-api-route)
- [Database Integration](#database-integration)
  - [Prisma ORM Setup](#prisma-orm-setup)
  - [Drizzle ORM Alternative](#drizzle-orm-alternative)
- [Authentication Strategies](#authentication-strategies)
  - [JWT Authentication](#jwt-authentication)
  - [Session-Based Authentication](#session-based-authentication)
- [Server Middleware](#server-middleware)
  - [Global Request Logger](#global-request-logger)
  - [CORS Configuration](#cors-configuration)
- [Storage Abstraction](#storage-abstraction)
  - [File System Storage](#file-system-storage)
  - [S3-Compatible Storage](#s3-compatible-storage)
- [Best Practices](#best-practices)
  - [1. Input Validation](#1-input-validation)
  - [2. Error Handling](#2-error-handling)
  - [3. Authentication & Authorization](#3-authentication-authorization)
  - [4. Database Queries](#4-database-queries)
  - [5. API Design](#5-api-design)

---
## Server Routes Fundamentals

### Basic API Endpoint

```typescript
// server/api/products/[id].get.ts
import { z } from 'zod'

const paramsSchema = z.object({
  id: z.string().uuid()
})

export default defineEventHandler(async (event) => {
  // Validate params
  const params = await getValidatedRouterParams(event, paramsSchema.parse)

  // Get database connection
  const db = useDatabase()

  // Fetch product with caching
  const product = await cachedFindProduct(params.id, {
    ttl: 60 * 5, // 5 minutes
  })

  if (!product) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Product not found'
    })
  }

  // Transform for API response
  return {
    id: product.id,
    name: product.name,
    description: product.description,
    price: product.price,
    image: product.imageUrl,
    inStock: product.stock > 0,
    createdAt: product.createdAt
  }
})

// Cached database query
async function cachedFindProduct(id: string, options?: { ttl?: number }) {
  const cached = await useStorage('redis').getItem(`product:${id}`)

  if (cached) {
    return cached
  }

  const product = await useDatabase().product.findUnique({
    where: { id }
  })

  if (product && options?.ttl) {
    await useStorage('redis').setItem(
      `product:${id}`,
      product,
      { ttl: options.ttl }
    )
  }

  return product
}
```

### Protected API Route

```typescript
// server/api/admin/products.post.ts
import { z } from 'zod'
import jwt from 'jsonwebtoken'

const bodySchema = z.object({
  name: z.string().min(1),
  description: z.string(),
  price: z.number().positive(),
  categoryId: z.string().uuid(),
  stock: z.number().int().min(0)
})

export default defineEventHandler(async (event) => {
  // Authentication
  const user = await requireAuth(event)

  // Authorization
  if (!user.permissions.includes('products.create')) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Insufficient permissions'
    })
  }

  // Validate body
  const body = await readValidatedBody(event, bodySchema.parse)

  // Create product
  const db = useDatabase()
  const product = await db.product.create({
    data: {
      ...body,
      createdById: user.id
    }
  })

  // Clear cache
  await useStorage('redis').removeItem('products:all')

  // Log activity
  await logActivity({
    userId: user.id,
    action: 'product.created',
    resourceId: product.id
  })

  return product
})

// Auth middleware
async function requireAuth(event: H3Event) {
  const token = getCookie(event, 'auth-token') || getHeader(event, 'authorization')?.replace('Bearer ', '')

  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Authentication required'
    })
  }

  try {
    const payload = jwt.verify(token, useRuntimeConfig().jwtSecret)
    return await getUserById(payload.userId)
  } catch (error) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Invalid token'
    })
  }
}
```

## Database Integration

### Prisma ORM Setup

```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        String   @id @default(uuid())
  title     String
  content   String
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

// server/utils/prisma.ts
import { PrismaClient } from '@prisma/client'

const prismaClientSingleton = () => {
  return new PrismaClient()
}

type PrismaClientSingleton = ReturnType<typeof prismaClientSingleton>

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClientSingleton | undefined
}

export const prisma = globalForPrisma.prisma ?? prismaClientSingleton()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

// server/api/posts/index.get.ts
export default defineEventHandler(async (event) => {
  const posts = await prisma.post.findMany({
    where: { published: true },
    include: { author: { select: { name: true, email: true } } },
    orderBy: { createdAt: 'desc' },
    take: 10
  })

  return posts
})
```

### Drizzle ORM Alternative

```typescript
// server/database/schema.ts
import { pgTable, text, timestamp, boolean, uuid } from 'drizzle-orm/pg-core'

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
})

export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  title: text('title').notNull(),
  content: text('content').notNull(),
  published: boolean('published').default(false),
  authorId: uuid('author_id').references(() => users.id),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
})

// server/utils/db.ts
import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import * as schema from '../database/schema'

const client = postgres(useRuntimeConfig().databaseUrl)
export const db = drizzle(client, { schema })

// server/api/posts/index.get.ts
import { eq, desc } from 'drizzle-orm'
import { posts, users } from '~/server/database/schema'

export default defineEventHandler(async () => {
  const result = await db
    .select()
    .from(posts)
    .leftJoin(users, eq(posts.authorId, users.id))
    .where(eq(posts.published, true))
    .orderBy(desc(posts.createdAt))
    .limit(10)

  return result
})
```

## Authentication Strategies

### JWT Authentication

```typescript
// server/api/auth/login.post.ts
import { z } from 'zod'
import bcrypt from 'bcrypt'
import jwt from 'jsonwebtoken'

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, loginSchema.parse)

  // Find user
  const user = await prisma.user.findUnique({
    where: { email: body.email }
  })

  if (!user) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Invalid credentials'
    })
  }

  // Verify password
  const validPassword = await bcrypt.compare(body.password, user.passwordHash)

  if (!validPassword) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Invalid credentials'
    })
  }

  // Generate JWT
  const token = jwt.sign(
    { userId: user.id, email: user.email },
    useRuntimeConfig().jwtSecret,
    { expiresIn: '7d' }
  )

  // Set cookie
  setCookie(event, 'auth-token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7 // 7 days
  })

  return {
    user: {
      id: user.id,
      email: user.email,
      name: user.name
    }
  }
})
```

### Session-Based Authentication

```typescript
// server/utils/session.ts
import { randomUUID } from 'crypto'

const sessions = new Map<string, { userId: string, expiresAt: number }>()

export async function createSession(userId: string) {
  const sessionId = randomUUID()
  const expiresAt = Date.now() + (7 * 24 * 60 * 60 * 1000) // 7 days

  sessions.set(sessionId, { userId, expiresAt })

  return sessionId
}

export async function getSession(sessionId: string) {
  const session = sessions.get(sessionId)

  if (!session || session.expiresAt < Date.now()) {
    sessions.delete(sessionId)
    return null
  }

  return session
}

export async function deleteSession(sessionId: string) {
  sessions.delete(sessionId)
}

// server/api/auth/session.get.ts
export default defineEventHandler(async (event) => {
  const sessionId = getCookie(event, 'session-id')

  if (!sessionId) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Not authenticated'
    })
  }

  const session = await getSession(sessionId)

  if (!session) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Session expired'
    })
  }

  const user = await prisma.user.findUnique({
    where: { id: session.userId }
  })

  return { user }
})
```

## Server Middleware

### Global Request Logger

```typescript
// server/middleware/logger.ts
export default defineEventHandler((event) => {
  const startTime = Date.now()

  event.node.res.on('finish', () => {
    const duration = Date.now() - startTime
    const { method, url } = event.node.req
    const { statusCode } = event.node.res

    console.log(`[${new Date().toISOString()}] ${method} ${url} - ${statusCode} (${duration}ms)`)
  })
})
```

### CORS Configuration

```typescript
// server/middleware/cors.ts
export default defineEventHandler((event) => {
  const config = useRuntimeConfig()

  setHeaders(event, {
    'Access-Control-Allow-Origin': config.public.allowedOrigins || '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Credentials': 'true'
  })

  if (event.node.req.method === 'OPTIONS') {
    event.node.res.statusCode = 204
    event.node.res.end()
  }
})
```

## Storage Abstraction

### File System Storage

```typescript
// server/api/uploads/[...path].ts
import { readFile } from 'fs/promises'

export default defineEventHandler(async (event) => {
  const path = getRouterParam(event, 'path')

  if (!path) {
    throw createError({ statusCode: 400, message: 'Path required' })
  }

  const storage = useStorage('uploads')
  const file = await storage.getItem(path)

  if (!file) {
    throw createError({ statusCode: 404, message: 'File not found' })
  }

  return file
})
```

### S3-Compatible Storage

```typescript
// nitro.config.ts
export default defineNitroConfig({
  storage: {
    s3: {
      driver: 's3',
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      bucket: process.env.S3_BUCKET,
      region: process.env.AWS_REGION
    }
  }
})

// server/api/files/upload.post.ts
export default defineEventHandler(async (event) => {
  const files = await readMultipartFormData(event)

  if (!files || files.length === 0) {
    throw createError({ statusCode: 400, message: 'No files uploaded' })
  }

  const storage = useStorage('s3')
  const uploadedFiles = []

  for (const file of files) {
    const key = `uploads/${Date.now()}-${file.filename}`
    await storage.setItemRaw(key, file.data)

    uploadedFiles.push({
      key,
      url: `https://${process.env.S3_BUCKET}.s3.amazonaws.com/${key}`
    })
  }

  return { files: uploadedFiles }
})
```

## Best Practices

### 1. Input Validation
- Always validate request params, query, and body
- Use Zod or similar validation libraries
- Return clear error messages

### 2. Error Handling
- Use `createError` for consistent errors
- Log errors appropriately
- Don't expose sensitive information

### 3. Authentication & Authorization
- Separate authentication from authorization
- Use middleware for common checks
- Implement proper token rotation

### 4. Database Queries
- Use connection pooling
- Implement query caching
- Optimize N+1 queries
- Use transactions for multi-step operations

### 5. API Design
- Follow REST conventions
- Use proper HTTP methods
- Implement pagination for lists
- Version your APIs when necessary
