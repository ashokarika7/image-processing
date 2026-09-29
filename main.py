from database.db import engine, Base
from models.image import Image
from fastapi import FastAPI
from routes.images import router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)  