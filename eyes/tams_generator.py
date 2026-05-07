import time, json, requests
from pathlib import Path

TOKEN = "710d872b-5799-4a49-94a6-52edb1c551ac"
BASE_URL = "https://ap-east-1.tensorart.cloud"
BASE_MODEL_ID = "879130987013876797"
LORA_MODEL_ID = "984264758779731123"

def generate_photo(prompt, seed=2380530673, output_path=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + TOKEN
    }
    body = {
        "requestId": str(int(time.time() * 1000)),
        "stages": [
            {
                "type": "INPUT_INITIALIZE",
                "inputInitialize": {"seed": seed, "count": 1}
            },
            {
                "type": "DIFFUSION",
                "diffusion": {
                    "width": 768,
                    "height": 1152,
                    "prompts": [{"text": prompt}],
                    "negativePrompts": [],
                    "sdModel": BASE_MODEL_ID,
                    "sdVae": "Automatic",
                    "sampler": "DPM++ 2S a Karras",
                    "steps": 20,
                    "cfgScale": 10,
                    "clipSkip": 2,
                    "lora": {
                        "items": [{"loraModel": LORA_MODEL_ID, "weight": 0.8}]
                    }
                }
            }
        ]
    }
    print("Отправляю запрос...")
    r = requests.post(BASE_URL + "/v1/jobs", headers=headers, json=body)
    print("Статус: " + str(r.status_code))
    response = r.json()
    print("Ответ:", json.dumps(response, indent=2))
    if "job" not in response:
        print("Ошибка:", response)
        return None
    job_id = response["job"]["id"]
    print("Job ID: " + job_id)
    for _ in range(60):
        time.sleep(3)
        status = requests.get(BASE_URL + "/v1/jobs/" + job_id, headers=headers).json()
        job_status = status.get("job", {}).get("status")
        print("Статус: " + str(job_status))
        if job_status == "SUCCESS":
            image_url = status["job"]["successInfo"]["images"][0]["url"]
            print("URL: " + image_url)
            if output_path:
                img_data = requests.get(image_url).content
                Path(output_path).write_bytes(img_data)
                print("Сохранено: " + output_path)
            return image_url
        elif job_status in ["FAILED", "CANCELLED"]:
            print("Провалилось:", status)
            return None
    print("Таймаут")
    return None

if __name__ == "__main__":
    Path("/root/elina/eyes/tams_tests").mkdir(exist_ok=True)
    prompts = [
        ("elina_woman, photorealistic, analog style, portrait of young woman sitting in cafe, black turtleneck, ash hair, blue eyes, fair skin, no makeup, soft window light, 8k, natural texture", "cafe"),
        ("elina_woman, photorealistic, analog style, young woman sitting by window, cream knit oversized sweater, morning light, cozy apartment, ash hair, blue eyes, fair skin, 8k", "home_window"),
        ("elina_woman, photorealistic, analog style, close up portrait, young woman looking at camera, soft natural light, ash hair, blue eyes, fair matte skin, no makeup, 8k", "closeup"),
    ]
    for prompt, name in prompts:
        print("Генерирую: " + name + "...")
        result = generate_photo(prompt=prompt, seed=2380530673, output_path="/root/elina/eyes/tams_tests/" + name + ".jpg")
        if result:
            print("Успех: " + name)
        time.sleep(2)
    print("Готово!")
