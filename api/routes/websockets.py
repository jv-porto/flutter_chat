# importing libraries and functions
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
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

@router.websocket('/chat_messages')
async def websocket_chat_messages(websocket: WebSocket, session: Session = db_session):
    await chat_messages_manager.connect(websocket)

    auth_json = await websocket.receive_json()

    if 'access_token' in auth_json:
        token = auth_json['access_token']
    else:
        await websocket.send_text('Unauthorized.')
        return await websocket.close()
    
    auth_user = await auth_handler.websocket_access_wrapper(websocket=websocket, token=token, session=session)
    if auth_user:
        await websocket.send_text('Successfully authorized!')
    else:
        return await websocket.close()

    chat_messages = crud.chat_message.read_all_chat_messages(session=session)
    chat_messages_list = []
    for message in chat_messages:
        message_json = {
            'id': message.id,
            'text': message.text,
            'created_at': message.created_at.isoformat(),
            'last_updated': message.last_updated.isoformat(),
            'is_hidden': message.is_hidden,
            'user_username': message.user_username,
        }
        chat_messages_list.append(message_json)
    await chat_messages_manager.send_json(websocket, chat_messages_list)
    
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
