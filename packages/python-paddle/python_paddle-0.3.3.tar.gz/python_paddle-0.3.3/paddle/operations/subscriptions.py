from typing import Literal

from datetime import datetime

from httpx import AsyncClient

from paddle.auth import BearerAuth
from paddle.schemas import (
    CollectionMode,
    Action,
    StatusSubscription,
    SubscriptionUpdate,
    SubscriptionCharge,
    EffectiveFrom,
    SubscriptionOnResume,
)
from paddle.exceptions import ApiError, ValidationError
from paddle.operations import Data

OrderBy = Literal[
    "id[ASC]",
    "id[DESC]",
]

Includes = Literal[
    "next_transaction",
    "recurring_transaction_details",
]


class SubscriptionOperationsMixin:
    _token: str
    _client: AsyncClient
    _endpoint: str

    async def list_subscriptions(
        self,
        *,
        address_id: list[str] = ...,
        after: str = ...,
        collection_mode: CollectionMode = ...,
        customer_id: list[str] = ...,
        id: list[str] = ...,
        order_by: OrderBy = ...,
        per_page: int = 200,
        price_id: list[str] = ...,
        scheduled_change_action: Action | None = ...,
        next_billed_at: list[str] | None = ...,
        status: list[StatusSubscription] = ...,
    ) -> Data:
        """List subscriptions."""

        url = f"https://{self._endpoint}/subscriptions"

        query = {}

        if address_id is not ...:
            query["address_id"] = ",".join(address_id)

        if after is not ...:
            query["after"] = after

        if collection_mode is not ...:
            query["collection_mode"] = collection_mode.value

        if customer_id is not ...:
            query["customer_id"] = ",".join(customer_id)

        if id is not ...:
            query["id"] = ",".join(id)

        if order_by is not ...:
            query["order_by"] = order_by

        if per_page is not ...:
            query["per_page"] = per_page

        if price_id is not ...:
            query["price_id"] = ",".join(price_id)

        if scheduled_change_action is not ...:
            if scheduled_change_action is None:
                query["scheduled_change_action"] = "null"
            else:
                query["scheduled_change_action"] = scheduled_change_action.value

        if next_billed_at is not ...:
            if next_billed_at is None:
                query["next_billed_at"] = "null"
            else:
                query["next_billed_at"] = ",".join(next_billed_at)

        if status is not ...:
            query["status"] = ",".join([s.value for s in status])

        try:
            response = await self._client.get(
                url,
                params=query,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def get_subscription(
        self, subscription_id: str, *, includes: list[Includes] = ...
    ) -> Data:
        """Retrieve a subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}"

        query = {}

        if includes is not ...:
            query["includes"] = ",".join(includes)

        try:
            response = await self._client.get(
                url,
                params=query,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def preview_subscription_update(
        self, subscription_id: str, update: SubscriptionUpdate
    ) -> Data:
        """Preview a subscription update."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/preview"

        try:
            response = await self._client.patch(
                url,
                json=update.model_dump(exclude_unset=True),
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def update_subscription(
        self, subscription_id: str, update: SubscriptionUpdate
    ) -> Data:
        """Update a subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}"

        try:
            response = await self._client.patch(
                url,
                json=update.model_dump(exclude_unset=True),
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def get_subscription_update_payment_method_transaction(
        self, subscription_id: str
    ) -> Data:
        """Retrieve the transaction for a customer to update their payment method for a subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/update-payment-method-transaction"

        try:
            response = await self._client.get(
                url,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def preview_subscription_one_time_charge(
        self,
        subscription_id: str,
        charge: SubscriptionCharge,
    ) -> Data:
        """Preview a one-time charge for a subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/charge/preview"

        try:
            response = await self._client.post(
                url,
                json=charge.model_dump(),
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def create_subscription_one_time_charge(
        self,
        subscription_id: str,
        charge: SubscriptionCharge,
    ) -> Data:
        """Create a one-time charge for a subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/charge"

        try:
            response = await self._client.post(
                url,
                json=charge.model_dump(),
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def activate_trialing_subscription(self, subscription_id: str) -> Data:
        """Activate a trialing subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/activate"

        try:
            response = await self._client.post(
                url,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def pause_subscription(
        self,
        subscription_id: str,
        *,
        effective_from: EffectiveFrom | None = None,
        resume_at: datetime | None = None,
        on_resume: SubscriptionOnResume,
    ) -> Data:
        """Pause a subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/pause"

        payload = {}

        if effective_from is not None:
            payload["effective_from"] = effective_from.value

        if resume_at is not None:
            payload["resume_at"] = resume_at.isoformat()

        payload["on_resume"] = on_resume.value

        try:
            response = await self._client.post(
                url,
                json=payload,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def resume_subscription(
        self,
        subscription_id: str,
        *,
        effective_from: datetime | Literal["immediately"],
        on_resume: SubscriptionOnResume = SubscriptionOnResume.start_new_billing_period,
    ) -> Data:
        """Resume a paused subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/resume"

        payload = {
            "on_resume": on_resume.value,
        }

        if isinstance(effective_from, datetime):
            payload["effective_from"] = effective_from.isoformat()
        else:
            payload["effective_from"] = effective_from

        try:
            response = await self._client.post(
                url,
                json=payload,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e

    async def cancel_subscription(
        self,
        subscription_id: str,
        *,
        effective_from: EffectiveFrom = EffectiveFrom.next_billing_period,
    ) -> Data:
        """Cancel a subscription."""

        url = f"https://{self._endpoint}/subscriptions/{subscription_id}/cancel"

        payload = {
            "effective_from": effective_from.value,
        }

        try:
            response = await self._client.post(
                url,
                json=payload,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError from e

        try:
            return response.json()

        except Exception as e:
            raise ValidationError from e
