from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Check if the DATABASE_URL environment variable is set, if not use a SQLite database
if "DB_CONNECTION_STR" not in os.environ:
    logger.warning("DB_CONNECTION_STR environment variable not set, using SQLite database.")
    logger.warning("All data will only be saved locally in a SQLite database.")
    logger.warning("Set the DB_CONNECTION_STR environment variable to use a more persistent database.")

DATABASE_URL = os.getenv("DB_CONNECTION_STR", "sqlite:///./database/predictions.db")


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import database.models
    Base.metadata.create_all(bind=engine)
