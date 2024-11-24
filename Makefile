.PHONY: up test install

PYTHON = python3
TEST_PATH = $(CURDIR)/tests/functional
BLACK_LINE_LENGTH = --line-length 79
SRC_DIR = src
TEST_DIR = tests

all: up

# Запуск приложения
up:
	@docker-compose up -d --build

# Запуск тестов
test:
	@echo "Запуск тестов..."
	@cd $(TEST_PATH) && docker-compose up -d --build

# Установка зависимостей
install:
	@echo "Установка зависимостей..."
	@pip install -r requirements.txt

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
	@echo "  make up         - Запуск приложения"
	@echo "  make test       - Запуск тестов"
	@echo "  make install    - Установка зависимостей"
	@echo "  make lint       - Запуск линтера"
	@echo "  make format     - Автоформатирование кода"
	@echo "  make clean      - Очистка временных файлов"
