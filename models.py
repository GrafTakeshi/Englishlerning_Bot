import sqlalchemy as sc
from sqlalchemy.orm import relationship, as_declarative

from sqlalchemy import create_engine

from config import DSN


@as_declarative()
class SimpleBase:
    id = sc.Column(sc.Integer, autoincrement=True, primary_key=True)


class Dicrionary(SimpleBase):
    __tablename__ = "dictionary"

    enword = sc.Column(sc.String(length=80), unique=True, nullable=False)
    ruword = sc.Column(sc.String(length=80), unique=True, nullable=False)


class Users(SimpleBase):
    __tablename__ = "users"

    tg_user_id = sc.Column(sc.BIGINT, unique=True, nullable=False)

    # def __repr__(self):
    #     return f'{self.id}: {self.tg_user_id}'


class Usersdict(SimpleBase):
    __tablename__ = "usersdict"

    userdictunit = sc.Column(sc.Integer, sc.ForeignKey("dictionary.id"), nullable=False)
    tg_user_id = sc.Column(sc.Integer, sc.ForeignKey("users.id"), nullable=False)

    # dictionary = relationship(Dicrionary, backref="userdicts")
    # users = relationship(Users, backref="userdicts")


def create_tables(engine):
    SimpleBase.metadata.create_all(engine)
