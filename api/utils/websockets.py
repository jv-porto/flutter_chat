from fastapi import WebSocket

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
