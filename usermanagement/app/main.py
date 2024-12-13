from fastapi import FastAPI
from .schema import query_router
from fastapi.middleware.cors import CORSMiddleware
from .user_mutations import register_and_update_user_router, assign_role_router, login_router, reset_password_router, refresh_access_token_router, delete_user_router
from .user_query import get_all_users_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(login_router, prefix="/api/user/login")
app.include_router(register_and_update_user_router, prefix="/api/user/register")
app.include_router(assign_role_router, prefix="/api/fost-bs/iam-service/v1/users/{userId}/roles")
app.include_router(reset_password_router, prefix="/api/user/resetpassword")
app.include_router(refresh_access_token_router, prefix="/api/user/refresh-token")
app.include_router(delete_user_router, prefix="/api/user/delete/{userId}")
app.include_router(get_all_users_router, prefix="/api/user/get-all")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Case Management System with FastAPI and YugabyteDB"}
