from typing import Dict, Tuple, List
import app.models.db.models as models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.exceptions.user import UserAlreadyExists
from app.models.pagination import QueryPagination, ResponsePagination
from app.models.schemas.user import UserInJWT
from app.models.user import User
from app.repositories.util import translate_query_pagination


def create(db: Session, user: User) -> models.User:
    """
    here the user already create himself
    with data from cookie
    there is no way other people create user for him/her
    """

    # now = datetime.now(timezone.utc)

    db_item = models.User(
        id=user.id,
        name=user.name,
        email=user.email,
    )
    db.add(db_item)
    # db.flush()
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExists(user_id=user.id)
    return db_item


def delete_all(db: Session) -> None:
    db.query(models.User).delete()


def delete(db: Session, user_id: str) -> None:
    db_item = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_item:
        raise Exception("user does not exist")
    db.delete(db_item)


def get(db: Session, user_id: str) -> models.User:
    db_item = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_item:
        raise Exception("user does not exist")
    return db_item


def get_user_data(db: Session, user_ids: str) -> Dict[str, User]:
    db_items: List[models.User] = db.query(models.User).filter(
        models.User.id.in_(user_ids)
    )

    return {x.id: User(id=x.id, name=x.name, email=x.email) for x in db_items}


def get_or_create(db: Session, user: UserInJWT) -> models.User:
    try:
        db_item = create(db=db, user=user)
    except UserAlreadyExists:
        db_item = db.query(models.User).filter(models.User.id == user.id).first()
    return db_item


def get_all(
    db: Session, query_pagination: QueryPagination, user_ids: List[str]
) -> Tuple[List[models.User], ResponsePagination]:
    """used for get sharees"""
    query = db.query(models.User)
    query = query.filter(models.User.id.in_(user_ids))

    total = query.count()
    limit, offset, paging = translate_query_pagination(
        total=total, query_pagination=query_pagination
    )

    db_items = query.order_by(models.User.name).limit(limit).offset(offset)
    return db_items, paging
