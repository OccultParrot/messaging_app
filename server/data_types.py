from pydantic import BaseModel

class Message(BaseModel):
    id: int | None = None
    content: str
    user_id: int
    logged_in: bool | None

class MessagesGet(BaseModel):
    contents: list[Message]

class User(BaseModel):
    id: int | None = None
    username: str
    color: str # As a hex code string, e.g., "#FF5733"

class UsersGet(BaseModel):
    contents: list[User]