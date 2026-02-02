"""Check database tables."""
from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [r[0] for r in result]
    print("Tables in database:", tables)
    
    # Check if users table has the right columns
    if 'users' in tables:
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'"))
        print("\nUsers table columns:")
        for col in result:
            print(f"  - {col[0]}: {col[1]}")
