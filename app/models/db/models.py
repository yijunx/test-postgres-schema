from sqlalchemy import (
    Column,
    String,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql.sqltypes import BigInteger
from app.models.db.base import Base


class CasbinRule(Base):
    __tablename__ = "casbin_rule"
    __table_args__ = (UniqueConstraint("v0", "v1", name="_v0_v1_uc"),)
    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True)
    ptype = Column(String, nullable=False)
    v0 = Column(
        String, nullable=True, index=True
    )  # user id or role id <- how about add an index here
    v1 = Column(String, nullable=True)  # role id if g, resource id if p
    v2 = Column(String, nullable=True)  # resource right enum
    v3 = Column(String, nullable=True)  # empty
    v4 = Column(String, nullable=True)  # empty
    v5 = Column(String, nullable=True)  # empty

    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    modified_by = Column(String, nullable=True)
    modified_at = Column(DateTime, nullable=True)


class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, index=True)
    # lets suppose the name should be unique
    name = Column(String, nullable=False, unique=True)
    desc = Column(String, nullable=False)

    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    modified_by = Column(String, nullable=True)
    modified_at = Column(DateTime, nullable=True)
