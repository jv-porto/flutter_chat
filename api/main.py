# importing libraries and functions
from fastapi import FastAPI

from db import migrate_db, populate_db, drop_db
from auth import router as auth_router
from routers import chat_message, user


# instantiating the FastAPI application
app = FastAPI()


# DB functions
# drop_db()
migrate_db()
populate_db()


# connecting the routers to the main application
app.include_router(auth_router, prefix='/api')
app.include_router(chat_message.router, prefix='/api')
app.include_router(user.router, prefix='/api')
