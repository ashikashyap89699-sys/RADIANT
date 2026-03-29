import os
import subprocess

# ===================== SCRIPT SELECTION =====================
INPUT_DIR = "input"

def get_script_file():
    scripts = sorted(
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".txt")
    )
    if not scripts:
        return None
    return os.path.join(INPUT_DIR, scripts[0])

SCRIPT_FILE = get_script_file()
print(f"📄 Using script: {SCRIPT_FILE}")
# ===========================================================

# ---------------- CONFIG ----------------
IMAGES_DIR = "images"
OUTPUT_DIR = "output"
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "final_video.mp4")

IMAGE_DURATION = 4
FPS = 30
# --------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

input_pattern = os.path.join(IMAGES_DIR, "img_%03d.jpg")

cmd = [
    "ffmpeg",
    "-y",
    "-framerate", f"1/{IMAGE_DURATION}",
    "-i", input_pattern,
    "-vf", "scale=1920:1080:flags=lanczos",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-r", str(FPS),
    OUTPUT_VIDEO
]

print("Creating video...")
subprocess.run(cmd, check=True)
print("✅ VIDEO CREATED:", OUTPUT_VIDEO)

# ===================== CLEANUP =====================
if SCRIPT_FILE and os.path.exists(OUTPUT_VIDEO):
    if os.path.exists(SCRIPT_FILE):
        os.remove(SCRIPT_FILE)
        print(f"🗑 Deleted used script: {SCRIPT_FILE}")
