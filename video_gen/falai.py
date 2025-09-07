# --- your imports kept, plus a few extras for parallelism ---
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import fal_client
import os
import sys
from google import genai
from PIL import Image
import os, json, requests, subprocess, pathlib, sys, shutil, math
from PIL import Image
from google import genai
from elevenlabs.client import ElevenLabs
import fal_client
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
load_dotenv()

# --- DO NOT TOUCH (kept exactly as you wrote) ---
# os.environ["FAL_KEY"] = ""
# os.environ["ELEVENLABS_API_KEY"] = ""
# os.environ["GEMINI_API_KEY"] = ""
GOOGLE_KEY = os.environ["GEMINI_API_KEY"]
ELEVEN_KEY = os.environ["ELEVENLABS_API_KEY"]
FAL_KEY = os.environ["FAL_KEY"]

# ---------- Paths / constants ----------
WORKDIR = pathlib.Path.cwd()
AUDIO_PATH = WORKDIR / "voiceover.mp3"
VIDEO_PATH = WORKDIR / "veo2.mp4"
OUTPUT_PATH = WORKDIR / "final_with_audio_1080p.mp4"

TARGET_WIDTH = 1920     # upscale to 1080p; set 3840 for 4K if you want
TARGET_FPS = 30         # normalize output fps
CRF_QUALITY = "17"      # lower = higher quality; 17–20 is visually excellent
X264_PRESET = "slow"    # slower = better compression/quality per bitrate

# ---------- Utilities ----------
def which_or_common(name):
    exe = shutil.which(name)
    if exe: return exe
    common = [
        rf"C:\ffmpeg\bin\{name}.exe",
        rf"C:\Program Files\ffmpeg\bin\{name}.exe",
        rf"C:\Program Files (x86)\ffmpeg\bin\{name}.exe",
        rf"C:\Users\{os.environ.get('USERNAME','')}\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\{name}.exe",
    ]
    for p in common:
        if os.path.exists(p):
            return p
    return None

ffmpeg = which_or_common("ffmpeg")
ffprobe = which_or_common("ffprobe")
if not ffmpeg or not ffprobe:
    raise RuntimeError("FFmpeg/ffprobe not found. Install via: winget install -e --id Gyan.FFmpeg")

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(log["message"])

def get_video_url(res: dict) -> str:
    v = res.get("video")
    if isinstance(v, dict) and "url" in v:
        return v["url"]
    if isinstance(v, str):
        return v
    out = res.get("output")
    if isinstance(out, dict):
        vv = out.get("video")
        if isinstance(vv, dict) and "url" in vv: return vv["url"]
        if isinstance(vv, str): return vv
    if isinstance(out, list) and out:
        maybe = out[0].get("video")
        if isinstance(maybe, dict) and "url" in maybe: return maybe["url"]
        if isinstance(maybe, str): return maybe
    raise RuntimeError("No video URL found in FAL result: " + json.dumps(res)[:400])

def pick_text(r):
    if hasattr(r, "text") and r.text: return r.text
    if hasattr(r, "output_text") and r.output_text: return r.output_text
    try:
        return r.candidates[0].content.parts[0].text
    except Exception:
        raise RuntimeError("Could not extract text from Gemini response")

def image_aspect_choice(path):
    im = Image.open(path)
    w, h = im.size
    return "16:9" if w >= h else "9:16"   # match orientation (avoid letterboxing)

# ---------- Parallel tasks ----------
def task_gemini_and_tts(image_path, eleven_key, google_key):
    # 1) Gemini: narration (CPU/Net bound)
    client = genai.Client(api_key=google_key)
    prompt = ("You are a room tour expert. Describe this room and focus on the furniture/decor in ~3 engaging sentences (~10 seconds of speech).")
    img = Image.open(image_path)
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, img])
    narration_text = pick_text(resp).strip()
    print("Narration:", narration_text)

    # 2) ElevenLabs: stream TTS to file (starts ASAP while video is generating)
    eleven = ElevenLabs(api_key=eleven_key)
    audio_stream = eleven.text_to_speech.convert(
        text=narration_text,
        voice_id="onwK4e9ZLuTAKqWW03F9",
        model_id="eleven_v3",
        output_format="mp3_44100_128",
    )
    with open(AUDIO_PATH, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
    return str(AUDIO_PATH)

def task_veo2_generate_and_download(image_path):
    # Upload image & start Veo2 job (runs in parallel with Gemini/TTS)
    aspect = image_aspect_choice(image_path)
    img_url = fal_client.upload_file(image_path)
    result = fal_client.subscribe(
        "fal-ai/veo2/image-to-video",
        arguments={
            "prompt": "A 360° room tour showcasing the furniture and decor; camera at center panning around.",
            "image_url": img_url,
            "aspect_ratio": aspect,   # align with source
            "duration": "8s",         # max duration supported for img->video
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    video_url = get_video_url(result)

    # Download MP4
    with requests.get(video_url, stream=True) as r:
        r.raise_for_status()
        with open(VIDEO_PATH, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
    return str(VIDEO_PATH)

def audio_duration_seconds(path):
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, capture_output=True, text=True
    )
    return float(probe.stdout.strip())

# ---------- Orchestration ----------
def main(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    print(f"Processing image: {image_path}")

    with ThreadPoolExecutor(max_workers=3) as ex:
        fut_video = ex.submit(task_veo2_generate_and_download, image_path)
        fut_audio = ex.submit(task_gemini_and_tts, image_path, ELEVEN_KEY, GOOGLE_KEY)

        # Wait for both to finish (they overlap)
        video_path = fut_video.result()
        audio_path = fut_audio.result()
        print("Assets ready:", video_path, audio_path)

    # Exact trim to audio length
    aud_dur = audio_duration_seconds(audio_path)

    # High-quality upscale + loop video until audio ends
    # - scale to 1080p width with lanczos, keep aspect via -2
    # - fps normalize; re-encode with CRF for quality
    # - stream_loop -1 repeats video; -t cuts to audio duration
    vf = f"fps={TARGET_FPS},scale={TARGET_WIDTH}:-2:flags=lanczos"
    ffmpeg_cmd = [
        ffmpeg, "-y",
        "-stream_loop", "-1", "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0",
        "-t", f"{aud_dur:.3f}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", X264_PRESET, "-crf", CRF_QUALITY,
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "224k",
        "-movflags", "+faststart",
        str(OUTPUT_PATH),
    ]

    try:
        res = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
        print("Muxed & upscaled:", OUTPUT_PATH)
    except subprocess.CalledProcessError as e:
        print("ffmpeg failed:", e.returncode, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fallai.py <image_path>")
        print("Example: python fallai.py 'C:/path/to/room/image.jpg'")
        sys.exit(1)

    image_path = sys.argv[1]
    main(image_path)
