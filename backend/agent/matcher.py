import os
import json
import sqlite3
import httpx
from typing import Dict, Any, List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv('DB_PATH', str(BASE_DIR / 'database' / 'events.db'))

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1').rstrip('/')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

def fetch_events_for_matching(city: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Сначала ищем события в городе пользователя и онлайн-события
    cur.execute('''
        SELECT id, title, city, category, format, date_str, time_str, location, price, vibe, description, tags, url
        FROM events
        WHERE is_active = 1 AND (LOWER(city) = LOWER(?) OR LOWER(city) = 'онлайн')
    ''', (city,))
    events = [dict(row) for row in cur.fetchall()]
    
    # Если в указанном городе мало событий, дополняем популярными общими мероприятиями
    if len(events) < 3:
        cur.execute('''
            SELECT id, title, city, category, format, date_str, time_str, location, price, vibe, description, tags, url
            FROM events
            WHERE is_active = 1
            LIMIT 6
        ''')
        events = [dict(row) for row in cur.fetchall()]
        
    conn.close()
    return events

async def generate_event_recommendation(user_profile: Dict[str, Any]) -> str:
    events = fetch_events_for_matching(user_profile.get('city', ''))
    
    system_prompt = """Ты — персональный AI-консьерж по мероприятиям и нетворкингу проекта 'VibeMatch'.
Твоя задача — сопоставить анкету человека с базой реальных мероприятий и составить вдохновляющий и емкий персональный дайджест.

Структура ответа:
1. Теплое персональное приветствие по имени с комплиментом его набору увлечений.
2. Выбери из базы ровно 2-3 наиболее подходящих мероприятия.
3. По каждому мероприятию укажи:
   - 📍 Название и формат
   - 🗓️ Дату, время и локацию
   - 💡 Почему это идеальный матч (поясни связь с его увлечениями и возрастом)
4. Дай 1 точный совет по легкому знакомству (Icebreaker) под его уровень готовности выбраться.
5. Пиши живым языком без канцелярщины, используй красивые эмодзи и четкие абзацы. Не выдумывай несуществующие события."""

    user_prompt = f"""
АНКЕТА ПОЛЬЗОВАТЕЛЯ:
- Имя: {user_profile.get('name', 'Гость')}
- Возраст: {user_profile.get('age', 'Не указан')}
- Город: {user_profile.get('city', 'Не указан')}
- Увлечения: {', '.join(user_profile.get('hobbies', []))}
- Любимый формат встреч: {', '.join(user_profile.get('eventTypes', []))}
- Готовность выбраться: {user_profile.get('readyToMeet', 'Присматриваюсь')}

БАЗА ДОСТУПНЫХ МЕРОПРИЯТИЙ:
{json.dumps(events, ensure_ascii=False, indent=2)}
"""

    # Если API ключ не задан, возвращаем структурированный мок-ответ для безопасного демо
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY.startswith('sk-your'):
        matched_sample = events[:2] if events else []
        return f"""👋 Привет, {user_profile.get('name', 'друг')}!

Мы подобрали отличные события под твои интересы ({', '.join(user_profile.get('hobbies', []))}):

📍 {matched_sample[0]['title'] if matched_sample else 'AI & Founders Meetup'}
🗓️ {matched_sample[0]['date_str'] if matched_sample else 'Каждую среду, 19:30'} · {matched_sample[0]['location'] if matched_sample else 'Центр города'}
💡 Идеально подходит под твой возраст и интерес к формату {', '.join(user_profile.get('eventTypes', []))}.

⚡ Лайфхак для знакомства: начни разговор с обсуждения темы встречи — это самый органичный способ завести полезные контакты без неловкости!

*(Для работы живого генератора укажите DEEPSEEK_API_KEY в .env)*"""

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }
    payload = {
        'model': DEEPSEEK_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 1200
    }
    
    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(f'{DEEPSEEK_BASE_URL}/chat/completions', headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        choice = data['choices'][0]['message']
        content = choice.get('content')
        if not content and 'reasoning_content' in choice:
            content = choice.get('reasoning_content')
        return content or 'Рекомендации успешно сформированы.'
