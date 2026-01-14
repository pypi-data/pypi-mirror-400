# Unofficial Paddle Billing Python SDK

A small Paddle Billing SDK. It uses pydantic for schemas derived from the Paddle Billing OpenAPI
file.

## Installation

To install the package, install it from pypi:

```sh
uv add python-paddle
# or
pip install python-paddle
```

Or your favorite package manager.

## Usage

Currently, the SDK does not provide functions to call the API for all resources. It does provide
two things:

1. API schemas as Pydantic models
2. Webhook validation
3. Operations on customers
4. Operations on transactions
5. Operations on saved payment methods
6. Operations on subscriptions

### Calling the API

To call the API, you need to initialize a client:

```py
from paddle import Paddle

client = Paddle(token="...")
```

In case you're using the sandbox environment, pass `production = False` as an argument when
initializing the `Paddle` class.

```py
client = Paddle(token="...", production=False)
```

Once you have the client, you can call any methods on it asynchronously. For example:

```py
transaction = await client.get_transaction(transaction_id)
```

### Schemas

The schemas can be found under `paddle.schemas`, like `paddle.schemas.Transaction`.

### Webhooks

Webhooks can be validated using `paddle.webhooks.verify`. For example:

```py
from paddle import webhooks

webhooks.verify(
    secret="YOUR_WEBHOOK_SECRET",
    signature="YOUR_WEBHOOK_SIGNATURE",  # Extract this value from the `Paddle-Signature` in the webhook request
    body="THE_REQUEST_BODY",
)
```

It'll raise a `paddle.webhooks.exceptions.ValidationError` if the webhook could not be verified,
otherwise it'll return `True`.

To instead get a `bool` returned from the function, without an error raised on failure, pass the
`error=False` argument.

```py
from paddle import webhooks

is_valid = webhooks.verify(
    secret="YOUR_WEBHOOK_SECRET",
    signature="YOUR_WEBHOOK_SIGNATURE",  # Extract this value from the `Paddle-Signature` in the webhook request
    body="THE_REQUEST_BODY",
    error=False,
)

if is_valid:
    print("Great!")

else:
    print("Damn")
```

### Exceptions

All exceptions raised by this library inherit from `paddle.exceptions.PaddleException`.

## Contributing

All contributions are welcome! Whether it's tests, bugs, documentation, or anything else, open an
issue in our [GitHub repository](https://github.com/Nekidev/paddle-py). Thanks for your interest!
