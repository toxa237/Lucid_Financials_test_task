from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import json

with open("config.json", "r") as f:
    db_patam = json.load(f)["db"]
    sql_engine = create_engine(
        f"{db_patam['server']}://{db_patam['user']}:{db_patam['password']}"
        f"@{db_patam['host']}:{db_patam['port']}/{db_patam['data_base']}"
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sql_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()