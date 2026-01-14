from typing import Any, Type, TypeVar

from aiohttp import ClientResponse


# Generic data class instance
T = TypeVar("T")

# Dict of data decoded from JSON
Data = dict[str, Any]


def from_dict(cls: Type[T], data: Data) -> T:
    return cls(**data)


def from_dict_list(cls: Type[T], items: list[Data]) -> list[T]:
    return [cls(**item) for item in items]


async def from_response(cls: Type[T], response: ClientResponse) -> T:
    data = await response.json()
    return cls(**data)


async def from_response_list(cls: Type[T], response: ClientResponse) -> list[T]:
    items = await response.json()
    return [cls(**item) for item in items]
