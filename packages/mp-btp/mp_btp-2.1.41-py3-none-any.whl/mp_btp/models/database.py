from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
from mp_btp.config import get_settings

settings = get_settings()

engine_kwargs = {"pool_pre_ping": True}

if settings.database_url.startswith("postgresql"):
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
elif settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)

# 动态 schema
if settings.database_url.startswith("postgresql"):
    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET search_path TO {settings.schema_name}, public")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_schema():
    """初始化 PostgreSQL schema"""
    if settings.database_url.startswith("postgresql"):
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.schema_name}"))
            conn.commit()


def migrate_db():
    """Run database migrations."""
    with engine.connect() as conn:
        # Add details column to operation_logs if not exists
        try:
            if settings.database_url.startswith("postgresql"):
                conn.execute(text("""
                    ALTER TABLE operation_logs ADD COLUMN IF NOT EXISTS details TEXT
                """))
            else:
                # SQLite
                conn.execute(text("""
                    ALTER TABLE operation_logs ADD COLUMN details TEXT
                """))
            conn.commit()
        except Exception:
            pass  # Column already exists
