# Language-Specific Code Review Guidelines

## Python

### Style (PEP 8)
- Use 4 spaces for indentation
- Max line length: 79 characters (code), 72 (comments)
- Two blank lines between top-level definitions
- Snake_case for functions and variables
- PascalCase for classes

### Type Hints
```python
def process_data(items: list[str], count: int = 10) -> dict[str, int]:
    ...
```

### Context Managers
```python
# Good: Automatic resource cleanup
with open('file.txt') as f:
    data = f.read()
```

### List Comprehensions
```python
# Good: Concise and readable
squares = [x**2 for x in range(10)]

# Bad: Too complex
result = [x for sublist in matrix for x in sublist if x > 0 and x % 2 == 0]
```

## JavaScript/TypeScript

### Modern Syntax
```javascript
// Use const/let, not var
const API_KEY = 'xxx';
let counter = 0;

// Arrow functions for short callbacks
items.map(item => item.id);

// Destructuring
const { name, age } = user;
const [first, ...rest] = array;

// Template literals
console.log(`Hello ${name}`);
```

### Async/Await
```javascript
// Good: Clear async flow
async function fetchData() {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}
```

### TypeScript Types
```typescript
interface User {
    id: number;
    name: string;
    email?: string;  // Optional
}

type Status = 'pending' | 'active' | 'completed';  // Union type
```

## Java

### Naming Conventions
- Classes: PascalCase
- Methods/variables: camelCase
- Constants: UPPER_SNAKE_CASE
- Packages: lowercase

### Streams API (Java 8+)
```java
// Good: Functional style
List<String> names = users.stream()
    .filter(user -> user.isActive())
    .map(User::getName)
    .collect(Collectors.toList());
```

### Optional
```java
// Avoid null pointer exceptions
Optional<User> user = findUser(id);
user.ifPresent(u -> sendEmail(u.getEmail()));

String name = user.map(User::getName).orElse("Unknown");
```

## Go

### Error Handling
```go
// Always check errors
data, err := os.ReadFile("file.txt")
if err != nil {
    return fmt.Errorf("failed to read file: %w", err)
}
```

### Goroutines
```go
// Use channels for communication
ch := make(chan int)

go func() {
    result := heavyComputation()
    ch <- result
}()

result := <-ch
```

### defer
```go
func processFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()  // Always executed

    // Process file...
    return nil
}
```

## Common Patterns Across Languages

### Dependency Injection
```python
# Good: Testable
class UserService:
    def __init__(self, db: Database):
        self.db = db

# Bad: Hard to test
class UserService:
    def __init__(self):
        self.db = Database()  # Hard-coded dependency
```

### Single Responsibility Principle
```python
# Bad: Does too much
class UserManager:
    def create_user(self): ...
    def send_email(self): ...
    def log_activity(self): ...
    def generate_report(self): ...

# Good: Focused responsibility
class UserService:
    def create_user(self): ...
    def update_user(self): ...

class EmailService:
    def send_email(self): ...
```

### Don't Repeat Yourself (DRY)
```python
# Bad: Repeated logic
def process_order(order):
    if order.status == 'pending':
        validate(order)
        calculate_total(order)
        apply_discount(order)
        save(order)

def process_quote(quote):
    if quote.status == 'draft':
        validate(quote)
        calculate_total(quote)
        apply_discount(quote)
        save(quote)

# Good: Extract common logic
def finalize_document(doc):
    validate(doc)
    calculate_total(doc)
    apply_discount(doc)
    save(doc)
```

See official style guides for complete guidelines.
