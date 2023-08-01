# importing libraries and functions
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from models import Base
import models


# loading environment variables
load_dotenv()

DB_URI = os.getenv('DB_URI')


# establishing a connection with the DB
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(bind=engine)


# Session dependency
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# creating the models
def migrate_db(session: Session = next(get_session())):
    Base.metadata.create_all(engine)

    session.execute(text('GRANT ALL ON ALL TABLES IN SCHEMA public TO "ibm-cloud-base-user";'))
    session.commit()


def drop_db(session: Session = next(get_session())):
    query = '''
        DROP TABLE "chat_message";
        DROP TABLE "user";
    '''
    session.execute(text(query))
    session.commit()


# populating the DB
def populate_db(session: Session = next(get_session())):
    users = [
        {
            'username': '1',
            'email': '1@1.com',
            'password': 'teste1',
            'first_name': '1',
            'last_name': '1',
            'image_url': '1.com',
        },
        {
            'username': '2',
            'email': '2@2.com',
            'password': 'teste2',
            'first_name': '2',
            'last_name': '2',
            'image_url': '2.com',
        },
        {
            'username': '3',
            'email': '3@3.com',
            'password': 'teste3',
            'first_name': '3',
            'last_name': '3',
            'image_url': '3.com',
        },
    ]

    if not session.query(models.User).count():
        for user in users:
            user_orm = models.User(**user)
            session.add(user_orm)
        session.commit()
    
    chat_messages = [
        {
            'text': '11111',
            'user_username': '1',
        },
        {
            'text': '222',
            'user_username': '2',
        },
        {
            'text': '3!!!!!',
            'user_username': '3',
        },
        {
            'text': '33333',
            'user_username': '3',
        },
    ]
        
    if not session.query(models.ChatMessage).count():
        for chat_message in chat_messages:
            chat_message_orm = models.ChatMessage(**chat_message)
            session.add(chat_message_orm)
        session.commit()
