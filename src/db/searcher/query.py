from abc import ABC

from db.searcher import IQuery


class FilmQuery(IQuery, ABC):
    pass


class PopularFilmQuery(IQuery, ABC):
    pass


class GenreQuery(IQuery, ABC):
    pass


class PersonQuery(IQuery, ABC):
    pass


class FilmsByPersonIDQuery(IQuery, ABC):
    pass
