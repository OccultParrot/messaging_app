from fastapi import WebSocket
from data_types import User

class ConnectionManager:
    connections: dict[int, WebSocket] = {}

    async def connect(self, user: User, websocket: WebSocket):
        if user.id == None:
            return
        
        for c in self.connections.values():
            await c.send_json({"joined": {"id": user.id, "username": user.username, "color": user.color}})

        self.connections[user.id] = websocket

    async def send_message(self, context: dict, user_id: int):
        for k in self.connections.keys():
            if k == user_id:
                continue # Skip sender
            await self.connections[k].send_json(context)