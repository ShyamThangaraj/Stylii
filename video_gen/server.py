from flask import Flask, request, jsonify, Response, stream_template
from elevenlabs.client import ElevenLabs
import fal_client
import os
import json
import requests
import subprocess
import pathlib
import tempfile
import uuid
from PIL import Image
from google import genai
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import shutil
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Environment variables (same as original)
#os.environ["FAL_KEY"] = ""
#os.environ["ELEVENLABS_API_KEY"] = ""
#os.environ["GEMINI_API_KEY"] = ""
GOOGLE_KEY = os.environ["GEMINI_API_KEY"]
ELEVEN_KEY = os.environ["ELEVENLABS_API_KEY"]
FAL_KEY = os.environ["FAL_KEY"]

# Constants (same as original)
TARGET_WIDTH = 1920
TARGET_FPS = 30
CRF_QUALITY = "17"
X264_PRESET = "slow"

# Global storage for streaming progress
progress_store = {}
progress_lock = threading.Lock()

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

def update_progress(job_id, status, message, progress=None, result=None):
    with progress_lock:
        progress_store[job_id] = {
            'status': status,
            'message': message,
            'progress': progress,
            'result': result,
            'timestamp': time.time()
        }

def on_queue_update_factory(job_id):
    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                update_progress(job_id, 'processing', log["message"])
    return on_queue_update

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
    return "16:9" if w >= h else "9:16"

def task_gemini_and_tts(image_path, eleven_key, google_key, job_id, temp_dir):
    try:
        update_progress(job_id, 'processing', 'Generating narration with Gemini...', 25)

        client = genai.Client(api_key=google_key)
        prompt = ("You are a room tour expert. Describe this room and focus on the furniture/decor in ~3 engaging sentences (~10 seconds of speech).")
        img = Image.open(image_path)
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, img])
        narration_text = pick_text(resp).strip()

        update_progress(job_id, 'processing', f'Generated narration: {narration_text[:50]}...', 35)

        audio_path = temp_dir / "voiceover.mp3"
        update_progress(job_id, 'processing', 'Converting text to speech...', 45)

        eleven = ElevenLabs(api_key=eleven_key)
        audio_stream = eleven.text_to_speech.convert(
            text=narration_text,
            voice_id="onwK4e9ZLuTAKqWW03F9",
            model_id="eleven_v3",
            output_format="mp3_44100_128",
        )
        with open(audio_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        update_progress(job_id, 'processing', 'Audio generation completed', 55)
        return str(audio_path)
    except Exception as e:
        update_progress(job_id, 'error', f'Audio generation failed: {str(e)}')
        raise

def task_veo2_generate_and_download(image_path, job_id, temp_dir):
    try:
        update_progress(job_id, 'processing', 'Starting video generation with Veo2...', 10)

        aspect = image_aspect_choice(image_path)
        img_url = fal_client.upload_file(image_path)

        update_progress(job_id, 'processing', 'Image uploaded, generating video...', 15)

        result = fal_client.subscribe(
            "fal-ai/veo2/image-to-video",
            arguments={
                "prompt": "A 360° room tour showcasing the furniture and decor; camera at center panning around.",
                "image_url": img_url,
                "aspect_ratio": aspect,
                "duration": "8s",
            },
            with_logs=True,
            on_queue_update=on_queue_update_factory(job_id),
        )

        video_url = get_video_url(result)
        video_path = temp_dir / "veo2.mp4"

        update_progress(job_id, 'processing', 'Downloading generated video...', 60)

        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(video_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)

        update_progress(job_id, 'processing', 'Video download completed', 70)
        return str(video_path)
    except Exception as e:
        update_progress(job_id, 'error', f'Video generation failed: {str(e)}')
        raise

def audio_duration_seconds(path):
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, capture_output=True, text=True
    )
    return float(probe.stdout.strip())

def process_video_generation(image_path, job_id):
    try:
        update_progress(job_id, 'processing', 'Starting video generation process...', 0)

        # Create temporary directory for this job
        temp_dir = pathlib.Path(tempfile.mkdtemp())

        with ThreadPoolExecutor(max_workers=3) as ex:
            fut_video = ex.submit(task_veo2_generate_and_download, image_path, job_id, temp_dir)
            fut_audio = ex.submit(task_gemini_and_tts, image_path, ELEVEN_KEY, GOOGLE_KEY, job_id, temp_dir)

            video_path = fut_video.result()
            audio_path = fut_audio.result()

        update_progress(job_id, 'processing', 'Combining video and audio...', 80)

        # Exact trim to audio length
        aud_dur = audio_duration_seconds(audio_path)

        output_path = temp_dir / "final_with_audio_1080p.mp4"

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
            str(output_path),
        ]

        subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)

        update_progress(job_id, 'completed', 'Video generation completed successfully!', 100, {
            'output_path': str(output_path),
            'duration': aud_dur
        })

    except Exception as e:
        update_progress(job_id, 'error', f'Processing failed: {str(e)}')

@app.route('/generate', methods=['POST'])
def generate_video():
    """Non-streaming endpoint that returns the complete result"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Save uploaded image
        temp_dir = pathlib.Path(tempfile.mkdtemp())
        image_path = temp_dir / image_file.filename
        image_file.save(str(image_path))

        job_id = str(uuid.uuid4())

        # Process synchronously for non-streaming endpoint
        process_video_generation(str(image_path), job_id)

        # Get final result
        with progress_lock:
            final_result = progress_store.get(job_id, {})

        if final_result.get('status') == 'completed':
            return jsonify({
                'status': 'success',
                'job_id': job_id,
                'result': final_result.get('result'),
                'message': final_result.get('message')
            })
        else:
            return jsonify({
                'status': 'error',
                'job_id': job_id,
                'message': final_result.get('message', 'Unknown error occurred')
            }), 500

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/generate/stream', methods=['POST'])
def generate_video_stream():
    """Streaming endpoint that returns real-time progress updates"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Save uploaded image
        temp_dir = pathlib.Path(tempfile.mkdtemp())
        image_path = temp_dir / image_file.filename
        image_file.save(str(image_path))

        job_id = str(uuid.uuid4())

        # Start processing in background
        thread = threading.Thread(target=process_video_generation, args=(str(image_path), job_id))
        thread.start()

        def generate():
            yield f"data: {json.dumps({'job_id': job_id, 'status': 'started'})}\n\n"

            last_timestamp = 0
            while True:
                with progress_lock:
                    current_progress = progress_store.get(job_id, {})

                if current_progress and current_progress.get('timestamp', 0) > last_timestamp:
                    last_timestamp = current_progress.get('timestamp', 0)
                    yield f"data: {json.dumps(current_progress)}\n\n"

                    if current_progress.get('status') in ['completed', 'error']:
                        break

                time.sleep(0.5)  # Poll every 500ms

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get current status of a job"""
    with progress_lock:
        progress = progress_store.get(job_id)

    if not progress:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(progress)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ffmpeg_available': ffmpeg is not None,
        'ffprobe_available': ffprobe is not None
    })

if __name__ == '__main__':
    if not ffmpeg or not ffprobe:
        print("Warning: FFmpeg/ffprobe not found. Some functionality may not work.")

    app.run(debug=True, host='0.0.0.0', port=5001)
