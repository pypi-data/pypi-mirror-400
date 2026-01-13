from typing import Any, List, Optional
from abs_repository_core.services.base_service import BaseService
from abs_repository_core.schemas.base_schema import FindBase, FindUniqueValues
from abs_auth_rbac_core.models.roles import Role
from abs_auth_rbac_core.repository.permission_repository import PermissionRepository
from pydantic import BaseModel


class PermissionService(BaseService):
    def __init__(self, repository:PermissionRepository):
        super().__init__(repository)
        self.repository = repository
        
    def list_permissions(self, schema: FindBase, eager: bool = True):
        return self.repository.read_by_options(schema, eager)
