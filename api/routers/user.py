# importing libraries and functions
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas, models
import crud.user
from db import get_session
from auth import auth_user_on_route


# instantiating the router
router = APIRouter()


# instantiating the routes
@router.post('/user')
def post_user(auth: Annotated[models.User, Depends(auth_user_on_route)], user: schemas.UserCreate, session: Session = Depends(get_session)):
    user_obj = crud.user.read_user(session=session, username=user.username)

    if user_obj:
        raise HTTPException(status_code=400, detail='Another user was already registered with this username. Please choose another username.')
    
    return crud.user.create_user(session=session, user=user)


@router.get('/user/{username}')
def get_user(auth: Annotated[models.User, Depends(auth_user_on_route)], username: str, session: Session = Depends(get_session)):
    user_info = crud.user.read_user(session=session, username=username)

    if user_info:
        return user_info
    else:
        raise HTTPException(status_code=404, detail='No user found with this username.')


@router.get('/users')
def get_all_users(auth: Annotated[models.User, Depends(auth_user_on_route)], session: Session = Depends(get_session)):
    return crud.user.read_all_users(session=session)


@router.get('/users/available')
def get_all_available_users(auth: Annotated[models.User, Depends(auth_user_on_route)], session: Session = Depends(get_session)):
    return crud.user.read_all_available_users(session=session)


@router.patch('/user/{username}')
def patch_user(auth: Annotated[models.User, Depends(auth_user_on_route)], username: str, user: schemas.UserChange, session: Session = Depends(get_session)):
    user_dict = user.model_dump()
    user_dict = {k: v for k, v in user_dict.items() if v}

    return crud.user.update_user(session=session, username=username, update_dict=user_dict)


@router.get('/user/{username}/toggle_enable')
def toggle_enable_user(auth: Annotated[models.User, Depends(auth_user_on_route)], username: str, session: Session = Depends(get_session)):
    user_info = crud.user.read_user(session=session, username=username)

    if not user_info:
        raise HTTPException(status_code=404, detail='No user found with this username.')

    return crud.user.toggle_enable_user(session=session, user=user_info)


@router.delete('/user/{username}')
def delete_user(auth: Annotated[models.User, Depends(auth_user_on_route)], username: str, session: Session = Depends(get_session)):
    return crud.user.delete_user(session=session, username=username)
