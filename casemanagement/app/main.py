from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from .schema import query_router
from .mutations import mutation_router, update_case_mutation_router
from . query import status_query_router, distinct_query_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(query_router, prefix="/api/get/cases")
app.include_router(mutation_router, prefix="/api/case/create")
app.include_router(update_case_mutation_router, prefix="/api/case/update")
app.include_router(status_query_router, prefix="/api/case-service/cases/states-count")
app.include_router(distinct_query_router, prefix="/api/api/v1/cases/{field}/distinct-values")



@app.get("/")
def read_root():
    return {"message": "Welcome to the Case Management System with FastAPI and YugabyteDB"}


# @app.middleware("http")
# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         response = await call_next(request)
#         return response
#     except ValueError as exc:
#         return JSONResponse(
#             status_code=400,
#             content={"detail": str(exc)},
#         )
#     except Exception as exc:
#         return JSONResponse(
#             status_code=500,
#             content={"detail": "An unexpected error occurred."},
#         )
#     except HTTPException as exc:
#         return JSONResponse(
#             status_code=400,
#             content={"detail": "invalid credentials entered nigga."}
#         )
