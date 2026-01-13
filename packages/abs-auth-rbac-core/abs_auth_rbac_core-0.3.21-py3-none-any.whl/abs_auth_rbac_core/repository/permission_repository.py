from typing import Any, List, Optional, Callable
from sqlalchemy.orm import joinedload
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from abs_repository_core.repository.base_repository import BaseRepository
from abs_repository_core.schemas.base_schema import FindBase, FindUniqueValues
from abs_auth_rbac_core.models.permissions import Permission

class PermissionRepository(BaseRepository):
    def __init__(self, db: Callable[..., Session]):
        self.db = db
        super().__init__(db, Permission)
