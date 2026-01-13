# Repository + UnitOfWork 模式指南

> **版本要求**: df-test-framework >= 3.7.0
> **更新日期**: 2025-12-24
> **最新版本**: v3.38.0

---

## 概述

本指南介绍如何使用 **Repository 模式** 和 **Unit of Work (UoW) 模式** 进行数据访问层设计。这两种模式是领域驱动设计（DDD）的核心模式，提供：

- **Repository** - 封装数据访问逻辑，提供类似集合的接口
- **Unit of Work** - 管理事务边界，维护业务对象的变更追踪

### 核心特性

- ✅ 统一的事务边界管理
- ✅ 多个 Repository 共享同一 Session
- ✅ 显式的提交/回滚控制
- ✅ 测试友好的数据隔离
- ✅ EventBus 集成（v3.14.0+）
- ✅ 自动发现 Repository（P1-2 模式）

---

## 快速开始

### 1. 定义 Repository

```python
from df_test_framework.capabilities.databases.repositories import BaseRepository
from sqlalchemy.orm import Session

class UserRepository(BaseRepository):
    """用户数据访问"""

    def __init__(self, session: Session):
        super().__init__(session, table_name="users")

    def find_by_username(self, username: str) -> dict | None:
        """根据用户名查找用户"""
        return self.find_one({"username": username})

    def find_active_users(self) -> list[dict]:
        """查找所有激活用户"""
        return self.find_all({"status": "ACTIVE"})

    def count_by_role(self, role: str) -> int:
        """统计指定角色的用户数"""
        return self.count({"role": role})
```

### 2. 定义 UnitOfWork

```python
from df_test_framework.capabilities.databases import UnitOfWork
from sqlalchemy.orm import Session

class MyProjectUoW(UnitOfWork):
    """项目 Unit of Work"""

    def __init__(self, session_factory, event_bus=None):
        super().__init__(session_factory, event_bus=event_bus)

    @property
    def users(self) -> UserRepository:
        """用户 Repository"""
        if not hasattr(self, "_users"):
            self._users = UserRepository(self.session)
        return self._users

    @property
    def orders(self) -> OrderRepository:
        """订单 Repository"""
        if not hasattr(self, "_orders"):
            self._orders = OrderRepository(self.session)
        return self._orders
```

### 3. 在测试中使用

```python
import pytest
from df_test_framework import Database

@pytest.fixture(scope="session")
def database():
    """数据库连接"""
    db = Database(
        host="localhost",
        port=3306,
        user="test",
        password="test",
        database="test_db"
    )
    yield db
    db.close()

@pytest.fixture
def uow(database):
    """Unit of Work"""
    with MyProjectUoW(database.session_factory) as uow:
        yield uow
        # 自动回滚（除非已 commit）

def test_create_user(uow):
    """测试创建用户"""
    # 创建用户
    user_data = {
        "username": "alice",
        "email": "alice@example.com",
        "status": "ACTIVE"
    }
    user_id = uow.users.create(user_data)

    # 提交事务
    uow.commit()

    # 验证
    user = uow.users.find_by_id(user_id)
    assert user["username"] == "alice"
```

---

## Repository 基类 API

### 查询方法

#### `find_by_id(id_value, id_column="id")`

根据 ID 查找记录：

```python
# 默认使用 id 列
user = repo.find_by_id(123)

# 指定 ID 列
user = repo.find_by_id("user_001", id_column="user_id")
```

#### `find_one(conditions)`

根据条件查找单条记录：

```python
user = repo.find_one({"username": "alice", "status": "ACTIVE"})
```

#### `find_all(conditions, order_by=None, limit=None, offset=None)`

根据条件查找多条记录：

```python
# 查找所有激活用户
users = repo.find_all({"status": "ACTIVE"})

# 排序和分页
users = repo.find_all(
    {"status": "ACTIVE"},
    order_by="created_at DESC",
    limit=20,
    offset=0
)
```

#### `count(conditions=None)`

统计记录数：

```python
# 统计所有记录
total = repo.count()

# 条件统计
active_count = repo.count({"status": "ACTIVE"})
```

#### `exists(conditions)`

检查记录是否存在：

```python
if repo.exists({"username": "alice"}):
    print("用户已存在")
```

### 修改方法

#### `create(data)`

创建记录：

```python
user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "status": "ACTIVE"
}
user_id = repo.create(user_data)
```

#### `update(conditions, data)`

更新记录：

```python
# 更新指定用户
affected = repo.update(
    {"username": "alice"},
    {"email": "alice_new@example.com"}
)
```

#### `delete(conditions)`

删除记录：

```python
# 删除指定用户
affected = repo.delete({"username": "alice"})
```

---

## Unit of Work 模式

### 核心概念

**Unit of Work (工作单元)** 维护受业务事务影响的对象列表，并协调变更的写入和并发问题的解决。

### 基本用法

```python
from df_test_framework.capabilities.databases import UnitOfWork

# 作为上下文管理器（推荐）
with UnitOfWork(session_factory) as uow:
    # 1. 执行业务操作
    user = uow.users.find_by_username("alice")
    uow.orders.create({"user_id": user["id"], "amount": 100})

    # 2. 显式提交
    uow.commit()
    # 如果不调用 commit()，退出时自动回滚
```

### 事务控制

#### `commit()`

提交事务：

```python
with UnitOfWork(session_factory) as uow:
    uow.users.create({"username": "alice"})
    uow.commit()  # 提交更改
```

#### `rollback()`

回滚事务：

```python
with UnitOfWork(session_factory) as uow:
    try:
        uow.users.create({"username": "alice"})
        uow.orders.create({"user_id": 999})  # 可能失败
        uow.commit()
    except Exception as e:
        uow.rollback()  # 回滚所有更改
        raise
```

### 共享 Session

Unit of Work 中的所有 Repository 共享同一 Session：

```python
with UnitOfWork(session_factory) as uow:
    # 所有操作在同一事务中
    user_id = uow.users.create({"username": "alice"})
    uow.orders.create({"user_id": user_id, "amount": 100})
    uow.payments.create({"order_id": ..., "amount": 100})

    # 一次性提交所有更改
    uow.commit()
```

---

## 高级用法

### 1. EventBus 集成（v3.14.0+）

Unit of Work 可以发布事务事件：

```python
from df_test_framework.infrastructure.events import EventBus

event_bus = EventBus()
uow = MyProjectUoW(session_factory, event_bus=event_bus)

# 订阅事务事件
@event_bus.subscribe("transaction.committed")
def on_committed(event):
    print(f"事务已提交: {event.timestamp}")

with uow:
    uow.users.create({"username": "alice"})
    uow.commit()  # 触发 transaction.committed 事件
```

### 2. 自动发现 Repository（P1-2 模式）

```python
class MyProjectUoW(UnitOfWork):
    """自动发现 repositories 包下的所有 Repository"""

    def __init__(self, session_factory):
        super().__init__(
            session_factory,
            repository_package="my_project.repositories"
        )
        # ✅ 自动发现并注册所有 Repository

# 使用
with MyProjectUoW(session_factory) as uow:
    # 自动注册的 Repository 可直接使用
    user = uow.users.find_by_username("alice")
    order = uow.orders.find_by_id(123)
```

### 3. 嵌套事务

```python
with UnitOfWork(session_factory) as outer_uow:
    user_id = outer_uow.users.create({"username": "alice"})

    # 内部 UoW 使用 savepoint
    with UnitOfWork(session_factory) as inner_uow:
        inner_uow.orders.create({"user_id": user_id})
        inner_uow.commit()  # 提交到 savepoint

    outer_uow.commit()  # 提交整个事务
```

### 4. 扩展 Repository

```python
class UserRepository(BaseRepository):
    """扩展 Repository 添加业务方法"""

    def find_by_email(self, email: str) -> dict | None:
        """根据邮箱查找用户"""
        return self.find_one({"email": email})

    def activate_user(self, user_id: int) -> int:
        """激活用户"""
        return self.update(
            {"id": user_id},
            {"status": "ACTIVE", "activated_at": "NOW()"}
        )

    def find_users_by_role_with_orders(self, role: str) -> list[dict]:
        """查找指定角色的用户及其订单（自定义 SQL）"""
        sql = """
            SELECT u.*, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.role = :role
            GROUP BY u.id
        """
        return self._query_all(sql, {"role": role})
```

---

## pytest 集成

### 基本 Fixture

```python
import pytest
from df_test_framework import Database

@pytest.fixture(scope="session")
def database():
    """数据库连接"""
    db = Database.from_env()
    yield db
    db.close()

@pytest.fixture
def uow(database, event_bus):
    """Unit of Work（带事件总线）"""
    with MyProjectUoW(database.session_factory, event_bus=event_bus) as uow:
        yield uow
        # 自动回滚，确保测试隔离
```

### 测试数据隔离

```python
def test_user_creation(uow):
    """测试用户创建（自动回滚）"""
    # 创建测试数据
    user_id = uow.users.create({"username": "test_user"})
    uow.commit()

    # 验证
    user = uow.users.find_by_id(user_id)
    assert user["username"] == "test_user"

    # fixture 结束时自动回滚，不影响其他测试
```

### 使用 CleanupManager

```python
from df_test_framework import CleanupManager

def test_user_with_cleanup(uow, cleanup):
    """测试用户创建（使用 CleanupManager）"""
    user_id = uow.users.create({"username": "test_user"})
    uow.commit()

    # 注册清理
    cleanup.add("users", user_id)

    # 测试逻辑...
```

---

## 最佳实践

### 1. Repository 职责单一

```python
# ✅ 好的实践 - Repository 只负责数据访问
class UserRepository(BaseRepository):
    def find_by_username(self, username: str) -> dict | None:
        return self.find_one({"username": username})

# ❌ 不好的实践 - 不要在 Repository 中处理业务逻辑
class UserRepository(BaseRepository):
    def authenticate(self, username: str, password: str) -> dict | None:
        user = self.find_one({"username": username})
        if user and verify_password(password, user["password_hash"]):
            return user
        return None
```

### 2. UoW 管理事务边界

```python
# ✅ 好的实践 - UoW 控制事务
def create_order_with_payment(uow, order_data, payment_data):
    order_id = uow.orders.create(order_data)
    payment_data["order_id"] = order_id
    uow.payments.create(payment_data)
    uow.commit()  # 一次性提交

# ❌ 不好的实践 - Repository 不应该提交事务
class OrderRepository(BaseRepository):
    def create_with_commit(self, data):
        order_id = self.create(data)
        self.session.commit()  # ❌ 不要这样做
        return order_id
```

### 3. 显式提交

```python
# ✅ 好的实践 - 显式提交
with UnitOfWork(session_factory) as uow:
    uow.users.create(data)
    uow.commit()  # 明确提交

# ❌ 不好的实践 - 依赖自动提交
with UnitOfWork(session_factory) as uow:
    uow.users.create(data)
    # 没有 commit()，会自动回滚
```

### 4. 测试隔离

```python
# ✅ 好的实践 - 使用 fixture 自动回滚
@pytest.fixture
def uow(database):
    with MyProjectUoW(database.session_factory) as uow:
        yield uow
        # 自动回滚

# ❌ 不好的实践 - 手动清理数据
def test_user_creation(database):
    uow = MyProjectUoW(database.session_factory)
    user_id = uow.users.create(data)
    uow.commit()
    # ... 测试
    uow.users.delete({"id": user_id})  # ❌ 不推荐
```

---

## 常见问题

### Q: Repository 和 DAO 的区别？

**Repository** 使用领域语言（如 `find_by_username`），而 **DAO** 使用数据库语言（如 `selectByUsername`）。Repository 更面向领域模型。

### Q: 为什么 Repository 返回字典而不是模型？

为了灵活性。你可以在 Repository 方法中转换为 Pydantic 模型：

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str

class UserRepository(BaseRepository):
    def find_by_username(self, username: str) -> User | None:
        data = self.find_one({"username": username})
        return User(**data) if data else None
```

### Q: 如何处理复杂查询？

使用 `_query_all()` 或 `_query_one()` 执行原生 SQL：

```python
def find_with_complex_join(self) -> list[dict]:
    sql = """
        SELECT u.*, p.name as profile_name
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.status = :status
    """
    return self._query_all(sql, {"status": "ACTIVE"})
```

---

## 相关文档

- [数据库使用指南](test_data.md)
- [测试数据清理指南](test_data_cleanup.md)
- [EventBus 使用指南](event_bus_guide.md)
