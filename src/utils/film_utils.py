from typing import List

from schemas.film import FilmSchema

from models.film import Film
from models.person import PersonFilm


async def get_response_list(lst: List) -> List:
    '''
    Формирует список ответов на основе входного списка объектов.
    '''
    resp_list = [
        FilmSchema(uuid=hit.id, title=hit.title, imdb_rating=hit.imdb_rating)
        for hit in lst
        ]
    return resp_list


async def convert_films_to_person_films(
        person_id: str, person_films: List[Film]) -> List[PersonFilm]:
    """
    Вспомогательная функция для формирования List[PersonFilm]
    со списком roles в каждом фильме.
    Параметры:
      :person_id: str UUID персоны
      :person_films: List[Film] список фильмов, полученный из ф-ии
                                _get_films_from_es_by_person_id(person_id)
    Возвращает: список PersonFilm.
    """

    films = []

    for person_film in person_films:

        roles = set()
        for pp, role in zip(
            [person_film.actors, person_film.directors, person_film.writers],
            ['actor', 'director', 'writer']
                ):
            for p in pp:
                if str(p.id) == person_id:
                    roles.add(role)

        films.append(PersonFilm(uuid=person_film.id, roles=roles))

    return films
