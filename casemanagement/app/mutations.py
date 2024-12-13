import strawberry
from .models import Case as CaseModel
from datetime import datetime, timezone
from .schema import CaseType
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db
import uuid
from .query import GetQuery
from .auth import IsAunthenticated, get_id_from_token
from typing import Optional


async def get_context(session: AsyncSession = Depends(get_db)):
    return {'session': session}

@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAunthenticated])
    async def create_case(self, title:str, description:str, status:str, info: strawberry.Info)->CaseType:
        token = info.context['request'].headers.get('Authorization', '').replace('Bearer ', '')
        user_id = get_id_from_token(token)
        case = CaseModel(title=title, description=description, status=status, created_by=user_id, assignee=user_id, created_on=datetime.now(timezone.utc))
        session = info.context["session"]
        try:
            session.add(case)
            await session.commit()
            await session.refresh(case)
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
        try:
            responseObj = CaseType(id=case.id, title=case.title, description=case.description, status=case.status, created_by=case.created_by, created_on=case.created_on, assignee=case.assignee, message="case created successfully")
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
        return responseObj



@strawberry.type
class UpdateCaseMutation:
    @strawberry.mutation(permission_classes=[IsAunthenticated])

    async def update_case(self, info: strawberry.Info, status_change_reason:str=None, comment:str=None, watchers:str=None, description:str=None, status:str=None)->CaseType:
        
        try:
            session = info.context["session"]
            request = info.context["request"]
            case_id = request.query_params.get("id")
            case_id = uuid.UUID(case_id)

        except Exception as e:

            raise HTTPException(status_code=404, detail=e)

        case = await session.get(CaseModel, case_id)

        if case is None:
            raise HTTPException(status_code=400, detail="invalid case id")
        
        if all(arg is None for arg in [description, status, status_change_reason, comment, watchers]):

            response = CaseType(id=case.id, title=case.title, description=case.description, created_by=case.created_by, created_on=case.created_on, status=case.status, updated_by=case.updated_by, updated_on=case.updated_on, assignee=case.assignee, status_change_reason=case.status_change_reason, watchers=case.watchers, comment=case.comment, message="case updated successfully" ) 

            return response
        
        case.description = description if description else case.description
        case.status = status if status else case.status
        case.status_change_reason = status_change_reason if status_change_reason else case.status_change_reason
        case.comment = comment if comment else case.comment
        
        token = info.context['request'].headers.get('Authorization', '').replace('Bearer ', '')
        user_id = get_id_from_token(token)

        case.watchers = case.watchers + [watchers] if watchers is not None else case.watchers
        case.watchers = list(set(case.watchers))
        case.updated_by = user_id
        case.updated_on = datetime.now(timezone.utc)

        try:
            await session.commit()
            await session.refresh(case)
            response = CaseType(id=case.id, title=case.title, description=case.description, created_by=case.created_by, created_on=case.created_on, status=case.status, updated_by=case.updated_by, updated_on=case.updated_on, assignee=case.assignee, status_change_reason=case.status_change_reason, watchers=str(case.watchers), comment=case.comment, message="case updated successfully" )

        except:
            raise HTTPException(status_code=404, detail=e)
        
        return response
    
    @strawberry.mutation(permission_classes=[IsAunthenticated])
    async def delete_case(self, info: strawberry.Info)->Optional[CaseType]:
        session = info.context["session"]
        request = info.context["request"]
        case_id = request.query_params.get("id")
        try:
            case_id = uuid.UUID(case_id)
            case = await session.get(CaseModel, case_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=e)
        
        if case is None:
            raise HTTPException(status_code=404, detail="invalid case id")

        try:
            await session.delete(case)
            await session.commit()
            response = CaseType(id=case.id, title=case.title, description=case.description, status=case.status, created_by=case.created_by, assignee=case.assignee, created_on=case.created_on, message="case deleted successfully")

        except Exception as e:
            raise HTTPException(status_code=404, detail=e)

        return response


@strawberry.type
class EmptyQuery:
    placeholder:str = "This is an empty query"


# def custom_error_handler(error: Exception):
#     if isinstance(error, HTTPException):
#         # Convert custom exception into an HTTP exception
#         raise HTTPException(status_code=401, detail=str(error))
#     # For other exceptions, raise internal server error
#     raise HTTPException(status_code=500, detail="An unexpected error occurred.")


mutation_schema = strawberry.Schema(query=EmptyQuery, mutation=Mutation)
mutation_router = GraphQLRouter(mutation_schema, context_getter=get_context)

update_case_mutation_schema = strawberry.Schema(query=GetQuery, mutation=UpdateCaseMutation)
update_case_mutation_router = GraphQLRouter(update_case_mutation_schema, context_getter=get_context)


