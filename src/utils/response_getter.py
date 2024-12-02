from typing import Dict

film_list_example = [
    {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Пример фильма",
        "imdb_rating": 8.5,
    },
    {
        "uuid": "123e4567-e89b-12d3-a456-426614174001",
        "title": "Другой фильм",
        "imdb_rating": 7.2,
    },
]


def get_film_list_response() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Успешный ответ, возвращает список фильмов.",
            "content": {"application/json": {"example": film_list_example}},
        },
        400: {
            "description": "Неверный запрос. Например, если указана \
                    недопустимая страница или поле сортировки.",
            "content": {
                "application/json": {
                    "example": {"detail": "Некорректный запрос"}
                }
            },
        },
        404: {
            "description": "Фильмы не найдены. Возвращается, если \
                    нет фильмов в бд",
            "content": {
                "application/json": {
                    "example": {"detail": "Фильмы не найдены"}
                }
            },
        },
    }


def get_film_by_id_response() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Успешный ответ",
            "content": {
                "application/json": {
                    "example": {
                        "uuid": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Пример фильма",
                        "description": "Описание примера фильма",
                        "imdb_rating": 8.5,
                        "genre": [{"uuid": "1", "name": "Драма"}],
                        "actors": [{"uuid": "2", "full_name": "Актер 1"}],
                        "writers": [{"uuid": "3", "full_name": "Автор 1"}],
                        "directors": [
                            {"uuid": "4", "full_name": "Режиссер 1"}
                        ],
                    }
                }
            },
        },
        404: {
            "description": "Фильм не найден. Возвращается, если \
                    нет фильмов c указанным id.",
            "content": {
                "application/json": {
                    "example": {"detail": "Фильмы не найдены"}
                }
            },
        },
    }


def search_film_response() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Успешный ответ, возвращает список найденных\
                  фильмов или пустой список, если фильмов с заданными \
                    критериями нет",
            "content": {"application/json": {"example": film_list_example}},
        },
        400: {
            "description": "Неверный запрос. Например, если указана \
                    недопустимая страница или поле сортировки.",
            "content": {
                "application/json": {
                    "example": {"detail": "Некорректный запрос"}
                }
            },
        },
    }


def get_person_by_id_response() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Успешный ответ, возвращает информацию\
                      о персоне.",
            "content": {
                "application/json": {
                    "example": {
                        "uuid": "123e4567-e89b-12d3-a456-426614174000",
                        "full_name": "Иван Иванов",
                        "films": [
                            {
                                "uuid": "456e4567-e89b-12d3-a456\
                                        -426614174001",
                                "roles": ["Actor"],
                            },
                            {
                                "uuid": "789e4567-e89b-12d3-a456-\
                                        426614174002",
                                "roles": ["Writer"],
                            },
                        ],
                    }
                }
            },
        },
        404: {
            "description": "Персона не найдена по указанному id.",
            "content": {
                "application/json": {"example": {"detail": "Person not found"}}
            },
        },
    }


def search_person_response() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Персоны успешно найдены",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "uuid": "123e4567-e89b-12d3-a456-426614174000",
                            "full_name": "Иван Иванов",
                            "films": [
                                {
                                    "uuid": "456e4567-e89b-12d3-a456\
                                        -426614174001",
                                    "roles": ["Главный герой", "Протагонист"],
                                },
                                {
                                    "uuid": "789e4567-e89b-12d3-a456\
                                        -426614174002",
                                    "roles": ["Антагонист"],
                                },
                            ],
                        },
                        {
                            "uuid": "123e4567-e89b-12d3-a456-426614174001",
                            "full_name": "Мария Петрова",
                            "films": [],
                        },
                    ]
                }
            },
        },
        400: {
            "description": "Некорректный запрос",
            "content": {
                "application/json": {
                    "example": {"detail": "Запрос не может быть пустым"}
                }
            },
        },
    }


def get_films_by_person() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Успешный ответ, возвращает список фильмов.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "uuid": "456e4567-e89b-12d3-a456-426614174001",
                            "title": "Фильм 1",
                            "imdb_rating": 6.0,
                        },
                        {
                            "uuid": "789e4567-e89b-12d3-a456-426614174002",
                            "title": "Фильм 2",
                            "imdb_rating": 5.0,
                        },
                    ]
                }
            },
        },
        404: {
            "description": "Персона не найдена по указанному id.",
            "content": {
                "application/json": {"example": {"detail": "Person not found"}}
            },
        },
    }


def get_genres_response() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Жанры успешно получены",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "uuid": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Научная фантастика",
                        },
                        {
                            "uuid": "123e4567-e89b-12d3-a456-426614174001",
                            "name": "Фэнтези",
                        },
                    ]
                }
            },
        },
        400: {
            "description": "Некорректный запрос",
            "content": {
                "application/json": {
                    "example": {"detail": "Страница: 3 превысила максимум: 2"}
                }
            },
        },
    }


def genres_by_id_response() -> Dict[int, Dict]:
    return {
        200: {
            "description": "Жанр успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "uuid": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Action",
                    }
                }
            },
        },
        404: {
            "description": "Жанр не найден",
            "content": {
                "application/json": {"example": {"detail": "Жанр не найден"}}
            },
        },
    }
