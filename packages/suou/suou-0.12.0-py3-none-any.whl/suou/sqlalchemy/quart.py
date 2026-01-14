"""
SQLAlchemy-Quart bindings
"""


from flask_sqlalchemy.pagination import Pagination


class AsyncSelectPagination(Pagination):
    """
    flask_sqlalchemy.SelectPagination but asynchronous.

    Pagination is not part of the public API, therefore expect that it may break
    """

    async def _query_items(self) -> list:
        select_q: Select = self._query_args["select"]
        select = select_q.limit(self.per_page).offset(self._query_offset)
        session: AsyncSession = self._query_args["session"]
        out = (await session.execute(select)).scalars()
        return out

    async def _query_count(self) -> int:
        select_q: Select = self._query_args["select"]
        sub = select_q.options(lazyload("*")).order_by(None).subquery()
        session: AsyncSession = self._query_args["session"]
        out = (await session.execute(select(func.count()).select_from(sub))).scalar()
        return out

    def __init__(self,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = 100,
        error_out: Exception | None = NotFoundError,
        count: bool = True,
        **kwargs):
        ## XXX flask-sqlalchemy says Pagination() is not public API.
        ## Things may break; beware.
        self._query_args = kwargs
        page, per_page = self._prepare_page_args(
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=error_out,
        )

        self.page: int = page
        """The current page."""

        self.per_page: int = per_page
        """The maximum number of items on a page."""

        self.max_per_page: int | None = max_per_page
        """The maximum allowed value for ``per_page``."""

        self.items = None
        self.total = None
        self.error_out = error_out
        self.has_count = count

    async def __aiter__(self):
        self.items = await self._query_items()
        if self.items is None:
            raise RuntimeError('query returned None')
        if not self.items and self.page != 1 and self.error_out:
            raise self.error_out
        if self.has_count:
            self.total = await self._query_count()
        for i in self.items:
            yield i




