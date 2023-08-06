# importing libraries and functions
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

import schemas
import crud.chat_message
from auth import AuthHandler
from db import get_session

auth_handler = AuthHandler()
db_session = Depends(get_session)


# instantiating the router
router = APIRouter()


# instantiating websocket
class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_json(self, websocket: WebSocket, json: dict):
        await websocket.send_json(json)

    async def broadcast_json(self, json: dict):
        for connection in self.active_connections:
            await connection.send_json(json)

manager = WebsocketConnectionManager()


# instantiating the websockets
@router.websocket('/chat_messages')
async def websocket_chat_messages(websocket: WebSocket, session: Session = db_session, auth_user=Depends(auth_handler.websocket_access_wrapper)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            try:
                schema = schemas.ChatMessageCreate(**data)
                chat_message = crud.chat_message.create_chat_message(session=session, chat_message=schema)
                await manager.broadcast_json({
                    'id': chat_message.id,
                    'text': chat_message.text,
                    'created_at': chat_message.created_at.isoformat(),
                    'last_updated': chat_message.last_updated.isoformat(),
                    'is_hidden': chat_message.is_hidden,
                    'user_username': chat_message.user_username,
                })
            except Exception as e:
                await manager.send_message(websocket, str(e))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
