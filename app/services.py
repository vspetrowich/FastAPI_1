# app/services.py
from datetime import datetime, timezone

from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from FastAPI_1DZ.app.schemas import FindAdvertResponse


async def add_item(
        session: AsyncSession,
        orm_model: type[models.Advert],
        item_data: schemas.CreateAdvertRequest
) -> models.Advert:
    """
    Универсальная функция для добавления записи в БД.
    """
    new_item = orm_model(**item_data.model_dump())
    session.add(new_item)
    try:
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except IntegrityError as e:
        await session.rollback()
        # Проверяем, является ли ошибка нарушением уникальности (код 23505 для PostgreSQL)
        if isinstance(e.orig, UniqueViolationError) and e.orig.pgcode == '23505':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with such data already exists."
            )
        else:
            # Если это другая ошибка целостности, пробрасываем её дальше
            raise e


async def get_item(
        session: AsyncSession,
        orm_model: type[models.Advert],
        item_id: int
) -> models.Advert:
    """
    Получает запись по ID или выбрасывает 404.
    """
    stmt = select(orm_model).where(orm_model.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with id {item_id} not found"
        )
    return item

async def find_item(
        session: AsyncSession,
        orm_model: type[models.Advert],
        find_data: schemas.FindAdvertRequest
) -> schemas.FindAdvertResponse:
    """
    Ищем в БД данные в запросе от клиента, проверяя если поле не пустое, то добавляем в запрос

    """

    query_all =[]
    if find_data['title'] != None:
        query_all.append(orm_model.title == find_data['title'])
    if find_data['price_min'] != None:
        query_all.append(orm_model.price >= find_data['price_min'])
    if find_data['price_max'] != None:
        query_all.append(orm_model.price <= find_data['price_max'])
    if find_data['author'] != None:
        query_all.append(orm_model.author == find_data['author'])

    stmt = select(orm_model).filter(and_(*query_all))
    result = await session.execute(stmt)
    items = result.all()
    list_item =[]
    for item in items:
        item_dict = schemas.GetAdvertResponse(**item.to_dict())
        answer = await get_item(session, orm_model, item_dict['item_id'])
        list_item.append(answer)


    return list_item


async def update_item(
        session: AsyncSession,
        orm_model: type[models.Advert],
        item_id: int,
        update_data: schemas.UpdateAdvertRequest
) -> models.Advert:
    """
    Обновляет запись.
    """
    item = await get_item(session, orm_model, item_id)

    # Преобразуем update_data в словарь, исключая поля со значением None
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(item, key, value)

    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(
        session: AsyncSession,
        orm_model: type[models.Advert],
        item_id: int
) -> None:
    """
    Удаляет запись.
    """
    item = await get_item(session, orm_model, item_id)
    await session.delete(item)
    await session.commit()
