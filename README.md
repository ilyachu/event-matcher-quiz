# ⚡ VibeMatch — AI Event Quiz & Matcher

> **Мини-продукт «под ключ»**: конверсионный карточный квиз в стиле **минималистичного Tinder** (по стандартам анти-AI-слоп дизайна **Hallmark**), умный AI-матчинг мероприятий через **DeepSeek 4.1 Flash**, сохранение заявок в SQL и обязательный гейт подписки в **Telegram** и **MAX** перед выдачей персональной подборки.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek_4.1_Flash-FF5A36.svg)](https://platform.deepseek.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

---

## 🧭 Архитектура и Customer Journey Map (CJM)

```
  [ Пользователь на лендинге ]
               │
               ▼
   1. КВИЗ В СТИЛЕ TINDER (6 вопросов)
      ├── Имя
      ├── Возраст (чипсы 18–24, 25–30, 31–40, 40+)
      ├── Город (чипсы популярных + свой ввод)
      ├── Увлечения (мультивыбор тегов)
      ├── Любимый формат событий
      └── Готовность выбраться («Хоть сегодня вечером»)
               │
               ▼ (POST /api/quiz/submit)
   2. SQL БАЗА ДАННЫХ (quiz_leads) ──► Генерация UUID лида + сохранение ответов
               │
               ▼
   3. СТРАНИЦА СПАСИБО (Шаг 7)
      ├── Сводка профиля пользователя
      ├── Кнопка Telegram с Deep Link: /start quiz_<UUID>
      ├── Кнопка MAX с параметром: ?uid=<UUID>&utm_source=quiz
      └── Интерактивное превью (Demo Mode прямо на сайте)
               │
      ┌────────┴──────────────────────────┐
      ▼                                   ▼
 4. TELEGRAM БОТ                     4. MAX / WEB CONNECTOR
      │                                   │
      ├─► getChatMember(@channel)         ├─► groups.isMember (API)
      │                                   │
      ├─► НЕ подписан:                    ├─► НЕ подписан:
      │   Кнопка «📢 Подписаться»          │   Кнопка «📢 Вступить»
      │   + Кнопка «✅ Проверить»         │   + Кнопка «✅ Проверить»
      │                                   │
      └─► ПОДПИСАН: ──────────────────────┴─► ПОДПИСАН:
               │                                   │
               ▼                                   ▼
   5. AI MATCHER (DeepSeek 4.1 Flash)
      ├── Сопоставление анкеты с базой events (город, формат, теги)
      ├── Персональное обращение по имени
      ├── Топ 2–3 идеальных матча с объяснением («почему именно тебе»)
      └── Практичный лайфхак для легкого старта / нетворкинга
```

---

## ✨ Ключевые особенности

1. **Дизайн Tinder-Level по фреймворку Hallmark**:
   - Строгая темная палитра (`#0B0D11`, `#16191F`, акцентный терракотовый `#FF5A36`), чистая иерархия шрифтов *Plus Jakarta Sans*.
   - Интерактивный стек карточек со свайп-эффектом и сторис-прогресс-баром сверху.
   - Никаких клише и AI-слопа (шаблонных градиентов и тяжелых карточек).
2. **AI-движок сопоставления (DeepSeek 4.1 Flash / OpenAI-compatible)**:
   - Анализирует город (с приоритетом локальных и онлайн-мероприятий), возрастную категорию и вайб встреч.
   - Формирует персонализированный отклик: обоснование каждого матча + ледокол (icebreaker) для знакомств.
3. **Гейт подписки (Subscription Wall)**:
   - Проверка наличия подписки на канал через метод Telegram Bot API `getChatMember`.
   - Поддержка параметров deep-linking `/start quiz_<UUID>` для сквозной передачи контекста между вебом и мессенджерами.
   - Готовый модуль-адаптер для интеграции с мессенджером MAX.
4. **Автономное SQL-пространство под базу мероприятий**:
   - База SQLite (в режиме WAL) / поддержка миграции на PostgreSQL.
   - Каталог с гибкими метаданными: город, формат, дата, время, локация, цена, вайб, теги и ключевые слова.
   - В комплекте CLI-инструмент для управления мероприятиями и просмотра аналитики заявок.

---

## 📂 Структура проекта

```
event-matcher-quiz/
├── frontend/
│   └── index.html               # Одностраничный лендинг с квизом и страницей «Спасибо»
├── backend/
│   ├── app.py                   # FastAPI сервер (REST API + раздача фронтенда)
│   ├── agent/
│   │   └── matcher.py           # Модуль матчинга на базе DeepSeek 4.1 Flash
│   └── database/
│       ├── schema.sql           # SQL-схема таблиц events и quiz_leads
│       ├── seed_events.py       # Сид-скрипт с 13+ реальными мероприятиями
│       └── manage_events.py     # CLI-утилита для управления базой и статистики
├── bot/
│   ├── telegram_bot.py          # Telegram-бот с гейтом подписки (aiogram 3.x)
│   └── max_connector.py         # Адаптер для мессенджера MAX
├── docker-compose.yml           # Multi-container Docker оркестрация
├── Dockerfile                   # Оптимизированный контейнер Python 3.12
├── nginx.conf                   # Конфиг Nginx reverse proxy
├── requirements.txt             # Зависимости Python
├── .env.example                 # Шаблон переменных окружения
└── README.md                    # Документация проекта
```

---

## 🚀 Быстрый старт (Local Development)

### 1. Клонирование репозитория

```bash
git clone https://github.com/ilyachu/event-matcher-quiz.git
cd event-matcher-quiz
```

### 2. Настройка окружения

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```ini
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@your_channel_username
```

### 3. Установка зависимостей и запуск

```bash
# Создание и активация venv
python3 -m venv venv
source venv/bin/activate

# Установка библиотек
pip install -r requirements.txt

# Инициализация базы данных и сидирование тестовых мероприятий
python backend/database/seed_events.py

# Запуск веб-сервера
python -m backend.app
```

Откройте в браузере: **`http://localhost:8080/`**

---

## 🐳 Запуск через Docker & Docker Compose

Запуск всего стека (бэкенд + Telegram-бот) одной командой:

```bash
docker compose up -d --build
```

Сервер будет доступен на порту `8080`. Для просмотра логов:
```bash
docker compose logs -f
```

---

## 🛠️ Управление базой мероприятий через CLI

В проект встроена утилита для быстрого просмотра и пополнения базы событий:

```bash
# Список всех активных мероприятий в каталоге
python backend/database/manage_events.py list

# Статистика заявок и популярности городов
python backend/database/manage_events.py stats

# Добавление нового мероприятия
python backend/database/manage_events.py add \
  "AI Breakfast" "Москва" "IT и Стартапы" "Камерные завтраки" "Пятница, 10:00" \
  "Surf Coffee на Покровке" "Утренний кофе с разработчиками" "https://t.me/event"
```

---

## 📡 API Эндпоинты

| Метод | Путь | Описание |
| :--- | :--- | :--- |
| `POST` | `/api/quiz/submit` | Принимает ответы квиза, сохраняет лид в SQL и возвращает `user_id` |
| `GET` | `/api/recommendations/{user_id}` | Генерирует или отдает из кэша персональные AI-рекомендации DeepSeek |
| `POST` | `/api/demo/recommendation` | Тестовый прогон рекомендаций без сохранения в базу (для мгновенного превью) |
| `GET` | `/api/health` | Проверка жизнеспособности сервиса |

---

## 🔒 Безопасность и конфигурация

* В репозитории **нет захардкоженных секретов**, токенов, IP-адресов серверов или учетных данных.
* Все ключи и параметры передаются исключительно через переменные окружения (`os.getenv`).
* База данных SQLite работает в режиме `WAL` (Write-Ahead Logging), обеспечивая высокую скорость параллельного чтения и записи.

---

## 📄 Лицензия

Проект распространяется под открытой лицензией [MIT](LICENSE).
