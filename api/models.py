# importing libraries and functions
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.ext.declarative import declarative_base


# instantiating the models
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    username = Column(String(), primary_key=True)
    email = Column(String())
    password = Column(String())
    first_name = Column(String())
    last_name = Column(String())
    image_url = Column(String())
    created_at = Column(DateTime())
    last_updated = Column(DateTime())
    is_enabled = Column(Boolean())
    chat_messages = relationship('ChatMessage', back_populates='user', lazy='joined')

    def __init__(self, username: str, email: str, password: str, first_name: str, last_name: str, image_url: str | None = None):
        from auth import get_password_hash

        self.username = username
        self.email = email
        self.password = get_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.image_url = image_url
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.is_enabled = True


class ChatMessage(Base):
    __tablename__ = 'chat_message'
    id = Column(String(), primary_key=True)
    text = Column(Text())
    created_at = Column(DateTime())
    last_updated = Column(DateTime())
    is_hidden = Column(Boolean())
    user_username = mapped_column(ForeignKey('user.username'))
    user = relationship('User', back_populates='chat_messages', lazy='joined')

    def __init__(self, text: str, user_username: str):
        self.id = str(uuid4())
        self.text = text
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.is_hidden = False
        self.user_username = user_username
