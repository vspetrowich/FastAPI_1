# app/app.py

from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from dependencies import get_db_session
from lifespan import lifespan
from services import add_item, get_item, update_item, delete_item, find_item

app = FastAPI(
    title="My Advert App",
    description="This is a very simple advert application API",
    version="0.0.1",
    lifespan=lifespan
)

# Создаём тип для зависимости сессии
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@app.post("/v1/advertisement", response_model=schemas.CreateAdvertResponse, summary="Создать новое объявление")
async def create_advert(
        advert_data: schemas.CreateAdvertRequest,
        session: SessionDep
):
    # Используем сервисную функцию
    new_advert = await add_item(session, models.Advert, advert_data)
    return schemas.CreateAdvertResponse(id=new_advert.id)


@app.get("/v1/advertisement/{item_id}", response_model=schemas.GetAdvertResponse, summary="Получить объявление по ID")
async def get_advert(
        item_id: int,
        session: SessionDep
):
    advert = await get_item(session, models.Advert, item_id)
    # Преобразуем ORM-модель в словарь и затем в Pydantic-схему
    return schemas.GetAdvertResponse(**advert.to_dict())

@app.get("/v1/advertisement?{query_string}", response_model=schemas.FindAdvertResponse, summary="Поиск по полям объявления")
async def find_advert(
        find_data: schemas.FindAdvertRequest,
        session: SessionDep
):
    found_advert = await find_item(session, models.Advert, find_data)
    return schemas.FindAdvertResponse(**found_advert.to_dict())


@app.patch("/v1/advertisement/{item_id}", response_model=schemas.UpdateAdvertResponse, summary="Обновить объявление")
async def update_advert(
        item_id: int,
        update_data: schemas.UpdateAdvertRequest,
        session: SessionDep
):
    updated_advert = await update_item(session, models.Advert, item_id, update_data)
    return schemas.UpdateAdvertResponse(**updated_advert.to_dict())


@app.delete("/v1/advertisement/{item_id}", response_model=schemas.OKResponse, summary="Удалить объявление")
async def delete_advert(
        item_id: int,
        session: SessionDep
):
    await delete_item(session, models.Advert, item_id)
    return schemas.OKResponse()
