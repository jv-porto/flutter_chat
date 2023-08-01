from datetime import datetime
from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

import models, schemas


def create_chat_message(session: Session, chat_message: schemas.ChatMessageCreate) -> models.ChatMessage:
    chat_message_dict = chat_message.model_dump()
    
    chat_message_obj = models.ChatMessage(**chat_message_dict)

    session.add(chat_message_obj)
    session.commit()
    session.refresh(chat_message_obj)
    
    return chat_message_obj


def read_chat_message(session: Session, id: str) -> models.ChatMessage | None:
    return session.query(models.ChatMessage).get(id)


def read_all_chat_messages(session: Session) -> list[models.ChatMessage]:
    return session.query(models.ChatMessage).all()


def read_all_available_chat_messages(session: Session) -> list[models.ChatMessage]:
    return session.query(models.ChatMessage).filter_by(is_hidden=False).all()


def update_chat_message(session: Session, id: str, update_dict: dict) -> models.ChatMessage | HTTPException:
    update_dict['last_updated'] = datetime.now()

    chat_message_update = session.query(models.ChatMessage).filter_by(id=id).update(update_dict)

    if chat_message_update == 0:
        raise HTTPException(status_code=404, detail='No chat message found with this id.')
    elif chat_message_update != 1:
        raise HTTPException(status_code=500, detail='An error occurred during this process.')
    
    session.commit()
    return read_chat_message(session=session, id=id)


def toggle_hide_chat_message(session: Session, chat_message: models.ChatMessage) -> models.ChatMessage | HTTPException:
    update_dict = {
        'is_hidden': not chat_message.is_hidden,
        'last_updated': datetime.now(),
    }
    chat_message_toggle_hide = session.query(models.ChatMessage).filter_by(id=chat_message.id).update(update_dict)

    if chat_message_toggle_hide == 0:   # verification already performed on route
        raise HTTPException(status_code=404, detail='No chat message found with this id.')
    elif chat_message_toggle_hide != 1:
        raise HTTPException(status_code=500, detail='An error occurred during this process.')
    
    session.commit()
    return read_chat_message(session=session, id=chat_message.id)


def delete_chat_message(session: Session, id: str) -> Response | HTTPException:
    chat_message_delete = session.query(models.ChatMessage).filter_by(id=id).delete()

    if chat_message_delete == 0:
        raise HTTPException(status_code=404, detail='No chat message found with this id.')
    elif chat_message_delete != 1:
        raise HTTPException(status_code=500, detail='An error occurred during this process.')
    
    session.commit()
    return Response(status_code=200, content='The chat message was deleted.')
