#!/usr/bin/env python3
"""Standalone test for Fish Audio TTS — runs inside the container."""
import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

TEST_PHRASE = "[soft voice] Привет. Меня зовут Элина. Как ты сегодня?"
OUTPUT_PATH = Path("/app/memory/data/test_voice.ogg")
DB_PATH = "/app/memory/data/memory.db"


async def main():
    api_key = os.getenv("FISH_API_KEY")
    if not api_key:
        print("ERROR: FISH_API_KEY not set in .env")
        sys.exit(1)

    daily_limit = int(os.getenv("FISH_DAILY_LIMIT", "200"))

    from voice.fish_tts import FishTTS
    from voice.voice_cache import VoiceCache

    tts = FishTTS(api_key=api_key, db_path=DB_PATH, daily_limit=daily_limit)
    cache = VoiceCache(cache_dir="/app/memory/data/voice_cache")

    print(f"Phrase : {TEST_PHRASE!r}")
    print(f"API key: {api_key[:8]}...")

    cached = cache.get(TEST_PHRASE)
    if cached:
        print(f"Cache hit — using cached audio ({len(cached)} bytes)")
        ogg_bytes = cached
    else:
        print("Calling Fish Audio API...")
        ogg_bytes = await tts.generate(TEST_PHRASE)

    if not ogg_bytes:
        print("FAILED: no audio returned (check logs above)")
        sys.exit(1)

    OUTPUT_PATH.write_bytes(ogg_bytes)
    if not cached:
        cache.put(TEST_PHRASE, ogg_bytes)

    size_kb = len(ogg_bytes) / 1024
    print(f"")
    print(f"SUCCESS")
    print(f"  Path : {OUTPUT_PATH}")
    print(f"  Size : {size_kb:.1f} KB")
    print(f"")
    print(f"To copy to host:")
    print(f"  docker cp elina:{OUTPUT_PATH} /root/elina/test_voice.ogg")


if __name__ == "__main__":
    asyncio.run(main())
