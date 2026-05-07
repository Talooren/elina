import fal_client
import os
import requests
from pathlib import Path

os.environ["FAL_KEY"] = "132fc180-0cae-42f1-8cda-e12d14f24fcf:0b546f28d815ec63eb32008c64ea29d6"

output_dir = Path("/root/elina/eyes/dataset_additions")
output_dir.mkdir(exist_ok=True)

prompts = [
    "portrait of young woman, ash blonde shoulder length hair, muted blue eyes, fair matte skin, thin ring on finger, sitting at desk by window, laptop open, soft natural daylight, cream knit sweater, looking at screen, 3/4 angle, photorealistic, analog film grain",
    "young woman, ash blonde hair, blue eyes, fair skin, lying on couch reading book, yellow book cover, grey oversized hoodie, warm lamp light, side profile, cozy apartment interior, photorealistic",
    "young woman, ash blonde hair, muted blue eyes, standing in small kitchen, holding white mug with both hands, morning light, no makeup, hair slightly messy, white t-shirt, soft shadows, eye level shot, photorealistic",
    "young woman, ash blonde shoulder length hair, blue eyes, sitting on windowsill, knees to chest, looking outside at rain, pensive expression, black oversized sweater, grey sky outside, low angle shot, photorealistic, film grain",
    "young woman, ash blonde hair, fair matte skin, thin ring, lying in bed, white sheets, morning light through curtains, eyes half open, no makeup, close up face shot, soft bokeh background, photorealistic",
    "young woman, ash blonde hair, blue eyes, sitting cross-legged on floor, grey cat nearby, wooden floor, afternoon light, beige knit sweater, looking down at cat with soft smile, top down angle, photorealistic",
    "young woman, ash blonde shoulder length hair, muted blue eyes, sitting alone in cafe, coffee cup on table, looking out window, black turtleneck, autumn light, slight side angle, candid style, photorealistic, film grain",
    "young woman, ash blonde hair, fair skin, thin ring, walking on empty street, autumn leaves, long beige coat, looking slightly down, candid shot from slight distance, overcast sky, photorealistic",
    "young woman, ash blonde hair, blue eyes, standing outside bookstore, holding small paper bag, light grey oversized jacket, paved street, soft cloudy light, 3/4 front angle, photorealistic",
    "young woman, ash blonde hair, muted blue eyes, sitting on park bench, earphones in, eyes closed, slight smile, black puffer jacket, autumn trees background, low angle, natural light, photorealistic",
    "extreme close up portrait, young woman, ash blonde hair, muted blue eyes with detail, fair matte skin, small imperfections, thin ring barely visible, no makeup, neutral expression, soft studio light, photorealistic, high detail",
    "young woman, ash blonde hair, back to camera, looking over shoulder, blue eyes, fair skin, black oversized sweater, home interior background blurred, over the shoulder shot, soft light, photorealistic",
    "young woman, ash blonde shoulder length hair, profile view, blue eyes, fair skin, sitting by window, looking outside, thoughtful expression, beige knit, natural side light, strict profile angle, photorealistic",
    "low angle shot looking up, young woman, ash blonde hair, muted blue eyes, fair skin, slight smile, cream sweater, indoor background, casual pose, photorealistic, film grain",
    "young woman, ash blonde hair, blue eyes, lying on stomach on bed, chin resting on hands, looking directly at camera, no makeup, white shirt, warm lamp light, intimate close angle, photorealistic",
]

negative = "blurry, deformed, ugly, bad anatomy, watermark, signature, extra fingers, bad hands, glowing eyes, oversaturated, plastic skin, makeup, jewelry except thin ring"

ok = 0
fail = 0

for i, prompt in enumerate(prompts):
    label = prompt[:60]
    print("Генерирую {}/15: {}...".format(i + 1, label), flush=True)
    try:
        result = fal_client.run(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "negative_prompt": negative,
                "image_size": "portrait_4_3",
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": False,
                "seed": 42 + i
            }
        )
        image_url = result["images"][0]["url"]
        resp = requests.get(image_url, timeout=30)
        filepath = output_dir / "elina_gen_{:02d}.jpg".format(i + 1)
        with open(filepath, "wb") as f:
            f.write(resp.content)
        print("  OK  Сохранено: {}".format(filepath), flush=True)
        ok += 1
    except Exception as e:
        print("  FAIL  Ошибка на {}: {}".format(i + 1, e), flush=True)
        fail += 1

print("\nИтого: {} успешно, {} ошибок".format(ok, fail))
print("Файлы в {}".format(output_dir))
