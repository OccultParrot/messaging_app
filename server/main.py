from fastapi import FastAPI, Response
from pydantic import BaseModel

from database_client import DatabaseClient

from dotenv import load_dotenv
load_dotenv()

import os

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set.")

db_client = DatabaseClient(db_url)

class Message(BaseModel):
    id: int | None = None
    content: str
    user_id: int

class MessagesGet(BaseModel):
    contents: list[Message]

class User(BaseModel):
    id: int | None = None
    username: str
    color: str # As a hex code string, e.g., "#FF5733"

class UsersGet(BaseModel):
    contents: list[User]

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
async def get_messages(response: Response):
    messages = db_client.get_messages()
    response.status_code = 200
    return {"contents": messages}

@app.post("/api/messages")
async def create_message(message: Message, response: Response):
    db_client.put_message(message.model_dump())
    response.status_code = 201
    return {"status": "Message created"}

@app.get("/api/users", response_model=UsersGet)
async def get_users(response: Response):
    users = db_client.get_users()
    response.status_code = 200
    return {"contents": users}

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int, response: Response):
    user = db_client.get_user(user_id)
    if user is None:
        response.status_code = 404
        return {"error": "User not found"}
    response.status_code = 200
    return User(id=user["id"], username=user["username"], color=user["color"])

@app.get("/api/auth/{username}", response_model=User)
async def authenticate_user(username: str, response: Response):
    user = db_client.get_user_by_username(username)
    if user is None:
        response.status_code = 404
        return {"error": "User not found"}

    if user["logged_in"]:
        response.status_code = 400
        return {"error": "User already logged in"}

    db_client.login_user(user["id"])  # Log the user in
    
    response.status_code = 200
    return User(id=user["id"], username=user["username"], color=user["color"])

@app.post("/api/logout/{username}")
async def logout_user(username: str, response: Response):
    user = db_client.get_user_by_username(username)
    if user is None:
        response.status_code = 404
        return {"error": "User not found"}

    if not user["logged_in"]:
        response.status_code = 400
        return {"error": "User is not logged in"}

    db_client.logout_user(user["id"])  # Log the user out
    
    response.status_code = 200
    return {"status": "User logged out"}

@app.post("/api/users")
async def create_user(user: User, response: Response):
    db_client.put_user(user.model_dump())
    response.status_code = 201
    return {"status": "User created"}

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Here you can handle the received data, e.g., broadcast it to other clients
        await websocket.send_text(f"Message received: {data}")