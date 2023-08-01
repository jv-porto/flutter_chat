# importing libraries and functions
from datetime import datetime
from pydantic import BaseModel, Extra
from typing import List


# instantiating the schemas - User
class UserChange(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    image_url: str | None = None

    class Config:
        extra = Extra.forbid

class UserBase(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    image_url: str | None = None

    class Config:
        extra = Extra.forbid

class UserCreate(UserBase):
    pass

class User(UserCreate):
    created_at: datetime
    last_updated: datetime
    is_enabled: bool
    chat_messages: List['ChatMessage'] | None = None

    class Config:
        from_attributes = True


# instantiating the schemas - ChatMessage
class ChatMessageChange(BaseModel):
    text: str | None = None

    class Config:
        extra = Extra.forbid

class ChatMessageBase(BaseModel):
    text: str
    user_username: str

    class Config:
        extra = Extra.forbid

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageCreate):
    id: str
    created_at: datetime
    last_updated: datetime
    is_hidden: bool
    user: User

    class Config:
        from_attributes = True
