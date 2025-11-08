# Performance Review Guide

Common performance issues and optimization patterns across different technologies.

## Database Performance

### 1. N+1 Query Problem

**Symptom**: Making N additional queries in a loop

**Bad**:
```python
# Django ORM
posts = Post.objects.all()
for post in posts:
    print(post.author.name)  # Query for each author!
```

**Good**:
```python
# Use select_related for foreign keys
posts = Post.objects.select_related('author').all()
for post in posts:
    print(post.author.name)  # No additional queries
```

**Detection**: Enable query logging and count queries per request

### 2. Missing Indexes

**What to Check**:
- Foreign key columns indexed
- Columns in WHERE clauses indexed
- Columns in JOIN conditions indexed
- Columns in ORDER BY indexed

**Example**:
```sql
-- Add index for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

### 3. Large Result Sets

**Bad**:
```python
all_users = User.objects.all()  # Loads everything into memory
```

**Good**:
```python
# Pagination
users = User.objects.all()[offset:offset+limit]

# Or use iterator for large datasets
for user in User.objects.iterator(chunk_size=1000):
    process(user)
```

### 4. Unnecessary Columns

**Bad**:
```sql
SELECT * FROM posts;  -- Gets all columns
```

**Good**:
```sql
SELECT id, title, created_at FROM posts;  -- Only needed columns
```

**ORM**:
```python
# Django
posts = Post.objects.values('id', 'title', 'created_at')

# SQLAlchemy
posts = session.query(Post.id, Post.title, Post.created_at)
```

## Algorithm Efficiency

### Time Complexity Issues

#### Linear Search in Loop
**Bad**: O(n²)
```python
def find_common(list1, list2):
    result = []
    for item1 in list1:
        for item2 in list2:  # O(n²)
            if item1 == item2:
                result.append(item1)
    return result
```

**Good**: O(n)
```python
def find_common(list1, list2):
    set2 = set(list2)  # O(n)
    return [item for item in list1 if item in set2]  # O(n)
```

#### Repeated Calculations
**Bad**:
```python
for i in range(len(arr)):
    if arr[i] > sum(arr) / len(arr):  # Recalculates every iteration!
        process(arr[i])
```

**Good**:
```python
average = sum(arr) / len(arr)  # Calculate once
for item in arr:
    if item > average:
        process(item)
```

### Space Complexity Issues

#### Unnecessary Copies
**Bad**:
```python
def process_items(items):
    result = items.copy()  # Unnecessary copy
    result.sort()
    return result
```

**Good**:
```python
def process_items(items):
    return sorted(items)  # Returns new sorted list
```

## Front-End Performance

### 1. Re-renders in React

**Bad**:
```javascript
function Component() {
    // Re-creates function on every render
    const handleClick = () => {
        doSomething();
    };

    return <Child onClick={handleClick} />;
}
```

**Good**:
```javascript
import { useCallback } from 'react';

function Component() {
    const handleClick = useCallback(() => {
        doSomething();
    }, []);  // Memoized

    return <Child onClick={handleClick} />;
}
```

### 2. Large Bundle Size

**Check**:
- [ ] Code splitting implemented
- [ ] Lazy loading for routes
- [ ] Tree shaking enabled
- [ ] No unnecessary dependencies
- [ ] Images optimized

```javascript
// Lazy load routes
const Dashboard = lazy(() => import('./Dashboard'));

// Component lazy loading
const HeavyComponent = lazy(() => import('./HeavyComponent'));

// Use React.memo for expensive components
export default React.memo(ExpensiveComponent);
```

### 3. Unnecessary Re-fetching

**Bad**:
```javascript
useEffect(() => {
    fetchData();  // Runs on every render!
}, []);
```

**Good**:
```javascript
// Use SWR or React Query for caching
import useSWR from 'swr';

const { data } = useSWR('/api/data', fetcher);
```

## Backend Performance

### 1. Synchronous I/O

**Bad**:
```python
def process_request():
    data1 = api_call_1()  # Blocks
    data2 = api_call_2()  # Blocks
    data3 = api_call_3()  # Blocks
    return combine(data1, data2, data3)
```

**Good**:
```python
import asyncio

async def process_request():
    # Run in parallel
    data1, data2, data3 = await asyncio.gather(
        api_call_1(),
        api_call_2(),
        api_call_3()
    )
    return combine(data1, data2, data3)
```

### 2. Missing Caching

**What to Cache**:
- Expensive computations
- External API calls
- Database queries for static data
- Rendered HTML fragments

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param):
    # Complex computation
    return result

# Redis for distributed caching
import redis
cache = redis.Redis()

def get_user(user_id):
    cached = cache.get(f'user:{user_id}')
    if cached:
        return json.loads(cached)

    user = db.get_user(user_id)
    cache.setex(f'user:{user_id}', 300, json.dumps(user))
    return user
```

### 3. Resource Leaks

**Bad**:
```python
def process_file(filename):
    file = open(filename)
    data = file.read()  # File never closed!
    return process(data)
```

**Good**:
```python
def process_file(filename):
    with open(filename) as file:  # Automatically closed
        data = file.read()
    return process(data)
```

## Memory Optimization

### 1. Large Object in Memory

**Bad**:
```python
# Loads entire file into memory
with open('huge_file.txt') as f:
    data = f.read()  # Out of memory for large files
    process(data)
```

**Good**:
```python
# Process line by line
with open('huge_file.txt') as f:
    for line in f:  # Streaming
        process(line)
```

### 2. Memory Leaks

**JavaScript**:
```javascript
// Bad: Event listener not removed
componentDidMount() {
    window.addEventListener('resize', this.handleResize);
}

// Good: Cleanup
componentWillUnmount() {
    window.removeEventListener('resize', this.handleResize);
}
```

**Python**:
```python
# Bad: Circular reference
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

# Good: Use weak references
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self._parent = None  # Use property with weakref
        self.children = []
```

## Network Performance

### 1. Too Many Requests

**Bad**:
```javascript
// Makes 100 separate requests
products.forEach(product => {
    fetch(`/api/product/${product.id}/details`)
});
```

**Good**:
```javascript
// Single batched request
fetch('/api/products/details', {
    method: 'POST',
    body: JSON.stringify({ ids: products.map(p => p.id) })
});
```

### 2. Large Payloads

**Optimize**:
- Use compression (gzip, brotli)
- Paginate results
- Use GraphQL to fetch only needed fields
- Implement field filtering

```python
# Bad: Returns all fields
@app.route('/users')
def get_users():
    return jsonify([user.to_dict() for user in User.query.all()])

# Good: Allow field selection
@app.route('/users')
def get_users():
    fields = request.args.get('fields', 'id,name').split(',')
    users = User.query.all()
    return jsonify([user.to_dict(fields=fields) for user in users])
```

### 3. No CDN for Static Assets

**Check**:
- [ ] Static assets served from CDN
- [ ] Cache headers set correctly
- [ ] Assets versioned/fingerprinted
- [ ] Image optimization (WebP, lazy loading)

## Profiling Tools

### Python
```python
# cProfile
python -m cProfile -o output.prof script.py
python -m pstats output.prof

# line_profiler
@profile
def slow_function():
    ...

# memory_profiler
@profile
def memory_intensive():
    ...
```

### JavaScript
```javascript
// Console timing
console.time('operation');
expensiveOperation();
console.timeEnd('operation');

// Performance API
const start = performance.now();
expensiveOperation();
const duration = performance.now() - start;

// Chrome DevTools
// Use Performance tab for profiling
```

### Database
```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT ...;

-- MySQL
EXPLAIN SELECT ...;

-- Check slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

## Performance Checklist

Quick checklist for performance review:

### Database
- [ ] Queries optimized (no N+1)
- [ ] Indexes on frequently queried columns
- [ ] Connection pooling configured
- [ ] Query result caching where appropriate

### Code
- [ ] Algorithms have reasonable complexity
- [ ] No unnecessary loops or iterations
- [ ] Expensive operations cached
- [ ] Resources properly released

### Frontend
- [ ] Code splitting implemented
- [ ] Images optimized and lazy-loaded
- [ ] Unnecessary re-renders avoided
- [ ] Bundle size reasonable

### Network
- [ ] API responses paginated
- [ ] Compression enabled
- [ ] CDN for static assets
- [ ] Request batching where possible

### Monitoring
- [ ] Performance metrics collected
- [ ] Slow queries logged
- [ ] Application performance monitoring (APM)
- [ ] Alerts for performance degradation

## Common Anti-Patterns

### 1. Premature Optimization
**Don't**: Optimize everything upfront
**Do**: Profile first, optimize bottlenecks

### 2. Over-Optimization
**Don't**: Make code unreadable for minor gains
**Do**: Balance readability and performance

### 3. Ignoring Asymptotic Complexity
**Don't**: Use O(n²) for large datasets
**Do**: Choose appropriate algorithms

### 4. Not Measuring
**Don't**: Guess what's slow
**Do**: Use profiling tools

## Performance Budget

Set and enforce performance budgets:

```javascript
// Example budget
{
  "bundleSize": {
    "main": "200kb",
    "vendor": "150kb"
  },
  "metrics": {
    "firstContentfulPaint": "1.5s",
    "timeToInteractive": "3.0s",
    "largestContentfulPaint": "2.5s"
  }
}
```

Monitor in CI:
```bash
# Lighthouse CI
lhci autorun

# Bundle size check
bundlesize
```

## Resources

- Web.dev Performance: https://web.dev/performance/
- High Performance Browser Networking: https://hpbn.co/
- Python Performance Tips: https://wiki.python.org/moin/PythonSpeed
- Database Performance Tuning: https://use-the-index-luke.com/
