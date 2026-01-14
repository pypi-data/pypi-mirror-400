"""
Utilities for Quart-Auth

(Require Quart and SQLAlchemy)

---

Copyright (c) 2025-2026 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from __future__ import annotations
from typing import Callable, TypeVar
from quart_auth import AuthUser, Action
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase
from .sqlalchemy.asyncio import AsyncSession, SQLAlchemy

_T = TypeVar('_T')

def user_loader(database: SQLAlchemy, user_class: type[DeclarativeBase], *,
        attr_loader: Callable[[type[AuthUser], str], _T] = lambda x, y: x.id == int(y)
    ):
    """
    Returns a properly subclassed AuthUser loader for use in Quart-Auth.

    Actual User object is at .user; other attributes are proxied.

    Requires to be awaited before request before usage.

    Uses SQLAlchemy's AsyncSession.

    Parameters:
    * database The database instance.
    * user_class The user class.
    * attr_loader A lambda taking user_class and auth_id, default (user_class, auth_id : user_class.id == int(auth_id))

    *New in 0.12.0*
    """
    class UserLoader(AuthUser):
        _auth_id: str | None
        _auth_obj: user_class | None
        id: _T

        def __init__(self, auth_id: str | None, action: Action = Action.PASS):
            self._auth_id = auth_id
            self._auth_obj = None
            self._auth_sess: AsyncSession | None = None
            self.action = action

        @property
        def auth_id(self) -> str | None:
            return self._auth_id

        @property
        async def is_authenticated(self) -> bool:
            await self._load()
            return self._auth_id is not None
        
        async def _load(self):
            if self._auth_obj is None and self._auth_id is not None:
                async with database as session:
                    self._auth_obj = (await session.execute(select(user_class).where(attr_loader(user_class, self._auth_id)))).scalar()
                    if self._auth_obj is None:
                        raise RuntimeError('failed to fetch user')
        
        def __getattr__(self, key):
            if self._auth_obj is None:
                raise RuntimeError('user is not loaded')
            return getattr(self._auth_obj, key)

        def __bool__(self):
            return self._auth_obj is not None

        @property
        def session(self):
            return self._auth_sess

        async def _unload(self):
            # user is not expected to mutate
            if self._auth_sess:
                await self._auth_sess.rollback()
        
        @property
        def user(self):
            return self._auth_obj

    return UserLoader

# Optional dependency: do not import into __init__.py
__all__ = ('user_loader',)

