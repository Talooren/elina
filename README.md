# Elina — Personal AI Assistant

Telegram-бот с «характером»: голосовые сообщения (ElevenLabs), генерация фото (fal.ai), распознавание речи (Deepgram), trust-логика 0–6, fallback-цепочки и memory-слой.

## Статус

**Архивный снапшот кода для демонстрации архитектуры.**  
Проект в стадии активного рефакторинга (CHANGELOG 2026-05-17).

## Структура

| Модуль | Назначение |
|---|---|
| `brain/` | Основной агент: диалоги, trust-логика, фото-запросы, fallback-цепочки |
| `voice/` | TTS (ElevenLabs, Fish Audio) + STT (Deepgram, Whisper) + голосовой кэш |
| `memory/` | SQLite-слой для долговременной памяти |
| `soul/` | SOUL.md (ядро личности) + trust_levels.json (матрица доверия) |
| `aiden/` | Экспериментальный второй агент (Instagram/Twitter) |

## Исключено из публичной версии

Модуль `eyes/` (генерация изображений через fal.ai Seedream 4.5, ComfyUI, InstantID, LoRA) **исключён** из данного репозитория.  
Для запуска потребуется восстановить этот модуль отдельно.

## Технологии

- Python 3.10+, aiogram 3.x, aiohttp
- Anthropic Claude (через AsyncAnthropic)
- ElevenLabs TTS, Deepgram STT, Groq
- fal.ai (Seedream, Flux Kontext)
- Docker, docker-compose
- SQLite (memory), trust-матрица 0–6

## Примечание по безопасности

Файлы `.env` и `.env.before_*` исключены из репозитория.  
API-ключи хранятся отдельно через `docker-compose.yml` → `env_file: .env`.

---

*Последнее обновление: 2026-09-13 — синхронизация с продакшен-сервера*