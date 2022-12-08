from typing import Dict, NoReturn, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from constants import DATABASE_NAME, DATABASE_TYPE
from dependencies import get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schemas import TaskList
from telebot import crud, telebot


app = FastAPI(dependencies=[Depends(get_db)])

app.include_router(telebot.router)

origins = [
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_pool() -> None:
    if DATABASE_TYPE == 'SQLITE':
        engine = create_engine(
            DATABASE_NAME,
            connect_args={'check_same_thread': False}
        )
    else:
        engine = create_engine(
            DATABASE_NAME
        )

    app.state.session = sessionmaker(autocommit=False, autoflush=False,
                                     bind=engine)


@app.head('/uptimerobot/', status_code=status.HTTP_200_OK)
async def uptimerobot():
    return None


@app.get('/add/{chat_id}', status_code=status.HTTP_201_CREATED)
async def add_task(chat_id: int, task: str = 'Empty',
                   db: Session = Depends(get_db)) -> Union[Dict, NoReturn]:
    user = crud.check_user(db, chat_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Chat id не существует')
    res = crud.add_task(db, chat_id, task)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Количество задач превышает допустимые')
    return {'status': 'Задача добавлена'}


@app.get('/list/{chat_id}', response_model=TaskList,
         status_code=status.HTTP_200_OK)
async def task_list(
    chat_id: int,
    db: Session = Depends(get_db)
) -> Union[NoReturn, TaskList]:
    user = crud.check_user(db, chat_id)
    if not user:
        raise HTTPException(status_code=404, detail='Chat id не существует')
    return TaskList(
        tasks=[task.task_name for task in crud.task_list(db, chat_id)]
    )
