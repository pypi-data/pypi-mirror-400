from __future__ import annotations

from pydantic import BaseModel, Field

from . import (
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


class Data(BaseModel):
    id: CustomerId | None = None
    name: Name | None = Field(
        None,
        description="Full name of this customer. Required when creating transactions where `collection_mode` is `manual` (invoices).",
    )
    email: Email | None = Field(None, description="Email address for this customer.")
    marketing_consent: bool | None = Field(
        False,
        description="""Whether this customer opted into marketing from you. `false` unless customers check the marketing consent box
when using Paddle Checkout. Set automatically by Paddle.""",
    )
    status: Status | None = "active"
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    locale: str | None = Field(
        "en", description="Valid IETF BCP 47 short form locale tag."
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Customer Notification"
    )


class Imported(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Customer Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Customer Notification"
    )
