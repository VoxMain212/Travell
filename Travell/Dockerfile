FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (для production)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Запуск через gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "Travell.wsgi:application"]