# Async Programming Patterns

## Promises

```javascript
const fetchData = (url) => {
  return fetch(url)
    .then(response => response.json())
    .catch(error => {
      console.error('Fetch failed:', error);
      throw error;
    });
};
```

## Async/Await (Preferred)

```javascript
async function fetchData(url) {
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error('Fetch failed:', error);
    throw error;
  }
}
```

## Promise Combinators

```javascript
// Promise.all - run in parallel, fail if any fails
const results = await Promise.all([
  fetchUser(1),
  fetchUser(2),
  fetchUser(3)
]);

// Promise.race - first to complete wins
const firstResult = await Promise.race([
  fetchWithTimeout(url, 5000),
  fallbackFetch(url)
]);

// Promise.allSettled - wait for all, never fails
const settled = await Promise.allSettled([
  riskyOperation1(),
  riskyOperation2()
]);
// settled[0].status = 'fulfilled' | 'rejected'
// settled[0].value or settled[0].reason
```

## Async Generators

```javascript
async function* fetchPages(baseUrl, maxPages) {
  for (let page = 1; page <= maxPages; page++) {
    const data = await fetch(`${baseUrl}?page=${page}`);
    yield await data.json();
  }
}

// Usage
for await (const pageData of fetchPages('/api/items', 10)) {
  processPage(pageData);
}
```

## Event Loop and Microtask Queue

```javascript
// Understanding execution order
console.log('1: Synchronous');

setTimeout(() => console.log('2: Macrotask (setTimeout)'), 0);

Promise.resolve().then(() => console.log('3: Microtask (Promise)'));

queueMicrotask(() => console.log('4: Microtask (queueMicrotask)'));

console.log('5: Synchronous');

// Output: 1, 5, 3, 4, 2
// Microtasks always run before next macrotask
```

## Common Pitfalls

### Blocking the Event Loop

```javascript
// BAD - blocks event loop
function blockingOperation() {
  const start = Date.now();
  while (Date.now() - start < 5000) {} // Blocks for 5 seconds
}

// GOOD - non-blocking with async
async function nonBlockingOperation() {
  await new Promise(resolve => setTimeout(resolve, 5000));
  // Event loop can process other tasks during wait
}
```

## Error Handling

```javascript
// Centralized error handling
class ApplicationError extends Error {
  constructor(message, statusCode = 500, details = {}) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.details = details;
    Error.captureStackTrace(this, this.constructor);
  }
}

// Async error handling with proper propagation
async function handleRequest(req, res) {
  try {
    const data = await fetchData(req.params.id);
    res.json(data);
  } catch (error) {
    if (error instanceof ApplicationError) {
      res.status(error.statusCode).json({
        error: error.message,
        details: error.details
      });
    } else {
      console.error('Unexpected error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

// Promise error handling with recovery
Promise.resolve()
  .then(step1)
  .then(step2)
  .catch(error => {
    console.error('Pipeline failed:', error);
    return fallbackValue; // Recover from error
  })
  .finally(() => {
    closeConnections(); // Always runs (cleanup)
  });
```
