# AsyncAPI movies service + tests
## Мой вклад в проект
В рамках разработки AsyncAPI movies service я выступал в роли тимлида и разработчика. Моя работа включала в себя:
1. Лидерство и управление.
    - Декомпозировал задание, выделил ключевые задачи и распределил их среди разработчиков.
    - Управлял прогрессом и контролировал выполнение задач, следил за соблюдением дедлайнов.
    - Обеспечивал качество кода, проводил код-ревью и контролировал соответствие стандартам разработки.
2. Разработка.
    - Описал структуру проекта.
    - Настроил логирование, обеспечив возможность удобного отслеживания работы сервиса.
    - Разработал логику для роутера фильмов, позволяя взаимодействовать с базой данных фильмов.
    - Добавил валидацию параметров, вводимых пользователем, улучшив устойчивость API к некорректным запросам.
    - Написал эндпоинты для films и persons, расширив функциональность API.
    - Настроил GitHub Actions для линтинга кода перед мерджем, улучшив процесс CI/CD.
    - Описал все команды для Makefile, упростив запуск и управление проектом.
    - Разработал инфраструктуру для интеграционных тестов, повысив надежность системы.
    - Написал интеграционные тесты для своих эндпоинтов, проверив корректность работы API.
    - Написал README, документировав работу сервиса для разработчиков и пользователей.

Мой вклад позволил создать структурированный, тестируемый и хорошо документированный сервис, который эффективно обрабатывает запросы к базе данных фильмов, жанров и персон.
## Описание
Cервис представляет собой асинхронный API для выдачи контента онлайн-кинотеатра. Он предоставляет возможность взаимодействия с базой данных фильмов, жанров и персон, а также осуществляет поиск по различным критериям.
- Все запросы к API являются асинхронными, что позволяет эффективно обрабатывать большое количество запросов одновременно.
- Для работы с API требуется аутентификация в сервисе Auth https://github.com/fersus85/Auth_sprint_2.
API предоставляет инструменты для работы с контентом онлайн-кинотеатра, позволяя пользователям легко находить и получать информацию о фильмах, жанрах и персоналиях.
## Документация
Подробную документацию в формате OpenAI с примерами запросов и ответов можно посмотреть, запустив проект (см. настройка, установка и запуск) и перейдя по адресу в браузере:
```bash
  http://127.0.0.1:80/api/openapi
```
## Стек
- Python 3.9
- FastAPI
- Приложение запускается под управлением сервера ASGI(uvicorn)
- В качестве хранилища используется ElasticSearch
- Для кеширования данных используется Redis Cluster
- Nginx
- Docker
## Установка
Системные требования:
- Python 3.9
- Docker
- Docker Compose
- утилита make (не обязательно)
## Настройки
Для конфигурации сервиса разместите в директории src файл .env, переместите в него переменные из .env.example
## Запуск
1. Клонируйте репозиторий:
```bash
  git clone https://github.com/fersus85/Async_API_sprint_2.git
```
2. Перейдите в директорию проекта:
```bash
  cd Async_API_sprint_1
```
3. Запустите docker-compose:
```bash
  docker compose up -d
```
или используйте команду
```bash
  make up
```
## Тестирование
Есть два сценария для тестирования:
- с запуском тестов в контейнере докер:
```bash
  cd /tests/functional \
  && docker compose -f docker-compose.local_test.yml -f docker-compose.yml up -d --build
```
или используйте команду:
```bash
  make test
```
- с запуском тестов локально:
1. Поднимите инфратсруктуру для тестов.
```bash
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  cd /tests/functional \
  &&docker compose -f docker-compose.local_test.yml up -d --build
```
или используйте команды:
```bash
  make install-dev
  make test-local-up
```
2. Запустите тесты
```bash
  SERVICE_URL=http://localhost:8000 \
  PYTHONPATH=src pytest /tests/functional
```
с make:
```bash
  make test-local-run
```
Тесты в проекте охватывают основные функциональные возможности API для работы с фильмами, жанрами и персонами. Они проверяют корректность работы эндпоинтов, а также функциональность кэширования.
### Важные сценарии
Наиболее важные сценарии, которые стоит выделить, включают:

- Успешные запросы: Проверка, что API корректно обрабатывает валидные запросы и возвращает    ожидаемые данные.
- Обработка ошибок: Проверка, что API правильно реагирует на невалидные запросы (например,    несуществующие ID или некорректный формат).
- Кэширование: Проверка, что кэширование работает корректно, что позволяет улучшить     производительность API.
- Пагинация и сортировка: Проверка, что API корректно обрабатывает параметры пагинации и    сортировки, что важно для удобства пользователей.
## Makefile
все команды makefile можно увидеть, вызвав
```bash
  make help
```
