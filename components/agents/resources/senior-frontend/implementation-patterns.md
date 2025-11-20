# Frontend Implementation Patterns

## Component Architecture

```typescript
// components/Button/Button.tsx
import { forwardRef, ButtonHTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'underline-offset-4 hover:underline text-primary',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4 py-2',
        lg: 'h-11 px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, disabled, children, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <Spinner className="mr-2 h-4 w-4 animate-spin" />
            {children}
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };
```

## Data Fetching Pattern

```typescript
// hooks/useUser.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { User, UpdateUserDTO } from '@/types/user';

// Query key factory
const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: string) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

// Fetch user hook
export function useUser(userId: string) {
  return useQuery({
    queryKey: userKeys.detail(userId),
    queryFn: async () => {
      const response = await api.get<User>(`/users/${userId}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: (failureCount, error) => {
      if (error.response?.status === 404) return false;
      return failureCount < 3;
    },
  });
}

// Update user mutation with optimistic updates
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, data }: { userId: string; data: UpdateUserDTO }) => {
      const response = await api.patch<User>(`/users/${userId}`, data);
      return response.data;
    },
    onMutate: async ({ userId, data }) => {
      await queryClient.cancelQueries({ queryKey: userKeys.detail(userId) });

      const previousUser = queryClient.getQueryData<User>(userKeys.detail(userId));

      queryClient.setQueryData<User>(userKeys.detail(userId), (old) => ({
        ...old!,
        ...data,
      }));

      return { previousUser };
    },
    onError: (err, { userId }, context) => {
      if (context?.previousUser) {
        queryClient.setQueryData(userKeys.detail(userId), context.previousUser);
      }
    },
    onSettled: (data, error, { userId }) => {
      queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
    },
  });
}
```

## Performance Monitoring

```typescript
// lib/performance.ts
import { getCLS, getFCP, getFID, getLCP, getTTFB } from 'web-vitals';

interface PerformanceMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  navigationType: 'navigate' | 'reload' | 'back-forward' | 'prerender';
}

function sendToAnalytics(metric: PerformanceMetric) {
  const body = JSON.stringify({
    ...metric,
    url: window.location.href,
    timestamp: Date.now(),
    connection: (navigator as any).connection?.effectiveType,
  });

  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/vitals', body);
  } else {
    fetch('/api/analytics/vitals', {
      body,
      method: 'POST',
      keepalive: true,
    });
  }
}

export function initWebVitals() {
  getCLS(sendToAnalytics);
  getFCP(sendToAnalytics);
  getFID(sendToAnalytics);
  getLCP(sendToAnalytics);
  getTTFB(sendToAnalytics);
}

export function measureComponent(componentName: string) {
  return {
    start: () => performance.mark(`${componentName}-start`),
    end: () => {
      performance.mark(`${componentName}-end`);
      performance.measure(
        componentName,
        `${componentName}-start`,
        `${componentName}-end`
      );

      const measure = performance.getEntriesByName(componentName)[0];
      console.log(`${componentName} render time:`, measure.duration);

      performance.clearMarks(`${componentName}-start`);
      performance.clearMarks(`${componentName}-end`);
      performance.clearMeasures(componentName);
    },
  };
}
```
