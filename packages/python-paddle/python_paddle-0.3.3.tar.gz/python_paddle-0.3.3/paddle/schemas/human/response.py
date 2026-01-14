from pydantic import BaseModel

from paddle.schemas import Meta, MetaPaginated


class Response[T](BaseModel):
    data: T
    meta: Meta


class PaginatedResponse[T](BaseModel):
    data: list[T]
    meta: MetaPaginated
