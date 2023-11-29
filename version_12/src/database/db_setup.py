from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.env_models import settings

engine = create_engine(
    f'mysql+pymysql://{settings.username}:{settings.key_db}@{settings.host}:{settings.port}/{settings.database}'
    )

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()