from typing import List, Tuple, Union
import app.models.db.models as models
from app.models.schemas.item import ItemCreate, ItemPatch, ItemQuery
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.pagination import ResponsePagination
from datetime import datetime, timezone
from app.models.exceptions.item import ItemAlreadyExists, ItemDoesNotExist
from app.repositories.util import translate_query_pagination
import uuid


def create(db: Session, item_create: ItemCreate, actor: User) -> models.Item:
    """ """
    db_item = models.Item(
        id=str(uuid.uuid4()),
        name=item_create.name,
        desc=item_create.desc,
        created_by=actor.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(db_item)
    # here we can try flush, and catch the integrity
    # error if there are unique contraints in the model
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ItemAlreadyExists(item_name=item_create.name)
    return db_item


def get(db: Session, item_id: str) -> models.Item:
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise ItemDoesNotExist(item_id=item_id)
    return db_item


def delete(db: Session, item_id: str) -> None:
    db_item = get(db=db, item_id=item_id)
    db.delete(db_item)


def get_by_name(db: Session, item_name: str) -> Union[models.Item, None]:
    db_item = db.query(models.Item).filter(models.Item.name == item_name).first()
    return db_item


def get_all_without_pagination(
    db: Session, item_name: str = None, limit: int = 50
) -> Tuple[List[models.Item], ResponsePagination]:
    """
    limit is things to get per batch...
    """

    query = db.query(models.Item)

    if item_name:
        query = query.filter(models.Item.name.contains(item_name))

    left_over = query.count()
    paging = ResponsePagination(
        total=left_over, page_size=left_over, current_page=1, total_pages=1
    )
    offset = 0
    results = []
    while left_over > 0:
        items_in_a_batch = (
            query.order_by(models.Item.created_at.desc()).limit(limit).offset(offset)
        )
        left_over -= limit
        offset += limit
        results += items_in_a_batch
    return results, paging


def get_all(
    db: Session, query_pagination: ItemQuery, admin_access: bool, item_ids: List[str]
) -> Tuple[List[models.Item], ResponsePagination]:

    query = db.query(models.Item)

    if not admin_access:
        # if there is no admin access, this user can only see what
        # he created or shared to
        query = query.filter(models.Item.id.in_(item_ids))

    if query_pagination.name:
        query = query.filter(models.Item.name.contains(query_pagination.name))

    total = query.count()
    limit, offset, paging = translate_query_pagination(
        total=total, query_pagination=query_pagination
    )
    db_items = query.order_by(models.Item.created_at.desc()).limit(limit).offset(offset)
    return db_items, paging


def update(
    db: Session, item_id: str, item_patch: ItemPatch, actor: User
) -> models.Item:
    """used for update item"""
    db_item = get(db=db, item_id=item_id)
    db_item.name = item_patch.name or db_item.name
    db_item.desc = item_patch.desc or db_item.desc
    # logs the action
    db_item.modified_at = datetime.now(timezone.utc)
    db_item.modified_by = actor.id
    return db_item
