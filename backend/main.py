from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.search import router as search_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#declaring fastapi app and some fastapi configurations
app.include_router(search_router)