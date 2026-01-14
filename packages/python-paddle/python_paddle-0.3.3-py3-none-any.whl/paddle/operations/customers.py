from typing import Literal

from httpx import AsyncClient

from paddle.auth import BearerAuth
from paddle.schemas import (
    CurrencyCode,
    CustomerCreate,
    CustomerUpdate,
    Status,
)
from paddle.exceptions import ApiError, ValidationError
from paddle.operations import Data


OrderBy = Literal[
    "id[ASC]",
    "id[DESC]",
]


class CustomerOperationsMixin:
    _token: str
    _client: AsyncClient
    _endpoint: str

    async def list_customers(
        self,
        *,
        after: str = ...,
        email: list[str] = ...,
        id: list[str] = ...,
        order_by: OrderBy = ...,
        per_page: int = 30,
        search: str = ...,
        status: Status = ...,
    ) -> Data:
        """List customers."""

        url = f"https://{self._endpoint}/customers"

        query = {}

        if after is not ...:
            query["after"] = after

        if email is not ...:
            query["email"] = ",".join(email)

        if id is not ...:
            query["id"] = ",".join(id)

        if order_by is not ...:
            query["order_by"] = order_by

        if per_page is not ...:
            query["per_page"] = per_page

        if search is not ...:
            query["search"] = search

        if status is not ...:
            query["status"] = status.value

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

    async def create_customer(
        self,
        customer: CustomerCreate,
    ) -> Data:
        """Create a new customer."""

        url = f"https://{self._endpoint}/customers"

        try:
            response = await self._client.post(
                url,
                json=customer.model_dump(
                    mode="json", exclude_unset=True, exclude_defaults=True
                ),
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

    async def get_customer(
        self,
        customer_id: str,
    ) -> Data:
        """Retrieve a specific customer by ID."""

        url = f"https://{self._endpoint}/customers/{customer_id}"

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

    async def update_customer(
        self,
        customer_id: str,
        customer: CustomerUpdate,
    ) -> Data:
        """Update a specific customer by ID."""

        url = f"https://{self._endpoint}/customers/{customer_id}"

        try:
            response = await self._client.put(
                url,
                json=customer.model_dump(mode="json"),
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

    async def get_customer_credit_balances(
        self,
        customer_id: str,
        *,
        currency_codes: list[CurrencyCode] = ...,
    ) -> Data:
        """Retrieve credit balances for a specific customer."""

        url = f"https://{self._endpoint}/customers/{customer_id}/credit-balances"

        query = {}

        if currency_codes is not ...:
            query["currency_codes"] = ",".join([code.value for code in currency_codes])

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

    async def create_customer_authentication_token(
        self,
        customer_id: str,
    ) -> Data:
        """Create an authentication token for a specific customer."""

        url = f"https://{self._endpoint}/customers/{customer_id}/auth-token"

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
