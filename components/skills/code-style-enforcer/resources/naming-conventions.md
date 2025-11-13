# 命名规范详解

> Clean Code原则下的命名最佳实践

## 总体原则

### 有意义的命名

**核心理念**: 代码是写给人看的，其次才是给机器执行的。

```python
# ❌ 糟糕的命名
def calc(d, m):
    return d * m * 0.1

# ✅ 优秀的命名
def calculateDiscount(orderAmount, membershipLevel):
    DISCOUNT_RATE = 0.1
    return orderAmount * membershipLevel * DISCOUNT_RATE
```

---

## 变量命名

### 1. 使用名词或名词短语

```javascript
// ❌ 动词形式
const fetch = getData();
const calculate = getTotalPrice();

// ✅ 名词形式
const userData = getData();
const totalPrice = getTotalPrice();
const calculationResult = calculate();
```

### 2. 避免过短的名称

```typescript
// ❌ 1-2字符
let i, j, k;
const n = users.length;
const t = Date.now();

// ✅ 有意义的名称（除非在极小的作用域内）
let userIndex, rowIndex, columnIndex;
const userCount = users.length;
const currentTimestamp = Date.now();

// ⚠️ 例外：小作用域内的循环计数器
for (let i = 0; i < 10; i++) {
    // 只在这3行内使用，可以接受
}
```

### 3. 布尔变量

**前缀**: `is`, `has`, `should`, `can`, `will`

```python
# ✅ 清晰表达布尔含义
is_active = user.status == 'active'
has_permission = check_permission(user)
should_retry = attempt_count < MAX_RETRIES
can_edit = user.role == 'admin'
will_expire_soon = days_until_expiry < 7
```

### 4. 集合类型

**使用复数形式**

```typescript
// ❌ 单数
const user = await fetchUsers();
const product = getProductList();

// ✅ 复数
const users = await fetchUsers();
const products = getProductList();
```

---

## 函数命名

### 1. 使用动词或动词短语

```javascript
// ❌ 名词形式
function userData() { }
function userList() { }

// ✅ 动词形式
function fetchUserData() { }
function getUserList() { }
function calculateTotal() { }
function validateInput() { }
```

### 2. 常用动词前缀

| 前缀 | 含义 | 示例 |
|------|------|------|
| `get` | 获取数据（通常同步） | `getUserName()` |
| `fetch` | 获取数据（通常异步） | `fetchUserData()` |
| `set` | 设置/更新值 | `setUserRole()` |
| `update` | 更新现有数据 | `updateUserProfile()` |
| `create` | 创建新数据 | `createNewUser()` |
| `delete` | 删除数据 | `deleteUserAccount()` |
| `remove` | 移除（通常指从集合中） | `removeFromCart()` |
| `is`/`has`/`can` | 返回布尔值 | `isValidEmail()` |
| `calculate` | 执行计算 | `calculateTotalPrice()` |
| `validate` | 执行验证 | `validateUserInput()` |
| `handle` | 处理事件 | `handleButtonClick()` |
| `on` | 事件处理器 | `onUserLogin()` |

### 3. 函数长度与命名

```typescript
// ❌ 函数做了很多事，名称却不清楚
function process(data) {
    validate(data);
    transform(data);
    save(data);
    notify(data);
}

// ✅ 明确每个步骤
function processAndSaveUserData(userData) {
    validateUserData(userData);
    const transformedData = transformUserData(userData);
    saveToDatabase(transformedData);
    notifyUserCreation(transformedData);
}

// ✅ 更好的方式：拆分为多个函数
function createUser(userData) {
    validateUserData(userData);
    const user = transformUserData(userData);
    saveUser(user);
    notifyUserCreation(user);
}
```

---

## 类和接口命名

### 1. 使用名词或名词短语

```python
# ❌ 动词或形容词
class Processing:
    pass

class Quick:
    pass

# ✅ 名词
class UserProcessor:
    pass

class QuickSortAlgorithm:
    pass
```

### 2. 接口命名规范

```typescript
// 风格A：使用 I 前缀（C#风格）
interface IUserService {
    getUser(id: string): Promise<User>;
}

// 风格B：不使用前缀（TypeScript推荐）
interface UserService {
    getUser(id: string): Promise<User>;
}

class UserServiceImpl implements UserService {
    // 实现类使用 Impl 后缀
}
```

### 3. 抽象类命名

```java
// ✅ 使用 Abstract 前缀或 Base 前缀
abstract class AbstractDataProcessor {
    // 通用逻辑
}

abstract class BaseRepository<T> {
    // 通用CRUD操作
}
```

---

## 常量命名

### 1. 全大写+下划线

```javascript
// ✅ 常量（不变的配置）
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = 'https://api.example.com';
const DEFAULT_TIMEOUT_MS = 5000;

// ⚠️ 非常量（运行时可能变化）
const userId = getCurrentUserId(); // 不是常量，用小驼峰
```

### 2. 枚举值

```typescript
// ✅ 枚举名用大驼峰，值用大写
enum UserRole {
    ADMIN = 'ADMIN',
    EDITOR = 'EDITOR',
    VIEWER = 'VIEWER'
}

// ✅ 或使用 const enum
const enum HttpStatus {
    OK = 200,
    NOT_FOUND = 404,
    INTERNAL_ERROR = 500
}
```

---

## 特殊场景

### 1. 临时变量

```python
# ✅ 中间结果使用描述性名称
filtered_users = [u for u in users if u.is_active]
sorted_users = sorted(filtered_users, key=lambda u: u.created_at)
paginated_users = sorted_users[offset:offset + limit]

# ❌ 避免
temp1 = [u for u in users if u.is_active]
temp2 = sorted(temp1, key=lambda u: u.created_at)
result = temp2[offset:offset + limit]
```

### 2. 循环变量

```javascript
// ✅ 小作用域可以用单字母
for (let i = 0; i < items.length; i++) {
    console.log(items[i]);
}

// ✅ 复杂循环使用描述性名称
for (let userIndex = 0; userIndex < users.length; userIndex++) {
    for (let orderIndex = 0; orderIndex < users[userIndex].orders.length; orderIndex++) {
        // 嵌套循环，使用清晰的命名
    }
}

// ✅ 使用 for-of 避免索引
for (const user of users) {
    for (const order of user.orders) {
        // 更清晰
    }
}
```

### 3. 回调和事件处理

```typescript
// ✅ 清晰的回调命名
const handleButtonClick = () => { };
const onUserLogin = (user: User) => { };
const afterDataLoad = (data: Data[]) => { };

// ✅ 使用命名函数而非匿名函数
button.addEventListener('click', handleButtonClick);

// ❌ 避免
button.addEventListener('click', () => {
    // 匿名函数难以调试
});
```

---

## 反模式

### ❌ 应该避免的命名

1. **单字母变量**（除了极小作用域）
```python
a = get_data()
b = process(a)
c = save(b)
```

2. **数字后缀**
```javascript
const user1 = getUser1();
const user2 = getUser2();
const temp1, temp2, temp3;
```

3. **模糊的名称**
```python
def do_something(data):
    result = process(data)
    return result
```

4. **缩写过度**
```typescript
function calcTtlPrc(ords: Ord[]): number {
    // calculate total price 简写太多
}
```

5. **匈牙利命名法**（大多数现代语言不推荐）
```csharp
// ❌ 过时的风格
string strUserName;
int intAge;
bool bIsActive;

// ✅ 现代风格
string userName;
int age;
bool isActive;
```

---

## 重构技巧

### 逐步改善命名

```python
# 步骤1：识别不清楚的命名
def calc(d, m):
    return d * m * 0.1

# 步骤2：添加类型提示
def calc(amount: float, level: int) -> float:
    return amount * level * 0.1

# 步骤3：重命名函数
def calculate_discount(amount: float, level: int) -> float:
    return amount * level * 0.1

# 步骤4：提取常量，完善参数命名
DISCOUNT_RATE = 0.1

def calculate_discount(order_amount: float, membership_level: int) -> float:
    """
    计算会员折扣金额

    Args:
        order_amount: 订单总金额
        membership_level: 会员等级（1-5）

    Returns:
        折扣金额
    """
    return order_amount * membership_level * DISCOUNT_RATE
```

---

## 检查清单

### 变量命名自检

- [ ] 是否使用了有意义的名词或名词短语？
- [ ] 是否避免了1-2字符的命名？
- [ ] 布尔变量是否使用了 `is/has/can/should` 前缀？
- [ ] 集合是否使用了复数形式？
- [ ] 是否避免了过度缩写？

### 函数命名自检

- [ ] 是否使用了动词或动词短语？
- [ ] 函数名是否清晰表达了其功能？
- [ ] 是否遵循了团队的命名约定？
- [ ] 是否避免了模糊的名称如 `process`, `handle`, `do`？

### 常量和类命名自检

- [ ] 常量是否使用了全大写+下划线？
- [ ] 类名是否使用了大驼峰（PascalCase）？
- [ ] 是否避免了无意义的前后缀？

---

## 语言特定规范

### JavaScript/TypeScript
- 变量和函数：小驼峰（camelCase）
- 类和接口：大驼峰（PascalCase）
- 常量：全大写+下划线（UPPER_SNAKE_CASE）
- 私有成员：前缀下划线（`_privateMethod`）或使用 `#` (ES2022+)

### Python
- 变量和函数：蛇形命名（snake_case）
- 类：大驼峰（PascalCase）
- 常量：全大写+下划线（UPPER_SNAKE_CASE）
- 私有成员：前缀单下划线（`_private`）或双下划线（`__private`）

### Java
- 变量和方法：小驼峰（camelCase）
- 类和接口：大驼峰（PascalCase）
- 常量：全大写+下划线（UPPER_SNAKE_CASE）
- 包名：全小写，无下划线

### Go
- 公开成员：大写字母开头（Public）
- 私有成员：小写字母开头（private）
- 常量：大驼峰或全大写

---

## 总结

**黄金规则**:
> 如果你需要注释来解释一个变量或函数的作用，说明命名还不够好。

**三秒原则**:
> 其他开发者应该在3秒内理解变量/函数的用途，无需查看实现。

**一致性原则**:
> 在同一项目中保持命名风格一致，比遵循某个特定规范更重要。
