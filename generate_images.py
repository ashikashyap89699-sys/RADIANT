import os
import torch
import hashlib
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# ===================== SCRIPT SELECTION =====================
INPUT_DIR = "input"

def get_script_file():
    scripts = sorted(
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".txt")
    )
    if not scripts:
        raise FileNotFoundError("❌ No script found in input/")
    return os.path.join(INPUT_DIR, scripts[0])

SCRIPT_FILE = get_script_file()
print(f"📄 Using script: {SCRIPT_FILE}")
# ===========================================================

# ===================== CONFIG =====================
MODEL_ID = "stabilityai/sdxl-turbo"

OUTPUT_DIR = "images"
IMAGES_TXT = "images.txt"
AUDIO_FILE = "voice.mp3"

WIDTH = 1024
HEIGHT = 576

STEPS = 6
FIRST_GUIDANCE = 1.6
BASE_GUIDANCE = 1.3

IMAGE_DURATION = 10
MIN_IMAGES = 6
MAX_IMAGES = 15

FALLBACK_AUDIO_DURATION = 120
# =================================================

# ===================== PROMPTS =====================
FIRST_IMAGE_PROMPT = """
Single person portrait of Jack Ma,
one subject only,
Asian male entrepreneur,
real human face, correct facial proportions,
calm friendly expression,
soft warm studio lighting,
bright exposure,
professional photography,
clean plain background,
85mm lens, shallow depth of field,
photorealistic
"""

BASE_PROMPT = """
Single person portrait of Jack Ma,
one subject only,
Asian male entrepreneur,
real human face, correct facial proportions,
neutral calm expression,
professional studio photography,
soft lighting,
clean plain background,
85mm lens, shallow depth of field,
photorealistic
"""

PROMPT_VARIATIONS = [
    "half-body portrait, relaxed posture",
    "three-quarter angle, thoughtful pose",
    "soft side lighting, calm mood",
    "natural window light, minimal background",
    "studio rim lighting, professional look",
    "slight smile, confident presence",
    "neutral expression, steady gaze",
]

NEGATIVE_PROMPT = """
two faces, double face, merged face,
duplicate person, cloned face,
mirror, reflection, symmetrical face,
two heads, extra head,
twins, crowd, group, background people,
face overlap, ghost face,
cartoon, anime, illustration, painting, cgi,
extra limbs, extra fingers,
distorted face, deformed face,
blurry, low quality,
text, watermark, logo
"""
# ==================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

audio_duration_sec = None
if os.path.exists(AUDIO_FILE) and os.path.getsize(AUDIO_FILE) > 10_000:
    try:
        audio = AudioSegment.from_file(AUDIO_FILE)
        audio_duration_sec = len(audio) / 1000
    except CouldntDecodeError:
        pass

if audio_duration_sec is None:
    audio_duration_sec = FALLBACK_AUDIO_DURATION

TOTAL_IMAGES = int(audio_duration_sec // IMAGE_DURATION)
TOTAL_IMAGES = max(MIN_IMAGES, min(MAX_IMAGES, TOTAL_IMAGES))

if os.path.exists(AUDIO_FILE):
    with open(AUDIO_FILE, "rb") as f:
        BASE_SEED = int(hashlib.md5(f.read()).hexdigest()[:8], 16)
else:
    BASE_SEED = 12345678

pipe = StableDiffusionXLPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=dtype,
    use_safetensors=True
).to(device)

pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe.vae.enable_slicing()
pipe.enable_attention_slicing()

generated_files = []

for idx in range(1, TOTAL_IMAGES + 1):
    if idx == 1:
        prompt = FIRST_IMAGE_PROMPT
        guidance = FIRST_GUIDANCE
        seed = BASE_SEED
    else:
        prompt = BASE_PROMPT + "\n" + PROMPT_VARIATIONS[(idx - 2) % len(PROMPT_VARIATIONS)]
        guidance = BASE_GUIDANCE
        seed = BASE_SEED + idx

    gen = torch.Generator(device=device).manual_seed(seed)

    image = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE_PROMPT,
        num_inference_steps=STEPS,
        guidance_scale=guidance,
        width=WIDTH,
        height=HEIGHT,
        generator=gen
    ).images[0]

    fname = f"img_{idx:03d}.jpg"
    image.save(os.path.join(OUTPUT_DIR, fname), quality=92, subsampling=0)
    generated_files.append(fname)

with open(IMAGES_TXT, "w") as f:
    for i, img in enumerate(generated_files):
        f.write(f"file 'images/{img}'\n")
        if i < len(generated_files) - 1:
            f.write(f"duration {IMAGE_DURATION}\n")

print("✅ Images generated successfully")
