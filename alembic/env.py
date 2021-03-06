# create (first) migration by
# python -m alembic revision --autogenerate -m "first migration" to create a migration
# run the migration by
# python -m alembic upgrade head

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.utils.config import configurations as app_config
from app.models.db.models import Base

from alembic import context
import app.utils.context_variables as contextvars
from app.utils.db import get_schema_for_tenant

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# this will overwrite the ini-file sqlalchemy.url path
# with the path given in the config of the main code
config.set_main_option("sqlalchemy.url", app_config.DATABASE_URI)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# schemas = config.get_main_option('schemas')

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # below statement will need to work with alembic -x
    # alembic -x tenant=some_schema revision -m "rev1" --autogenerate
    # if current_tenant is None:
    #     current_tenant = context.get_x_argument(as_dictionary=True).get("tenant")

    with connectable.connect() as connection:

        # set search path on the connection, which ensures that
        # PostgreSQL will emit all CREATE / ALTER / DROP statements
        # in terms of this schema by default
        schema = contextvars.schema.get()
        if schema is None:
            schema = get_schema_for_tenant(app_config.DEFAULT_TENANT_ID)
        print(f"schema to do is {schema}")
        conn = connection.execution_options(schema_translate_map={None: schema})
        # print(f"SCHEMA is: {schema}")

        # connection.execute("set search_path to %s" % schema)

        # make use of non-supported SQLAlchemy attribute to ensure
        # the dialect reflects tables in terms of the current tenant name
        # connection.dialect.default_schema_name = schema

        context.configure(
            connection=conn, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
