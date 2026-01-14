from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, RootModel

from . import (
    CreatedAt,
    CurrencyCode,
    CustomData,
    DiscountId,
    DiscountMode,
    Event,
    ImportMeta,
    NotificationId,
    StatusDiscount,
    Timestamp,
    UpdatedAt,
)


class Type(Enum):
    flat = "flat"
    flat_per_seat = "flat_per_seat"
    percentage = "percentage"


class RestrictToItem(
    RootModel[Annotated[str, Field(pattern="^(pri|pro)_[a-z\\d]{26}$")]]
):
    root: Annotated[str, Field(pattern="^(pri|pro)_[a-z\\d]{26}$")]


class Data(BaseModel):
    id: DiscountId | None = None
    status: StatusDiscount | None = None
    description: Annotated[str, Field(min_length=1, max_length=500)] | None = Field(
        None,
        description="Short description for this discount for your reference. Not shown to customers.",
    )
    enabled_for_checkout: bool | None = Field(
        True,
        description="Whether this discount can be redeemed by customers at checkout (`true`) or not (`false`).",
    )
    code: (
        Annotated[
            str, Field(pattern="^[a-zA-Z0-9]{1,32}$", min_length=1, max_length=32)
        ]
        | None
    ) = Field(
        None,
        description="Unique code that customers can use to redeem this discount at checkout. Not case-sensitive.",
    )
    type: Type | None = Field(
        None,
        description="Type of discount. Determines how this discount impacts the checkout or transaction total.",
        title="DiscountType",
    )
    mode: DiscountMode | None = None
    amount: str | None = Field(
        None,
        description="Amount to discount by. For `percentage` discounts, must be an amount between `0.01` and `100`. For `flat` and `flat_per_seat` discounts, amount in the lowest denomination for a currency.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Required where discount type is `flat` or `flat_per_seat`.",
    )
    recur: bool | None = Field(
        False,
        description="Whether this discount applies for multiple subscription billing periods (`true`) or not (`false`).",
    )
    maximum_recurring_intervals: int | None = Field(
        None,
        description="""Number of subscription billing periods that this discount recurs for. Requires `recur`. `null` if this discount recurs forever.

Subscription renewals, midcycle changes, and one-time charges billed to a subscription aren't considered a redemption. `times_used` is not incremented in these cases.""",
    )
    usage_limit: int | None = Field(
        None,
        description="""Maximum number of times this discount can be redeemed. This is an overall limit for this discount, rather than a per-customer limit. `null` if this discount can be redeemed an unlimited amount of times.

Paddle counts a usage as a redemption on a checkout, transaction, or the initial application against a subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    restrict_to: list[RestrictToItem] | None = Field(
        None,
        description="Product or price IDs that this discount is for. When including a product ID, all prices for that product can be discounted. `null` if this discount applies to all products and prices.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    expires_at: Timestamp | None = Field(
        None,
        description="""RFC 3339 datetime string of when this discount expires. Discount can no longer be redeemed after this date has elapsed. `null` if this discount can be redeemed forever.

Expired discounts can't be redeemed against transactions or checkouts, but can be applied when updating subscriptions.""",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class Created(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Discount Notification"
    )


class Imported(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Discount Notification"
    )


class DataModel(BaseModel):
    id: DiscountId | None = None
    status: StatusDiscount | None = None
    description: Annotated[str, Field(min_length=1, max_length=500)] | None = Field(
        None,
        description="Short description for this discount for your reference. Not shown to customers. Not case-sensitive.",
    )
    enabled_for_checkout: bool | None = Field(
        True,
        description="Whether this discount can be redeemed by customers at checkout (`true`) or not (`false`).",
    )
    code: (
        Annotated[
            str, Field(pattern="^[a-zA-Z0-9]{1,32}$", min_length=1, max_length=32)
        ]
        | None
    ) = Field(
        None,
        description="Unique code that customers can use to redeem this discount at checkout.",
    )
    type: Type | None = Field(
        None,
        description="Type of discount. Determines how this discount impacts the checkout or transaction total.",
        title="DiscountType",
    )
    mode: DiscountMode | None = None
    amount: str | None = Field(
        None,
        description="Amount to discount by. For `percentage` discounts, must be an amount between `0.01` and `100`. For `flat` and `flat_per_seat` discounts, amount in the lowest denomination for a currency.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Required where discount type is `flat` or `flat_per_seat`.",
    )
    recur: bool | None = Field(
        False,
        description="Whether this discount applies for multiple subscription billing periods (`true`) or not (`false`).",
    )
    maximum_recurring_intervals: int | None = Field(
        None,
        description="""Number of subscription billing periods that this discount recurs for. Requires `recur`. `null` if this discount recurs forever.

Subscription renewals, midcycle changes, and one-time charges billed to a subscription aren't considered a redemption. `times_used` is not incremented in these cases.""",
    )
    usage_limit: int | None = Field(
        None,
        description="""Maximum number of times this discount can be redeemed. This is an overall limit for this discount, rather than a per-customer limit. `null` if this discount can be redeemed an unlimited amount of times.

Paddle counts a usage as a redemption on a checkout, transaction, or the initial application against a subscription. Transactions created for subscription renewals, midcycle changes, and one-time charges aren't considered a redemption.""",
    )
    restrict_to: list[RestrictToItem] | None = Field(
        None,
        description="Product or price IDs that this discount is for. When including a product ID, all prices for that product can be discounted. `null` if this discount applies to all products and prices.",
    )
    custom_data: CustomData | None = Field(
        None, description="Your own structured key-value data."
    )
    import_meta: ImportMeta | None = Field(
        None,
        description="Import information for this entity. `null` if this entity is not imported.",
    )
    expires_at: Timestamp | None = Field(
        None,
        description="""RFC 3339 datetime string of when this discount expires. Discount can no longer be redeemed after this date has elapsed. `null` if this discount can be redeemed forever.

Expired discounts can't be redeemed against transactions or checkouts, but can be applied when updating subscriptions.""",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None


class Updated(Event):
    notification_id: NotificationId | None = None
    data: DataModel | None = Field(
        None, description="New or changed entity.", title="Discount Notification"
    )
