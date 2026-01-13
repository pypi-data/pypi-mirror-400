from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from pytest import FixtureRequest
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.pool import NullPool, Pool
from sqlalchemy_utils import create_database, database_exists, drop_database

from codercore.db import get_connection_url, sessionmaker
from codercore.db.models import Base
from codercore.lib.redis import Redis, connection
from codercore.lib.settings import EnvSettings


def connection_settings(
    user: str,
    password: str,
    host: str,
    database: str,
) -> dict[str, str]:
    return {
        "user": user,
        "password": password,
        "host": host,
        "database": database,
    }


def sync_db_connection_url(connection_settings: dict[str, str]) -> str:
    return get_connection_url("postgresql", **connection_settings)


def async_db_connection_url(connection_settings: dict[str, str]) -> str:
    return get_connection_url("postgresql+asyncpg", **connection_settings)


def DBSession(  # noqa
    sync_db_connection_url: str,
    async_db_connection_url: str,
    *args,
    poolclass: type[Pool] = NullPool,
    **kwargs,
) -> sessionmaker_:
    if not database_exists(sync_db_connection_url):
        create_database(sync_db_connection_url)
    return sessionmaker(async_db_connection_url, *args, poolclass=poolclass, **kwargs)


async def db_session(
    DBSession: sessionmaker_,  # noqa
    metadata: MetaData = Base.metadata,
) -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            async with session.bind.begin() as conn:
                await conn.run_sync(metadata.create_all)
            yield session
        finally:
            async with session.bind.begin() as conn:
                await conn.run_sync(metadata.drop_all)


def clean_up_for_worker(request: FixtureRequest, sync_db_connection_url: str) -> None:
    def cleanup():
        if not database_exists(sync_db_connection_url):
            return

        drop_database(sync_db_connection_url)

    request.addfinalizer(cleanup)


@asynccontextmanager
async def _redis_connection_maker(
    worker_id: str,
) -> AsyncIterator[Awaitable[Redis]]:
    async def redis_connection() -> Redis:
        return connection.__wrapped__(db=int(worker_id[2:]), **EnvSettings.redis)

    try:
        conn = await redis_connection()
        yield conn
    finally:
        await conn.flushdb()
        await conn.close()


async def redis_connection_maker(
    worker_id: str,
) -> Callable[[], AsyncIterator[Awaitable[Redis]]]:
    return _redis_connection_maker


async def redis_connection(
    redis_connection_maker: Callable[[], Awaitable[Redis]],
    worker_id: str,
) -> Redis:
    async with redis_connection_maker(worker_id) as conn:
        return conn
