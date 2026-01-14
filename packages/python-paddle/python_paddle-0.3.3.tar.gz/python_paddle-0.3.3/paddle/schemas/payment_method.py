from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from . import (
    AddressId,
    CustomerId,
    Event,
    NotificationId,
    PaymentMethodId,
    SavedAt,
    UpdatedAt,
)


class DeletionReason(Enum):
    replaced_by_newer_version = "replaced_by_newer_version"
    api = "api"


class Type(Enum):
    alipay = "alipay"
    apple_pay = "apple_pay"
    card = "card"
    google_pay = "google_pay"
    korea_local = "korea_local"
    paypal = "paypal"


class Origin(Enum):
    saved_during_purchase = "saved_during_purchase"
    subscription = "subscription"


class Data(BaseModel):
    id: PaymentMethodId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this payment method is saved for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address for this payment method, prefixed with `add_`.",
    )
    deletion_reason: DeletionReason | None = Field(
        None,
        description="Reason why this payment method was deleted.",
        title="PaymentMethodDeletionReason",
    )
    type: Type | None = Field(
        None,
        description="Type of payment method saved.",
        title="SavedPaymentMethodType",
    )
    origin: Origin | None = Field(
        None,
        description="Describes how this payment method was saved.",
        title="PaymentMethodOrigin",
    )
    saved_at: SavedAt | None = None
    updated_at: UpdatedAt | None = None


class Deleted(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None,
        description="New or changed entity.",
        title="Payment Method Deleted Notification",
    )


class DataModel(BaseModel):
    id: PaymentMethodId | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this payment method is saved for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address for this payment method, prefixed with `add_`.",
    )
    type: Type | None = Field(
        None,
        description="Type of payment method saved.",
        title="SavedPaymentMethodType",
    )
    origin: Origin | None = Field(
        None, description="Describes how this payment method was saved."
    )
    saved_at: SavedAt | None = None
    updated_at: UpdatedAt | None = None


class Saved(Event):
    notification_id: NotificationId | None = None
    data: DataModel | None = Field(
        None,
        description="New or changed entity.",
        title="Payment Method Saved Notification",
    )
