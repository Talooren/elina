import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DeepgramSTT:
    """Speech-to-text через Deepgram SDK v6+."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
        if api_key:
            try:
                from deepgram import AsyncDeepgramClient
                self._client = AsyncDeepgramClient(api_key=api_key)
                logger.info("DeepgramSTT: client initialized (SDK v6)")
            except Exception as e:
                logger.error(f"DeepgramSTT init error: {e}")

    async def transcribe_voice(self, message, bot) -> Optional[str]:
        if not self._client:
            return None

        try:
            file_info = await bot.get_file(message.voice.file_id)
            downloaded = await bot.download_file(file_info.file_path)
            audio_bytes = downloaded.read()

            response = await self._client.listen.v1.media.transcribe_file(
                request=audio_bytes,
                model="nova-2",
                language="ru",
                smart_format=True,
            )

            transcript = response.results.channels[0].alternatives[0].transcript
            if transcript and transcript.strip():
                logger.info(
                    f"STT: {message.voice.duration}s -> {repr(transcript.strip()[:100])}"
                )
                return transcript.strip()

            logger.warning("STT: empty transcript returned")
            return None

        except Exception as e:
            logger.error(f"STT transcribe error: {e}")
            return None
