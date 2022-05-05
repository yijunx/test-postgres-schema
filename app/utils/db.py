from contextlib import contextmanager
from app.utils.config import configurations as conf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from alembic.config import Config
from alembic import command


alembic_cfg = Config("/path/to/yourapp/alembic.ini")


@contextmanager
def get_db(tenand_id: str):
    """now we need to embed the tenant id here"""
    dbschema = tenand_id
    db_engine = create_engine(
        url=conf.DATABASE_URI,
        pool_pre_ping=True,
        connect_args={"options": f"-csearch_path={dbschema}"},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        # can roll other things back here
        raise
    finally:
        session.close()


def get_all_schemas():
    engine = create_engine(url=conf.DATABASE_URI)
    with engine.connect() as conn:
        rs = conn.execute(
            text("SELECT schema_name FROM information_schema.schemata;")
        )
    return [row[0] for row in rs]


def remove_a_schema():
    ...


def migrate_a_schema(tenand_id: str):
    dbschema = tenand_id
    engine = create_engine(
        url=conf.DATABASE_URI,
        pool_pre_ping=True,
        connect_args={"options": f"-csearch_path={dbschema}"},
    )
    with engine.begin() as connection:
        alembic_cfg.attributes['connection'] = connection
        command.upgrade(alembic_cfg, "head")


def migrate_all_schemas():
    # get all tenant ids
    # well i hope is working
    ...
