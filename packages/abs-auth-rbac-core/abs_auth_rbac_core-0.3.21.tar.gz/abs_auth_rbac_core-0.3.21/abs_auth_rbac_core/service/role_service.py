from typing import Any, List, Optional
from abs_repository_core.services.base_service import BaseService
from abs_repository_core.schemas.base_schema import FindBase, FindUniqueValues
from abs_auth_rbac_core.models.roles import Role
from abs_auth_rbac_core.repository.role_repository import RoleRepository
from pydantic import BaseModel


class RoleService(BaseService):
    def __init__(self, repository:RoleRepository):
        self.repository = repository
        super().__init__(repository)


    def list_roles(self, schema: FindBase, eager: bool = True):
        return self.repository.read_by_options(schema, eager)
    
    