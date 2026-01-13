from functools import cache
from typing import Callable, Optional, Type

from asyncpg.connection import Connection
from asyncstdlib.functools import cache as async_cache
from frozendict import frozendict
from google.cloud.sql.connector import IPTypes, create_async_connector
from sqlalchemy.dialects.postgresql.asyncpg import (
    AsyncAdapt_asyncpg_connection,
    AsyncAdapt_asyncpg_dbapi,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session as Session_, sessionmaker as sessionmaker_
from sqlalchemy.pool import Pool
from sqlalchemy.util import await_only

from codercore.db.models import Base


@cache
def Session(connection_url: str) -> Session_:  # noqa
    return sessionmaker(connection_url)()


@cache
def sessionmaker(
    connection_url: str,
    *args,
    poolclass: Optional[Type[Pool]] = None,
    engine_kwargs: frozendict | None = None,
    **kwargs,
) -> sessionmaker_:
    if engine_kwargs is None:
        engine_kwargs = {}
    engine = create_async_engine(connection_url, poolclass=poolclass, **engine_kwargs)
    Base.metadata.bind = engine
    return sessionmaker_(engine, *args, class_=AsyncSession, **kwargs)


def get_connection_url(
    driver: str, user: str, password: str, host: str, database: str
) -> str:
    return f"{driver}://{user}:{password}@{host}/{database}"


@async_cache
async def get_connection_with_auto_iam_creator(
    instance_connection_name: str,
    user: str,
    database: str,
) -> Callable[[], Connection]:
    connector = await create_async_connector()

    def creator() -> AsyncAdapt_asyncpg_connection:
        connection = connector.connect_async(
            instance_connection_name,
            "asyncpg",
            user=user,
            db=database,
            enable_iam_auth=True,
            ip_type=IPTypes.PUBLIC,
        )
        return AsyncAdapt_asyncpg_connection(
            AsyncAdapt_asyncpg_dbapi(__import__("asyncpg")),
            await_only(connection),
        )

    return creator
