from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .. import config
import os
from pathlib import Path

# Ensure the db directory exists based on config.db_path
if config.db_path.startswith("sqlite:///"):
    db_file = config.db_path.replace("sqlite:///", "")
    db_dir = os.path.dirname(os.path.abspath(db_file))
    os.makedirs(db_dir, exist_ok=True)

engine = create_engine(config.db_path, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
