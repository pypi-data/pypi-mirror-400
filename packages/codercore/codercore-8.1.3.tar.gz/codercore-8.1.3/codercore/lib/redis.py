from __future__ import annotations

import inspect
from functools import cache as functools_cache, wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Concatenate,
    Optional,
    ParamSpec,
    TypeVar,
    Union,
)

from redis.asyncio import StrictRedis

T = TypeVar("T")
Cacheable = TypeVar("Cacheable", bytes, memoryview, str, int, float)
RT = TypeVar("RT", bound=Cacheable)
CT = TypeVar("CT", Cacheable, Awaitable[Cacheable])
P = ParamSpec("P")


@functools_cache
def connection(
    host: str,
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    default_ttl_in_seconds: Optional[int] = None,
) -> Redis:
    return Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        default_ttl_in_seconds=default_ttl_in_seconds,
    )


class Redis(StrictRedis):
    default_ttl_in_seconds: Optional[int]

    def __init__(
        self,
        *args,
        default_ttl_in_seconds: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.default_ttl_in_seconds = default_ttl_in_seconds

    async def set(
        self,
        *args,
        ex: Optional[int] = None,
        **kwargs,
    ) -> Union[Awaitable, Any]:
        if not ex:
            ex = self.default_ttl_in_seconds
        await super().set(*args, ex=ex, **kwargs)


def cache(
    key: Callable[P, str] | str,
    ex: int | None = None,
    deserialize: Callable[[Any], RT] = lambda x: x,
) -> Callable[
    Callable[P, CT],
    Callable[Concatenate[Redis, str, P], Awaitable[RT]],
]:
    def decorate(
        func: Callable[P, CT],
    ) -> Callable[Concatenate[Redis, str, P], Awaitable[RT]]:
        @wraps(func)
        async def wrapper(
            *args: P.args,
            connection: Redis,
            **kwargs: P.kwargs,
        ) -> RT:
            formatted_key = key if isinstance(key, str) else key(*args, **kwargs)
            if (result := await connection.get(formatted_key)) is not None:
                return deserialize(result)
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                result = await result
            if result is not None:
                await connection.set(formatted_key, result, ex=ex)
                return deserialize(result)

        return wrapper

    return decorate
