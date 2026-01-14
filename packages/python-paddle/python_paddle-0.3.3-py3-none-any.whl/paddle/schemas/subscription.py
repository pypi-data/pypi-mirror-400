from __future__ import annotations

from pydantic import BaseModel, Field

from . import (
    AddressId,
    BillingDetails,
    BusinessId,
    CollectionMode,
    CreatedAt,
    CurrencyCode,
    CustomData,
    CustomerId,
    DiscountSubscription,
    Duration,
    Event,
    ImportMeta,
    ItemSubscription,
    NotificationId,
    StatusSubscription,
    SubscriptionId,
    SubscriptionScheduledChange,
    TimePeriod,
    Timestamp,
    TransactionId,
    UpdatedAt,
)


class Data(BaseModel):
    id: SubscriptionId | None = None
    status: StatusSubscription | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this subscription is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this subscription is for, prefixed with `add_`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this subscription is for, prefixed with `biz_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Transactions for this subscription are created in this currency. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    started_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription started. This may be different from `first_billed_at` if the subscription started in trial.",
    )
    first_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was first billed. This may be different from `started_at` if the subscription started in trial.",
    )
    next_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription is next scheduled to be billed.",
    )
    paused_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was paused. Set automatically by Paddle when the pause subscription operation is used. `null` if not paused.",
    )
    canceled_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was canceled. Set automatically by Paddle when the cancel subscription operation is used. `null` if not canceled.",
    )
    discount: DiscountSubscription | None = None
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for transactions created for this subscription. `automatic` for checkout, `manual` for invoices.",
    )
    billing_details: BillingDetails | None = None
    current_billing_period: TimePeriod | None = Field(
        None,
        description="Current billing period for this subscription. Set automatically by Paddle based on the billing cycle. `null` for `paused` and `canceled` subscriptions.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this subscription renews. Set automatically by Paddle based on the prices on this subscription.",
    )
    scheduled_change: SubscriptionScheduledChange | None = None
    items: list[ItemSubscription] | None = Field(
        None,
        description="List of items on this subscription. Only recurring items are returned.",
        max_length=100,
        min_length=1,
    )
    custom_data: CustomData | None = None
    import_meta: ImportMeta | None = None


class Activated(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )


class Canceled(Event):
    notification_id: NotificationId | None = None
    data: Data | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )


class DataModel(BaseModel):
    id: SubscriptionId | None = None
    transaction_id: TransactionId | None = Field(
        None,
        description="Paddle ID for the transaction entity that resulted in this subscription being created, prefixed with `txn_`.",
    )
    status: StatusSubscription | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this subscription is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this subscription is for, prefixed with `add_`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this subscription is for, prefixed with `biz_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Transactions for this subscription are created in this currency. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    started_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription started. This may be different from `first_billed_at` if the subscription started in trial.",
    )
    first_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was first billed. This may be different from `started_at` if the subscription started in trial.",
    )
    next_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription is next scheduled to be billed.",
    )
    paused_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was paused. Set automatically by Paddle when the pause subscription operation is used. `null` if not paused.",
    )
    canceled_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was canceled. Set automatically by Paddle when the cancel subscription operation is used. `null` if not canceled.",
    )
    discount: DiscountSubscription | None = None
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for transactions created for this subscription. `automatic` for checkout, `manual` for invoices.",
    )
    billing_details: BillingDetails | None = None
    current_billing_period: TimePeriod | None = Field(
        None,
        description="Current billing period for this subscription. Set automatically by Paddle based on the billing cycle. `null` for `paused` and `canceled` subscriptions.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this subscription renews. Set automatically by Paddle based on the prices on this subscription.",
    )
    scheduled_change: SubscriptionScheduledChange | None = None
    items: list[ItemSubscription] | None = Field(
        None,
        description="List of items on this subscription. Only recurring items are returned.",
        max_length=100,
        min_length=1,
    )
    custom_data: CustomData | None = None
    import_meta: ImportMeta | None = None


class Created(Event):
    notification_id: NotificationId | None = None
    data: DataModel | None = Field(
        None,
        description="New or changed entity.",
        title="Subscription Created Notification",
    )


class DataModel1(BaseModel):
    id: SubscriptionId | None = None
    status: StatusSubscription | None = None
    customer_id: CustomerId | None = Field(
        None,
        description="Paddle ID of the customer that this subscription is for, prefixed with `ctm_`.",
    )
    address_id: AddressId | None = Field(
        None,
        description="Paddle ID of the address that this subscription is for, prefixed with `add_`.",
    )
    business_id: BusinessId | None = Field(
        None,
        description="Paddle ID of the business that this subscription is for, prefixed with `biz_`.",
    )
    currency_code: CurrencyCode | None = Field(
        None,
        description="Supported three-letter ISO 4217 currency code. Transactions for this subscription are created in this currency. Must be `USD`, `EUR`, or `GBP` if `collection_mode` is `manual`.",
    )
    created_at: CreatedAt | None = None
    updated_at: UpdatedAt | None = None
    started_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription started. This may be different from `first_billed_at` if the subscription started in trial.",
    )
    first_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was first billed. This may be different from `started_at` if the subscription started in trial.",
    )
    next_billed_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription is next scheduled to be billed.",
    )
    paused_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was paused. Set automatically by Paddle when the pause subscription operation is used. `null` if not paused.",
    )
    canceled_at: Timestamp | None = Field(
        None,
        description="RFC 3339 datetime string of when this subscription was canceled. Set automatically by Paddle when the cancel subscription operation is used. `null` if not canceled.",
    )
    discount: DiscountSubscription | None = None
    collection_mode: CollectionMode | None = Field(
        "automatic",
        description="How payment is collected for transactions created for this subscription. `automatic` for checkout, `manual` for invoices.",
    )
    billing_details: BillingDetails | None = None
    current_billing_period: TimePeriod | None = Field(
        None,
        description="Current billing period for this subscription. Set automatically by Paddle based on the billing cycle. `null` for `paused` and `canceled` subscriptions.",
    )
    billing_cycle: Duration | None = Field(
        None,
        description="How often this subscription renews. Set automatically by Paddle based on the prices on this subscription.",
    )
    scheduled_change: SubscriptionScheduledChange | None = None
    items: list[ItemSubscription] | None = Field(
        None,
        description="List of items on this subscription. Only recurring items are returned.",
        max_length=100,
        min_length=1,
    )
    custom_data: CustomData | None = None
    import_meta: ImportMeta | None = None


class Imported(Event):
    notification_id: NotificationId | None = None
    data: DataModel1 | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )


class PastDue(Event):
    notification_id: NotificationId | None = None
    data: DataModel1 | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )


class Paused(Event):
    notification_id: NotificationId | None = None
    data: DataModel1 | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )


class Resumed(Event):
    notification_id: NotificationId | None = None
    data: DataModel1 | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )


class Trialing(Event):
    notification_id: NotificationId | None = None
    data: DataModel1 | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )


class Updated(Event):
    notification_id: NotificationId | None = None
    data: DataModel1 | None = Field(
        None, description="New or changed entity.", title="Subscription Notification"
    )
