from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


from server.config import CONFIG

engine = create_engine(CONFIG.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
