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

VOICE_ID = "e824c4ee4482427c94ed3f6e21003cac"
FISH_TTS_URL = "https://api.fish.audio/v1/tts"
MAX_TEXT_LENGTH = 500


class FishTTS:
    def __init__(self, api_key: str, db_path: str, daily_limit: int = 200):
        self.api_key = api_key
        self.db_path = db_path
        self.daily_limit = daily_limit
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

    async def generate(self, text: str):
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(f"Voice skipped: text too long ({len(text)} chars)")
            return None

        today_count = self._get_today_count()
        if today_count >= self.daily_limit:
            logger.warning(f"Voice skipped: daily limit reached ({today_count}/{self.daily_limit})")
            return None

        try:
            wav_bytes = await self._call_fish_api(text)
            if not wav_bytes:
                return None

            ogg_bytes = await self._convert_to_ogg(wav_bytes)
            if ogg_bytes:
                self._increment_count()
                logger.info(f"Fish TTS: generated {len(ogg_bytes)} bytes (daily: {today_count + 1}/{self.daily_limit})")
            return ogg_bytes

        except Exception as e:
            logger.error(f"Fish TTS unexpected error: {e}")
            return None

    async def _call_fish_api(self, text: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "reference_id": VOICE_ID,
            "format": "wav",
            "chunk_length": 200,
            "normalize": False,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(FISH_TTS_URL, headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.error(f"Fish API error: HTTP {resp.status_code} — {resp.text[:300]}")
                    return None
                if not resp.content:
                    logger.error("Fish API: empty response body")
                    return None
                return resp.content
            except httpx.TimeoutException:
                logger.error("Fish API: request timeout (30s)")
                return None
            except httpx.RequestError as e:
                logger.error(f"Fish API: network error — {e}")
                return None

    async def _convert_to_ogg(self, wav_bytes: bytes):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_file.write(wav_bytes)
            wav_path = wav_file.name

        ogg_path = wav_path.replace(".wav", ".ogg")
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", wav_path,
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
            logger.error("ffmpeg not found — cannot convert WAV to OGG")
            return None
        finally:
            Path(wav_path).unlink(missing_ok=True)
            Path(ogg_path).unlink(missing_ok=True)
