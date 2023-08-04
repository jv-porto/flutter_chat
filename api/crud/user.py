from datetime import datetime
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

import models, schemas


def create_user(session: Session, user: schemas.UserCreate) -> models.User:
    user_dict = user.model_dump()
    
    user_obj = models.User(**user_dict)

    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    
    return user_obj


def read_user(session: Session, username: str) -> models.User | None:
    return session.query(models.User).get(username)


def read_all_users(session: Session) -> list[models.User]:
    return session.query(models.User).order_by(models.User.created_at.desc()).all()


def read_all_available_users(session: Session) -> list[models.User]:
    return session.query(models.User).filter_by(is_enabled=True).order_by(models.User.created_at.desc()).all()


def update_user(session: Session, username: str, update_dict: dict) -> models.User | HTTPException:
    from auth import AuthHandler
    auth_handler = AuthHandler()

    if 'password' in update_dict:
        update_dict['password'] = auth_handler.get_password_hash(update_dict['password'])
    
    update_dict['last_updated'] = datetime.now()
    user_update = session.query(models.User).filter_by(username=username).update(update_dict)

    if user_update == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user found with this username.')
    elif user_update != 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occurred during this process.')
    
    session.commit()
    if 'username' in update_dict:
        return read_user(session=session, username=update_dict['username'])
    else:
        return read_user(session=session, username=username)


def toggle_enable_user(session: Session, user: models.User) -> models.User | HTTPException:
    update_dict = {
        'is_enabled': not user.is_enabled,
        'last_updated': datetime.now(),
    }
    user_toggle_enable = session.query(models.User).filter_by(username=user.username).update(update_dict)

    if user_toggle_enable == 0:   # verification already performed on route
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user found with this username.')
    elif user_toggle_enable != 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occurred during this process.')
    
    session.commit()
    return read_user(session=session, username=user.username)


def delete_user(session: Session, username: str) -> Response | HTTPException:
    user_delete = session.query(models.User).filter_by(username=username).delete()

    if user_delete == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user found with this username.')
    elif user_delete != 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occurred during this process.')
    
    session.commit()
    return Response(status_code=status.HTTP_200_OK, content=f'The user was deleted.')
