# app/services.py
from datetime import datetime, timezone

from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas


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
) -> models.Advert:
    """
    Ищем в БД данные в запросе от клиента, проверяя если поле не пустое, то добавляем в запрос

    """
    query_all =''
    if find_data['title'] != None:
        query_all = query_all + ' ' + 'orm_model.title == ' + find_data['title']
    if query_all != '':
        query_all = query_all + ' and '
    if find_data['description'] != None:
        query_all = query_all + ' ' + 'orm_model.description == ' + find_data['description']
    if query_all != '' and  find_data['description'] != None:
        query_all = query_all + ' and '
    if find_data['price'] != None:
        query_all = query_all + ' ' + 'orm_model.price == ' + find_data['price']
    if query_all != '' and  find_data['price'] != None:
        query_all = query_all + ' and '
    if find_data['author_id'] != None:
        query_all = query_all + ' ' + 'orm_model.author_id == ' + find_data['author_id']

    stmt = select(orm_model).where(query_all)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    itemdict = schemas.GetAdvertResponse(**item.to_dict())

    item = await get_item(session, orm_model, itemdict['item_id'])

    # Преобразуем update_data в словарь, исключая поля со значением None
    find_dict = find_data.model_dump(exclude_unset=True)

    for key, value in find_dict.items():
        setattr(item, key, value)


    await session.commit()
    await session.refresh(item)
    return item


async def update_item(
        session: AsyncSession,
        orm_model: type[models.Advert],
        item_id: int,
        update_data: schemas.UpdateAdvertRequest
) -> models.Advert:
    """
    Обновляет запись. Если done=True, автоматически проставляет finish_time.
    """
    item = await get_item(session, orm_model, item_id)

    # Преобразуем update_data в словарь, исключая поля со значением None
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(item, key, value)

    # Если дело отмечено как выполненное, и finish_time ещё нет, ставим текущее время
    if update_dict.get('done') and item.finish_time is None:
        item.finish_time = datetime.now(timezone.utc)

    # Если дело снова стало невыполненным, сбрасываем finish_time
    if update_dict.get('done') is False:
        item.finish_time = None

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
