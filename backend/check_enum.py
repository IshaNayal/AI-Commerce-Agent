from app.config import settings
from sqlalchemy import create_engine, text
e=create_engine(settings.database_url)
c=e.connect()
print(c.execute(text("SELECT typname FROM pg_type WHERE typname = 'order_status'")).fetchall())
c.close()
