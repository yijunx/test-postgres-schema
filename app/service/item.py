from app.utils.db import get_db
from app.models.schemas.item import (
    ItemCreate,
    ItemPatch,
    ItemQuery,
)
from app.models.item import Item, ItemWithPaging
from app.models.pagination import QueryPagination
from app.models.schemas.user import UserInJWT, UserShare
from app.models.exceptions.casbin import CasbinNotAuthorised

# from app.schemas.casbin import CasbinPolicy, CasbinGroup
import app.repositories.item as ItemRepo
import app.repositories.user as UserRepo
import app.repositories.casbin as CasbinRepo

# get the enforce functions
from app.casbin.enforcer import enforce
from app.casbin.resource_id_converter import (
    get_item_id_from_resource_id,
    get_resource_id_from_item_id,
)
from app.casbin.role_definition import (
    ResourceDomainEnum,
    ResourceRightsEnum,
    ResourceActionsEnum,
)
from app.casbin.enforcer import get_or_create_enforcer


def create_item(item_create: ItemCreate, actor: UserInJWT) -> Item:
    """no need to implement enforce here
    cos everyone can create item"""

    with get_db() as db:
        # create the item
        db_item = ItemRepo.create(db=db, item_create=item_create, actor=actor)

        # create the casbin policy for the creator
        _ = CasbinRepo.create_policy(
            db=db,
            resource_id=get_resource_id_from_item_id(
                item_id=db_item.id,
                domain=ResourceDomainEnum.items,
                tenant_id=actor.tenant_id,
            ),
            user_id=actor.id,
            right=ResourceRightsEnum.own,
            actor=actor,
        )
        # well we dont need to talk to the user management anymore
        item = Item.from_orm(db_item)
        # item.created_by_name = actor.name
    return item


def update_item(item_id: str, item_patch: ItemPatch, actor: UserInJWT) -> Item:
    """here we need to enforce it, cos"""

    enforce(
        actor=actor,
        item_id=item_id,
        domain=ResourceDomainEnum.items,
        action=ResourceActionsEnum.update,
    )

    with get_db() as db:
        db_item = ItemRepo.update(
            db=db, item_id=item_id, item_patch=item_patch, actor=actor
        )
        # user_data_dict = UserRepo.get_user_data(db=db, user_ids=[db_item.created_by])
        item = Item.from_orm(db_item)
        # item.created_by_name = user_data_dict[db_item.created_by].name
        # item.modified_by_name = actor.name
    return item


def list_items(item_query: ItemQuery, actor: UserInJWT) -> ItemWithPaging:
    """no need to enforce"""

    with get_db() as db:
        casbin_enforcer = get_or_create_enforcer(
            tenant_id=actor.tenant_id, actor_id=actor.id
        )
        permissions = casbin_enforcer.get_permissions_for_user_in_domain(
            user=actor.id, domain=actor.tenant_id
        )

        item_ids = [
            get_item_id_from_resource_id(
                resource_id=p[2],
                domain=ResourceDomainEnum.items,
                tenant_id=actor.tenant_id,
            )
            for p in permissions
            if ResourceDomainEnum.items in p[2]
        ]

        db_items, paging = ItemRepo.get_all(
            db=db,
            query_pagination=item_query,
            item_ids=item_ids,
        )

        # use list(set([])) to remove dups
        # user_ids = list(
        #     set([x.created_by for x in db_items] + [x.modified_by for x in db_items])
        # )
        # user_data_dict = UserRepo.get_user_data(
        #     db=db, user_ids=[x for x in user_ids if x is not None]
        # )

        items = [Item.from_orm(x) for x in db_items]
        # for item in items:
        #     item.created_by_name = user_data_dict.get(item.created_by).name
        #     if item.modified_by:
        #         item.modified_by_name = user_data_dict.get(item.modified_by).name

    return ItemWithPaging(data=items, paging=paging)


def share_item(item_id: str, user_share: UserShare, actor: UserInJWT):
    """POST /items/item_id/sharees user_share"""
    enforce(
        actor=actor,
        item_id=item_id,
        domain=ResourceDomainEnum.items,
        action=ResourceActionsEnum.share,
    )
    with get_db() as db:

        # ask the user management if the user
        # exists, and get name and email of the user
        # so here need to ask user management

        # raises exception if the user does not exist
        # sharee = UserManagementService.get_user_info_from_user_management(
        #     user_id=user_share.id, tenant_id=actor.tenant_id
        # )
        # create the user if the user is not here
        db_sharee = UserRepo.get_or_create(db=db, user=sharee)

        # add casbin, raises exception if user has right to the resource already
        CasbinRepo.create_or_update_policy(
            db=db,
            resource_id=get_resource_id_from_item_id(
                item_id=item_id,
                domain=ResourceDomainEnum.items,
                tenant_id=actor.tenant_id,
            ),
            user_id=db_sharee.id,
            right=user_share.role,
            actor=actor,
        )


def unshare_item(item_id: str, user_id: str, actor: UserInJWT):
    enforce(
        actor=actor,
        item_id=item_id,
        domain=ResourceDomainEnum.items,
        action=ResourceActionsEnum.share,
    )
    with get_db() as db:
        CasbinRepo.delete_policy(
            db=db,
            resource_id=get_resource_id_from_item_id(
                item_id=item_id,
                domain=ResourceDomainEnum.items,
                tenant_id=actor.tenant_id,
            ),
            user_id=user_id,
            tenant_id=actor.tenant_id,
        )


def get_item(item_id: str, actor: UserInJWT) -> Item:
    enforce(
        actor=actor,
        item_id=item_id,
        domain=ResourceDomainEnum.items,
        action=ResourceActionsEnum.get,
    )
    with get_db() as db:
        db_item = ItemRepo.get(db=db, item_id=item_id)

        # involved_user_ids = [db_item.created_by]
        # if db_item.modified_by:
        #     involved_user_ids.append(db_item.modified_by)
        # user_data_dict = UserRepo.get_user_data(db=db, user_ids=involved_user_ids)
        item = Item.from_orm(db_item)
        # item.created_by_name = user_data_dict[db_item.created_by].name
        # item.modified_by_name = (
        #     None
        #     if db_item.modified_by is None
        #     else user_data_dict[db_item.modified_by].name
        # )
    return item


def patch_item(item_id: str, actor: UserInJWT) -> None:
    enforce(
        actor=actor,
        item_id=item_id,
        domain=ResourceDomainEnum.items,
        action=ResourceActionsEnum.update,
    )
    print("can patch..")


def delete_item(item_id: str, actor: UserInJWT) -> None:
    enforce(
        actor=actor,
        item_id=item_id,
        domain=ResourceDomainEnum.items,
        action=ResourceActionsEnum.delete,
    )
    with get_db() as db:
        ItemRepo.delete(db=db, item_id=item_id)
        CasbinRepo.delete_policies_with_resource_id(
            db=db,
            resource_id=get_resource_id_from_item_id(
                item_id=item_id,
                domain=ResourceDomainEnum.items,
                tenant_id=actor.tenant_id,
            ),
        )


def list_sharee_of_item(
    item_id: str, query_pagination: QueryPagination, actor: UserInJWT
):
    enforce(
        actor=actor,
        item_id=item_id,
        domain=ResourceDomainEnum.items,
        action=ResourceActionsEnum.get,
    )
    with get_db() as db:

        policies = CasbinRepo.get_all_policies_of_resource(
            db=db,
            resource_id=get_resource_id_from_item_id(
                item_id=item_id,
                domain=ResourceDomainEnum.items,
                tenant_id=actor.tenant_id,
            ),
            # tenant_id=actor.tenant_id,
        )

        user_id_to_resource_right_mapping = {
            p.v0: p.v3 for p in policies if p.v0 != RoleEnum.admin
        }
    return user_id_to_resource_right_mapping

    #     db_users, paging = UserRepo.get_all(
    #         db=db,
    #         query_pagination=query_pagination,
    #         user_ids=list(user_id_to_resource_right_mapping.keys()),
    #     )

    #     users_as_sharee = [UserAsSharee.from_orm(x) for x in db_users]

    #     for user in users_as_sharee:
    #         user.role = user_id_to_resource_right_mapping[user.id]

    # return UserAsShareeWithPaging(data=users_as_sharee, paging=paging)
