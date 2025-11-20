# Advanced TypeScript Patterns


## 📑 Table of Contents

- [Generics with Constraints](#generics-with-constraints)
- [Conditional Types](#conditional-types)
- [Mapped Types](#mapped-types)
- [Template Literal Types](#template-literal-types)
- [Discriminated Unions](#discriminated-unions)
- [Utility Types](#utility-types)
- [Type Inference Optimization](#type-inference-optimization)
- [Decorators](#decorators)

---
## Generics with Constraints

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: 'Alice', age: 30 };
const name = getProperty(user, 'name'); // type: string
const age = getProperty(user, 'age');   // type: number
```

## Conditional Types

```typescript
type IsString<T> = T extends string ? true : false;
type A = IsString<string>;  // true
type B = IsString<number>;  // false

// Extract return type
type Unpromisify<T> = T extends Promise<infer U> ? U : T;
type Result = Unpromisify<Promise<string>>;  // string
```

## Mapped Types

```typescript
// Built-in mapped types
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

// Custom mapped type with key remapping
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface User {
  name: string;
  age: number;
}

type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number; }
```

## Template Literal Types

```typescript
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<'click'>;  // 'onClick'
type HoverEvent = EventName<'hover'>;  // 'onHover'

// Route builder
type Route = '/users' | '/posts';
type RouteId = `${Route}/:id`;
// '/users/:id' | '/posts/:id'
```

## Discriminated Unions

```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

function handleResult<T>(result: Result<T>) {
  if (result.success) {
    console.log(result.data);  // TypeScript knows data exists
  } else {
    console.error(result.error); // TypeScript knows error exists
  }
}

// Shape example
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
  }
}
```

## Utility Types

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  age: number;
  role: 'admin' | 'user';
}

// Pick - select subset
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit - exclude properties
type UserWithoutEmail = Omit<User, 'email'>;

// Record - create object type
type UserRoles = Record<'admin' | 'user' | 'guest', string[]>;

// ReturnType - extract function return type
function getUser(): User { /* ... */ }
type UserType = ReturnType<typeof getUser>;

// Parameters - extract function parameters
function updateUser(id: string, updates: Partial<User>): void {}
type UpdateParams = Parameters<typeof updateUser>;
// [id: string, updates: Partial<User>]
```

## Type Inference Optimization

```typescript
// Inferred return types
function createUser(name: string, age: number) {
  return { name, age, createdAt: new Date() };
}
// Return type inferred as: { name: string; age: number; createdAt: Date }

// Const assertions for literal types
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
} as const;
// Type: { readonly apiUrl: "https://api.example.com"; readonly timeout: 5000 }

// Type guards
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function process(value: string | number) {
  if (isString(value)) {
    return value.toUpperCase();
  }
  return value.toFixed(2);
}
```

## Decorators

```typescript
// Class decorator
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class User {
  constructor(public name: string) {}
}

// Method decorator
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey} with:`, args);
    const result = originalMethod.apply(this, args);
    console.log(`Result:`, result);
    return result;
  };

  return descriptor;
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}

// Property decorator
function readonly(target: any, propertyKey: string) {
  Object.defineProperty(target, propertyKey, {
    writable: false
  });
}

class Config {
  @readonly
  apiKey: string = 'secret-key';
}
```
