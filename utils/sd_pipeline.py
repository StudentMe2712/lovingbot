# Локальная генерация отключена, только cloud-генерация или заглушка

def generate_image_local(*args, **kwargs):
    raise NotImplementedError("Локальная генерация отключена на Railway")

def generate_image_sd3_local(*args, **kwargs):
    raise NotImplementedError("Локальная генерация SD3 отключена на Railway")

DEVICE = "cpu"

# --- Ниже весь старый код закомментирован для совместимости, чтобы не было ошибок ---
# MODEL_ID = "sd-legacy/stable-diffusion-v1-5"
#
# try:
#     pipe = StableDiffusionPipeline.from_pretrained(
#         MODEL_ID,
#         torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
#     )
#     pipe = pipe.to(DEVICE)
#     # Отключить NSFW-фильтр (на свой страх и риск)
#     pipe.safety_checker = lambda images, **kwargs: (images, False)
# except Exception:
#     pipe = None
#
# def generate_image_local(prompt: str):
#     if pipe is None:
#         raise NotImplementedError("Локальная генерация отключена на Railway")
#     image = pipe(prompt).images[0]
#     return image
#
# # --- SD3 ---
# SD3_MODEL_NAME = "stabilityai/stable-diffusion-3-medium-diffusers"
# SD3_DTYPE = torch.float16
# SD3_DEVICE = DEVICE
#
# def generate_image_sd3_local(prompt: str, output_filename: str = None):
#     print(f"Загрузка модели '{SD3_MODEL_NAME}' на устройство: {SD3_DEVICE} с типом данных {SD3_DTYPE}...")
#     try:
#         pipe3 = StableDiffusion3Pipeline.from_pretrained(
#             SD3_MODEL_NAME,
#             torch_dtype=SD3_DTYPE,
#         )
#         if SD3_DEVICE == "cuda":
#             pipe3.to(SD3_DEVICE)
#             pipe3.enable_model_cpu_offload()
#         else:
#             pipe3.to("cpu")
#             print("ВНИМАНИЕ: Запуск на CPU будет очень медленным.")
#         print("Модель успешно загружена. Начинаю генерацию изображения...")
#         image = pipe3(
#             prompt=prompt,
#             negative_prompt="lowres, low quality, worst quality, bad anatomy, bad art, blurry",
#             num_inference_steps=28,
#             height=1024,
#             width=1024,
#             guidance_scale=7.0,
#         ).images[0]
#         if output_filename:
#             image.save(output_filename)
#             print(f"Изображение успешно сохранено как '{output_filename}'")
#         return image
#     except Exception as e:
#         print(f"Произошла ошибка во время генерации изображения: {e}")
#         if "CUDA out of memory" in str(e):
#             print("\nВНИМАНИЕ: Ошибка нехватки VRAM (видеопамяти). Попробуйте включить offload или уменьшить размер модели.")
#         elif "Cannot load model" in str(e) or "access token" in str(e):
#             print("\nВНИМАНИЕ: Возможно, вы не приняли условия использования модели на Hugging Face или не вошли через 'huggingface-cli login'.")
#         elif "device" in str(e) and "cuda" in str(e) and "cpu" in str(e):
#             print("\nВНИМАНИЕ: Проверьте, что PyTorch установлен с поддержкой CUDA для вашей версии GPU, или установите DEVICE='cpu' если у вас нет NVIDIA GPU.")
#         return None 

import os
from huggingface_hub import InferenceClient
from io import BytesIO

client = InferenceClient(
    provider="nebius",
    api_key=os.environ["HUGGINGFACE_API_KEY"],
)

async def generate_postcard(prompt: str) -> bytes:
    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-schnell",
    )
    buf = BytesIO()
    image.save(buf, format='PNG')
    return buf.getvalue() 