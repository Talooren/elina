import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

VOICE_ID = "e824c4ee4482427c94ed3f6e21003cac"
MAX_CACHE_FILES = 500


class VoiceCache:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_to_path(self, text: str, mood: str = "") -> Path:
        raw = f"{text}|{VOICE_ID}"
        if mood:
            raw += f"|{mood}"
        key = hashlib.sha256(raw.encode()).hexdigest()
        return self.cache_dir / f"{key}.ogg"

    def get(self, text: str, mood: str = ""):
        path = self._key_to_path(text, mood)
        if path.exists():
            path.touch()
            logger.debug(f"Voice cache hit: {path.name}")
            return path.read_bytes()
        return None

    def put(self, text: str, data: bytes, mood: str = ""):
        self._evict_if_needed()
        path = self._key_to_path(text, mood)
        path.write_bytes(data)
        count = self._count()
        logger.info(f"Voice cache: saved {path.name} ({len(data)} bytes), total={count} files")

    def _count(self) -> int:
        return len(list(self.cache_dir.glob("*.ogg")))

    def _evict_if_needed(self):
        files = sorted(self.cache_dir.glob("*.ogg"), key=lambda f: f.stat().st_mtime)
        while len(files) >= MAX_CACHE_FILES:
            oldest = files.pop(0)
            oldest.unlink()
            logger.info(f"Voice cache: evicted {oldest.name} (LRU)")
