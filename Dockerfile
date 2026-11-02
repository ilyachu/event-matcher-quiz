FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY backend /app/backend
COPY frontend /app/frontend
COPY bot /app/bot

# Инициализация базы данных и сидирование тестовых мероприятий
ENV DB_PATH=/app/backend/database/events.db
RUN python backend/database/seed_events.py

EXPOSE 8080

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
