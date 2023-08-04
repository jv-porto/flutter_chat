# importing libraries and functions
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import AuthHandler
import schemas
import crud.user
from db import get_session

auth_handler = AuthHandler()
db_session = Depends(get_session)


# instantiating the router
router = APIRouter()


# instantiating the routes
@router.post('/user', response_model=schemas.User)
def post_user(user: schemas.UserCreate, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    user_obj = crud.user.read_user(session=session, username=user.username)
    if user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Another user has already registered with this username.')
    
    return crud.user.create_user(session=session, user=user)


@router.get('/user/{username}', response_model=schemas.User)
def get_user(username: str, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    return crud.user.read_user(session=session, username=username)


@router.get('/users', response_model=list[schemas.User])
def get_all_users(session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    return crud.user.read_all_users(session=session)


@router.get('/users/available', response_model=list[schemas.User])
def get_all_available_users(session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    return crud.user.read_all_available_users(session=session)


@router.patch('/user/{username}', response_model=schemas.User)
def patch_user(username: str, user: schemas.UserChange, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    user_obj =  crud.user.read_user(session=session, username=username)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user found with this username.')
    
    user_dict = user.model_dump()
    user_dict = {k: v for k, v in user_dict.items() if v}

    return crud.user.update_user(session=session, username=username, update_dict=user_dict)


@router.get('/user/{username}/toggle_enable', response_model=schemas.User)
def toggle_enable_user(username: str, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    user_obj = crud.user.read_user(session=session, username=username)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user found with this username.')

    return crud.user.toggle_enable_user(session=session, user=user_obj)


@router.delete('/user/{username}')
def delete_user(username: str, session: Session = db_session, auth_user=Depends(auth_handler.auth_access_wrapper)):
    user_obj = crud.user.read_user(session=session, username=username)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user found with this username.')
    
    return crud.user.delete_user(session=session, username=username)
