from __future__ import annotations

from pydantic import BaseModel, Field

from . import (
    AdjustmentAction,
    AdjustmentId,
    AdjustmentItem,
    AdjustmentItemId,
    AdjustmentPayoutTotals,
    AdjustmentTaxRatesUsed,
    AdjustmentTotals,
    AdjustmentType,
    CreatedAt,
    CurrencyCode,
    CustomerId,
    Event,
    NotificationId,
    StatusAdjustment,
    SubscriptionId,
    TransactionId,
    UpdatedAt,
)


class Item(AdjustmentItem):
    id: AdjustmentItemId | None = Field(
        None,
        description="Unique Paddle ID for this adjustment item, prefixed with `adjitm_`.",
    )


class Data(BaseModel):
    id: AdjustmentId | None = None
    action: AdjustmentAction | None = None
    type: AdjustmentType | None = None
    transaction_id: TransactionId | None = Field(
        None,
        description="Paddle ID of the transaction that this adjustment is for, prefixed with `txn_`.",
    )
    subscription_id: SubscriptionId | None = Field(
        None,
        description="""Paddle ID for the subscription related to this adjustment, prefixed with `sub_`.
Set automatically by Paddle based on the `subscription_id` of the related transaction.""",
    )
    customer_id: CustomerId | None = Field(
        None,
        description="""Paddle ID for the customer related to this adjustment, prefixed with `ctm_`.
Set automatically by Paddle based on the `customer_id` of the related transaction.""",
    )
    reason: str | None = Field(
        None,
        description="Why this adjustment was created. Appears in the Paddle dashboard. Retained for recordkeeping purposes.",
    )
    credit_applied_to_balance: bool | None = Field(
        None,
        description="Whether this adjustment was applied to the related customer's credit balance. `null` unless adjustment `action` is not `credit`.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Three-letter ISO 4217 currency code for this adjustment. Set automatically by Paddle based on the `currency_code` of the related transaction.",
    )
    status: StatusAdjustment | None = None
    items: list[Item] | None = Field(
        None,
        description="List of items on this adjustment.",
        max_length=100,
        min_length=1,
    )
    totals: AdjustmentTotals | None = None
    payout_totals: AdjustmentPayoutTotals | None = Field(
        None,
        description="Breakdown of how this adjustment affects your payout balance.",
    )
    tax_rates_used: AdjustmentTaxRatesUsed | None = None
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Adjustment Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Adjustment Notification"
    )
