import os
import time
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load env
load_dotenv()

BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
TELEGRAM_TOKEN = os.getenv("TG_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TG_CHAT_ID")
TARGET_USERNAME = os.getenv("TARGET_USERNAME")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))

DB_PATH = "database.db"
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS following (
        target_id TEXT,
        followed_id TEXT,
        followed_at TEXT,
        PRIMARY KEY(target_id, followed_id)
    )
    """)
    conn.commit()
    conn.close()


def get_user_id(username):
    url = f"https://api.x.com/2/users/by/username/{username}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()["data"]["id"]


def fetch_following(user_id):
    url = f"https://api.x.com/2/users/{user_id}/following"
    params = {"max_results": 1000}
    results = []
    next_token = None
    while True:
        if next_token:
            params["pagination_token"] = next_token
        r = requests.get(url, headers=HEADERS, params=params, timeout=20)
        if r.status_code == 429:
            print("⚠️ Rate limit hit. Waiting 15 minutes...")
            time.sleep(900)
            continue
        r.raise_for_status()
        js = r.json()
        if "data" in js:
            results.extend([u["id"] for u in js["data"]])
        next_token = js.get("meta", {}).get("next_token")
        if not next_token:
            break
    return set(results)


def load_saved_set(target_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT followed_id FROM following WHERE target_id=?", (target_id,))
    rows = c.fetchall()
    conn.close()
    return set(r[0] for r in rows)


def save_added(target_id, added):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    for fid in added:
        c.execute("INSERT OR IGNORE INTO following VALUES (?,?,?)",
                  (target_id, fid, now))
    conn.commit()
    conn.close()


def remove_removed(target_id, removed):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for fid in removed:
        c.execute("DELETE FROM following WHERE target_id=? AND followed_id=?", (target_id, fid))
    conn.commit()
    conn.close()


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


def main():
    init_db()
    target_id = get_user_id(TARGET_USERNAME)
    print(f"✅ Tracking following of @{TARGET_USERNAME} (ID: {target_id})...")
    while True:
        try:
            current = fetch_following(target_id)
            saved = load_saved_set(target_id)
            added = current - saved
            removed = saved - current

            if added:
                for fid in added:
                    send_telegram(f"🟢 @{TARGET_USERNAME} started following user ID: `{fid}`")
                save_added(target_id, added)

            if removed:
                for fid in removed:
                    send_telegram(f"🔴 @{TARGET_USERNAME} unfollowed user ID: `{fid}`")
                remove_removed(target_id, removed)

            print(f"[{datetime.utcnow().isoformat()}] Checked — Added: {len(added)}, Removed: {len(removed)}")

        except Exception as e:
            print("Error:", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
