# importing libraries and functions
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models, schemas
import crud.user
from db import get_session


# loading environment variables
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


# instantiating the router
router = APIRouter()


# auth
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')

############### TRANSFORM PASSWORD ###############
def get_password_hash(password) -> str:
    return pwd_context.hash(password)

##### AUTH ROUTE #####
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, session = next(get_session())) -> models.User | bool:
    user = crud.user.read_user(session=session, username=username)
    if not user:
        return False
    
    if not verify_password(password, user.password):
        return False
    
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


@router.post('/auth')
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrent username and password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)

    return {'access_token': access_token, 'token_type': 'bearer'}


############### AUTHENTICATE USER ON ROUTE ###############
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session = next(get_session())) -> models.User:
    def credentials_exception(error, message: str = 'Could not validate credentials.'):
        if error:
            message += ' ' + str(error)
        
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')

        if username is None:
            raise credentials_exception()
        
    except JWTError as e:
        raise credentials_exception(error=e)
    
    user = crud.user.read_user(session=session, username=username)
    if user is None:
        raise credentials_exception()
    
    return user


async def auth_user_on_route(auth: Annotated[str, Depends(oauth2_scheme)]):
    return await get_current_user(auth)


##### GET CURRENT USER ROUTE #####
async def get_current_active_user(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.User:
    if not current_user.is_enabled:
        raise HTTPException(status_code=400, detail='Inactive user.')
    
    return current_user


@router.get('/users/me', response_model=schemas.User)
async def read_users_me(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> models.User:
    return current_user


@router.get('/users/me/items')
async def read_own_items(current_user: Annotated[models.User, Depends(get_current_active_user)]) -> list:
    return [{'item_id': 'Foo', 'owner': current_user.username}]
