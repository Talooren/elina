# ELINA — лог изменений 17.05.2026

## 1. Деплой нового генератора фото (eyes/fal_generator.py)
- Создан drop-in replacement для eyes/generator.py на базе fal.ai Seedream 4.5 edit
- agent.py: заменены 3 импорта eyes.generator → eyes.fal_generator (строки 32, 226, 931)
- logger.info/warning/error заменены на print() для видимости в docker logs

## 2. Логика trust для фото-запросов (agent.py)
Разделены «максимум доступного» и «дефолт при запросе»:
- PHOTO_TRIGGERS («покажи себя») → effective_trust = min(real_trust, 3) — всегда одетая
- INTIMATE_PHOTO_TRIGGERS → effective_trust = min(real_trust, 5), требует real_trust ≥ 4
- EXPLICIT (detect_explicit_scene) → effective_trust = 6, требует real_trust ≥ 5
- При недостаточном trust — in-character отказ текстом
- Добавлены триггеры «в белье», «в нижнем», «в купальнике», «в бикини», «в стрингах»
- Groq classify вызывается только при effective_trust ≥ 4 (не для обычных фото)

## 3. Фикс отправки фото (agent.py — handle_photo_request)
- Было: bot.send_photo(url) — Telegram сам тянет URL, fal.media URLs истекают за ~100с
- Стало: скачиваем байты через aiohttp, отправляем BufferedInputFile
- Если generate_photo вернул None — in-character сообщение («блин, камера тупит..»)

## 4. Референсные фото (eyes/reference_urls.json)
- Удалены dataset-v4-08, dataset-v4-24, dataset-v5-04, dataset-v5-21 — вызывали CPV
- Оставлены 7 SFW-референсов: face-final-01, face_cropped, face-ref-neutral2,
  batch_03_fixed, test_scene9_fixed, v8_002_fixed, lowq_009_fixed
- Создан upload_references.py для пересоздания JSON

## 5. Fallback chain (eyes/fal_generator.py — generate_photo)
- Удалён фоллбэк на TensorArt (давал «старое лицо»)
- Новая цепочка: Seedream → retry (sleep 3s) → Flux Kontext → return None
- Flux Kontext: fal-ai/flux-kontext/dev, image_url=первый референс

## 6. ELINA_IDENTITY
- «Bright vivid blue eyes» → «Pale blue-grey eyes»
- Добавлены: возраст 22, 168cm, fair skin with light freckles, slim athletic build
- Грудь: «full round C-cup breasts» (без visible cleavage — конфликтовало с trust 0-3)

## 7. TRUST_MODIFIERS (0-6)
Все значения переписаны с явным указанием типа съёмки и одежды:
- trust 0-3: «POV selfie from phone camera», закрытая одежда, явный запрет декольте
- trust 4: «POV selfie in bedroom, thin silk nightgown, bare shoulders»
- trust 5: «mirror selfie, black lace bralette and shorts»
- trust 6: «mirror selfie, lingerie»

## 8. Groq system prompt (build_prompt_groq)
- Убрано описание лица/волос/глаз из system prompt (дублировало ELINA_IDENTITY)
- Добавлены CRITICAL CAMERA RULES:
  - POV selfie = камера смотрит на неё, рука НЕ видна в кадре
  - Mirror selfie = отражение, телефон виден в руке, вспышка в зеркале
  - Дома — всегда selfie (она живёт одна)
  - Third-person только на улице/публичном месте

## 9. Диагностика CPV (content_policy_violation)
- Все 7 SFW-референсов по отдельности — OK
- 3 face-only референса — BLOCKED (ByteDance блокирует 3 портрета + bust в промпте)
- Вывод: использовать все 7 (body+scene контекст снижает риск CPV)
- Intermittent CPV покрывается retry-логикой
