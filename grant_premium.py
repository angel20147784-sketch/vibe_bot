import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vibe_bot.db")
db = sqlite3.connect(DB_PATH)
db.execute("INSERT OR IGNORE INTO premium_users (user_id) VALUES (8639540904)")
db.commit()
print("Premium added for 8639540904")
db.close()
