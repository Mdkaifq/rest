import strawberry
from typing import List
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from typing import  Optional


@strawberry.type
class UserType:
    id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    phone_no:Optional[str] = None
    role:Optional[str] = None
    createdOn:Optional[str] = None

@strawberry.input
class UserCreateInput:
    username: str
    email: str
    password: str
    first_name:Optional[str] = "null"
    last_name:Optional[str] = "null"

@strawberry.type
class AuthResponse:
    access_token: str
    refresh_token: str



@strawberry.type
class CaseType:
    id: Optional[str] = None
    title:Optional[str] = None
    description:Optional[str] = None
    status:Optional[str] = None
    created_by:Optional[str] = None
    created_on:Optional[str] = None
    assignee:Optional[str] = None 
    status_change_reason:str = None
    comment:Optional[str]  = None
    watchers:Optional[str] = None
    updated_by:Optional[str]   = None
    updated_on:Optional[str]   = None


@strawberry.type
class CaseDistinctFields:
    result: JSON


@strawberry.type
class CaseStatusType:
    category: str = "Null"
    count: int = 0
      

@strawberry.type
class Query:
    @strawberry.field
    async def get_cases(self)->List[CaseType]:
        pass


query_schema = strawberry.Schema(query=Query)
query_router = GraphQLRouter(query_schema)
