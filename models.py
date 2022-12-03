from sqlalchemy import (Column, DateTime, ForeignKey,
                        Integer, BigInteger, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()


class Telebot_User(Base):
    __tablename__ = "telebot_users"
    chat_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(30), nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())

    tasks = relationship("Telebot_Task", back_populates="owner")


class Telebot_Task(Base):
    __tablename__ = "telebot_tasks"
    task_id = Column(BigInteger().with_variant(Integer, "sqlite"),
                     primary_key=True)
    task_name = Column(String(30), nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(BigInteger, ForeignKey("telebot_users.chat_id"))

    owner = relationship("Telebot_User", back_populates="tasks")
