from contextlib import contextmanager
from app.utils.config import configurations as conf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from alembic.config import Config
from alembic import command
import app.utils.context_variables as contextvars


alembic_cfg = Config("alembic.ini")


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


def get_schema_for_tenant(tenant_id: str):
    return (
        f"tenant_{tenant_id.replace('-', '_')}"
        if tenant_id != conf.DEFAULT_TENANT_ID
        else "public"
    )


def get_all_schemas():
    engine = create_engine(url=conf.DATABASE_URI)
    with engine.connect() as conn:
        rs = conn.execute(text("SELECT schema_name FROM information_schema.schemata;"))
    return [row[0] for row in rs if "tenant_" in row[0]] + ["public"]


def remove_a_schema_for_tenant(tenant_id):
    # DROP SCHEMA IF EXISTS accounting;
    engine = create_engine(url=conf.DATABASE_URI)
    with engine.connect() as conn:
        rs = conn.execute(
            text(f"DROP SCHEMA IF EXISTS {get_schema_for_tenant(tenant_id=tenant_id)};")
        )
    return [row[0] for row in rs if "tenant-" in row[0]]


def schema_exists(schema):
    return schema in get_all_schemas()


def migrate_a_schema(schema: str):
    engine = create_engine(
        url=conf.DATABASE_URI,
        pool_pre_ping=True,
        # connect_args={
        #     "options": f"-csearch_path={get_schema_name(tenant_id=tenant_id)}"
        # },
    )
    contextvars.schema.set(schema)
    # with engine.begin() as connection:
        # connection.execute(text(f"SET search_path TO testtest, public"))
        # print(connection.engine.url)
        # conn = connection.execution_options(schema_translate_map={None: schema})
    print("lets see ensure...")
    # create table if there is no table


    with engine.connect() as conn:
        conn.execute(
            text(f"CREATE TABLE IF NOT EXISTS {schema}.alembic_version (version_num varchar(32), PRIMARY KEY( version_num ));")
        )

    # command.ensure_version(alembic_cfg)
    print("well..we make sure the table is there")
    # alembic_cfg.attributes["connection"] = connection
    # alembic_cfg.attributes["schemas"] = [get_schema_name(tenant_id=tenant_id)]
    command.upgrade(alembic_cfg, "head")
    print(f"migration for schema {schema} is done!")


def migrate_all_schemas():
    """used for software update requires db change.."""
    schemas = get_all_schemas()
    for schema in schemas:
        print(f"doing schema {schema}")
        migrate_a_schema(schema=schema)


def get_ready_for_tenant(tenant_id):
    """used for prepare db schema for a new comer"""
    schema = get_schema_for_tenant(tenant_id=tenant_id)
    if schema_exists(schema=schema):
        migrate_a_schema(schema=schema)
    else:
        raise Exception("schema not created yet")
