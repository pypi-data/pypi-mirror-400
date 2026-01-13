# 🦥 LazyQL

[![PyPI version](https://img.shields.io/pypi/v/lazyql.svg)](https://pypi.org/project/lazyql/)
[![Python versions](https://img.shields.io/pypi/pyversions/lazyql.svg)](https://pypi.org/project/lazyql/)
[![License](https://img.shields.io/pypi/l/lazyql.svg)](https://gitlab.com/creibaud/lazyql/-/blob/main/LICENSE)
[![pipeline status](https://gitlab.com/creibaud/lazyql/badges/main/pipeline.svg)](https://gitlab.com/creibaud/lazyql/-/commits/main)
[![coverage report](https://gitlab.com/creibaud/lazyql/badges/main/coverage.svg)](https://gitlab.com/creibaud/lazyql/-/commits/main)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://gitlab.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

**LazyQL** is a powerful Python library that instantly generates full-featured GraphQL CRUD APIs from **Pydantic** models with **MongoDB** (via Motor). Stop writing boilerplate—focus on your business logic.

---

## ✨ Key Features

- 🚀 **Instant CRUD**: Generate complete GraphQL `Query` and `Mutation` types from Pydantic models in seconds
- 🎯 **Advanced Filtering**: Rich, type-safe filtering system with 15+ operators (contains, gte, in, all, etc.)
- 🔒 **Built-in Security**: Granular permission system for create, update, delete, and list operations
- 📊 **Audit Logging**: Automatic change tracking in MongoDB Time Series collections
- 🗑️ **Soft Deletes**: Native support for soft deletion and restoration
- ⚡ **Async & Fast**: Built on Motor for high-performance asynchronous MongoDB operations
- 🔄 **ACID Transactions**: Full MongoDB transaction support
- 🧩 **Extensible**: Easily customize resolvers, filters, and permissions
- 🏗️ **Nested Models**: Full support for nested Pydantic models in filters and queries
- 📅 **DateTime Support**: Comprehensive datetime filtering with all operators

---

## 📦 Installation

```bash
pip install lazyql
```

Or with Poetry:

```bash
poetry add lazyql
```

**Requirements:**
- Python 3.11+
- MongoDB 4.4+
- Motor 3.7+

---

## ⚡ Quick Start

### 1. Define Your Model

```python
from lazyql import BaseDBModel
from pydantic import Field
from datetime import datetime

class User(BaseDBModel):
    name: str
    email: str
    age: int
    role: str = Field(default="user")
    active: bool = True
    tags: list[str] = []
    created_at: datetime  # Automatically managed
```

### 2. Generate GraphQL API

```python
import strawberry
from motor.motor_asyncio import AsyncIOMotorClient
from lazyql import create_crud_api

# Connect to MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.my_database

# Generate CRUD API
Query, Mutation = create_crud_api(
    model=User,
    collection_name="users"
)

# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### 3. Integrate with FastAPI

```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

app = FastAPI()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

### 4. Use Your API

```graphql
# Query with filters
query {
  users(
    filters: {
      age: { gte: 18, lte: 65 }
      name: { contains: "John" }
      role: { in: ["admin", "user"] }
      active: { eq: true }
    }
    limit: 10
    skip: 0
  ) {
    id
    name
    email
    age
  }
}

# Create mutation
mutation {
  createUser(
    data: {
      name: "John Doe"
      email: "john@example.com"
      age: 30
    }
  ) {
    id
    name
  }
}

# Update mutation
mutation {
  updateUser(
    id: "507f1f77bcf86cd799439011"
    data: { age: 31 }
  ) {
    id
    age
  }
}
```

---

## 🎯 Advanced Features

### Rich Filtering System

LazyQL provides a powerful, type-safe filtering system with nested operators:

```graphql
query {
  users(
    filters: {
      # String operators
      name: { 
        contains: "John"
        startsWith: "J"
        endsWith: "n"
        in: ["John", "Jane"]
      }
      
      # Numeric operators
      age: { 
        gte: 18
        lte: 65
        ne: 25
      }
      
      # List operators
      tags: {
        all: ["verified", "premium"]
        size: 2
      }
      
      # Boolean
      active: { eq: true }
      
      # DateTime
      created_at: {
        gte: "2024-01-01T00:00:00Z"
        lte: "2024-12-31T23:59:59Z"
      }
      
      # Nested models
      profile: {
        address: {
          city: { eq: "Paris" }
        }
      }
    }
  ) {
    id
    name
  }
}
```

**Available Operators:**

| Operator | Description | Types |
|----------|-------------|-------|
| `eq` | Equality | All |
| `ne` | Not equal | All |
| `gt`, `gte` | Greater than (or equal) | Int, Float, DateTime |
| `lt`, `lte` | Less than (or equal) | Int, Float, DateTime |
| `contains` | String contains (case-insensitive) | String |
| `startsWith` | String starts with | String |
| `endsWith` | String ends with | String |
| `in` | Value in list | All scalars |
| `nin` | Value not in list | All scalars |
| `all` | List contains all elements | List |
| `size` | List size | List |
| `exists` | Field exists | All |

### Permissions

Control access to operations with custom permission checkers:

```python
from lazyql import create_crud_api, PermissionChecker
from strawberry.types import Info

def is_admin(info: Info) -> bool:
    """Check if user is admin."""
    user = getattr(info.context, "user", None)
    return user and user.get("role") == "admin"

def is_authenticated(info: Info) -> bool:
    """Check if user is authenticated."""
    return hasattr(info.context, "user") and info.context.user is not None

# Apply permissions
Query, Mutation = create_crud_api(
    model=User,
    collection_name="users",
    permissions={
        "create": is_admin,
        "update": is_authenticated,
        "delete": is_admin,
        "list": is_authenticated,
    }
)
```

### Audit Logging

Automatic audit trail for all mutations:

```python
from lazyql import init_audit_timeseries

# Initialize audit log collection (Time Series optimized)
await init_audit_timeseries(db)

# All mutations are automatically logged:
# - CREATE, UPDATE, DELETE, RESTORE operations
# - Before/after state diffs
# - User who performed the action
# - Timestamp
```

### Soft Deletes

Built-in soft delete support:

```graphql
# Soft delete
mutation {
  deleteUser(id: "507f1f77bcf86cd799439011") {
    id
    deleted_at
  }
}

# Restore
mutation {
  restoreUser(id: "507f1f77bcf86cd799439011") {
    id
    deleted_at
  }
}

# Query excludes soft-deleted by default
query {
  users { id name }  # Only active users
}

# Include deleted
query {
  users(includeDeleted: true) { id name }
}
```

### Nested Models

Full support for nested Pydantic models:

```python
from lazyql import BaseDBModel, register_sub_model

class Address(BaseDBModel):
    street: str
    city: str
    zip_code: str
    country: str

class Profile(BaseDBModel):
    first_name: str
    last_name: str
    address: Address

class User(BaseDBModel):
    name: str
    profile: Profile

# Register nested models
register_sub_model(Address)
register_sub_model(Profile)

# Now you can filter on nested fields:
# filters: { profile: { address: { city: { eq: "Paris" } } } }
```

### Direct Service Usage

Use the service layer directly for custom logic:

```python
from lazyql import LazyQL

service = LazyQL(db, "users", User)

# Get all with filters
users = await service.get_all(
    filters={"age": {"$gte": 18}},
    limit=10,
    skip=0,
    sort_by="age",
    sort_order=-1
)

# Create
user = await service.create(
    User(name="John", email="john@example.com", age=30),
    user="admin"
)

# Update
updated = await service.update(
    id=user.id,
    data={"age": 31},
    user="admin"
)

# Soft delete
await service.delete(id=user.id, user="admin")

# Restore
await service.restore(id=user.id, user="admin")
```

---

## 📚 Documentation

- **[Full Documentation](docs/DOCUMENTATION.md)** - Complete API reference and guides
- **[Filtering Guide](docs/FILTERING.md)** - Deep dive into the filtering system
- **[Permissions Guide](docs/PERMISSIONS.md)** - Security and access control
- **[Examples](examples/)** - Real-world examples and patterns

---

## 🧪 Testing

LazyQL is thoroughly tested with:
- **571 tests** covering all features
- **91% code coverage**
- **59 integration tests** with real MongoDB
- Comprehensive filter operator testing

Run tests:

```bash
poetry run pytest
```

With coverage:

```bash
poetry run pytest --cov=lazyql --cov-report=html
```

---

## 🏗️ Architecture

LazyQL follows clean architecture principles:

- **Service Layer**: `LazyQL` class handles all MongoDB operations
- **Factory Pattern**: `create_crud_api` generates GraphQL types and resolvers
- **Strategy Pattern**: Extensible operator handlers for filters
- **Type Safety**: Full Pydantic and Strawberry type integration

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

LazyQL is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Strawberry GraphQL](https://strawberry.rocks/) - GraphQL library
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Motor](https://motor.readthedocs.io/) - Async MongoDB driver
- [MongoDB](https://www.mongodb.com/) - Database

---

## 📞 Support

- **Issues**: [GitLab Issues](https://gitlab.com/creibaud/lazyql/-/issues)
- **Documentation**: [Full Docs](docs/DOCUMENTATION.md)
- **Repository**: [GitLab](https://gitlab.com/creibaud/lazyql)
