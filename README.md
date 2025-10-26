# 🐦 Twitter (X) Following Tracker Bot

A simple Python + Telegram bot to track when someone **follows or unfollows** new accounts on X (Twitter).

---

## ⚙️ Features
- Track following changes of a specific user
- Sends Telegram alerts for new/unfollowed accounts
- Stores data in SQLite (auto-created)
- Docker-ready deployment

---

## 🧰 Setup

### 1️⃣ Clone Repo
```bash
git clone https://github.com/yourusername/twitter-follow-tracker-bot.git
cd twitter-follow-tracker-bot
```

---
### 2️⃣ Install Dependencies
```
pip install -r requirements.txt
```
### 3️⃣ Configure .env
Copy .env.example → .env and fill your tokens:
```
cp .env.example .env
```
### 4️⃣ Run Bot
```
python track_following.py
```
or via Docker:
```
docker build -t follow-bot .
docker run --env-file .env follow-bot
```

---

### 🧠 Notes

- You must have a valid Twitter API Bearer Token.
- Use responsibly, obey rate limits & TOS.
- For large accounts (many following), polling may take longer.
- Default polling: every 5 minutes (adjust in .env).

---

### 💡 Tips:

"TG_CHAT_ID" bisa didapat dengan kirim pesan ke botmu, lalu buka "https://api.telegram.org/botYOUR_TOKEN/getUpdates"

"POLL_INTERVAL" dalam detik (300 = 5 menit)
```
