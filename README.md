# Проектная работа 4 спринта: AsyncAPI movies services
**Ссылка на приватный репозиторий с командной работой: https://github.com/fersus85/Async_API_sprint_1**
## Описание
Асинхронный API для кинотеатра.
- Маршрут *api/v1/films/search* - ищет фильмы в БД по ключевому слову
- Маршрут *api/v1/films* - ищет фильмы в БД. Есть возможность фильтровать по жанрам
- Маршрут *api/v1/films{film_id}* - ищет фильм по id в БД
- Маршрут *api/v1/genres* - ищет жанры в БД
- Маршрут *api/v1/genres{genre_id}* - ищет жанр по id в БД
- Маршрут *api/v1/persons/search* - ищет людей по имени
- Маршрут *api/v1/persons/{person_id}* - ищет персону по id в БД
- Маршрут *api/v1/persons/{person_id}/film* - ищет фильмы с участием персоны по её id
## Стек
- Python 3.9
- FastAPI
- Приложение запускается под управлением сервера ASGI(uvicorn)
- В качестве хранилища используется ElasticSearch
- Для кеширования данных используется Redis Cluster
- Nginx
- Docker
## Настройки
Для конфигурации сервиса разместите в директории src файл .env, переместите в него переменные из .env.example
## Запуск
1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/fersus85/Async_API_sprint_1.git
    ```
2. Перейдите в директорию проекта:
    ```bash
    cd Async_API_sprint_1
    ```
3. Запустите docker-compose:
  ```bash
    docker compose up -d
  ```
