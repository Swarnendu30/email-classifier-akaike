from fastapi import FastAPI
from api import router
import uvicorn

# Initialize the FastAPI app
app = FastAPI()

# Include the router from api.py
app.include_router(router)