from sqlalchemy import Column, Integer, VARCHAR, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase
import json

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(VARCHAR(50), unique=True, index=True)
    hashed_password = Column(VARCHAR(60))
    token = Column(VARCHAR(32), default=None, )
    last_action = Column(DateTime, default=None)


class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(VARCHAR(1000))
    owner_id = Column(Integer, ForeignKey("users.id"))


if __name__ == "__main__":
    with open("config.json", "r") as f:
        db_patam = json.load(f)["db"]
        sql_engine = create_engine(
            f"{db_patam['server']}://{db_patam['user']}:{db_patam['password']}"
            f"@{db_patam['host']}:{db_patam['port']}/{db_patam['data_base']}"
        )
    Base.metadata.create_all(sql_engine)

