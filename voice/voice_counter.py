import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

VOICE_STREAK_LIMIT = 3   # голосовых до переключения: 1, 2, 3-й замыкает цикл
TEXT_UNLOCK_COUNT  = 5   # текстовых сообщений в blocked-режиме для разблокировки


class VoiceStreakCounter:
    def __init__(self, db_path: str, owner_id: int = 0):
        self.db_path = db_path
        self.owner_id = owner_id
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS voice_streak (
                user_id    INTEGER PRIMARY KEY,
                streak     INTEGER DEFAULT 0,
                blocked    INTEGER DEFAULT 0,
                text_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for col in ("blocked", "text_count"):
            try:
                conn.execute(f"ALTER TABLE voice_streak ADD COLUMN {col} INTEGER DEFAULT 0")
            except Exception:
                pass
        conn.commit()
        conn.close()

    def get_reply_mode(self, user_id: int, incoming_is_voice: bool) -> str:
        """
        voice   — голосовое 1..LIMIT-1, отвечать голосом нормально
        switch  — голосовое LIMIT, отвечать голосом "хватит голосовых"
        blocked — голосовое после switch, отвечать текстом
        text    — текстовое сообщение
        """
        if self.owner_id and user_id == self.owner_id:
            return "voice" if incoming_is_voice else "text"

        streak, blocked, text_count = self._get(user_id)

        if not incoming_is_voice:
            if blocked:
                new_count = text_count + 1
                if new_count >= TEXT_UNLOCK_COUNT:
                    # разблокировка после 5 текстовых
                    self._set(user_id, streak=0, blocked=0, text_count=0)
                    logger.info(f"Voice unlocked for user {user_id} after {TEXT_UNLOCK_COUNT} texts")
                else:
                    self._set(user_id, streak=streak, blocked=1, text_count=new_count)
                    logger.debug(f"User {user_id} blocked, text {new_count}/{TEXT_UNLOCK_COUNT}")
            else:
                # не заблокирован — сбрасываем streak при тексте
                self._set(user_id, streak=0, blocked=0, text_count=0)
            return "text"

        # --- входящее голосовое ---
        if blocked:
            return "blocked"

        if streak >= VOICE_STREAK_LIMIT:
            self._set(user_id, streak=0, blocked=1, text_count=0)
            logger.info(f"Voice cycle closed for user {user_id}")
            return "switch"

        self._set(user_id, streak=streak + 1, blocked=0, text_count=0)
        logger.debug(f"Voice streak for user {user_id}: {streak + 1}/{VOICE_STREAK_LIMIT}")
        return "voice"

    def _get(self, user_id: int):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT streak, blocked, text_count FROM voice_streak WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return (row[0], row[1], row[2]) if row else (0, 0, 0)

    def _set(self, user_id: int, streak: int, blocked: int, text_count: int):
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO voice_streak (user_id, streak, blocked, text_count, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                streak = ?, blocked = ?, text_count = ?, updated_at = ?
        """, (user_id, streak, blocked, text_count, now,
              streak, blocked, text_count, now))
        conn.commit()
        conn.close()
