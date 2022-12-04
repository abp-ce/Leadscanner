from typing import Optional

from sqlalchemy.orm import Session

import schemas
from dependencies import get_db
from fastapi import APIRouter, Depends, status

from . import crud

LIST_COMMAND = '\n  /list - список задач'

router = APIRouter(
    prefix="/telebot",
    tags=["telebot"]
)


def add_task(db: Session, update: schemas.tgrmUpdate,
             chat_id: int, res: schemas.tgrmSendMessage):
    task = crud.add_task(db, chat_id, update.message.text)
    if task:
        res.text = 'Задача добавлена' + LIST_COMMAND
    else:
        res.text = 'Количество задач превышает допустимые'


def make_list(db: Session, chat_id: int, res: schemas.tgrmSendMessage):
    res.text = ('Нажмите на задачу, что бы удалить'
                + LIST_COMMAND)
    tasks = crud.task_list(db, chat_id)
    row = []
    for task in tasks:
        row.append([schemas.tgrmInlineKeyboardButton(
            text=task.task_name,
            callback_data=task.task_id
        )])
    res.reply_markup = schemas.tgrmInlineKeyboardMarkup(
        tag='Inline',
        inline_keyboard=row
    )


@router.post("/", response_model=Optional[schemas.tgrmSendMessage],
             response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def telebot(update: schemas.tgrmUpdate, db: Session = Depends(get_db)):
    res = None
    if update.callback_query:
        crud.delete_task(db, update.callback_query.data)
        res = schemas.tgrmSendMessage(
            chat_id=update.callback_query.message.chat.id,
            text='Успешно удалено' + LIST_COMMAND
        )
    elif update.message:
        res = schemas.tgrmSendMessage(chat_id=update.message.chat.id, text='')
        user = crud.create_get_update_user(db, update.message.chat.id,
                                           update.message.from_.first_name)
        if update.message.text == '/add':
            res.text = 'Введите задачу'
        elif update.message.text == '/list':
            make_list(db, user.chat_id, res)
        elif update.message.text:
            add_task(db, update, user.chat_id, res)
    if res:
        res.method = 'sendMessage'
    return res
