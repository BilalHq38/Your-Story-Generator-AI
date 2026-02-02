"""Fix alembic version in database."""
from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("UPDATE alembic_version SET version_num = '003'"))
    conn.commit()
    print("Updated alembic version to '003'")
