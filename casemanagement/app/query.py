import strawberry
from .models import Case as CaseModel
from .schema import CaseType, CaseStatusType
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_db
import uuid
from sqlalchemy import select, func
from typing import List


async def get_context(session: AsyncSession = Depends(get_db)):
    return {'session': session}

async def get_field_and_context(request: Request, session: AsyncSession = Depends(get_db))->str:
    return  {'session': session, 'field': request.path_params["field"]}



@strawberry.type
class StatusQuery:
    @strawberry.field
    async def get_cases_status(self, info: strawberry.Info)->list[CaseStatusType]:
        session = info.context["session"]
        stmt = select(CaseModel.status, func.count().label('frequency')).group_by(CaseModel.status)
        case = await session.execute(stmt)
        try:
            frequency = case.fetchall()
            response = [CaseStatusType(category=row[0], count=row[1]) for row in frequency]
        except Exception as e:
            raise HTTPException(status_code=404, detail=e)
        return response
    

@strawberry.type
class GetQuery:
    @strawberry.field
    
    async def get_all_cases(self, info: strawberry.Info)->list[CaseType]:
        session = info.context["session"]
        stmt = select(CaseModel)
        case = await session.execute(stmt)
        try:
            all_cases = case.fetchall()
            response = [CaseType(id = cases[0].id, title=cases[0].title, description=cases[0].description, status=cases[0].status, assignee=cases[0].assignee, created_by=cases[0].created_by, created_on=cases[0].created_on, status_change_reason=cases[0].status_change_reason or "Null", comment=cases[0].comment or "Null", updated_by=cases[0].updated_by or "Null", updated_on=cases[0].updated_on or "Null", watchers=cases[0].watchers or [] ) for cases in all_cases]
        except Exception as e:
            raise HTTPException(status_code=404, detail=e)
        return response

    @strawberry.field
    async def get_cases_by_id(self, info: strawberry.Info)->CaseType:

        try:
            session = info.context["session"]
            request = info.context["request"]
            case_id = request.query_params.get("id")
            case_id = uuid.UUID(case_id)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
        
        case = await session.get(CaseModel, case_id)

        if case is None:
            raise HTTPException(status_code=400, detail="invalid case id")
        
        response = CaseType(id = case.id, title=case.title, description=case.description, status=case.status, assignee=case.assignee, created_by=case.created_by, created_on=case.created_on, status_change_reason=case.status_change_reason or "Null", comment=case.comment or "Null", updated_by=case.updated_by or "Null", updated_on=case.updated_on or "Null", watchers=case.watchers or [] )

        return response


@strawberry.type
class DistinctQuery:

    @strawberry.field
    async def get_distinct_values(self, info: strawberry.Info)->List[strawberry.scalars.JSON]:
        session = info.context["session"]
        field = info.context["field"]
        stmt = select(CaseModel.title, CaseModel.__dict__[field])
        result = await session.execute(stmt)
        try:
            result = result.fetchall()
            data = [{field:str(case[1]), "title":case[0]} for case in result]
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
        return data



status_query_schema = strawberry.Schema(query=StatusQuery)
status_query_router = GraphQLRouter(status_query_schema, context_getter=get_context)

distinct_query_schema = strawberry.Schema(query=DistinctQuery)
distinct_query_router = GraphQLRouter(distinct_query_schema, context_getter=get_field_and_context)