from typing import Literal

from httpx import AsyncClient
from pydantic import ValidationError as PydanticValidationError

from paddle.auth import BearerAuth
from paddle.exceptions import ApiError, ValidationError
from paddle.operations import Data
from paddle.schemas import CustomerPaymentMethod
from paddle.schemas.human.response import PaginatedResponse, Response


OrderBy = Literal[
    "id[ASC]",
    "id[DESC]",
]


class PaymentMethodOperationsMixin:
    _token: str
    _client: AsyncClient
    _endpoint: str

    async def list_payment_methods(
        self,
        customer_id: str,
        *,
        address_id: str = ...,
        after: str = ...,
        order_by: OrderBy = ...,
        per_page: int = 200,
        supports_checkout: bool = ...,
    ) -> Data:
        """List a customer's payment methods."""

        url = f"https://{self._endpoint}/customers/{customer_id}/payment-methods"

        query = {}

        if address_id is not ...:
            query["address_id"] = ",".join(address_id)

        if after is not ...:
            query["after"] = after

        if order_by is not ...:
            query["order_by"] = order_by

        if per_page is not ...:
            query["per_page"] = per_page

        if supports_checkout is not ...:
            query["supports_checkout"] = str(supports_checkout).lower()

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

    async def get_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> Data:
        """Retrieve a customer's payment method."""

        url = f"https://{self._endpoint}/customers/{customer_id}/payment-methods/{payment_method_id}"

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

    async def delete_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> None:
        """Delete a customer's payment method."""

        url = f"https://{self._endpoint}/customers/{customer_id}/payment-methods/{payment_method_id}"

        try:
            response = await self._client.delete(
                url,
                auth=BearerAuth(self._token),
            )

        except Exception as e:
            raise ApiError from e

        try:
            response.raise_for_status()

        except Exception as e:
            raise ApiError(response.text) from e
