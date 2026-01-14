"""API module.

This module contains all API endpoints organized by domain.

Routers:
    - health: Health and readiness checks
    - sources: Data source CRUD operations
    - schemas: Schema learning and management
    - validations: Validation execution and history
    - profile: Data profiling
"""

from .router import api_router

__all__ = ["api_router"]
