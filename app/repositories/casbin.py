from typing import List, Tuple
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.functions import user
from app.models.db import models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.schemas.user import UserInJWT as User
from app.models.pagination import QueryPagination, ResponsePagination
from datetime import datetime, timezone
from app.casbin.role_definition import ResourceRightsEnum, PolicyTypeEnum
from app.models.exceptions.casbin import CasbinRuleAlreadyExists, CasbinRuleDoesNotExist
from app.repositories.util import translate_query_pagination


def create_grouping(
    db: Session, user_id: str, role_id: str, actor: User
) -> models.CasbinRule:
    """used when creating an admin user"""
    db_item = models.CasbinRule(
        # id is auto increment,
        ptype=PolicyTypeEnum.g,
        v0=user_id,
        v1=role_id,
        created_at=datetime.now(timezone.utc),
        created_by=actor.id,
    )

    db.add(db_item)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise CasbinRuleAlreadyExists(user_id=user_id, resource_id=role_id)
    return db_item


def create_policy(
    db: Session, resource_id: str, user_id: str, right: ResourceRightsEnum, actor: User
) -> models.CasbinRule:
    """
    used when share..
    """
    db_item = models.CasbinRule(
        # id is auto increment,
        ptype=PolicyTypeEnum.p,
        v0=user_id,
        v1=resource_id,
        v2=right,
        created_at=datetime.now(timezone.utc),
        created_by=actor.id,
    )
    db.add(db_item)
    # here we can try flush, and catch the integrity
    # error if there are unique contraints in the model
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise CasbinRuleAlreadyExists(user_id=user_id, resource_id=resource_id)
    return db_item


def get_policy(db: Session, resource_id: str, user_id: str) -> models.CasbinRule:
    query = db.query(models.CasbinRule).filter(
        and_(
            models.CasbinRule.ptype == PolicyTypeEnum.p,
            models.CasbinRule.v0 == user_id,
            models.CasbinRule.v1 == resource_id,
        )
    )
    db_item = query.first()
    if db_item is None:
        raise CasbinRuleDoesNotExist(user_id=user_id, resource_id=resource_id)
    return db_item


def get_all_policies_of_resource(
    db: Session, resource_id: str
) -> List[models.CasbinRule]:
    query = db.query(models.CasbinRule).filter(
        and_(
            models.CasbinRule.ptype == PolicyTypeEnum.p,
            models.CasbinRule.v1 == resource_id,
        )
    )
    return query.all()


def get_grouping(db: Session, role_id: str, user_id: str) -> models.CasbinRule:
    query = db.query(models.CasbinRule).filter(
        and_(
            models.CasbinRule.ptype == PolicyTypeEnum.g,
            models.CasbinRule.v0 == user_id,
            models.CasbinRule.v1 == role_id,
        )
    )
    db_item = query.first()
    if db_item is None:
        raise CasbinRuleDoesNotExist(user_id=user_id, resource_id=role_id)
    return db_item


def delete_policies_with_resource_id(db: Session, resource_id: str) -> None:
    """used when the item is deleted"""
    db_items = db.query(models.CasbinRule).filter(models.CasbinRule.v1 == resource_id)
    # only want to delete the records and
    # do not care about the records in the session after the deletion
    # can choose the strategy that ignores the session synchronization
    db_items.delete(synchronize_session=False)


def delete_policy(db: Session, resource_id: str, user_id: str) -> None:
    """used when unshare"""
    db_item = get_policy(db=db, resource_id=resource_id, user_id=user_id)
    db.delete(db_item)


def delete_grouping(db: Session, role_id: str, user_id: str) -> None:
    db_item = get_grouping(db=db, role_id=role_id, user_id=user_id)
    db.delete(db_item)


def update_policy(
    db: Session, resource_id: str, user_id: str, right: ResourceRightsEnum, actor: User
) -> models.CasbinRule:
    """used when update the user rights
    for example, to make a user from view to owner or editor"""
    db_item = get_policy(db=db, resource_id=resource_id, user_id=user_id)
    db_item.v2 = right
    # logs the action
    db_item.modified_at = datetime.now(timezone.utc)
    db_item.modified_by = actor.id
    return db_item


def get_all_grouping(
    db: Session, role_id: str, query_pagination: QueryPagination
) -> Tuple[List[models.CasbinRule], ResponsePagination]:
    query = db.query(models.CasbinRule)
    query = query.filter(models.CasbinRule.v1 == role_id)

    # get paging
    total = query.count()
    limit, offset, paging = translate_query_pagination(
        total=total, query_pagination=query_pagination
    )
    db_items = (
        query.order_by(models.CasbinRule.created_at.desc()).limit(limit).offset(offset)
    )
    return db_items, paging


def create_or_update_policy(
    db: Session, resource_id: str, user_id: str, right: ResourceRightsEnum, actor: User
) -> models.CasbinRule:
    try:
        db_item = update_policy(
            db=db, resource_id=resource_id, user_id=user_id, right=right, actor=actor
        )
    except CasbinRuleDoesNotExist:
        db_item = create_policy(
            db=db, resource_id=resource_id, user_id=user_id, right=right, actor=actor
        )
    return db_item
