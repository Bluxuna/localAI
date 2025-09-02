import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import json
import os

DB_FILE = "ollama_models.db"

def detect_model_type(text: str) -> str:
    text = text.lower()
    if "embedding" in text or "embeddings" in text:
        return "embedding"
    if "vision" in text:
        return "vision"
    if "speech" in text or "audio" in text:
        return "speech"
    if "code" in text or "programming" in text:
        return "code"
    if "chat" in text or "general" in text or "llm" in text:
        return "general llm"
    return "other"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        description TEXT,
        sizes TEXT,
        tags TEXT,
        pulls TEXT,
        updated TEXT,
        type TEXT
    )
    """)
    conn.commit()
    return conn

def fetch_models(url="https://ollama.com/library"):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    conn = init_db()
    cur = conn.cursor()

    for item in soup.select("li a[href^='/library/']"):
        name = item.text.strip()
        if not name:
            continue

        parent_li = item.find_parent("li")
        if not parent_li:
            continue

        full_text = parent_li.get_text(separator=" ", strip=True)
        desc = full_text.replace(name, "", 1).strip()

        sizes = re.findall(r"\d+(?:\.\d+)?b", full_text.lower())
        pulls_match = re.search(r"(\d+(?:\.\d+)?[MK]?)\s+Pulls", full_text)
        pulls = pulls_match.group(1) if pulls_match else None
        updated_match = re.search(r"Updated\s+([\w\s]+)", full_text)
        updated = updated_match.group(1).strip() if updated_match else None

        tags = []
        if "Tags" in full_text:
            after_tags = full_text.split("Tags", 1)[1]
            tags = after_tags.split("Updated", 1)[0].split()
            tags = [t.strip(",") for t in tags if t.strip(",")]

        model_type = detect_model_type(full_text + " " + " ".join(tags))

        # Insert or ignore duplicates
        cur.execute("""
            INSERT INTO models (name, description, sizes, tags, pulls, updated, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO NOTHING
        """, (
            name,
            desc,
            json.dumps(sizes),  # store list as JSON
            json.dumps(tags),
            pulls,
            updated,
            model_type
        ))

    conn.commit()
    conn.close()

def get_all_models():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT name, description, sizes, tags, pulls, updated, type FROM models")
    rows = cur.fetchall()
    conn.close()

    # Convert back JSON fields
    result = []
    for r in rows:
        result.append({
            "name": r[0],
            "description": r[1],
            "sizes": json.loads(r[2]) if r[2] else [],
            "tags": json.loads(r[3]) if r[3] else [],
            "pulls": r[4],
            "updated": r[5],
            "type": r[6],
        })
    return result

if __name__ == "__main__":
    fetch_models()
    print(json.dumps(get_all_models(), ensure_ascii=False, indent=2))