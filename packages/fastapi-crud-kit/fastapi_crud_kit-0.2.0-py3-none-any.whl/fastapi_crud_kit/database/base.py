"""
Base declarative SQLAlchemy shared.

This module exports the declarative base that must be used by all
models to ensure consistency and allow migrations.
"""

from sqlalchemy.ext.declarative import declarative_base

# Shared declarative base
# All models must inherit from this Base
Base = declarative_base()

__all__ = ["Base"]
