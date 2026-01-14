from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from . import (
    BusinessId,
    CreatedAt,
    CustomData,
    CustomerId,
    Email,
    Event,
    ImportMeta,
    Name,
    NotificationId,
    Status,
    UpdatedAt,
)


class Contact(BaseModel):
    name: Name = Field(..., description="Full name of this contact.")
    email: Email = Field(..., description="Email address for this contact.")


class Data(BaseModel):
    id: BusinessId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID for the customer related to this business, prefixed with `cus_`.",
    )
    name: Annotated[str, Field(min_length=1, max_length=1024)] | None = Field(
        None, description="Name of this business."
    )
    company_number: Annotated[str, Field(max_length=1024)] | None = Field(
        None, description="Company number for this business.", examples=["123456789"]
    )
    tax_identifier: Annotated[str, Field(max_length=1024)] | None = Field(
        None,
        description="Tax or VAT Number for this business.",
        examples=["AB0123456789"],
    )
    status: Status | None = "active"
    contacts: list[Contact] | None = Field(
        None,
        description="List of contacts related to this business, typically used for sending invoices.",
        max_length=100,
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Business Notification"
    )


class Imported(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Business Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Business Notification"
    )
