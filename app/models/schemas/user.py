from pydantic import BaseModel
from typing import List, Optional
from app.casbin.role_definition import ResourceRightsEnum



class UserShare(BaseModel):
    id: str
    role: ResourceRightsEnum


class UserInJWT(BaseModel):
    id: str
    email: str = "no use for now"
    name: str
    user_name: Optional[str]
    tenant_id: str = "DEFAULT-TENANT"
    roles: Optional[List[str]]  # they are role names

    @property
    def is_admin(self):
        if self.roles and "algobox-admin" in self.roles:
            return True
        else:
            return False
