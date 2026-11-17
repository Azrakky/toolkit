from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, threading, webbrowser, subprocess, sys, shutil, re, uuid, time
from urllib.parse import urlsplit
from urllib.parse import urlparse

# Constants and global variables
BASE = Path(__file__).resolve().parent
FRONTEND = BASE / "frontend"
SETTINGS = BASE / "settings.json"
PORT = 3000
JOBS = {}
JOBS_LOCK = threading.Lock()
MAX_JOBS = 100

def allowed_url(value):
    try:
        u = urlsplit(value)
        return u.scheme == "https" and (u.hostname or "").lower() in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"} and bool(u.path.strip("/")) and not u.username and not u.password and not u.port
    except ValueError:
        return False

def dependency_status():
    try:
        check = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], capture_output=True, text=True, timeout=8)
        ytdlp = check.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        ytdlp = False
    return {"yt_dlp": ytdlp, "ffmpeg": shutil.which("ffmpeg") is not None}

def update_job(job_id, **values):
    with JOBS_LOCK:
        JOBS[job_id].update(values)

def run_conversion(job_id, url, fmt, quality, folder):
    out = str(folder / "%(title).180B [%(id)s].%(ext)s")
    cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "--newline", "--no-overwrites", "--restrict-filenames", "--windows-filenames", "--max-filesize", "2G", "--print", "after_move:FILE:%(filepath)s", "-o", out]
    if fmt == "mp3":
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    else:
        height = {"best": "1080", "720": "720", "480": "480"}[quality]
        cmd += ["-f", f"bv*[height<={height}]+ba/b[height<={height}]/best", "--merge-output-format", "mp4", "--recode-video", "mp4"]
    cmd += ["--", url]
    try:
        update_job(job_id, status="running", message="Downloading…")
        last = []
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        for raw in proc.stdout:
            line = raw.strip()
            if not line: continue
            if line.startswith("FILE:"):
                update_job(job_id, file=Path(line[5:]).name)
            m = re.search(r"\[download\]\s+([\d.]+)%", line)
            if m: update_job(job_id, progress=min(99, float(m.group(1))), message="Downloading…")
            elif "[ExtractAudio]" in line: update_job(job_id, message="Converting to MP3…")
            elif "[VideoConvertor]" in line or "[Merger]" in line: update_job(job_id, message="Processing MP4…")
            last.append(line[:300]); last = last[-8:]
        code = proc.wait()
        if code == 0: update_job(job_id, status="complete", progress=100, message="Saved to " + str(folder))
        else: update_job(job_id, status="failed", message="Conversion failed. " + " ".join(last)[-700:])
    except Exception as exc:
        update_job(job_id, status="failed", message=f"Could not run converter: {exc}")

GADGETS = [
    {"id": "connection-test", "name": "Backend Connection Test", "description": "Verify that the dashboard can communicate with Python.", "status": "ready"},
    {"id": "video-converter", "name": "Video Converter", "description": "Download and convert authorized YouTube videos to MP3 / MP4.", "status": "ready"},
    {"id": "pdf-toolkit", "name": "PDF Toolkit", "description": "PDF utilities (planned).", "status": "planned"},
]

def read_settings():
    defaults = {"display_name": "UtilityHub", "download_folder": str(Path.home() / "Downloads")}
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
        return {**defaults, **{k: v for k, v in data.items() if k in defaults and isinstance(v, str)}}
    except (OSError, ValueError):
        return defaults

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/health":
            return self.respond(200, {"ok": True, "app": "UtilityHub", "version": "0.3", "backend": "Python standard library"})
        if route == "/api/gadgets":
            return self.respond(200, {"gadgets": GADGETS})
        if route == "/api/settings":
            return self.respond(200, read_settings())
        if route == "/api/converter/dependencies":
            return self.respond(200, dependency_status())
        if route.startswith("/api/converter/jobs/"):
            job_id = route.rsplit("/", 1)[-1]
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                return self.respond(200, dict(job)) if job else self.respond(404, {"error": "Job not found"})
        if route.startswith("/api/"):
            return self.respond(404, {"error": "Unknown API endpoint"})
        return super().do_GET()

    def do_POST(self):
        route = urlparse(self.path).path
        if route not in ("/api/settings", "/api/gadgets/connection-test", "/api/converter/start"):
            return self.respond(404, {"error": "Unknown API endpoint"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 <= size <= 8192:
                return self.respond(413, {"error": "Request too large"})
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Expected an object")
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": "Invalid JSON"})
        if route.endswith("connection-test"):
            return self.respond(200, {"ok": True, "message": "Dashboard → Python backend → Dashboard: successful!"})
        if route == "/api/converter/start":
            url, fmt, quality = data.get("url"), data.get("format"), data.get("quality", "best")
            if not isinstance(url, str) or len(url) > 2048 or not allowed_url(url):
                return self.respond(400, {"error": "Enter a valid HTTPS YouTube video URL."})
            if fmt not in ("mp3", "mp4") or quality not in ("best", "720", "480"):
                return self.respond(400, {"error": "Invalid format or quality."})
            deps = dependency_status()
            if not deps["yt_dlp"] or not deps["ffmpeg"]:
                return self.respond(409, {"error": "Missing dependencies: " + ", ".join(k for k,v in deps.items() if not v) + ". See setup instructions."})
            folder = Path(read_settings()["download_folder"]).expanduser()
            try:
                folder.mkdir(parents=True, exist_ok=True)
                if not folder.is_dir(): raise OSError("Not a folder")
            except OSError as exc:
                return self.respond(400, {"error": "Cannot use download folder: " + str(exc)})
            with JOBS_LOCK:
                if sum(j["status"] in ("queued", "running") for j in JOBS.values()) >= 2:
                    return self.respond(429, {"error": "Two conversions are already running. Please wait."})
                if len(JOBS) >= MAX_JOBS:
                    for key in list(JOBS):
                        if JOBS[key]["status"] not in ("queued", "running"):
                            del JOBS[key]
                            break
                job_id = uuid.uuid4().hex
                JOBS[job_id] = {"id": job_id, "status": "queued", "progress": 0, "message": "Queued", "file": ""}
            threading.Thread(target=run_conversion, args=(job_id,url,fmt,quality,folder), daemon=True).start()
            return self.respond(202, {"id": job_id})
        allowed = ("display_name", "download_folder")
        if any(k not in allowed or not isinstance(v, str) or len(v) > 500 for k, v in data.items()):
            return self.respond(400, {"error": "Invalid settings"})
        settings = {**read_settings(), **data}
        SETTINGS.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        return self.respond(200, {"ok": True, "settings": settings})

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 3000))

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)

    print(f"UtilityHub running on port {port}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        
# if __name__ == "__main__":
#     try:
#         server = ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", PORT))), Handler)
#     except OSError as exc:
#         print(f"Unable to start UtilityHub on port {PORT}: {exc}", flush=True)
#         raise SystemExit(1)
#     print(f"UtilityHub v0.3 running at http://localhost:{PORT}", flush=True)
#     if not os.environ.get("RAILWAY_ENVIRONMENT"):

#         threading.Timer(1, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
#     try:
#         server.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     finally:
#         server.server_close()
