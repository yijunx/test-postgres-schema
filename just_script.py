import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text


engine = create_engine("postgresql://postgres:postgres@db:5432/db")


with engine.connect() as conn:
    rs = conn.execute(
        text("SELECT schema_name FROM information_schema.schemata;")
    )

print(rs)
for line in rs:
    print(line)
