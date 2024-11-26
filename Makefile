.PHONY: up test install test-local-up test-local-run clean lint format

PYTHON = python3
TEST_PATH = $(CURDIR)/tests/functional
BLACK_LINE_LENGTH = --line-length 79
SRC_DIR = src
TEST_DIR = tests

all: up

# Запуск приложения
up:
	@docker-compose up -d --build

# Запуск тестов в докере
test:
	@echo "Запуск тестов в докере..."
	@cd $(TEST_PATH) \
	&& docker-compose -f docker-compose.local_test.yml -f docker-compose.yml up -d --build

# Поднятие инфраструктуры для запуска тестов локально
test-local-up:
	@echo "Поднятие инфраструктуры для запуска тестов локально..."
	@cd $(TEST_PATH) && \
	docker-compose -f docker-compose.local_test.yml up -d --build

# Запуск тестов локально
test-local-run:
	@echo "Запуск тестов локально..."
	@SERVICE_URL=http://localhost:8000 \
	PYTHONPATH=src pytest $(TEST_PATH)

# Установка зависимостей продашен
install:
	@echo "Установка зависимостей..."
	@pip install -r requirements.txt

# Установка зависимостей dev
install-dev:
	@echo "Установка зависимостей..."
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt

# Линтинг
lint:
	@echo "Запуск линтинга с помощью flake8..."
	@$(PYTHON) -m flake8 $(SRC_DIR) $(TEST_DIR)
	@echo "All done! ✨ 🍰 ✨"

# Автоформатирование
format:
	@echo "Запуск форматирования с помощью black..."
	@$(PYTHON) -m black $(BLACK_LINE_LENGTH) $(SRC_DIR) $(TEST_DIR)

# Очистка
clean:
	@echo "Очистка временных файлов и контейнеров..."
	@docker-compose down -v
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete

# Вывод справки
help:
	@echo "Доступные команды:"
	@echo "  make up             - Запуск приложения"
	@echo "  make test           - Запуск тестов в докере"
	@echo "  make test-local-up  - Поднятие инфраструктуры для запуска тестов"
	@echo "  make test-local-run - Запуск тестов локально"
	@echo "  make install        - Установка зависимостей продакшен"
	@echo "  make install-dev    - Установка зависимостей dev"
	@echo "  make lint           - Запуск линтера"
	@echo "  make format         - Автоформатирование кода"
	@echo "  make clean          - Очистка временных файлов"
