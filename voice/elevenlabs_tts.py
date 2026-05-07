import asyncio
import logging
import os
import sqlite3
import subprocess
import tempfile
from datetime import date
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

VOICE_ID = "a6EWqlBvacPq4UeRtQEm"
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
MODEL_ID = "eleven_v3"
MAX_TEXT_LENGTH = 500

DEFAULT_MOOD = "neutral"
MOOD_VOICE_SETTINGS = {
    "sleepy":        {"stability": 0.80, "similarity_boost": 0.60, "style": 0.05, "speed": 0.80},
    "warm":          {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, "speed": 0.88},
    "neutral":       {"stability": 0.60, "similarity_boost": 0.75, "style": 0.0,  "speed": 0.85},
    "philosophical": {"stability": 0.70, "similarity_boost": 0.65, "style": 0.10, "speed": 0.82},
}


class ElevenLabsTTS:
    def __init__(self, api_key: str, db_path: str, daily_limit: int = 200, voice_id: str = ""):
        self.api_key = api_key
        self.db_path = db_path
        self.daily_limit = daily_limit
        self.voice_id = voice_id or VOICE_ID
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS voice_api_usage (
                date TEXT PRIMARY KEY,
                call_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def _get_today_count(self) -> int:
        today = str(date.today())
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT call_count FROM voice_api_usage WHERE date = ?", (today,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0

    def _increment_count(self):
        today = str(date.today())
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO voice_api_usage (date, call_count) VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET call_count = call_count + 1
        """, (today,))
        conn.commit()
        conn.close()

    async def generate(self, text: str, mood: str = DEFAULT_MOOD, bypass_limit: bool = False):
        if not bypass_limit and len(text) > MAX_TEXT_LENGTH:
            logger.warning(f"Voice skipped: text too long ({len(text)} chars)")
            return None

        today_count = self._get_today_count()
        if not bypass_limit and today_count >= self.daily_limit:
            logger.warning(f"Voice skipped: daily limit reached ({today_count}/{self.daily_limit})")
            return None

        try:
            mp3_bytes = await self._call_elevenlabs_api(text, mood)
            if not mp3_bytes:
                return None

            ogg_bytes = await self._convert_to_ogg(mp3_bytes)
            if ogg_bytes:
                self._increment_count()
                logger.info(f"ElevenLabs TTS: mood={mood} generated {len(ogg_bytes)} bytes (daily: {today_count + 1}/{self.daily_limit})")
            return ogg_bytes

        except Exception as e:
            logger.error(f"ElevenLabs TTS unexpected error: {e}")
            return None

    async def _call_elevenlabs_api(self, text: str, mood: str = DEFAULT_MOOD):
        url = ELEVENLABS_TTS_URL.format(voice_id=self.voice_id)
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        settings = MOOD_VOICE_SETTINGS.get(mood, MOOD_VOICE_SETTINGS[DEFAULT_MOOD])
        payload = {
            "text": text,
            "model_id": MODEL_ID,
            "voice_settings": settings,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.error(f"ElevenLabs API error: HTTP {resp.status_code} — {resp.text[:300]}")
                    return None
                if not resp.content:
                    logger.error("ElevenLabs API: empty response body")
                    return None
                return resp.content
            except httpx.TimeoutException:
                logger.error("ElevenLabs API: request timeout (30s)")
                return None
            except httpx.RequestError as e:
                logger.error(f"ElevenLabs API: network error — {e}")
                return None

    async def _convert_to_ogg(self, mp3_bytes: bytes):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_file:
            mp3_file.write(mp3_bytes)
            mp3_path = mp3_file.name

        ogg_path = mp3_path.replace(".mp3", ".ogg")
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", mp3_path,
                "-c:a", "libopus", "-b:a", "64k",
                ogg_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.error(f"ffmpeg conversion failed: {stderr.decode()[:300]}")
                return None
            with open(ogg_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            logger.error("ffmpeg not found — cannot convert MP3 to OGG")
            return None
        finally:
            Path(mp3_path).unlink(missing_ok=True)
            Path(ogg_path).unlink(missing_ok=True)
