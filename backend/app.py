import os
import json
import uuid
import sqlite3
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from backend.agent.matcher import generate_event_recommendation

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.getenv('DB_PATH', str(BASE_DIR / 'database' / 'events.db'))
FRONTEND_DIR = str(BASE_DIR.parent / 'frontend')

app = FastAPI(title="VibeMatch Event Quiz API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuizSubmission(BaseModel):
    name: str
    age: str
    city: str
    hobbies: List[str]
    eventTypes: List[str]
    readyToMeet: str
    utm_source: Optional[str] = "direct"
    utm_id: Optional[str] = None

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "VibeMatch Event Quiz"}

@app.post("/api/quiz/submit")
async def submit_quiz(data: QuizSubmission):
    user_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO quiz_leads (id, name, age, city, hobbies, event_types, ready_to_meet, utm_source, utm_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.name.strip(),
        data.age,
        data.city.strip(),
        json.dumps(data.hobbies, ensure_ascii=False),
        json.dumps(data.eventTypes, ensure_ascii=False),
        data.readyToMeet,
        data.utm_source,
        data.utm_id
    ))
    conn.commit()
    conn.close()
    return {"status": "ok", "user_id": user_id}

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM quiz_leads WHERE id = ?', (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем наличие закэшированного ответа
    cached = row['ai_recommendation']
    if cached:
        conn.close()
        return {"user_id": user_id, "recommendation": cached, "cached": True}

    user_profile = {
        "name": row['name'],
        "age": row['age'],
        "city": row['city'],
        "hobbies": json.loads(row['hobbies']),
        "eventTypes": json.loads(row['event_types']),
        "readyToMeet": row['ready_to_meet']
    }

    try:
        rec_text = await generate_event_recommendation(user_profile)
        cur.execute('UPDATE quiz_leads SET ai_recommendation = ? WHERE id = ?', (rec_text, user_id))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Ошибка генерации рекомендаций: {str(e)}")

    conn.close()
    return {"user_id": user_id, "recommendation": rec_text, "cached": False}

@app.post("/api/demo/recommendation")
async def demo_recommendation(data: QuizSubmission):
    user_profile = {
        "name": data.name.strip(),
        "age": data.age,
        "city": data.city.strip(),
        "hobbies": data.hobbies,
        "eventTypes": data.eventTypes,
        "readyToMeet": data.readyToMeet
    }
    rec_text = await generate_event_recommendation(user_profile)
    return {"status": "ok", "recommendation": rec_text}

# Раздача фронтенда
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("backend.app:app", host=host, port=port, reload=True)
