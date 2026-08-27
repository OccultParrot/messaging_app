from fastapi import WebSocket
from data_types import User

class ConnectionManager:
    connections: dict[int, WebSocket]

    async def connect(self, user: User, websocket: WebSocket):
        if user.id == None:
            return
        
        for c in self.connections.values():
            await c.send_json({"joined": user})

        self.connections[user.id] = websocket