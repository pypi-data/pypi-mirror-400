from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from . import (
    AddressId,
    CountryCode,
    CreatedAt,
    CustomData,
    CustomerId,
    Event,
    ImportMeta,
    NotificationId,
    Status,
    UpdatedAt,
)


class Data(BaseModel):
    id: AddressId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID for the customer related to this address, prefixed with `cus_`.",
    )
    description: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Memorable description for this address.",
        examples=["Paddle.com"],
    )
    first_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="First line of this address.", examples=["3811 Ditmars Blvd"]
    )
    second_line: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Second line of this address."
    )
    city: Annotated[str, Field(max_length=200)] | None = Field(
        None, description="City of this address.", examples=["Astoria"]
    )
    postal_code: Annotated[str, Field(max_length=200)] | None = Field(
        None,
        description="ZIP or postal code of this address. Required for some countries.",
        examples=["11105-1803"],
    )
    region: Annotated[str, Field(max_length=200)] | None = Field(
        None, description="State, county, or region of this address.", examples=["NY"]
    )
    country_code: CountryCode | None = Field(
        None,
        description="Supported two-letter ISO 3166-1 alpha-2 country code for this address.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    status: Status | None = "active"
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Address Notification"
    )


class Imported(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Address Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Address Notification"
    )
