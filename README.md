# Travell

Веб-приложение для планирования поездок. Реализовано на Django, переведено с SQLite на PostgreSQL и упаковано в Docker для соответствия промышленным стандартам разработки.

## Основной функционал

- Создание, просмотр, редактирование и удаление поездок (CRUD)
- AJAX-поиск по названию и месту назначения
- Удобный интерфейс на основе HTML/CSS/JavaScript
- Админка Django для управления данными

## Технологии

- **Backend**: Python, Django
- **База данных**: PostgreSQL
- **Контейнеризация**: Docker, Docker Compose
- **Зависимости**: psycopg2-binary, python-decouple, gunicorn

## Требования

- Docker
- Docker Compose

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-логин/travell.git
   cd travell

   docker-compose up --build
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser #Если нужно
   ```

## Структура проекта
- **planner/** — основное Django-приложение (модели, представления, шаблоны)
- **Travell/** — конфигурация Django-проекта (settings.py, urls.py)
- **Dockerfile** — инструкции для сборки образа
- **docker-compose.yml** — оркестрация контейнеров (Django + PostgreSQL)
- **requirements.txt** — зависимости Python