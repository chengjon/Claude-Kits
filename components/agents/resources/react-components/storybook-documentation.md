# Storybook Documentation & Testing

Complete guide to component documentation with Storybook, including setup, writing stories, visual testing, and documentation patterns.

## 📑 Table of Contents

- [Storybook Setup & Configuration](#storybook-setup--configuration)
  - [Installation & Basic Setup](#installation--basic-setup)
  - [Storybook Configuration](#storybook-configuration)
- [Writing Component Stories](#writing-component-stories)
  - [Basic Story Pattern](#basic-story-pattern)
  - [Interactive Stories with Play Functions](#interactive-stories-with-play-functions)
  - [Complex Component Stories](#complex-component-stories)
- [Component Variants & Controls](#component-variants--controls)
  - [Advanced ArgTypes Configuration](#advanced-argtypes-configuration)
- [Visual Testing](#visual-testing)
  - [Accessibility Testing](#accessibility-testing)
  - [Snapshot Testing](#snapshot-testing)
- [Documentation Patterns](#documentation-patterns)
  - [MDX Documentation](#mdx-documentation)
  - [Component Documentation Template](#component-documentation-template)
- [Component Testing](#component-testing)
  - [Unit Tests for Components](#unit-tests-for-components)
  - [Integration Tests](#integration-tests)
- [Best Practices](#best-practices)
  - [Story Organization](#story-organization)
  - [Testing Strategy](#testing-strategy)
  - [Documentation Guidelines](#documentation-guidelines)

---

## Storybook Setup & Configuration

### Installation & Basic Setup

```bash
# Install Storybook for Next.js
npx storybook@latest init

# Install addons
npm install --save-dev @storybook/addon-a11y @storybook/addon-interactions @storybook/testing-library
```

### Storybook Configuration

```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/nextjs';

const config: StorybookConfig = {
  stories: ['../components/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
  ],
  framework: {
    name: '@storybook/nextjs',
    options: {},
  },
  docs: {
    autodocs: 'tag',
  },
  staticDirs: ['../public'],
};

export default config;
```

```typescript
// .storybook/preview.ts
import type { Preview } from '@storybook/react';
import '../app/globals.css';

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#0a0a0a' },
      ],
    },
  },
};

export default preview;
```

## Writing Component Stories

### Basic Story Pattern

```typescript
// Button.stories.ts
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Atoms/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'destructive', 'outline'],
      description: 'The visual style variant of the button',
      table: {
        type: { summary: 'string' },
        defaultValue: { summary: 'primary' },
      },
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg', 'icon'],
      description: 'The size of the button',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the button is disabled',
    },
    loading: {
      control: 'boolean',
      description: 'Whether the button is in loading state',
    },
    onClick: {
      action: 'clicked',
      description: 'Click event handler',
    },
  },
  parameters: {
    docs: {
      description: {
        component: 'A flexible button component with multiple variants and sizes.',
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
  },
};

export const Destructive: Story = {
  args: {
    children: 'Delete',
    variant: 'destructive',
  },
};

export const Loading: Story = {
  args: {
    children: 'Loading...',
    loading: true,
  },
};

export const AllSizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All available button sizes displayed together.',
      },
    },
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex gap-4">
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost</Button>
      </div>
      <div className="flex gap-4">
        <Button variant="destructive">Destructive</Button>
        <Button variant="outline">Outline</Button>
      </div>
    </div>
  ),
};
```

### Interactive Stories with Play Functions

```typescript
// Form.stories.ts
import type { Meta, StoryObj } from '@storybook/react';
import { userEvent, within, expect } from '@storybook/test';
import { LoginForm } from './LoginForm';

const meta: Meta<typeof LoginForm> = {
  title: 'Components/Forms/LoginForm',
  component: LoginForm,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithValidation: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Type invalid email
    const emailInput = canvas.getByLabelText(/email/i);
    await userEvent.type(emailInput, 'invalid-email');

    // Submit form
    const submitButton = canvas.getByRole('button', { name: /submit/i });
    await userEvent.click(submitButton);

    // Expect validation error
    await expect(canvas.getByText(/invalid email format/i)).toBeInTheDocument();
  },
};

export const SuccessfulSubmit: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Fill in valid data
    await userEvent.type(canvas.getByLabelText(/email/i), 'user@example.com');
    await userEvent.type(canvas.getByLabelText(/password/i), 'password123');

    // Submit form
    await userEvent.click(canvas.getByRole('button', { name: /submit/i }));

    // Expect success message (mock the API call in the component)
    await expect(canvas.getByText(/logged in successfully/i)).toBeInTheDocument();
  },
};
```

### Complex Component Stories

```typescript
// DataTable.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { DataTable } from './DataTable';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

const meta: Meta<typeof DataTable<User>> = {
  title: 'Components/Organisms/DataTable',
  component: DataTable,
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <div className="p-8">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof meta>;

const mockUsers: User[] = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User' },
];

export const Default: Story = {
  args: {
    data: mockUsers,
    columns: [
      { header: 'Name', accessor: 'name' },
      { header: 'Email', accessor: 'email' },
      { header: 'Role', accessor: 'role' },
    ],
  },
};

export const WithSorting: Story = {
  args: {
    data: mockUsers,
    columns: [
      { header: 'Name', accessor: 'name', sortable: true },
      { header: 'Email', accessor: 'email', sortable: true },
      { header: 'Role', accessor: 'role', sortable: true },
    ],
  },
};

export const Loading: Story = {
  args: {
    data: [],
    columns: [
      { header: 'Name', accessor: 'name' },
      { header: 'Email', accessor: 'email' },
      { header: 'Role', accessor: 'role' },
    ],
    loading: true,
  },
};

export const Empty: Story = {
  args: {
    data: [],
    columns: [
      { header: 'Name', accessor: 'name' },
      { header: 'Email', accessor: 'email' },
      { header: 'Role', accessor: 'role' },
    ],
    emptyMessage: 'No users found',
  },
};
```

## Component Variants & Controls

### Advanced ArgTypes Configuration

```typescript
// Card.stories.ts
import type { Meta, StoryObj } from '@storybook/react';
import { Card } from './Card';

const meta: Meta<typeof Card> = {
  title: 'Components/Molecules/Card',
  component: Card,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'bordered', 'elevated', 'ghost'],
      description: 'Visual variant of the card',
      table: {
        category: 'Appearance',
        defaultValue: { summary: 'default' },
      },
    },
    padding: {
      control: { type: 'select' },
      options: ['none', 'sm', 'md', 'lg'],
      description: 'Internal padding of the card',
      table: {
        category: 'Spacing',
      },
    },
    radius: {
      control: { type: 'select' },
      options: ['none', 'sm', 'md', 'lg', 'full'],
      description: 'Border radius of the card',
      table: {
        category: 'Appearance',
      },
    },
    background: {
      control: { type: 'color' },
      description: 'Background color override',
      table: {
        category: 'Appearance',
      },
    },
    onClick: {
      action: 'clicked',
      description: 'Click handler for interactive cards',
      table: {
        category: 'Events',
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Playground: Story = {
  args: {
    children: 'Card content',
    variant: 'default',
    padding: 'md',
    radius: 'md',
  },
};
```

## Visual Testing

### Accessibility Testing

```typescript
// Button.stories.ts with a11y
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Atoms/Button',
  component: Button,
  parameters: {
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
          {
            id: 'button-name',
            enabled: true,
          },
        ],
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const AccessibleButton: Story = {
  args: {
    children: 'Accessible Button',
  },
  parameters: {
    a11y: {
      element: 'button',
    },
  },
};
```

### Snapshot Testing

```typescript
// Button.test.tsx
import { composeStories } from '@storybook/react';
import { render } from '@testing-library/react';
import * as stories from './Button.stories';

const { Primary, Secondary, Loading } = composeStories(stories);

describe('Button Snapshots', () => {
  test('Primary button matches snapshot', () => {
    const { container } = render(<Primary />);
    expect(container).toMatchSnapshot();
  });

  test('Secondary button matches snapshot', () => {
    const { container } = render(<Secondary />);
    expect(container).toMatchSnapshot();
  });

  test('Loading button matches snapshot', () => {
    const { container } = render(<Loading />);
    expect(container).toMatchSnapshot();
  });
});
```

## Documentation Patterns

### MDX Documentation

```mdx
{/* Button.mdx */}
import { Meta, Canvas, Story, Controls } from '@storybook/blocks';
import * as ButtonStories from './Button.stories';

<Meta of={ButtonStories} />

# Button

A versatile button component that supports multiple variants, sizes, and states.

## Features

- Multiple visual variants (primary, secondary, ghost, destructive, outline)
- Flexible sizing options (sm, md, lg, icon)
- Loading state support
- Full accessibility with keyboard navigation and screen reader support
- TypeScript support with full type safety

## Usage

```tsx
import { Button } from '@/components/ui/button';

export function MyComponent() {
  return (
    <Button variant="primary" size="md" onClick={() => console.log('clicked')}>
      Click me
    </Button>
  );
}
```

## Variants

<Canvas of={ButtonStories.AllVariants} />

## Sizes

<Canvas of={ButtonStories.AllSizes} />

## API

<Controls of={ButtonStories.Primary} />

## Accessibility

This component follows WCAG 2.1 Level AA standards:

- Keyboard accessible with Enter and Space keys
- Proper focus indicators
- Screen reader friendly with semantic HTML
- Sufficient color contrast ratios
- Disabled state properly announced

## Best Practices

- Use `primary` for main call-to-action buttons
- Use `secondary` for alternative actions
- Use `destructive` for dangerous actions (delete, remove)
- Use `ghost` for tertiary actions or toolbar buttons
- Always provide meaningful button text (avoid "Click here")
```

### Component Documentation Template

```typescript
// ComponentName.stories.ts - Complete documentation template
import type { Meta, StoryObj } from '@storybook/react';
import { ComponentName } from './ComponentName';

const meta: Meta<typeof ComponentName> = {
  title: 'Category/ComponentName',
  component: ComponentName,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
# ComponentName

Brief description of what this component does and when to use it.

## Features

- Feature 1
- Feature 2
- Feature 3

## When to Use

Describe the use cases for this component.

## Accessibility

Describe accessibility features and WCAG compliance.
        `,
      },
    },
  },
  argTypes: {
    // Define all props with descriptions
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// 1. Default story
export const Default: Story = {
  args: {
    // Default props
  },
};

// 2. All variants story
export const AllVariants: Story = {
  render: () => (
    <div className="space-y-4">
      {/* Show all variants */}
    </div>
  ),
};

// 3. Interactive story
export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    // User interactions
  },
};

// 4. Edge cases
export const EdgeCases: Story = {
  render: () => (
    <div className="space-y-4">
      {/* Show edge cases: empty, loading, error states */}
    </div>
  ),
};

// 5. Real-world example
export const RealWorldExample: Story = {
  render: () => (
    // Show component in realistic context
  ),
};
```

## Component Testing

### Unit Tests for Components

```typescript
// Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles correctly', () => {
    const { container } = render(<Button variant="secondary">Secondary</Button>);
    const button = container.querySelector('button');
    expect(button).toHaveClass('bg-gray-200');
  });

  it('is keyboard accessible', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    const button = screen.getByRole('button');
    button.focus();
    await userEvent.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalled();

    await userEvent.keyboard(' ');
    expect(handleClick).toHaveBeenCalledTimes(2);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Button</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });
});
```

### Integration Tests

```typescript
// Form.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('validates email format', async () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    await userEvent.type(emailInput, 'invalid-email');
    await userEvent.tab();

    expect(screen.getByText(/invalid email format/i)).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    const onSubmit = jest.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'password123',
    });
  });

  it('shows error message on failed submission', async () => {
    const onSubmit = jest.fn().mockRejectedValue(new Error('Login failed'));
    render(<LoginForm onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(await screen.findByText(/login failed/i)).toBeInTheDocument();
  });
});
```

## Best Practices

### Story Organization

1. **Naming**: Use clear, descriptive names for stories (Default, AllVariants, WithError, etc.)
2. **Categories**: Organize with title hierarchy: `Components/Atoms/Button`, `Components/Molecules/Card`
3. **Documentation**: Always include descriptions for component and individual stories
4. **Controls**: Define argTypes for all important props with descriptions

### Testing Strategy

1. **Unit Tests**: Test individual component behavior
2. **Integration Tests**: Test component interactions
3. **Visual Tests**: Use Storybook for visual regression
4. **Accessibility Tests**: Use @storybook/addon-a11y
5. **Interaction Tests**: Use play functions for user flows

### Documentation Guidelines

1. **Component Description**: Clear explanation of purpose and use cases
2. **Props Documentation**: Document all props with types and descriptions
3. **Examples**: Provide realistic usage examples
4. **Accessibility**: Document WCAG compliance and keyboard navigation
5. **Best Practices**: Include do's and don'ts
