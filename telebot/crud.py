from typing import List

from sqlalchemy.orm import Session

import models
from constants import MAX_TASKS


def check_user(db: Session, chat_id: int):
    return db.query(models.Telebot_User).filter(
        models.Telebot_User.chat_id == chat_id
    ).first()


def create_get_update_user(db: Session, chat_id: int,
                           first_name: str) -> models.Telebot_User:
    user = check_user(db, chat_id)
    if user:
        if user.first_name == first_name:
            return user
        else:
            user.first_name = first_name
    else:
        user = models.Telebot_User(chat_id=chat_id, first_name=first_name)
        db.add(user)
    db.commit()
    return user


def add_task(db: Session, chat_id: int,
             task: str) -> models.Telebot_Task:
    count = db.query(models.Telebot_Task).filter(
        models.Telebot_Task.owner_id == chat_id
    ).count()
    if count >= MAX_TASKS:
        return None
    task = models.Telebot_Task(task_name=task, owner_id=chat_id)
    db.add(task)
    db.commit()
    return task


def task_list(db: Session,
              chat_id: models.Telebot_User) -> List[models.Telebot_Task]:
    return db.query(models.Telebot_Task).filter(
        models.Telebot_Task.owner_id == chat_id
    ).order_by(models.Telebot_Task.creation_date.desc()).all()


def delete_task(db: Session, task_id: int) -> None:
    db.query(models.Telebot_Task).filter(
        models.Telebot_Task.task_id == task_id
    ).delete()
    db.commit()
