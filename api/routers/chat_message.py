# importing libraries and functions
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import AuthHandler
import schemas
import crud.chat_message, crud.user
from db import get_session

auth_handler = AuthHandler()
db_session = Depends(get_session)


# instantiating the router
router = APIRouter()


# instantiating the routes
@router.post('/chat_message', response_model=schemas.ChatMessage)
def post_chat_message(chat_message: schemas.ChatMessageCreate, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    user_obj = crud.user.read_user(session=session, username=chat_message.user_username)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No user found with this username.')

    return crud.chat_message.create_chat_message(session=session, chat_message=chat_message)


@router.get('/chat_message/{id}', response_model=schemas.ChatMessage)
def get_chat_message(id: str, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    chat_message_info = crud.chat_message.read_chat_message(session=session, id=id)

    if chat_message_info:
        return chat_message_info
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No chat message found with this id.')  


@router.get('/chat_messages', response_model=list[schemas.ChatMessage])
def get_all_chat_messages(session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    return crud.chat_message.read_all_chat_messages(session=session)


@router.get('/chat_messages/available', response_model=list[schemas.ChatMessage])
def get_all_available_chat_messages(session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    return crud.chat_message.read_all_available_chat_messages(session=session)


@router.patch('/chat_message/{id}', response_model=schemas.ChatMessage)
def patch_chat_message(id: str, chat_message: schemas.ChatMessageChange, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    chat_message_obj = crud.chat_message.read_chat_message(session=session, id=id)
    if not chat_message_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No chat message found with this id.')
    
    chat_message_dict = chat_message.model_dump()
    chat_message_dict = {k: v for k, v in chat_message_dict.items() if v}

    return crud.chat_message.update_chat_message(session=session, id=id, update_dict=chat_message_dict)


@router.get('/chat_message/{id}/toggle_hide', response_model=schemas.ChatMessage)
def toggle_hide_chat_message(id: str, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    chat_message_obj = crud.chat_message.read_chat_message(session=session, id=id)
    if not chat_message_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No chat message found with this id.')

    return crud.chat_message.toggle_hide_chat_message(session=session, chat_message=chat_message_obj)


@router.delete('/chat_message/{id}')
def delete_chat_message(id: str, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    chat_message_obj = crud.chat_message.read_chat_message(session=session, id=id)
    if not chat_message_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No chat message found with this id.')
    
    return crud.chat_message.delete_chat_message(session=session, id=id)
