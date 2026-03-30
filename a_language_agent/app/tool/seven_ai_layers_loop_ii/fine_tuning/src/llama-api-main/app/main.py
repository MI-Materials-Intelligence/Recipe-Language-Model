from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(title="LLaMA Factory API Service")

app.include_router(router)
