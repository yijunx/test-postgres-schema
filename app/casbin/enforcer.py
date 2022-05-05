import casbin_sqlalchemy_adapter
import casbin
from app.casbin.resource_id_converter import get_resource_id_from_item_id
from app.models.schemas.user import UserInJWT
from app.utils.config import configurations as conf
from app.casbin.role_definition import (
    ResourceRightsEnum,
    ResourceDomainEnum,
    resource_right_action_mapping,
    RoleEnum,
)
from app.models.exceptions.casbin import CasbinNotAuthorised
import app.repositories.casbin as CasbinRepo
from app.utils.db import get_db
from typing import Dict, List


# now this guy has to be run dynamically.. # well we can cache it somehow
enforcer_cache: Dict[str, casbin.Enforcer] = {
    # this avoids the enforcer to be created time and time again
    "tenant_id": "the enforcer to be created"
}

# need to observe the size of this enforcer_cache


def create_casbin_enforcer(tenand_id: str):
    """this enforcer preloads the policies for the actor"""
    schema_name = tenand_id
    db_uri = f"{conf.DATABASE_URI}?options=-c%20search_path={schema_name}"
    adapter = casbin_sqlalchemy_adapter.Adapter(db_uri)
    # well not sure if its working
    # but definitely the the casbin enforcer needs to created dynamically
    # postgresql://postgres:password@localhost:5432/database?options=-c%20search_path=schema_name

    casbin_enforcer = casbin.Enforcer("app/casbin/model.conf", adapter)

    def actions_mapping(
        action_from_request: str, resource_right_from_policy: str
    ) -> bool:
        """
        actions are get download patch share...
        resource_right are own / edit / view
        """
        if resource_right_from_policy in resource_right_action_mapping:
            if (
                action_from_request
                in resource_right_action_mapping[resource_right_from_policy]
            ):
                return True
        return False

    def objects_mapping(object_from_request: str, object_from_policy: str) -> bool:
        """
        admin users will have * in obj in the admin role policy, so admin user can
        do things on any resource
        """
        # shall we use startswith? what is the complexity here
        if object_from_request.startswith(object_from_policy):
            return True
        else:
            return object_from_request == object_from_policy

    casbin_enforcer.add_function("actions_mapping", actions_mapping)
    casbin_enforcer.add_function("objects_mapping", objects_mapping)
    return casbin_enforcer


def get_or_create_enforcer(tenand_id: str) -> casbin.Enforcer:
    if tenand_id in enforcer_cache:
        return enforcer_cache[tenand_id]
    else:
        # check if the we have the schema

        # if there is such schema
        casbin_enforcer = create_casbin_enforcer(tenand_id=tenand_id)
    return 


def resource_exits(resource_id: str) -> bool:
    """This function make sure the admin actor has the access to a domain of his
    tenancy
    """
    with get_db() as db:
        print("checking if the resource is valid...")
        policies = CasbinRepo.get_all_policies_of_resource(
            db=db, resource_id=resource_id
        )
    return bool(policies)


class Filter:
    def __init__(self, v0: List[str], v1: List[str] = None) -> None:
        self.ptype = []
        self.v0 = v0  # the only setup
        self.v1 = v1 if v1 is not None else []
        self.v2 = []
        self.v3 = []
        self.v4 = []
        self.v5 = []


def enforce(
    actor: UserInJWT, action: str, item_id: str, domain: ResourceDomainEnum
) -> None:
    """just raise error if not ok, does not return anything"""


    resource_id = get_resource_id_from_item_id(
        item_id=item_id, domain=domain, tenant_id=actor.tenant_id
    )

    # everytime a new enforcer needs to be created
    casbin_enforcer = get_or_create_enforcer(tenand_id=actor.tenant_id)
    casbin_enforcer.load_filtered_policy(filter=Filter(v0=[actor.id, "admin"]))

    print("REQUEST: ", actor.id, actor.tenant_id, resource_id, action)
    verdict = casbin_enforcer.enforce(
        actor.id, actor.tenant_id, resource_id, action
    )

    if verdict is False:
        raise CasbinNotAuthorised(
            actor=actor, resource_id=resource_id, action=action
        )
