import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read DATABASE_URL from env (set by docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@db:5432/greenlink")

# echo=True will print SQL (useful while learning)
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
