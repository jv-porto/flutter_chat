# importing libraries and functions
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import schemas
import crud.chat_message, crud.user
from utils.websockets import WebsocketConnectionManager

# load environment variables
load_dotenv()
API_URI = os.getenv('API_URI')


# instantiating the router
router = APIRouter()

# instantiating dependencies
from auth import AuthHandler
from db import get_session

auth_handler = AuthHandler()
db_session = Depends(get_session)


# instantiating websockets
chat_messages_manager = WebsocketConnectionManager()

@router.get('/chat_messages')
def https_websocket_chat_messages():
    return RedirectResponse(f'wss://{API_URI}/ws/chat_messages')

@router.websocket('/chat_messages')
async def websocket_chat_messages(websocket: WebSocket, session: Session = db_session):#, auth_user=Depends(auth_handler.websocket_access_wrapper)):
    await chat_messages_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            try:
                schema = schemas.ChatMessageCreate(**data)
                chat_message = crud.chat_message.create_chat_message(session=session, chat_message=schema)
                await chat_messages_manager.broadcast_json({
                    'id': chat_message.id,
                    'text': chat_message.text,
                    'created_at': chat_message.created_at.isoformat(),
                    'last_updated': chat_message.last_updated.isoformat(),
                    'is_hidden': chat_message.is_hidden,
                    'user_username': chat_message.user_username,
                })

            except Exception as e:
                await chat_messages_manager.send_message(websocket, str(e))

    except WebSocketDisconnect:
        chat_messages_manager.disconnect(websocket)


auth_login_manager = WebsocketConnectionManager()

@router.get('/auth/login')
def https_websocket_auth_login():
    return RedirectResponse(f'wss://{API_URI}/ws/auth/login')

@router.websocket('/auth/login')
async def websocket_auth_login(websocket: WebSocket, session: Session = db_session):
    await auth_login_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            try:
                schema = schemas.Login(**data)

                user = crud.user.read_user(session=session, username=schema.username)
                if user == None:
                    await auth_login_manager.send_message(websocket, 'Incorrect username.')
                else:
                    correct_password = auth_handler.verify_password(schema.password, user.password)
                    if not correct_password:
                        await auth_login_manager.send_message(websocket, 'Incorrect password.')
                    else:
                        auth_info = auth_handler.encode_login_token(user.username)
                        await auth_login_manager.send_json(websocket, auth_info)

            except Exception as e:
                await auth_login_manager.send_message(websocket, str(e))

    except WebSocketDisconnect:
        auth_login_manager.disconnect(websocket)


auth_update_token_manager = WebsocketConnectionManager()

@router.get('/auth/update_token')
def https_websocket_update_token():
    return RedirectResponse(f'wss://{API_URI}/ws/auth/update_token')

@router.websocket('/auth/update_token')
async def websocket_auth_update_token(websocket: WebSocket, session: Session = db_session):
    await auth_update_token_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            try:
                await auth_handler.websocket_refresh_wrapper(websocket=websocket, token=data, session=session)

            except Exception as e:
                await auth_update_token_manager.send_message(websocket, str(e))

    except WebSocketDisconnect:
        auth_update_token_manager.disconnect(websocket)
