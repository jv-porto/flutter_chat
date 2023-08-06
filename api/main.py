# importing libraries and functions
from fastapi import FastAPI

from db import migrate_db, populate_db, drop_db
from routes import auth, chat_message, user, websockets


# instantiating the FastAPI application
app = FastAPI()


# DB functions
# drop_db()
# migrate_db()
# populate_db()


# connecting the routers to the main application
app.include_router(auth.router, prefix='/api/auth')
app.include_router(chat_message.router, prefix='/api')
app.include_router(user.router, prefix='/api')
app.include_router(websockets.router, prefix='/ws')
