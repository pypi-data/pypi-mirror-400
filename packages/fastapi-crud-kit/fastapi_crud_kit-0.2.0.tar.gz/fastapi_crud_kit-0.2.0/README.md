# FastAPI CRUD Kit

[![CI](https://github.com/mawuva/fastapi-crud-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/mawuva/fastapi-crud-kit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/fastapi-crud-kit.svg)](https://pypi.org/project/fastapi-crud-kit/)
[![Python Version](https://img.shields.io/pypi/pyversions/fastapi-crud-kit.svg)](https://pypi.org/project/fastapi-crud-kit/)
![GitHub License](https://img.shields.io/github/license/mawuva/fastapi-crud-kit)

A powerful CRUD toolkit for FastAPI with SQLAlchemy, featuring query building, filtering, sorting, and field selection with async/sync support.

## Why FastAPI CRUD Kit?

Building REST APIs with FastAPI and SQLAlchemy often requires writing repetitive CRUD code, handling query parameters, managing database sessions, and implementing common patterns like pagination, filtering, and soft deletes. FastAPI CRUD Kit eliminates this boilerplate by providing:

- **Ready-to-use CRUD operations** that work with any SQLAlchemy model
- **Advanced query building** with automatic parsing and validation of query parameters
- **Production-ready features** like transactions, retries, timeouts, and read-only operations
- **Type-safe operations** with full type hints support
- **Flexible architecture** supporting both async and sync SQLAlchemy sessions

## Features

- 🚀 **Full CRUD Operations**: Create, Read, Update, Delete with minimal boilerplate
- 🔍 **Advanced Query Building**: Filtering, sorting, field selection, and relationship loading
- ⚡ **Async & Sync Support**: Works seamlessly with both async and sync SQLAlchemy sessions
- 🛡️ **Filter Validation**: Configurable filter validation with custom callbacks
- 🔒 **Type Safe**: Full type hints support throughout
- 📦 **Production Ready**: Context managers for transactions, retries, and timeouts
- 🗑️ **Soft Delete**: Built-in support for soft delete functionality
- 📊 **Pagination**: Built-in pagination support with complete metadata

## Installation

```bash
pip install fastapi-crud-kit
```

Or using poetry:

```bash
poetry add fastapi-crud-kit
```

## Quick Example

```python
from fastapi_crud_kit.crud.base import CRUDBase
from fastapi_crud_kit.models import BaseModel
from fastapi_crud_kit.query import AllowedFilters, QueryBuilderConfig, parse_query_params
from sqlalchemy import Column, String

# Define your model
class Category(BaseModel):
    __tablename__ = "categories"
    name = Column(String, nullable=False)

# Create CRUD class
class CategoryCRUD(CRUDBase[Category]):
    def __init__(self):
        query_config = QueryBuilderConfig(
            allowed_filters=[AllowedFilters.exact("name")]
        )
        super().__init__(model=Category, use_async=True, query_config=query_config)

# Use in FastAPI route
@router.get("/categories")
async def list_categories(request: Request, db: AsyncSession = Depends(get_db)):
    query_params = parse_query_params(request.query_params)
    return await category_crud.list_paginated(db, query_params)
```

## How It Works

### CRUD Operations

The `CRUDBase` class provides all standard CRUD operations (`list`, `get`, `create`, `update`, `delete`) that work with any SQLAlchemy model. It automatically handles:

- Query building from URL parameters
- Filter validation and application
- Pagination with metadata
- Soft delete filtering (if supported by the model)
- Relationship loading (eager loading)

### Query Building

The query builder automatically parses and validates query parameters from the request URL:

- **Filters**: `?filter[name]=Tech&filter[price][gte]=100`
- **Sorting**: `?sort=name&sort=-created_at`
- **Field Selection**: `?fields=id,name`
- **Includes**: `?include=products,tags`
- **Pagination**: `?page=1&per_page=20`

All query parameters are validated against your configuration, preventing SQL injection and ensuring type safety.

### Base Models

The package provides ready-to-use base models with common features:

- `BaseModel`: Includes primary key, UUID, timestamps, and soft delete
- `BaseModelWithUUIDPK`: UUID as primary key
- Individual mixins for custom combinations

### Database Management

The `DatabaseFactory` simplifies database setup by automatically detecting the database type and configuring the appropriate drivers. It supports PostgreSQL, MySQL, and SQLite in both async and sync modes.

### Context Managers

Production-ready context managers for common patterns:

- **Transactions**: Automatic commit/rollback
- **Retries**: Exponential backoff for transient failures
- **Timeouts**: Prevent operations from hanging
- **Read-only**: Enforce read-only operations

## Requirements

- Python >= 3.10
- SQLAlchemy >= 2.0.45
- Pydantic >= 2.12.5
- FastAPI >= 0.128.0

## Documentation

Comprehensive documentation with examples, guides, and API reference is available at:

**[https://mawuva.github.io/fastapi-crud-kit/](https://mawuva.github.io/fastapi-crud-kit/)**

Or build it locally:

```bash
mkdocs serve
```

## Examples

See the `examples/` directory for complete working examples.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/mawuva/fastapi-crud-kit).
