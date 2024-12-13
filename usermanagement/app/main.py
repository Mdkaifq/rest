from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as user_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(user_router, prefix="/api")
