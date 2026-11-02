import sqlite3
import json
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.getenv('DB_PATH', str(BASE_DIR / 'events.db'))

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def list_events():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, title, city, category, format, date_str, location FROM events WHERE is_active = 1 ORDER BY id ASC')
    rows = cur.fetchall()
    print(f'=== Всего активных мероприятий: {len(rows)} ===')
    for r in rows:
        print(f'[{r["id"]}] {r["title"]} | {r["city"]} | {r["category"]} | {r["format"]} | {r["date_str"]}')
    conn.close()

def stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM events')
    events_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM quiz_leads')
    leads_count = cur.fetchone()[0]
    cur.execute('SELECT city, COUNT(*) as cnt FROM quiz_leads GROUP BY city ORDER BY cnt DESC LIMIT 5')
    top_cities = cur.fetchall()
    print('📊 СТАТИСТИКА:')
    print(f'- Мероприятий в базе: {events_count}')
    print(f'- Заполненных квизов (лидов): {leads_count}')
    if top_cities:
        print('- Топ городов по лидам:')
        for c in top_cities:
            print(f'  • {c["city"]}: {c["cnt"]}')
    conn.close()

def add_event(title, city, category, format_type, date_str, location, description, url):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO events (title, city, category, format, date_str, location, description, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, city, category, format_type, date_str, location, description, url))
    conn.commit()
    new_id = cur.lastrowid
    print(f'✓ Мероприятие успешно добавлено с ID #{new_id}')
    conn.close()

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        list_events()
    elif cmd == 'stats':
        stats()
    elif cmd == 'add' and len(sys.argv) >= 9:
        add_event(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
    else:
        print('Использование:')
        print('  python3 manage_events.py list')
        print('  python3 manage_events.py stats')
        print('  python3 manage_events.py add <title> <city> <category> <format> <date> <location> <desc> <url>')
