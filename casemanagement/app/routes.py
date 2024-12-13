from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .db import get_db
from .models import Case as CaseModel, User as UserModel
from .schemas import *
import uuid
from typing import List, Annotated
from datetime import datetime, timezone
from .auth import is_authenticated, get_id_from_token
from starlette import status

db_dependency = Annotated[AsyncSession, get_db]

router = APIRouter()

@router.get("/case/get-all", response_model=List[CaseType])
async def get_all_cases(session: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    stmt = select(CaseModel)
    result = await session.execute(stmt)
    cases = result.scalars().all()
    return [CaseType(**case.__dict__) for case in cases]


@router.get("/case/status")
async def get_cases_status(session: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    stmt = select(CaseModel.status, func.count().label('count')).group_by(CaseModel.status)
    result = await session.execute(stmt)
    res = [{"category": row[0], "count": row[1]} for row in result]
    print("********************************")
    print(res)
    print("********************************")
    return res



@router.get("/case/get/{case_id}", response_model=CaseType)
async def get_case_by_id(case_id: str, session: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    try:
        case_uuid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    case = await session.get(CaseModel, case_uuid)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return CaseType(**case.__dict__)

@router.get("/case/distinct/{field}", response_model=List[DistinctValueType])
async def get_distinct_values(field: str, session: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    if field not in CaseModel.__table__.columns:
        raise HTTPException(status_code=400, detail=f"Field '{field}' does not exist")
    
    stmt = select(CaseModel.title, getattr(CaseModel, field))
    result = await session.execute(stmt)
    data = [{"field": str(row[1]), "title": row[0]} for row in result]
    return data



@router.post("/case/create", response_model=CaseType)
async def create_case(
    request: Request,
    case_data: CreateCaseRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated),
):

    new_case = CaseModel(
        title=case_data.title,
        description=case_data.description,
        status=case_data.status,
        created_by=current_user.id,
        assignee=current_user.id,
        created_on=datetime.now(timezone.utc)
    )
    try:
        session.add(new_case)
        await session.commit()
        await session.refresh(new_case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CaseType(
        id=str(new_case.id),
        title=new_case.title,
        description=new_case.description,
        status=new_case.status,
        created_by=str(new_case.created_by),
        assignee=str(new_case.assignee),
        created_on=str(new_case.created_on),
        message="Case created successfully"
    )


@router.put("/case/update/{case_id}", response_model=CaseType)
async def update_case(
    request: Request,
    case_id: str,
    case_data: UpdateCaseRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated)
):

    try:
        case_id = uuid.UUID(case_id)
        case = await session.get(CaseModel, case_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not case:
        raise HTTPException(status_code=404, detail="Invalid case ID")

    if not any(vars(case_data).values()):
        raise HTTPException(status_code=400, detail="No fields to update")

    case.description = case_data.description or case.description
    case.status = case_data.status or case.status
    case.status_change_reason = case_data.status_change_reason or case.status_change_reason
    case.comment = case_data.comment or case.comment
    case.watchers = list(set((case.watchers or []) + ([case_data.watchers] or [])))
    case.updated_by = current_user.id
    case.updated_on = datetime.now(timezone.utc)

    try:
        await session.commit()
        await session.refresh(case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CaseType(
        id=case.id,
        title=case.title,
        description=case.description,
        status=case.status,
        created_by=case.created_by,
        assignee=case.assignee,
        created_on=case.created_on,
        updated_by=case.updated_by,
        updated_on=case.updated_on,
        status_change_reason=case.status_change_reason,
        watchers=case.watchers,
        comment=case.comment,
        message="Case updated successfully"
    )


@router.delete("/case/delete/{case_id}", response_model=CaseType)
async def delete_case(
    case_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated)
):

    try:
        case_id = uuid.UUID(case_id)
        case = await session.get(CaseModel, case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Invalid case ID")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        await session.delete(case)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CaseType(
        id=case.id,
        title=case.title,
        description=case.description,
        status=case.status,
        created_by=case.created_by,
        assignee=case.assignee,
        created_on=case.created_on,
        message="Case deleted successfully"
    )

