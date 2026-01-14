from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from . import CurrencyCodePayout, Event, NotificationId


class Status(Enum):
    unpaid = "unpaid"
    paid = "paid"


class Data(BaseModel):
    id: str | None = Field(None, description="ID for this payout.")
    status: Status | None = Field(None, description="Status of this payout.")
    amount: str | None = Field(
        None, description="Amount paid, or scheduled to be paid, for this payout."
    )
    currency_code: CurrencyCodePayout | None = Field(
        None, description="Three-letter ISO 4217 currency code for this payout."
    )


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Payout Notification"
    )


class Paid(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Payout Notification"
    )
