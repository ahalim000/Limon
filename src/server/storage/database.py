from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from server.config import CONFIG

engine = create_engine(CONFIG.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
