# importing libraries and functions
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Extra

import schemas
import crud.user
from auth import AuthHandler
from db import get_session

auth_handler = AuthHandler()
db_session = Depends(get_session)


# instantiating the router
router = APIRouter()


# instantiating the routes
@router.post('/login')
async def auth(login_info: schemas.Login, session: Session = db_session):
    user = crud.user.read_user(session=session, username=login_info.username)
    if user == None:
        raise HTTPException(status_code=401, detail='Incorrect username.')
    
    correct_password = auth_handler.verify_password(login_info.password, user.password)
    if not correct_password:
        raise HTTPException(status_code=401, detail='Incorrect password.')
    
    return auth_handler.encode_login_token(user.username)


@router.get('/update_token')
async def refresh_token(updated_credentials=Depends(auth_handler.auth_refresh_wrapper)):
    return updated_credentials


@router.get('/me')
async def current_user(auth_user=Depends(auth_handler.auth_access_wrapper)):
    return auth_user
