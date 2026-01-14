from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from . import (
    CatalogType,
    CreatedAt,
    CustomData,
    Duration,
    Event,
    ImportMeta,
    Money,
    NotificationId,
    PriceId,
    PriceQuantity,
    ProductId,
    Status,
    TaxMode,
    UnitPriceOverride,
    UpdatedAt,
)


class Data(BaseModel):
    id: PriceId | None = None
    product_id: ProductId | None = Field(
        None,
        description="Paddle ID for the product that this price is for, prefixed with `pro_`.",
    )
    description: Annotated[str, Field(min_length=2, max_length=500)] | None = Field(
        None,
        description="Internal description for this price, not shown to customers. Typically notes for your team.",
    )
    type: CatalogType | None = None
    name: Annotated[str, Field(min_length=1, max_length=150)] | None = Field(
        None,
        description="Name of this price, shown to customers at checkout and on invoices. Typically describes how often the related product bills.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this price should be charged. `null` if price is non-recurring (one-time).",
    )
    trial_period: Duration | None = Field(
        None,
        description="Trial period for the product related to this price. The billing cycle begins once the trial period is over. `null` for no trial period. Requires `billing_cycle`.",
    )
    tax_mode: TaxMode | None = "account_setting"
    unit_price: Money | None = Field(
        None,
        description="Base price. This price applies to all customers, except for customers located in countries where you have `unit_price_overrides`.",
    )
    unit_price_overrides: list[UnitPriceOverride] | None = Field(
        None,
        description="List of unit price overrides. Use to override the base price with a custom price and currency for a country or group of countries.",
        max_length=250,
    )
    quantity: PriceQuantity | None = Field(
        None,
        description="Limits on how many times the related product can be purchased at this price. Useful for discount campaigns.",
    )
    status: Status | None = None
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    created_at: CreatedAt | None = Field(
        None,
        description="RFC 3339 datetime string of when this entity was created. Set automatically by Paddle.",
    )
    updated_at: UpdatedAt | None = Field(
        None,
        description="RFC 3339 datetime string of when this entity was updated. Set automatically by Paddle.",
    )


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="Represents a price entity.", title="Price Notification"
    )


class Imported(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="Represents a price entity.", title="Price Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="Represents a price entity.", title="Price Notification"
    )
