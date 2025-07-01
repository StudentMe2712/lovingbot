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
                description TEXT,
                tags TEXT,
                emotion TEXT
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
                remind_at TEXT NOT NULL,
                shared_with_partner BOOLEAN DEFAULT FALSE
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_partners (
                user_id INTEGER,
                blocked_id INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item TEXT NOT NULL,
                done BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, name):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)', (user_id, name))
        self.conn.commit()

    def add_memory(self, type, content, file_id=None, description=None, tags=None, emotion=None):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO memories (type, content, file_id, description, tags, emotion) VALUES (?, ?, ?, ?, ?, ?)', (type, content, file_id, description, tags, emotion))
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

    def add_reminder(self, user_id: int, text: str, remind_at: str, shared_with_partner: bool = False):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (user_id, text, remind_at, shared_with_partner) VALUES (?, ?, ?, ?)",
            (user_id, text, remind_at, int(shared_with_partner))
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_reminders(self, user_id: int, include_shared: bool = True):
        cursor = self.conn.cursor()
        if include_shared:
            cursor.execute(
                "SELECT id, text, remind_at, shared_with_partner FROM reminders WHERE user_id = ? OR (shared_with_partner = 1 AND user_id != ?) ORDER BY remind_at",
                (user_id, user_id)
            )
        else:
            cursor.execute(
                "SELECT id, text, remind_at, shared_with_partner FROM reminders WHERE user_id = ? ORDER BY remind_at",
                (user_id,)
            )
        return cursor.fetchall()

    def remove_reminder(self, user_id: int, reminder_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM reminders WHERE (user_id = ? OR shared_with_partner = 1) AND id = ?",
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

    def block_partner(self, user_id: int, blocked_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO blocked_partners (user_id, blocked_id) VALUES (?, ?)",
            (user_id, blocked_id)
        )
        self.conn.commit()

    def unblock_partner(self, user_id: int, blocked_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM blocked_partners WHERE user_id = ? AND blocked_id = ?",
            (user_id, blocked_id)
        )
        self.conn.commit()

    def is_partner_blocked(self, user_id: int, partner_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM blocked_partners WHERE user_id = ? AND blocked_id = ?",
            (user_id, partner_id)
        )
        return cursor.fetchone() is not None

    def add_wish(self, user_id: int, item: str, created_at: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO wishlists (user_id, item, done, created_at) VALUES (?, ?, 0, ?)",
            (user_id, item, created_at)
        )
        self.conn.commit()
        return cursor.lastrowid

    def remove_wish(self, user_id: int, wish_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM wishlists WHERE user_id = ? AND id = ?",
            (user_id, wish_id)
        )
        self.conn.commit()

    def get_wishlist(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, item, done, created_at FROM wishlists WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return cursor.fetchall()

    def mark_wish_done(self, user_id: int, wish_id: int, done: bool = True):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE wishlists SET done = ? WHERE user_id = ? AND id = ?",
            (int(done), user_id, wish_id)
        )
        self.conn.commit()

    def close(self):
        self.conn.close() 