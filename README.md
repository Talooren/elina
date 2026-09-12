# Elina — Персональный AI-ассистент

Telegram-бот с «характером»: голосовые сообщения (ElevenLabs), генерация фото (fal.ai), распознавание речи (Deepgram), trust-логика 0–6, fallback-цепочки и memory-слой.

## 🎯 Обзор

Персональный AI-ассистент в Telegram с «живым» характером. Поддерживает голосовое общение (TTS через ElevenLabs/Fish Audio, STT через Deepgram/Whisper), генерацию изображений (fal.ai Seedream, Flux Kontext), долговременную память (SQLite) и trust-матрицу доверия 0–6. Развёрнут на VPS (Docker, docker-compose). Включает экспериментального второго агента Aiden (Instagram/Twitter).

## 📁 Структура

| Модуль | Назначение |
|---|---|
| `brain/` | Основной агент: диалоги, trust-логика, фото-запросы, fallback-цепочки |
| `voice/` | TTS (ElevenLabs, Fish Audio) + STT (Deepgram, Whisper) + голосовой кэш |
| `memory/` | SQLite-слой для долговременной памяти |
| `soul/` | SOUL.md (ядро личности) + trust_levels.json (матрица доверия) |
| `aiden/` | Экспериментальный второй агент (Instagram/Twitter) |

Модуль `eyes/` (генерация изображений через fal.ai Seedream 4.5, ComfyUI, InstantID, LoRA) исключён из репозитория. Для запуска потребуется восстановить этот модуль отдельно.

## 🔐 Безопасность

Секреты (.env, API-ключи) не включены в репозиторий.

## 🛠 Технологический стек

- Python 3.10+, aiogram 3.x, aiohttp
- Anthropic Claude (AsyncAnthropic)
- ElevenLabs TTS, Deepgram STT, Groq
- fal.ai (Seedream, Flux Kontext)
- Docker, docker-compose
- SQLite (memory), trust-матрица 0–6

## 📖 Документация

- `ARCHITECTURE.md` — архитектура проекта
- `SOUL.md` — ядро личности
- `CHANGELOG_2026-05-17.md` — история изменений

## 📦 Статус

🟡 Архивный снапшот кода для демонстрации архитектуры. Проект в стадии активного рефакторинга.

---

*Последнее обновление: 2026-09-13*