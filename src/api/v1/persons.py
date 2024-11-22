from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from schemas.person import FilmByPersonSchema, PersonFilmSchema, PersonSchema
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/search", response_model=List[PersonSchema])
async def search_persons(
    query: str,
    page_size: int = Query(
        50, ge=1, le=50, description="Кол-во персон в выдаче (1-50)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы выдачи"),
    person_service: PersonService = Depends(get_person_service),
) -> List[PersonSchema]:
    """
    Обработчик маршрута api/v1/persons/search,
    ищет людей по имени
    Параметры:
      :query: str Ключевое слово для поиска
      :page_size: int Кол-во персон в выдаче
      :page_number: int Номер страницы выдачи
      :person_service: Сервис, управляющий извлечением данных из ES
    Возвращает:
    Список моделей PersonSchema
    """

    person_list = await person_service.search(query, page_size, page_number)

    persons = []

    for person in person_list:

        films_list = [
            PersonFilmSchema(uuid=pf.uuid, roles=pf.roles)
            for pf in person.films
        ]

        persons.append(
            PersonSchema(
                uuid=person.id, full_name=person.full_name, films=films_list
            )
        )

    return persons


@router.get("/{person_id}", response_model=PersonSchema)
async def get_person_by_id(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonSchema:
    """
    Обработчик маршрута api/v1/persons/{person_id},
    ищет персону по id в БД.
    Параметры:
      :person_id: str Id персоны
      :person_service: Сервис, управляющий извлечением данных из ES
    Возвращает:
    Модель PersonSchema
    """

    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Person not found"
        )

    films_list = [
        PersonFilmSchema(uuid=pf.uuid, roles=pf.roles) for pf in person.films
    ]

    return PersonSchema(
        uuid=person.id, full_name=person.full_name, films=films_list
    )


@router.get("/{person_id}/film", response_model=List[FilmByPersonSchema])
async def get_films_by_person_id(
    person_id: str,
    page_size: int = Query(
        50, ge=1, le=50, description="Кол-во фильмов в выдаче (1-50)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы выдачи"),
    person_service: PersonService = Depends(get_person_service),
) -> List[FilmByPersonSchema]:
    """
    Обработчик маршрута api/v1/persons/{person_id}/film,
    ищет фильмы с участием персоны по её id.
    Параметры:
      :person_id: str Id персоны
      :page_size: int Кол-во персон в выдаче
      :page_number: int Номер страницы выдачи
      :person_service: Сервис, управляющий извлечением данных из ES
    Возвращает: список моделей FilmByPersonSchema
    """

    films = await person_service.get_films_by_person_id(
        person_id, page_size, page_number
    )

    if not films:
        return []

    return films
