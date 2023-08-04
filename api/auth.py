# importing libraries and functions
import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import crud.user
from db import get_session

db_session = Depends(get_session)

from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))



# implementing auth
class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    
    ############### SECURE PASSWORD ###############
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)


    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)


    def encode_token(self, username, type):
        payload = dict(
            iat = datetime.utcnow(),
            iss = username,
            sub = type,
        )
        to_encode = payload.copy()

        if type == 'access_token':
            to_encode.update({'exp': to_encode['iat'] + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
        else:
            to_encode.update({'exp': to_encode['iat'] + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


    ############### LOG IN (GET USER CREDENTIALS) ###############
    def encode_login_token(self, username):
        access_token = self.encode_token(username, 'access_token')
        refresh_token = self.encode_token(username, 'refresh_token')

        login_token = dict(
            access_token=f'{access_token}',
            refresh_token=f'{refresh_token}'
        )
        return login_token


    def encode_update_token(self, username):
        access_token = self.encode_token(username, 'access_token')

        update_token = dict(
            access_token=f'{access_token}'
        ) 
        return update_token


    def decode_access_token(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            if payload['sub'] != 'access_token':
                raise jwt.InvalidTokenError()
            
            return payload['iss']
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Signature has expired.')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.')
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication error. Please try again later.')


    def decode_refresh_token(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            if payload['sub'] != 'refresh_token':
                raise jwt.InvalidTokenError()
            
            return payload['iss']
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Signature has expired.')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.')
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication error. Please try again later.')


    ############### AUTHENTICATE USER ###############
    def auth_access_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security), session: Session = db_session):
        username = self.decode_access_token(auth.credentials)

        if username == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized.')
        
        user = crud.user.read_user(session=session, username=username)

        if user == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found.')
        elif not user.is_enabled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is currently unenabled.')
        
        return user


    ############### UPDATE USER CREDENTIALS ###############
    def auth_refresh_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security), session: Session = db_session):
        username = self.decode_refresh_token(auth.credentials)

        if username == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized.')
        
        user = crud.user.read_user(session=session, username=username)

        if user == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found.')
        elif not user.is_enabled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is currently unenabled.')

        updated_credentials = self.encode_update_token(username)
        
        return updated_credentials
