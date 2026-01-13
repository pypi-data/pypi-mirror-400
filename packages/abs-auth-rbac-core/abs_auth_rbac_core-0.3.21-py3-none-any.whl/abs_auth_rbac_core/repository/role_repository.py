from typing import Any, List, Optional, Callable
from sqlalchemy.orm import joinedload
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from abs_repository_core.repository.base_repository import BaseRepository
from abs_auth_rbac_core.models.roles import Role
from abs_exception_core.exceptions import NotFoundError
from abs_repository_core.schemas import FilterSchema, FindBase


class RoleRepository(BaseRepository):
    def __init__(self, db: Callable[..., Session]):
        self.db = db
        super().__init__(db, Role)




