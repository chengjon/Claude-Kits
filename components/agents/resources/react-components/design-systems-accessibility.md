# Design Systems & Accessibility

Comprehensive guide to building accessible design systems with WCAG compliance, ARIA patterns, and modern design system integration.


## 📑 Table of Contents

- [Design System Fundamentals](#design-system-fundamentals)
  - [Design Tokens](#design-tokens)
  - [Theme System](#theme-system)
- [Accessibility Implementation](#accessibility-implementation)
  - [WCAG 2.1/2.2 Compliance](#wcag-2122-compliance)
  - [Keyboard Navigation](#keyboard-navigation)
  - [Screen Reader Support](#screen-reader-support)
- [Design System Integration](#design-system-integration)
  - [shadcn/ui Integration](#shadcnui-integration)
  - [Radix UI Primitives](#radix-ui-primitives)
  - [Headless UI Components](#headless-ui-components)
- [Color Contrast & Visual Design](#color-contrast-visual-design)

---
## Design System Fundamentals

### Design Tokens

```typescript
// tokens.ts - Design token system
export const tokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      900: '#1e3a8a',
    },
    neutral: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e5e5e5',
      500: '#737373',
      900: '#0a0a0a',
    },
    semantic: {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
    },
  },
  typography: {
    fontFamily: {
      sans: 'Inter, system-ui, sans-serif',
      mono: 'Fira Code, monospace',
    },
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  spacing: {
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  },
};

// Type-safe token access
export type ColorToken = keyof typeof tokens.colors;
export type SpacingToken = keyof typeof tokens.spacing;
```

### Theme System

```typescript
// theme.ts - Theme provider with CSS variables
'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'light' | 'dark';
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const root = window.document.documentElement;
    const isDark =
      theme === 'dark' ||
      (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

    root.classList.remove('light', 'dark');
    root.classList.add(isDark ? 'dark' : 'light');
    setResolvedTheme(isDark ? 'dark' : 'light');
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

## Accessibility Implementation

### WCAG 2.1/2.2 Compliance

```typescript
// Accessible Modal Component
'use client';

import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

interface ModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
}

export function Modal({ open, onOpenChange, title, description, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!open) return;

    // Store previously focused element
    previousFocusRef.current = document.activeElement as HTMLElement;

    // Focus first focusable element in modal
    const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    firstFocusable?.focus();

    // Trap focus within modal
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onOpenChange(false);
      }

      if (e.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (!focusableElements || focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
      // Restore focus to previously focused element
      previousFocusRef.current?.focus();
    };
  }, [open, onOpenChange]);

  if (!open) return null;

  return createPortal(
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={() => onOpenChange(false)}
        aria-hidden="true"
      />

      {/* Modal dialog */}
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby={description ? 'modal-description' : undefined}
        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-lg shadow-lg p-6 z-50"
      >
        <h2 id="modal-title" className="text-xl font-bold mb-4">
          {title}
        </h2>
        {description && (
          <p id="modal-description" className="text-gray-600 mb-4">
            {description}
          </p>
        )}
        {children}
      </div>
    </>,
    document.body
  );
}
```

### Keyboard Navigation

```typescript
// Accessible Dropdown Menu
'use client';

import React, { useState, useRef, useEffect } from 'react';

interface DropdownProps {
  trigger: React.ReactNode;
  children: React.ReactNode;
}

export function Dropdown({ trigger, children }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (!open) return;

      const items = dropdownRef.current?.querySelectorAll<HTMLElement>('[role="menuitem"]');
      if (!items || items.length === 0) return;

      const currentIndex = Array.from(items).indexOf(document.activeElement as HTMLElement);

      switch (event.key) {
        case 'Escape':
          setOpen(false);
          triggerRef.current?.focus();
          break;
        case 'ArrowDown':
          event.preventDefault();
          const nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
          items[nextIndex].focus();
          break;
        case 'ArrowUp':
          event.preventDefault();
          const prevIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
          items[prevIndex].focus();
          break;
        case 'Home':
          event.preventDefault();
          items[0].focus();
          break;
        case 'End':
          event.preventDefault();
          items[items.length - 1].focus();
          break;
      }
    }

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [open]);

  return (
    <div ref={dropdownRef} className="relative">
      <button
        ref={triggerRef}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        className="inline-flex items-center justify-center"
      >
        {trigger}
      </button>

      {open && (
        <div
          role="menu"
          className="absolute top-full left-0 mt-2 w-48 bg-white border rounded-lg shadow-lg py-1 z-50"
        >
          {children}
        </div>
      )}
    </div>
  );
}

interface DropdownItemProps {
  onSelect: () => void;
  children: React.ReactNode;
}

Dropdown.Item = function DropdownItem({ onSelect, children }: DropdownItemProps) {
  return (
    <button
      role="menuitem"
      className="w-full text-left px-4 py-2 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
      onClick={() => {
        onSelect();
      }}
    >
      {children}
    </button>
  );
};
```

### Screen Reader Support

```typescript
// Live Region Announcer for dynamic content
'use client';

import React, { useEffect, useState } from 'react';

interface AnnouncerProps {
  message: string;
  politeness?: 'polite' | 'assertive';
  clearAfter?: number;
}

export function Announcer({ message, politeness = 'polite', clearAfter = 3000 }: AnnouncerProps) {
  const [announcement, setAnnouncement] = useState('');

  useEffect(() => {
    setAnnouncement(message);

    if (clearAfter) {
      const timer = setTimeout(() => setAnnouncement(''), clearAfter);
      return () => clearTimeout(timer);
    }
  }, [message, clearAfter]);

  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  );
}

// Usage in components
export function FormWithAnnouncement() {
  const [message, setMessage] = useState('');

  const handleSubmit = async () => {
    try {
      // Submit form...
      setMessage('Form submitted successfully');
    } catch (error) {
      setMessage('Error submitting form. Please try again.');
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* form fields */}
      </form>
      <Announcer message={message} />
    </div>
  );
}
```

## Design System Integration

### shadcn/ui Integration

```typescript
// Using shadcn/ui components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

export function UserDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Edit Profile</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit profile</DialogTitle>
          <DialogDescription>
            Make changes to your profile here. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input id="name" className="col-span-3" />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

### Radix UI Primitives

```typescript
// Building custom components with Radix UI
import * as Select from '@radix-ui/react-select';
import { CheckIcon, ChevronDownIcon } from '@radix-ui/react-icons';

export function CustomSelect() {
  return (
    <Select.Root>
      <Select.Trigger className="inline-flex items-center justify-between px-4 py-2 bg-white border rounded-md">
        <Select.Value placeholder="Select an option" />
        <Select.Icon>
          <ChevronDownIcon />
        </Select.Icon>
      </Select.Trigger>

      <Select.Portal>
        <Select.Content className="bg-white border rounded-md shadow-lg">
          <Select.Viewport className="p-1">
            <Select.Item value="option1" className="px-4 py-2 hover:bg-gray-100 cursor-pointer">
              <Select.ItemText>Option 1</Select.ItemText>
              <Select.ItemIndicator className="absolute left-2">
                <CheckIcon />
              </Select.ItemIndicator>
            </Select.Item>
            <Select.Item value="option2" className="px-4 py-2 hover:bg-gray-100 cursor-pointer">
              <Select.ItemText>Option 2</Select.ItemText>
              <Select.ItemIndicator className="absolute left-2">
                <CheckIcon />
              </Select.ItemIndicator>
            </Select.Item>
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
}
```

### Headless UI Components

```typescript
// Using Headless UI with Tailwind
import { Listbox, Transition } from '@headlessui/react';
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/20/solid';
import { Fragment, useState } from 'react';

const people = [
  { id: 1, name: 'Wade Cooper' },
  { id: 2, name: 'Arlene Mccoy' },
];

export function HeadlessListbox() {
  const [selected, setSelected] = useState(people[0]);

  return (
    <Listbox value={selected} onChange={setSelected}>
      <div className="relative">
        <Listbox.Button className="relative w-full cursor-default rounded-lg bg-white py-2 pl-3 pr-10 text-left shadow-md">
          <span className="block truncate">{selected.name}</span>
          <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronUpDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
          </span>
        </Listbox.Button>
        <Transition
          as={Fragment}
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 shadow-lg">
            {people.map((person) => (
              <Listbox.Option
                key={person.id}
                value={person}
                className={({ active }) =>
                  `relative cursor-default select-none py-2 pl-10 pr-4 ${
                    active ? 'bg-amber-100' : ''
                  }`
                }
              >
                {({ selected }) => (
                  <>
                    <span className={`block truncate ${selected ? 'font-medium' : ''}`}>
                      {person.name}
                    </span>
                    {selected && (
                      <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                        <CheckIcon className="h-5 w-5" aria-hidden="true" />
                      </span>
                    )}
                  </>
                )}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}
```

## Color Contrast & Visual Design

```typescript
// Color contrast utilities
export function checkContrast(foreground: string, background: string): {
  ratio: number;
  wcagAA: boolean;
  wcagAAA: boolean;
} {
  // Simplified contrast calculation (use actual library in production)
  const ratio = calculateContrastRatio(foreground, background);

  return {
    ratio,
    wcagAA: ratio >= 4.5,   // WCAG AA for normal text
    wcagAAA: ratio >= 7,    // WCAG AAA for normal text
  };
}

// Component with contrast validation
export function ContrastSafeText({ className }: { className?: string }) {
  const bgColor = '#ffffff';
  const textColor = '#333333';
  const contrast = checkContrast(textColor, bgColor);

  if (!contrast.wcagAA) {
    console.warn('Text color does not meet WCAG AA contrast requirements');
  }

  return (
    <p className={className} data-contrast-ratio={contrast.ratio}>
      Accessible text with sufficient contrast
    </p>
  );
}
```
