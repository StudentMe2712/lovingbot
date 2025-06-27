import sqlite3
import random

class DatabaseManager:
    def __init__(self, db_path='romantic_bot.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                join_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                date DATE DEFAULT CURRENT_DATE,
                type TEXT,
                content TEXT,
                file_id TEXT,
                description TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_tracking (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                date DATE DEFAULT CURRENT_DATE,
                mood_score INTEGER CHECK(mood_score >= 1 AND mood_score <= 10),
                note TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_stats (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                game_type TEXT,
                score INTEGER,
                date DATE DEFAULT CURRENT_DATE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS important_dates (
                id INTEGER PRIMARY KEY,
                date DATE,
                title TEXT,
                description TEXT,
                recurring BOOLEAN DEFAULT FALSE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                remind_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_by INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, name):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)', (user_id, name))
        self.conn.commit()

    def add_memory(self, type, content, file_id=None, description=None):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO memories (type, content, file_id, description) VALUES (?, ?, ?, ?)', (type, content, file_id, description))
        self.conn.commit()

    def get_random_memory(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM memories')
        ids = [row[0] for row in cursor.fetchall()]
        if not ids:
            return None
        random_id = random.choice(ids)
        cursor.execute('SELECT * FROM memories WHERE id = ?', (random_id,))
        return cursor.fetchone()

    def get_mood_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT AVG(mood_score), COUNT(*) FROM mood_tracking')
        avg, count = cursor.fetchone()
        return avg, count

    def get_game_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT game_type, SUM(score) FROM game_stats GROUP BY game_type')
        return cursor.fetchall()

    def add_reminder(self, user_id: int, text: str, remind_at: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (user_id, text, remind_at) VALUES (?, ?, ?)",
            (user_id, text, remind_at)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_reminders(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, text, remind_at FROM reminders WHERE user_id = ? ORDER BY remind_at",
            (user_id,)
        )
        return cursor.fetchall()

    def remove_reminder(self, user_id: int, reminder_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM reminders WHERE user_id = ? AND id = ?",
            (user_id, reminder_id)
        )
        self.conn.commit()

    def add_mood(self, user_id: int, mood: int, timestamp: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO mood_logs (user_id, mood, timestamp) VALUES (?, ?, ?)",
            (user_id, mood, timestamp)
        )
        self.conn.commit()

    def get_moods(self, user_id: int, since: str = None):
        cursor = self.conn.cursor()
        if since:
            cursor.execute(
                "SELECT mood, timestamp FROM mood_logs WHERE user_id = ? AND timestamp >= ? ORDER BY timestamp",
                (user_id, since)
            )
        else:
            cursor.execute(
                "SELECT mood, timestamp FROM mood_logs WHERE user_id = ? ORDER BY timestamp",
                (user_id,)
            )
        return cursor.fetchall()

    def get_memories_by_period(self, user_id: int, since: str = None):
        if since:
            self.cursor.execute(
                "SELECT id, type, content, created_at FROM memories WHERE user_id = ? AND created_at >= ? ORDER BY created_at",
                (user_id, since)
            )
        else:
            self.cursor.execute(
                "SELECT id, type, content, created_at FROM memories WHERE user_id = ? ORDER BY created_at",
                (user_id,)
            )
        return self.cursor.fetchall()

    def close(self):
        self.conn.close() 