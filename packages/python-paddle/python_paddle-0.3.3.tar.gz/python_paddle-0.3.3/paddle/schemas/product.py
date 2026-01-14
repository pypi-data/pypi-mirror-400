from __future__ import annotations

from typing import Annotated

from pydantic import AnyUrl, BaseModel, Field

from . import (
    CatalogType,
    CreatedAt,
    CustomData,
    Event,
    ImportMeta,
    NotificationId,
    ProductId,
    Status,
    TaxCategory,
    UpdatedAt,
)


class Data(BaseModel):
    id: ProductId | None = None
    name: Annotated[str, Field(min_length=1, max_length=200)] | None = Field(
        None, description="Name of this product."
    )
    description: Annotated[str, Field(max_length=2048)] | None = Field(
        None, description="Short description for this product."
    )
    type: CatalogType | None = None
    tax_category: TaxCategory | None = None
    image_url: Annotated[str, Field(min_length=0, max_length=0)] | AnyUrl | None = (
        Field(
            None,
            description="Image for this product. Included in the checkout and on some customer documents.",
        )
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    status: Status | None = "active"
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = Field(
        None,
        description="RFC 3339 datetime string of when this entity was updated. Set automatically by Paddle.",
    )


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="Represents a product entity.", title="Product Notification"
    )


class Imported(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="Represents a product entity.", title="Product Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="Represents a product entity.", title="Product Notification"
    )
