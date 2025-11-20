# Component Design Patterns

Advanced React component architecture patterns, composition strategies, and reusable component design.


## 📑 Table of Contents

- [Atomic Design Structure](#atomic-design-structure)
  - [Button Component with Variants](#button-component-with-variants)
  - [Input Component with Validation](#input-component-with-validation)
- [Compound Components Pattern](#compound-components-pattern)
  - [Form Group with Context](#form-group-with-context)
- [Render Props Pattern](#render-props-pattern)
- [Higher-Order Components (HOC)](#higher-order-components-hoc)
- [Custom Hooks Patterns](#custom-hooks-patterns)
  - [useToggle Hook](#usetoggle-hook)
  - [useLocalStorage Hook](#uselocalstorage-hook)
- [Component Architecture Best Practices](#component-architecture-best-practices)
  - [Folder Organization](#folder-organization)
  - [Component File Structure](#component-file-structure)
  - [Prop Interface Patterns](#prop-interface-patterns)
  - [Composition over Inheritance](#composition-over-inheritance)

---
## Atomic Design Structure

### Button Component with Variants

```typescript
// /components/atoms/Button/Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus-visible:ring-gray-500',
        ghost: 'text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-500',
        destructive: 'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500',
        outline: 'border-2 border-gray-300 hover:bg-gray-100 focus-visible:ring-gray-500',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => (
    <button
      className={buttonVariants({ variant, size, className })}
      ref={ref}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  )
);

Button.displayName = 'Button';

export { Button, buttonVariants, type ButtonProps };
```

### Input Component with Validation

```typescript
// /components/atoms/Input/Input.tsx
import React from 'react';
import { cva } from 'class-variance-authority';

const inputVariants = cva(
  'w-full rounded-md border bg-white px-3 py-2 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
  {
    variants: {
      state: {
        default: 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
        error: 'border-red-500 focus:border-red-500 focus:ring-red-500',
        success: 'border-green-500 focus:border-green-500 focus:ring-green-500',
      },
    },
    defaultVariants: {
      state: 'default',
    },
  }
);

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  state?: 'default' | 'error' | 'success';
  error?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, state = 'default', error, ...props }, ref) => (
    <div className="w-full">
      <input
        className={inputVariants({ state: error ? 'error' : state, className })}
        ref={ref}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
);

Input.displayName = 'Input';

export { Input, type InputProps };
```

## Compound Components Pattern

### Form Group with Context

```typescript
// /components/molecules/FormGroup/FormGroup.tsx
'use client';

import React, { createContext, useContext, useId } from 'react';

interface FormGroupContextType {
  id: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

const FormGroupContext = createContext<FormGroupContextType | undefined>(undefined);

function useFormGroup() {
  const context = useContext(FormGroupContext);
  if (!context) {
    throw new Error('FormGroup components must be used within FormGroup');
  }
  return context;
}

interface FormGroupProps {
  error?: string;
  disabled?: boolean;
  required?: boolean;
  children: React.ReactNode;
}

function FormGroup({ error, disabled, required, children }: FormGroupProps) {
  const id = useId();

  return (
    <FormGroupContext.Provider value={{ id, error, disabled, required }}>
      <div className="space-y-2">{children}</div>
    </FormGroupContext.Provider>
  );
}

function Label({ children, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  const { id, disabled, required } = useFormGroup();
  return (
    <label
      htmlFor={id}
      className={`block text-sm font-medium ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      {...props}
    >
      {children}
      {required && <span className="ml-1 text-red-500">*</span>}
    </label>
  );
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

function Input({ className, ...props }: InputProps) {
  const { id, error, disabled, required } = useFormGroup();
  return (
    <input
      id={id}
      required={required}
      className={`w-full px-3 py-2 border rounded-md transition-colors ${
        error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
      } ${disabled ? 'opacity-50 cursor-not-allowed bg-gray-50' : ''} ${className || ''}`}
      disabled={disabled}
      aria-invalid={!!error}
      aria-describedby={error ? `${id}-error` : undefined}
      {...props}
    />
  );
}

function Error() {
  const { id, error } = useFormGroup();
  if (!error) return null;
  return (
    <p id={`${id}-error`} className="text-sm text-red-600" role="alert">
      {error}
    </p>
  );
}

function Helper({ children }: { children: React.ReactNode }) {
  const { id } = useFormGroup();
  return (
    <p id={`${id}-helper`} className="text-sm text-gray-600">
      {children}
    </p>
  );
}

// Compose the compound component
FormGroup.Label = Label;
FormGroup.Input = Input;
FormGroup.Error = Error;
FormGroup.Helper = Helper;

export { FormGroup };

// Usage example
export function LoginForm() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [errors, setErrors] = React.useState<{ email?: string; password?: string }>({});

  const validateEmail = (value: string) => {
    if (!value) return 'Email is required';
    if (!/\S+@\S+\.\S+/.test(value)) return 'Invalid email format';
    return undefined;
  };

  return (
    <form className="space-y-4">
      <FormGroup error={errors.email} required>
        <FormGroup.Label>Email</FormGroup.Label>
        <FormGroup.Input
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            const error = validateEmail(e.target.value);
            setErrors((prev) => ({ ...prev, email: error }));
          }}
        />
        <FormGroup.Error />
        <FormGroup.Helper>We'll never share your email.</FormGroup.Helper>
      </FormGroup>

      <FormGroup error={errors.password} required>
        <FormGroup.Label>Password</FormGroup.Label>
        <FormGroup.Input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <FormGroup.Error />
      </FormGroup>
    </form>
  );
}
```

## Render Props Pattern

```typescript
// /components/utilities/Toggle/Toggle.tsx
interface ToggleProps {
  children: (props: {
    on: boolean;
    toggle: () => void;
    setOn: (value: boolean) => void;
  }) => React.ReactNode;
}

export function Toggle({ children }: ToggleProps) {
  const [on, setOn] = React.useState(false);
  const toggle = () => setOn((prev) => !prev);

  return <>{children({ on, toggle, setOn })}</>;
}

// Usage
export function ToggleExample() {
  return (
    <Toggle>
      {({ on, toggle }) => (
        <div>
          <button onClick={toggle}>{on ? 'ON' : 'OFF'}</button>
          {on && <p>Content is visible!</p>}
        </div>
      )}
    </Toggle>
  );
}
```

## Higher-Order Components (HOC)

```typescript
// /components/hoc/withLoading.tsx
import React from 'react';

interface WithLoadingProps {
  loading?: boolean;
}

export function withLoading<P extends object>(
  Component: React.ComponentType<P>,
  LoadingComponent: React.ComponentType = () => <div>Loading...</div>
) {
  return function WithLoadingComponent(props: P & WithLoadingProps) {
    const { loading, ...restProps } = props;

    if (loading) {
      return <LoadingComponent />;
    }

    return <Component {...(restProps as P)} />;
  };
}

// Usage
function UserProfile({ user }: { user: User }) {
  return <div>{user.name}</div>;
}

const UserProfileWithLoading = withLoading(UserProfile);

// In parent component
<UserProfileWithLoading user={user} loading={isLoading} />;
```

## Custom Hooks Patterns

### useToggle Hook

```typescript
// /hooks/useToggle.ts
import { useState, useCallback } from 'react';

export function useToggle(initialValue = false): [boolean, () => void, (value: boolean) => void] {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => setValue((prev) => !prev), []);
  const setDirectValue = useCallback((newValue: boolean) => setValue(newValue), []);

  return [value, toggle, setDirectValue];
}

// Usage
function ToggleComponent() {
  const [isOpen, toggleOpen, setIsOpen] = useToggle(false);

  return (
    <div>
      <button onClick={toggleOpen}>Toggle</button>
      <button onClick={() => setIsOpen(true)}>Open</button>
      {isOpen && <p>Content</p>}
    </div>
  );
}
```

### useLocalStorage Hook

```typescript
// /hooks/useLocalStorage.ts
import { useState, useEffect } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = (value: T) => {
    try {
      setStoredValue(value);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(value));
      }
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  };

  return [storedValue, setValue];
}

// Usage
function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Current theme: {theme}
    </button>
  );
}
```

## Component Architecture Best Practices

### Folder Organization

```
components/
├── atoms/                 # Basic building blocks
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   ├── Input/
│   └── Badge/
├── molecules/             # Simple component combinations
│   ├── FormGroup/
│   ├── Card/
│   └── SearchBar/
├── organisms/             # Complex component sections
│   ├── Header/
│   ├── ProductCard/
│   └── DataTable/
├── templates/             # Page-level layouts
│   ├── DashboardLayout/
│   └── AuthLayout/
└── pages/                 # Complete pages (if needed)
```

### Component File Structure

```typescript
// Component.tsx
import React from 'react';
import { type VariantProps } from 'class-variance-authority';
import { componentVariants } from './Component.styles';
import type { ComponentProps } from './Component.types';

export function Component({ variant, size, children }: ComponentProps) {
  return (
    <div className={componentVariants({ variant, size })}>
      {children}
    </div>
  );
}

// Component.styles.ts
import { cva } from 'class-variance-authority';

export const componentVariants = cva('base-classes', {
  variants: { /* ... */ },
});

// Component.types.ts
export interface ComponentProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

// index.ts
export { Component } from './Component';
export type { ComponentProps } from './Component.types';
```

### Prop Interface Patterns

```typescript
// Base props with extensions
interface BaseButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

// Extending HTML attributes
interface ButtonProps
  extends BaseButtonProps,
    React.ButtonHTMLAttributes<HTMLButtonElement> {}

// Discriminated unions for type safety
type LoadingState =
  | { loading: true; data?: never; error?: never }
  | { loading: false; data: Data; error?: never }
  | { loading: false; data?: never; error: Error };

interface ComponentProps {
  state: LoadingState;
}
```

### Composition over Inheritance

```typescript
// Bad: Deep component hierarchy
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>

// Good: Flexible composition
<Card>
  <div className="card-header">
    <h2>Title</h2>
  </div>
  <div className="card-content">Content</div>
</Card>

// Better: Provide both options
export function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      {title && <div className="card-header"><h2>{title}</h2></div>}
      <div className="card-content">{children}</div>
    </div>
  );
}

// With sub-components for advanced use
Card.Header = CardHeader;
Card.Content = CardContent;
Card.Footer = CardFooter;
```
