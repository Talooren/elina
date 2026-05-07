import os
import asyncio
import random
import time
import requests

TAMS_TOKEN = os.getenv("TAMS_TOKEN", "710d872b-5799-4a49-94a6-52edb1c551ac")
TAMS_BASE_URL = os.getenv("TAMS_BASE_URL", "https://ap-east-1.tensorart.cloud")
TAMS_BASE_MODEL = os.getenv("TAMS_BASE_MODEL", "879130987013876797")
TAMS_LORA_MODEL = os.getenv("TAMS_LORA_MODEL", "984264758779731123")

BASE = "elina_woman, photorealistic, analog style, portrait of young woman, ash cool-toned grey-blonde hair shoulder length, pale blue-grey eyes, fair matte skin"

NEGATIVE_SFW      = "anime, cartoon, 3d render, deformed, blurry, watermark, plastic skin, old, ugly, nsfw, extra limbs"
NEGATIVE_INTIMATE = "anime, cartoon, 3d render, deformed, blurry, watermark, plastic skin, old, ugly, extra limbs"
NEGATIVE_EXPLICIT = "anime, cartoon, 3d render, deformed, blurry, watermark, plastic skin, old, ugly, extra limbs, bad hands"

# =============================================================================
# SFW-сцены (trust 0-3)
# =============================================================================
TIME_SCENES = {
    "night": [
        "lying on bed, soft bedside lamp warm glow, dark cozy bedroom, oversized hoodie, sleepy relaxed expression",
        "sitting on bed against headboard, single bedside lamp, dark room, oversized t-shirt, phone in hand, tired look",
        "bedroom at night, under blanket, lamp on nightstand, cozy and sleepy, messy hair",
    ],
    "morning": [
        "just woke up, soft morning window light, bedroom, messy hair, oversized t-shirt, warm cozy light",
        "morning routine, kitchen, mug of coffee, natural window light, knit sweater, calm",
        "sitting by window, morning sun, cozy home, oversized sweater, thoughtful",
    ],
    "day": [
        "sitting by window, natural daylight, home interior, knit sweater, thoughtful",
        "cozy living room, soft natural light, reading or resting, casual clothes",
        "kitchen, natural light, making tea, casual, relaxed",
    ],
    "evening": [
        "evening home, warm lamp light, cozy interior, knit sweater, relaxed",
        "sitting on sofa, warm indoor light, cozy evening atmosphere, book or mug",
        "dim evening light, home, contemplative mood, oversized sweater",
    ],
}

# =============================================================================
# Intimate-сцены (trust 4-5) — нагота, без одежды
# =============================================================================
TIME_SCENES_INTIMATE = {
    "night": [
        "lying on bed, soft bedside lamp warm glow, dark cozy bedroom, messy hair, sleepy relaxed expression",
        "sitting on bed against headboard, single bedside lamp, dark room, phone in hand, tired look",
        "bedroom at night, tangled in sheets, lamp on nightstand, soft shadows, close shot",
    ],
    "morning": [
        "just woke up, soft morning window light, bedroom, messy hair, warm golden light, close shot",
        "sitting by window, morning sun streaming in, cozy bedroom, thoughtful expression",
        "lying in bed, morning light, rumpled sheets, natural light, soft focus",
    ],
    "day": [
        "sitting by window, natural daylight, cozy bedroom, thoughtful, close portrait",
        "cozy bedroom, soft natural light, lying on bed, relaxed, shallow depth of field",
        "warm afternoon light, bedroom, sitting on bed, natural pose",
    ],
    "evening": [
        "evening bedroom, warm lamp light, lying on bed, soft shadows, intimate atmosphere",
        "dim warm light, bedroom, sitting on bed, contemplative mood, close shot",
        "evening glow, bedroom, soft light from lamp, relaxed natural pose",
    ],
}

# =============================================================================
# Explicit-сцены (trust 6) — по типу запроса
# =============================================================================

# --- 1. Анус крупно, руки раздвигают ягодицы ---
SCENES_ANUS_SPREAD = [
    "on all fours on bed, (spreading ass cheeks with both hands:1.4), (anus close-up:1.5), (pink anus clearly visible:1.4), camera from directly behind, bedroom lamp light, detailed",
    "lying face down on bed, reaching back with both hands (spreading ass cheeks wide:1.4), (anus exposed close-up:1.5), soft lamp, detailed realistic",
    "kneeling on bed, bent forward, hands pulling apart ass cheeks, (anus hole visible:1.5), (anal close-up:1.4), from behind angle, warm light",
    "doggy position, (hands spreading buttocks wide:1.4), (anus clearly visible:1.5), (close-up of anus:1.4), camera zoomed in from behind, bedroom",
    "squatting, (hands pulling ass cheeks apart:1.4), (anus gaping slightly:1.3), (close-up spread anus:1.5), natural light, detailed",
    "bent over edge of bed, hands reaching back spreading cheeks, (anus pink and visible:1.5), (anal hole close-up:1.4), lamp light from side",
    "on knees face down, pulling ass cheeks apart with both hands, (tight pink anus visible:1.5), macro close-up from behind, detailed realistic skin",
    "lying on back, legs raised and spread, hands pulling ass cheeks apart, (anus visible:1.5), (close-up anus:1.4), overhead camera angle",
]

# --- 2. Дилдо в анусе ---
SCENES_DILDO_ANAL = [
    "(dildo inserted in anus:1.5), (anal dildo:1.4), dildo handle sticking out, on all fours on bed, ass up toward camera, bedroom lamp",
    "lying face down, (dildo penetrating anus:1.5), (anal penetration dildo:1.4), close-up from behind, dildo partially inserted, realistic",
    "kneeling, reaching back, (dildo in ass:1.5), (anal dildo visible:1.4), hand holding dildo, ass spread, warm bedroom light",
    "(thick dildo in anus:1.5), ass cheeks spread, (anal penetration:1.4), dildo half inserted, close-up from behind, detailed",
    "doggy position, (dildo in anus:1.5), (anal dildo penetration:1.4), hand pushing dildo in, close-up ass, realistic skin texture",
    "lying on side, (dildo inserted in anus:1.5), (anal toy:1.4), hand holding dildo base, close-up, lamp light, realistic",
    "squatting, sitting down on dildo, (dildo in ass:1.5), (anal insertion:1.4), side view, dildo fully inserted, realistic",
    "(butt plug in anus:1.4), (anal toy:1.5), hands spreading cheeks showing toy, close-up anus with plug, detailed realistic",
]

# --- 3. Дилдо в вагине ---
SCENES_DILDO_VAGINAL = [
    "lying on back, legs spread wide, (dildo inserted in vagina:1.5), (vaginal dildo:1.4), hand holding dildo base, close-up between legs, bedroom lamp",
    "(dildo in pussy:1.5), (vaginal penetration dildo:1.4), legs spread, dildo half inserted, close-up, realistic skin, natural light",
    "sitting on bed, legs apart, (dildo penetrating vagina:1.5), (masturbating with dildo:1.4), hand pushing dildo in, close-up",
    "kneeling on bed, (dildo in vagina:1.5), (pink dildo in pussy:1.4), holding dildo with both hands, thrusting, close-up genitals",
    "lying on back, knees bent up, (large dildo in pussy:1.5), (dildo penetration:1.4), pussy lips spread around dildo, close-up, detailed",
    "(dildo thrusting in vagina:1.5), (dildo in wet pussy:1.4), legs spread wide, close-up from between legs, glistening, realistic",
    "on all fours, (dildo inserted in pussy from behind:1.5), (vaginal dildo:1.4), hand holding dildo, close-up from behind, realistic",
    "sitting on dildo, (dildo fully inserted in vagina:1.5), (riding dildo:1.4), straddling, close-up side view, realistic",
]

# --- 4. Писает ---
SCENES_PEEING = [
    "squatting over toilet, (peeing:1.5), (urine stream:1.4), (pissing:1.4), close-up between legs, stream of urine, bathroom, realistic",
    "standing in shower, (peeing:1.5), (urine stream flowing:1.4), legs slightly apart, (piss stream:1.4), bathroom tiles, water",
    "squatting outdoors on grass, (peeing:1.5), (urine stream:1.4), close-up genitals, stream, realistic, natural light",
    "sitting on edge of bathtub, legs open, (peeing:1.5), (urine stream:1.4), close-up, bathroom light, realistic",
    "(golden shower:1.3), (peeing:1.5), (urine stream:1.4), squatting, close-up between legs, realistic skin",
    "lying on back, legs raised, (peeing:1.5), (urine stream arcing:1.4), close-up, bed, realistic",
    "squatting over drain, (pissing:1.5), (urine stream:1.4), bathroom floor, close-up genitals, realistic",
]

# --- 5. Влажная вагина / возбуждена ---
SCENES_WET_VAGINA = [
    "(wet pussy:1.5), (dripping vagina:1.4), (aroused:1.3), legs spread, close-up between legs, (vaginal fluid glistening:1.4), detailed",
    "close-up spread pussy, (wet glistening vagina:1.5), (dripping wet:1.4), legs wide apart, (aroused labia:1.3), macro, detailed skin",
    "(soaking wet pussy:1.5), (vaginal moisture:1.4), (glistening labia:1.3), lying on back legs spread, overhead close-up, realistic",
    "legs apart, (wet spread vagina:1.5), (moisture dripping:1.4), close-up macro, (excited glistening:1.3), warm lamp light, detailed",
    "(dripping wet aroused pussy:1.5), close-up, (vaginal fluid on labia:1.4), (wet pink vagina:1.3), legs spread wide, detailed realistic",
    "(very wet pussy:1.5), (fluid dripping down:1.4), (aroused glistening:1.3), lying on back, close-up between legs, detailed",
]

# --- 6. Сок из вагины / выделения ---
SCENES_VAGINAL_JUICE = [
    "(pussy juice dripping:1.5), (vaginal secretion:1.4), (creamy discharge:1.3), legs spread, close-up, (fluid running down:1.4), realistic",
    "close-up vagina, (pussy juice flowing:1.5), (vaginal fluid dripping:1.4), (cream dripping:1.3), spread legs, macro, detailed",
    "(vaginal cream dripping:1.5), (juicy wet pussy:1.4), (discharge running:1.3), lying on back, close-up, realistic skin",
    "(copious pussy juice:1.5), (dripping vaginal fluid:1.4), (creamy wet:1.3), spread labia, close-up macro, detailed realistic",
    "legs wide spread, (pussy juice running down:1.5), (vaginal secretion dripping:1.4), (wet and creamy:1.3), close-up, realistic",
    "close-up pussy, (thick vaginal discharge:1.4), (juice dripping from vagina:1.5), (creamy pussy:1.3), spread, detailed skin texture",
]

# --- 7. Двойной самотык / двойное проникновение ---
SCENES_DOUBLE_PENETRATION = [
    "(double penetration:1.5), (dildo in vagina and dildo in anus simultaneously:1.4), (double dildo:1.4), both holes filled, close-up from behind, realistic",
    "(double dildo:1.5), (one dildo in pussy one dildo in ass:1.4), (dp penetration:1.3), doggy position, both holes filled, realistic",
    "on all fours, (dildo in vagina:1.4) and (dildo in anus:1.4), (double penetration:1.5), close-up from behind, both inserted, realistic skin",
    "(double stuffed:1.5), (vaginal and anal dildo:1.4), (dp:1.3), lying on back legs raised, both holes filled, close-up, detailed",
    "squatting, (double dildo both holes:1.5), (vagina and anus filled:1.4), (double penetration close-up:1.3), side view, realistic",
    "(two dildos simultaneously:1.5), (anal and vaginal penetration:1.4), (double dp:1.3), doggy style, both holes stretched, realistic",
]

# --- 8. Пальчиком в анус ---
SCENES_ANAL_FINGER = [
    "on all fours, (finger inserted in anus:1.5), (anal fingering:1.4), (finger penetrating anus:1.4), hand reaching back, close-up from behind, detailed",
    "lying face down, (finger in ass:1.5), (anal finger penetration:1.4), hand reaching between legs fingering anus, close-up, lamp light",
    "doggy position, (fingering anus:1.5), (finger in anal hole:1.4), (anal stimulation:1.3), close-up from behind, realistic skin",
    "bent over, hand reaching back, (finger inserted into anus:1.5), (anal fingering:1.4), close-up, detailed realistic",
    "lying on back legs raised, (finger penetrating anus:1.5), (anal finger:1.4), (fingering ass hole:1.3), close-up between legs, lamp light",
    "(two fingers in anus:1.5), (double anal fingering:1.4), ass spread, close-up anus with fingers inside, from behind, realistic",
    "squatting, reaching between legs, (finger in anus:1.5), (anal fingering close-up:1.4), side angle, detailed realistic",
]

# --- 9. Мастурбация / пальчиком в вагину ---
SCENES_MASTURBATION = [
    "lying on back, legs spread, (fingering pussy:1.5), (masturbating:1.4), (fingers in vagina:1.4), hand between legs, close-up, bedroom lamp",
    "(rubbing clit:1.5), (masturbation:1.4), (fingers on pussy:1.4), legs spread wide, close-up between legs, glistening, detailed",
    "(two fingers in vagina:1.5), (fingering:1.4), (masturbating:1.3), lying on back, legs apart, close-up, hand moving, realistic",
    "sitting on bed legs spread, (hand rubbing pussy:1.5), (masturbation:1.4), (clitoral stimulation:1.3), close-up genitals, lamp light",
    "(fingers inside vagina:1.5), (vaginal fingering:1.4), (masturbating:1.3), knees bent, close-up between legs, wet, detailed realistic",
    "(rubbing wet pussy:1.5), (masturbating with fingers:1.4), legs spread, (aroused:1.3), close-up, glistening, natural light",
    "(circular motion on clit:1.5), (masturbation close-up:1.4), (fingers on vagina:1.3), lying on back, legs wide, detailed skin",
    "(three fingers in pussy:1.5), (deep fingering:1.4), (masturbating:1.3), close-up from between legs, wet glistening, realistic",
]

# --- 10. В ванне / душ на вагину ---
SCENES_SHOWER = [
    "(shower head aimed at vagina:1.5), (water stream on pussy:1.4), (shower masturbation:1.3), bathroom, standing in shower, legs apart, water flowing, realistic",
    "in bathtub, (shower head on pussy:1.5), (water jet on vagina:1.4), (hydro masturbation:1.3), legs spread over tub edge, bathroom light, wet body",
    "(water stream directly on clit:1.5), (shower on vagina:1.4), standing shower, legs apart, head back in pleasure, bathroom tiles, water flowing",
    "sitting in bathtub, (shower nozzle on pussy:1.5), (water jet masturbation:1.4), legs spread over sides of tub, close-up genitals, wet, bathroom",
    "(bath faucet on vagina:1.5), (water stream on pussy:1.4), lying in bathtub, legs spread over faucet, (water flow on clit:1.3), bathroom, wet",
    "in shower, (detachable shower head on pussy:1.5), (water jet:1.4), legs apart, (shower masturbation:1.3), water running down body, bathroom tiles",
    "(water pressure on vagina:1.5), (shower head masturbation:1.4), kneeling in shower, (water jet on clit:1.3), wet entire body, bathroom realistic",
]

# --- 11. Общий explicit (fallback) ---
SCENES_GENERAL_EXPLICIT = [
    "lying on bed, legs spread wide, (pussy visible:1.5), (vagina close-up:1.4), explicit, from above, bedroom lamp, detailed",
    "on all fours, (spreading ass cheeks:1.4), (anus visible:1.5), close-up from behind, explicit, bedroom",
    "lying on back, knees raised and spread, (vagina exposed:1.5), (explicit genitals:1.4), overhead camera, lamp light",
    "kneeling, legs spread, (spread pussy:1.5), (vagina and anus visible:1.4), explicit close-up, bedroom light",
    "doggy position, (ass and pussy from behind:1.5), (explicit close-up:1.4), spread legs, detailed realistic",
]

# Маппинг типа сцены → пул
EXPLICIT_SCENE_POOLS = {
    "anus_spread":          SCENES_ANUS_SPREAD,
    "dildo_anal":           SCENES_DILDO_ANAL,
    "dildo_vaginal":        SCENES_DILDO_VAGINAL,
    "peeing":               SCENES_PEEING,
    "wet_vagina":           SCENES_WET_VAGINA,
    "vaginal_juice":        SCENES_VAGINAL_JUICE,
    "double_penetration":   SCENES_DOUBLE_PENETRATION,
    "anal_finger":          SCENES_ANAL_FINGER,
    "masturbation":         SCENES_MASTURBATION,
    "shower":               SCENES_SHOWER,
    "general_explicit":     SCENES_GENERAL_EXPLICIT,
}

# =============================================================================
# Модификаторы и вспомогательные функции
# =============================================================================

TRUST_MODIFIERS = {
    0: "fully clothed, modest",
    1: "casual home clothes, relaxed",
    2: "relaxed intimate home setting",
    3: "intimate cozy atmosphere, close shot",
    4: "bare shoulders, cleavage, partially undressed, revealing",
    5: "topless, nude, bare breasts, bare skin",
    6: "nude, explicit, nsfw, uncensored, photorealistic, highly detailed genitals",
}


def _get_time_of_day(hour: int) -> str:
    if hour >= 22 or hour < 6:
        return "night"
    elif 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "day"
    else:
        return "evening"


def build_prompt(trust_level: int, hour: int, scene_type: str = None) -> tuple:
    """Возвращает (positive_prompt, negative_prompt) по trust_level, времени и типу сцены."""
    time_of_day = _get_time_of_day(hour)

    if trust_level >= 6:
        pool = EXPLICIT_SCENE_POOLS.get(scene_type, SCENES_GENERAL_EXPLICIT)
        scene = random.choice(pool)
        trust_mod = TRUST_MODIFIERS[6]
        negative = NEGATIVE_EXPLICIT
    elif trust_level >= 4:
        scene = random.choice(TIME_SCENES_INTIMATE[time_of_day])
        trust_mod = TRUST_MODIFIERS.get(trust_level, TRUST_MODIFIERS[5])
        negative = NEGATIVE_INTIMATE
    else:
        scene = random.choice(TIME_SCENES[time_of_day])
        trust_mod = TRUST_MODIFIERS.get(trust_level, TRUST_MODIFIERS[0])
        negative = NEGATIVE_SFW

    positive = f"{BASE}, {scene}, {trust_mod}, 8k, natural texture, shallow depth of field"
    return positive, negative


def _generate_sync(positive: str, negative: str, seed: int = None) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + TAMS_TOKEN,
    }
    if seed is None:
        seed = random.randint(0, 2 ** 32 - 1)

    body = {
        "requestId": str(int(time.time() * 1000)),
        "stages": [
            {
                "type": "INPUT_INITIALIZE",
                "inputInitialize": {"seed": seed, "count": 1},
            },
            {
                "type": "DIFFUSION",
                "diffusion": {
                    "width": 768,
                    "height": 1152,
                    "prompts": [{"text": positive}],
                    "negativePrompts": [{"text": negative}],
                    "sdModel": TAMS_BASE_MODEL,
                    "sdVae": "Automatic",
                    "sampler": "DPM++ 2S a Karras",
                    "steps": 25,
                    "cfgScale": 7,
                    "clipSkip": 2,
                    "lora": {
                        "items": [{"loraModel": TAMS_LORA_MODEL, "weight": 0.8}]
                    },
                },
            },
        ],
    }

    r = requests.post(TAMS_BASE_URL + "/v1/jobs", headers=headers, json=body, timeout=30)
    response = r.json()

    if "job" not in response:
        raise Exception("TAMS job creation failed: " + str(response))

    job_id = response["job"]["id"]

    for _ in range(60):
        time.sleep(3)
        status = requests.get(
            TAMS_BASE_URL + "/v1/jobs/" + job_id, headers=headers, timeout=30
        ).json()
        job_status = status.get("job", {}).get("status")

        if job_status == "SUCCESS":
            return status["job"]["successInfo"]["images"][0]["url"]
        elif job_status in ["FAILED", "CANCELLED"]:
            raise Exception("TAMS job failed: " + str(status))

    raise Exception("TAMS job timeout")


async def generate_photo(
    trust_level: int = 0,
    hour: int = None,
    custom_prompt: str = None,
    scene_type: str = None,
) -> str:
    if custom_prompt:
        positive = custom_prompt
        negative = NEGATIVE_SFW if trust_level < 4 else NEGATIVE_INTIMATE
    else:
        import datetime as _dt
        if hour is None:
            hour = _dt.datetime.now().hour
        positive, negative = build_prompt(trust_level, hour, scene_type=scene_type)
    print(f"[GEN] trust={trust_level} scene={scene_type}\nPOS: {positive[:120]}...")
    return await asyncio.to_thread(_generate_sync, positive, negative)


async def handle_photo_request(
    user_id: int, bot, trust_level: int = 0, scene_type: str = None
) -> None:
    import datetime as _dt
    hour = _dt.datetime.now().hour
    await asyncio.sleep(random.uniform(5, 15))
    await bot.send_chat_action(user_id, "upload_photo")
    await asyncio.sleep(random.uniform(3, 7))

    try:
        photo_url = await generate_photo(
            trust_level=trust_level, hour=hour, scene_type=scene_type
        )
        await bot.send_photo(user_id, photo_url)
    except Exception as e:
        print("Photo generation error: " + str(e))


# Оставляем для обратной совместимости с возможными импортами
PHOTO_TRIGGERS = [
    "пришли фото", "покажи себя", "как ты выглядишь",
    "покажи фото", "хочу увидеть тебя", "сфотографируйся",
    "покажись", "скинь фото", "отправь фото", "покажи как ты",
    "хочу твоё фото", "send photo", "show yourself",
]


def is_photo_request(text: str) -> bool:
    text_lower = text.lower()
    return any(trigger in text_lower for trigger in PHOTO_TRIGGERS)
