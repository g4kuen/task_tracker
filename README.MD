# Task Tracker

Инструкция по развертыванию проекта (пока без Docker)

---

## Быстрый старт

```bash
# 1. Инициализация Git-репозитория (если ещё не сделано)
git init

# 2. Клонирование ветки master из репозитория
git clone -b master https://github.com/g4kuen/task_tracker.git

# 3. Создайте виртуальное окружение

# 4. Переход в каталог проекта
cd fastapiCRUD

# 5. Установка зависимостей
pip install -r requirements.txt

# 6. Создание базы данных в PostgreSQL
CREATE DATABASE todo_db;

# 7. Создайте .env файл и введите ссылку доступа к базе данных
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db

# 8. Миграции в терминале cd\fastapiCRUD
alembic upgrade head

# 9. Запуск проекта в терминале
uvicorn main:app --reload --port 8080

# 10. Запуск тестов pytest в терминале cd\fastapiCRUD
pytest test_main.py

```

---
## Веб-интерфейс

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/` | Главная страница со списком задач |
| `GET` | `/tasks/create` | Форма создания новой задачи |
| `POST` | `/tasks/create` | Создание новой задачи |
| `GET` | `/tasks/{id}` | Просмотр конкретной задачи |
| `GET` | `/tasks/{id}/edit` | Форма редактирования задачи |
| `POST` | `/tasks/{id}/edit` | Обновление задачи |
| `POST` | `/tasks/{id}/delete` | Удаление задачи |

## REST API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/api/health` | Проверка здоровья приложения |
| `GET` | `/api/tasks` | Получение всех задач в формате JSON |
| `GET` | `/api` | Информация о API |

## Документация

| Метод | Эндпоинт | Описание     |
|-------|----------|--------------|
| `GET` | `/docs` | Документация |

