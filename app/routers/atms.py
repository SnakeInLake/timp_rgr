# app/routers/atms.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

# Импортируем все необходимое из наших модулей
import crud
import models
import schemas # Убедитесь, что schemas импортирован для response_model и типов входных данных
from database import get_db
from deps import get_current_user, get_current_admin_or_superuser
from security import get_api_key # <--- ИМПОРТИРУЕМ ЗАВИСИМОСТЬ ДЛЯ API-КЛЮЧА
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi_cache.decorator import cache

router = APIRouter()


# --- Эндпоинт для получения списка статусов ---
@router.get("/statuses/", response_model=List[schemas.ATMStatus])
@cache(expire=3600)
async def read_atm_statuses(db: Session = Depends(get_db)):
    statuses = db.query(models.ATMStatus).order_by(models.ATMStatus.id).all()
    return statuses


# --- Эндпоинт для получения списка банкоматов ---
@router.get("/", response_model=List[schemas.ATM])
async def read_atms(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status_id: Optional[int] = Query(None, description="Filter by status ID"),
        location: Optional[str] = Query(None, description="Search keyword for location"),
        atm_uid: Optional[str] = Query(None, description="Search keyword for ATM UID"),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    total_count = crud.get_atms_count(
        db, status_id=status_id, location_keyword=location, atm_uid_keyword=atm_uid
    )
    atms = crud.get_atms(
        db, skip=skip, limit=limit, status_id=status_id, location_keyword=location, atm_uid_keyword=atm_uid
    )
    content_to_serialize = jsonable_encoder(atms)
    return JSONResponse(
        content=content_to_serialize,
        headers={
            "X-Total-Count": str(total_count),
            "Access-Control-Expose-Headers": "X-Total-Count"
        }
    )

# --- Эндпоинт создания банкомата ---
# Убрал дублирование декоратора
@router.post("/", response_model=schemas.ATM, status_code=status.HTTP_201_CREATED)
async def create_new_atm(
        atm_in: schemas.ATMCreate,
        db: Session = Depends(get_db),
        current_user_with_admin_rights: models.User = Depends(get_current_admin_or_superuser)
):
    existing_atm = crud.get_atm_by_uid(db, atm_uid=atm_in.atm_uid)
    if existing_atm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ATM with UID {atm_in.atm_uid} already exists."
        )
    status_obj = db.query(models.ATMStatus).filter(models.ATMStatus.id == atm_in.status_id).first()
    if not status_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ATMStatus with id {atm_in.status_id} not found."
        )
    try:
        created_atm = crud.create_atm(db=db, atm=atm_in, user_id=current_user_with_admin_rights.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return created_atm

# --- Эндпоинт получения одного банкомата по ID ---
@router.get("/{atm_id}", response_model=schemas.ATM)
async def read_atm_by_id(
        atm_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    db_atm = crud.get_atm(db, atm_id=atm_id)
    if db_atm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ATM not found")
    return db_atm


# --- Эндпоинт обновления банкомата ---
@router.put("/{atm_id}", response_model=schemas.ATM)
async def update_existing_atm(
        atm_id: int,
        atm_in: schemas.ATMUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    db_atm = crud.get_atm(db, atm_id=atm_id)
    if db_atm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ATM not found")
    if not (db_atm.added_by_user_id == current_user.id or current_user.role in ["admin", "superadmin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this ATM"
        )
    if atm_in.status_id is not None:
        status_obj = db.query(models.ATMStatus).filter(models.ATMStatus.id == atm_in.status_id).first()
        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ATMStatus with id {atm_in.status_id} not found for update."
            )
    if atm_in.atm_uid is not None and atm_in.atm_uid != db_atm.atm_uid:
        existing_atm = crud.get_atm_by_uid(db, atm_uid=atm_in.atm_uid)
        if existing_atm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ATM with UID {atm_in.atm_uid} already exists."
            )
    try:
        updated_atm = crud.update_atm(db=db, db_atm=db_atm, atm_in=atm_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated_atm


# --- Эндпоинт удаления банкомата ---
@router.delete("/{atm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_atm(
        atm_id: int,
        db: Session = Depends(get_db),
        current_user_with_admin_rights: models.User = Depends(get_current_admin_or_superuser)
):
    deleted_atm = crud.delete_atm(db, atm_id=atm_id)
    if deleted_atm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ATM not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- НОВЫЙ ЭНДПОИНТ: Создание лога для банкомата (защищен API-ключом) ---
@router.post("/{atm_id}/logs/",
                 response_model=schemas.ATMLog,
                 status_code=status.HTTP_201_CREATED,
                 dependencies=[Depends(get_api_key)]) # <--- ЗАЩИЩАЕМ ЭТОТ ЭНДПОИНТ API-КЛЮЧОМ
async def create_log_for_specific_atm( # Переименовал для ясности
    atm_id: int,
    log_in: schemas.ATMLogCreate, # Используем схему для создания лога
    db: Session = Depends(get_db)
    # current_user здесь не нужен, так как авторизация по API-ключу
):
    """
    Создает новую запись лога для указанного банкомата.
    Этот эндпоинт предназначен для использования ATM симуляторами с API-ключом.
    """
    # Проверяем, существует ли банкомат
    db_atm = crud.get_atm(db, atm_id=atm_id)
    if not db_atm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ATM with id {atm_id} not found")

    # Проверки для log_level_id и event_type_id (если они не null)
    if log_in.log_level_id:
        log_level = db.query(models.LogLevel).filter(models.LogLevel.id == log_in.log_level_id).first()
        if not log_level:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"LogLevel with id {log_in.log_level_id} not found.")

    if log_in.event_type_id is not None: # event_type_id может быть NULL
        event_type = db.query(models.EventType).filter(models.EventType.id == log_in.event_type_id).first()
        if not event_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"EventType with id {log_in.event_type_id} not found.")
    
    try:
        created_log = crud.create_atm_log(db=db, log=log_in, atm_id=atm_id)
        return created_log
    except ValueError as e: # Например, если crud.create_atm_log выбрасывает ValueError
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # Общий обработчик на случай других ошибок CRUD
        # Логирование ошибки на сервере было бы здесь полезно
        print(f"Error in create_log_for_specific_atm: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error while creating log.")