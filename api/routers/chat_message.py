# importing libraries and functions
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas, models
import crud.chat_message, crud.user
from db import get_session
from auth import auth_user_on_route


# instantiating the router
router = APIRouter()


# instantiating the routes
@router.post('/chat_message')
def post_chat_message(auth: Annotated[models.User, Depends(auth_user_on_route)], chat_message: schemas.ChatMessageCreate, session: Session = Depends(get_session)):
    user_info = crud.user.read_user(session=session, username=chat_message.user_username)

    if not user_info:
        return HTTPException(status_code=400, detail='No user found with this username. Please check and try again later.')

    return crud.chat_message.create_chat_message(session=session, chat_message=chat_message)


@router.get('/chat_message/{id}')
def get_chat_message(auth: Annotated[models.User, Depends(auth_user_on_route)], id: str, session: Session = Depends(get_session)):
    chat_message_info = crud.chat_message.read_chat_message(session=session, id=id)

    if chat_message_info:
        return chat_message_info
    else:
        raise HTTPException(status_code=404, detail='No chat message found with this id.')


@router.get('/chat_messages')
def get_all_chat_messages(auth: Annotated[models.User, Depends(auth_user_on_route)], session: Session = Depends(get_session)):
    return crud.chat_message.read_all_chat_messages(session=session)


@router.get('/chat_messages/available')
def get_all_available_chat_messages(auth: Annotated[models.User, Depends(auth_user_on_route)], session: Session = Depends(get_session)):
    return crud.chat_message.read_all_available_chat_messages(session=session)


@router.patch('/chat_message/{id}')
def patch_chat_message(auth: Annotated[models.User, Depends(auth_user_on_route)], id: str, chat_message: schemas.ChatMessageChange, session: Session = Depends(get_session)):
    chat_message_dict = chat_message.model_dump()
    chat_message_dict = {k: v for k, v in chat_message_dict.items() if v}

    return crud.chat_message.update_chat_message(session=session, id=id, update_dict=chat_message_dict)


@router.get('/chat_message/{id}/toggle_hide')
def toggle_hide_chat_message(auth: Annotated[models.User, Depends(auth_user_on_route)], id: str, session: Session = Depends(get_session)):
    chat_message_info = crud.chat_message.read_chat_message(session=session, id=id)

    if not chat_message_info:
        raise HTTPException(status_code=404, detail='No chat message found with this id.')

    return crud.chat_message.toggle_hide_chat_message(session=session, chat_message=chat_message_info)


@router.delete('/chat_message/{id}')
def delete_chat_message(auth: Annotated[models.User, Depends(auth_user_on_route)], id: str, session: Session = Depends(get_session)):
    return crud.chat_message.delete_chat_message(session=session, id=id)