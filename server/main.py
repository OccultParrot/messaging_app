from fastapi import FastAPI, Response, HTTPException, WebSocket

from data_types import User, UsersGet, Message, MessagesGet
from database_client import DatabaseClient
from connection_manager import ConnectionManager

from dotenv import load_dotenv
load_dotenv()

import os

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set.")

db_client = DatabaseClient(db_url)

connection_manager = ConnectionManager()



app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

"""
Routes we need.
/api/messages - GET - Get all messages
/api/messages - POST - Create a new message

/api/users - GET - Get all users
/api/users/{user_id} - GET - Get a specific user by ID
/api/users - POST - Create a new user
"""

@app.get("/api/messages", response_model=MessagesGet)
async def get_messages():
    messages = db_client.get_messages()
    return {"contents": messages}

@app.post("/api/messages")
async def create_message(message: Message):
    db_client.put_message(message.model_dump())
    return {"status": "Message created"}

@app.get("/api/users", response_model=UsersGet)
async def get_users():
    users = db_client.get_users()
    return {"contents": users}

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = db_client.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user

@app.get("/api/auth/{username}", response_model=User)
async def authenticate_user(username: str):
    user = db_client.get_user_by_username(username)

    print(user)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    if user["logged_in"]:
        raise HTTPException(status_code=400, detail="User already logged in.")

    db_client.login_user(user["id"])  # Log the user in
    
    return User(id=user["id"], username=user["username"], color=user["color"])

@app.post("/api/logout/{username}")
async def logout_user(username: str):
    user = db_client.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user["logged_in"]:
        raise HTTPException(status_code=400, detail="User is not logged in.")

    db_client.logout_user(user["id"])  # Log the user out
    
    return {"status": "User logged out"}

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    db_client.put_user(user.model_dump())

    user_data = db_client.get_user_by_username(user.username)

    return user_data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    user = db_client.get_user(user_id)
    print(user)
    if not user:
        return
    
    await connection_manager.connect(user, websocket)
    
    while True:
        data = await websocket.receive_json()

        user_id = data.get("user_id")
        message = data.get("message", "")

        user_data = db_client.get_user(user_id)
        if not user_data:
            print("Error, Null user")
            continue
        
        # Here you can handle the received data, e.g., broadcast it to other clients
        await connection_manager.send_message({
            "username": user_data.username,
            "color": user_data.color,
            "message": message
        }, user_id)