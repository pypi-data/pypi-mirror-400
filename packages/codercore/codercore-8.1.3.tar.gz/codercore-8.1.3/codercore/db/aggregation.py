from abc import ABCMeta
from datetime import datetime
from typing import Type, TypeVar

from sqlalchemy import column, desc, select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import Executable

from codercore.db import Base
from codercore.lib.aggregation import (
    AggregationParameters,
    DatedAggregationParametersMixin,
    DatePrecision,
)

T = TypeVar("T", bound=AggregationParameters)
U = TypeVar("U", bound=Base)


class AggregationQuery(metaclass=ABCMeta):
    model_class: Type[U]
    order_by_column: str
    select_args: tuple
    where_args: tuple
    group_by_args: tuple

    def __init__(self, params: T) -> None:
        self._add_query_defaults(params)
        self._expand_query(params)

    def _add_query_defaults(self, params: T) -> None:
        self.select_args = (*[column(prop) for prop in params.grouped_by],)
        self.group_by_args = tuple(params.grouped_by)
        self.where_args = ()

    def _expand_query(self, params: T) -> None:
        if self.group_by_args:
            self._order_by_leading_group_by_arg()

    def _order_by_leading_group_by_arg(self) -> None:
        self.order_by_column = self.group_by_args[0]

    def _create_executable(self) -> Executable:
        return (
            select(*self.select_args)
            .where(*self.where_args)
            .group_by(*self.group_by_args)
            .order_by(desc(self.order_by_column))
        )

    async def execute(self, session: AsyncSession) -> ChunkedIteratorResult:
        return await session.execute(self._create_executable())


class DatedAggregationQueryMixin(metaclass=ABCMeta):
    date_column: str = "date"

    def _expand_query(self, params: DatedAggregationParametersMixin) -> None:
        if params.date_precision:
            self._add_date_precision(params.date_precision)
        if params.min_date:
            self._add_min_date(params.min_date)
        if params.max_date:
            self._add_max_date(params.max_date)

    def _add_date_precision(self, date_precision: DatePrecision) -> None:
        date_precision = str(date_precision)
        self.select_args = (
            func.date_trunc(date_precision, self._get_date()).label(date_precision),
            *self.select_args,
        )
        self.group_by_args = (date_precision, *self.group_by_args)

    def _add_min_date(self, min_date: datetime) -> None:
        self.where_args = (*self.where_args, self._get_date() >= min_date)

    def _add_max_date(self, max_date: datetime) -> None:
        self.where_args = (*self.where_args, self._get_date() <= max_date)

    def _get_date(self) -> datetime:
        return getattr(self.model_class, self.date_column)
