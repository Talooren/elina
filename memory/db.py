import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple


class MemoryDB:
    """Работа с SQLite базой данных"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация схемы БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        schema_path = Path(self.db_path).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
                cursor.executescript(schema)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_key TEXT UNIQUE,
                answer TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
    
    def get_or_create_user(self, telegram_id: str, username: str = None, first_name: str = None) -> int:
        """Получить или создать пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = cursor.fetchone()
        
        if row:
            user_id = row[0]
            cursor.execute(
                "UPDATE users SET last_seen = ? WHERE id = ?",
                (datetime.now(), user_id)
            )
        else:
            cursor.execute(
                "INSERT INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)",
                (telegram_id, username, first_name)
            )
            user_id = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO trust_levels (user_id) VALUES (?)",
                (user_id,)
            )
        
        conn.commit()
        conn.close()
        return user_id
    
    def get_trust_level(self, user_id: int) -> int:
        """Получить уровень доверия пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT level, message_count FROM trust_levels WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row[0]
        return 0
    
    def increment_message_count(self, user_id: int):
        """Увеличить счётчик сообщений"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE trust_levels SET message_count = message_count + 1, last_interaction = ? WHERE user_id = ?",
            (datetime.now(), user_id)
        )
        
        cursor.execute(
            "SELECT message_count FROM trust_levels WHERE user_id = ?",
            (user_id,)
        )
        count = cursor.fetchone()[0]
        
        new_level = 0
        if count >= 1000:
            new_level = 5
        elif count >= 500:
            new_level = 4
        elif count >= 200:
            new_level = 3
        elif count >= 50:
            new_level = 2
        elif count >= 5:
            new_level = 1
        
        if new_level > 0:
            cursor.execute(
                "UPDATE trust_levels SET level = ? WHERE user_id = ? AND level < ?",
                (new_level, user_id, new_level)
            )
        
        conn.commit()
        conn.close()
    
    def save_message(self, user_id: int, role: str, content: str):
        """Сохранить сообщение в историю"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        
        conn.commit()
        conn.close()
    
    def get_active_users(self) -> List[Tuple[int, str]]:
        """Получить всех пользователей (id, telegram_id)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, telegram_id FROM users")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_last_user_message_time(self, user_id: int):
        """Получить время последнего сообщения пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(timestamp) FROM messages WHERE user_id = ? AND role = 'user'",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            try:
                return datetime.fromisoformat(str(row[0]))
            except Exception:
                try:
                    return datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S')
                except Exception:
                    return None
        return None

    def get_unread_user_messages(self, user_id: int) -> List[str]:
        """Сообщения пользователя после последнего ответа Элины (без ответа)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(timestamp) FROM messages WHERE user_id = ? AND role = 'assistant'",
            (user_id,)
        )
        row = cursor.fetchone()
        last_assistant_time = row[0] if row and row[0] else '1970-01-01'
        cursor.execute(
            "SELECT content FROM messages WHERE user_id = ? AND role = 'user' AND timestamp > ? ORDER BY timestamp",
            (user_id, last_assistant_time)
        )
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def save_learned_fact(self, question_key: str, answer: str, source: str = "web"):
        """Сохранить выученный факт"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO learned_facts (question_key, answer, source) VALUES (?, ?, ?)",
            (question_key, answer, source)
        )
        conn.commit()
        conn.close()

    def get_learned_fact(self, question_key: str):
        """Получить выученный факт"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT answer FROM learned_facts WHERE question_key = ?",
            (question_key,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def get_recent_messages(self, user_id: int, limit: int = 20) -> List[Tuple[str, str]]:
        """Получить последние сообщения пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [(role, content) for role, content in reversed(rows)]
