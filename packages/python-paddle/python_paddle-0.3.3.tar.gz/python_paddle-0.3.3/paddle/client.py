import httpx

from paddle.operations.customers import CustomerOperationsMixin
from paddle.operations.transactions import TransactionOperationsMixin
from paddle.operations.subscriptions import SubscriptionOperationsMixin
from paddle.operations.payment_methods import PaymentMethodOperationsMixin


class Paddle(
    CustomerOperationsMixin,
    TransactionOperationsMixin,
    SubscriptionOperationsMixin,
    PaymentMethodOperationsMixin,
):
    """A Paddle client."""

    _client = httpx.AsyncClient()

    def __init__(self, token: str, production: bool = True) -> None:
        """Initialize a Paddle client.

        Args:
            token (str): The API token for authentication.
            production (bool, optional): Whether to use the production environment. Defaults to
                True.
        """

        self._token = token

        if production:
            self._endpoint = "api.paddle.com"

        else:
            self._endpoint = "sandbox-api.paddle.com"
