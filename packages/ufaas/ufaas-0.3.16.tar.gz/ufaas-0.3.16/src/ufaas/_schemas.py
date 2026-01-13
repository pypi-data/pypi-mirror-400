"""Pydantic schemas for entities."""

from datetime import datetime, timezone
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

try:
    from fastapi_mongo_base.schemas import (
        BaseEntitySchema,
        PaginatedResponse,
        TenantScopedEntitySchema,
        TenantUserEntitySchema,
        UserOwnedEntitySchema,
    )

    __all__ = [
        "BaseEntitySchema",
        "PaginatedResponse",
        "TenantScopedEntitySchema",
        "TenantUserEntitySchema",
        "UserOwnedEntitySchema",
    ]
except ImportError:

    class BaseEntitySchema(BaseModel):
        """Base Pydantic schema for entities with common fields."""

        uid: str
        created_at: datetime = Field(
            default_factory=lambda: datetime.now(timezone.utc),  # noqa: UP017
        )
        updated_at: datetime = Field(
            default_factory=lambda: datetime.now(timezone.utc),  # noqa: UP017
        )
        is_deleted: bool = False
        meta_data: dict | None = None

        model_config = ConfigDict(
            from_attributes=True, validate_assignment=True
        )

        def __hash__(self) -> int:
            """Compute hash based on serialized model."""
            return hash(self.model_dump_json())

        def expired(self, days: int = 3) -> bool:
            """
            Check if entity has not been updated for specified days.

            Args:
                days: Number of days to check (default: 3).

            Returns:
                True if entity is expired, False otherwise.

            """
            return (datetime.now(timezone.utc) - self.updated_at).days > days  # noqa: UP017

    class UserOwnedEntitySchema(BaseEntitySchema):
        """Schema for entities owned by a user."""

        user_id: str

    class TenantScopedEntitySchema(BaseEntitySchema):
        """Schema for entities scoped to a tenant."""

        tenant_id: str

    class TenantUserEntitySchema(
        TenantScopedEntitySchema, UserOwnedEntitySchema
    ):
        """Schema for entities scoped to both tenant and user."""

    class PaginatedResponse[TSCHEMA: BaseModel](BaseModel):
        """Generic paginated response model for list endpoints."""

        heads: dict[str, dict[str, str]] = Field(default_factory=dict)
        items: list[TSCHEMA]
        total: int
        offset: int
        limit: int

        @model_validator(mode="after")
        def validate_heads(self) -> Self:
            """
            Auto-generate heads dictionary from item fields if not provided.

            Returns:
                Self with heads populated.

            """
            if self.heads:
                return self
            if not self.items:
                return self
            self.heads = {
                field: {"en": field.replace("_", " ").title()}
                for field in self.items[0].__class__.model_fields
            }
            return self
