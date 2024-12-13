from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as cases_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include REST routes
app.include_router(cases_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Case Management System with FastAPI"}
