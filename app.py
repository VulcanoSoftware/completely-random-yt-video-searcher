import os
import random
import string
from pathlib import Path

import yt_dlp
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)

RAW_PREFIXES = ["IMG_", "OBS", "VID_", "replay", "MOV_", "Desktop", "Screen Recording"]
YDL_OPTS = {
    "extract_flat": True,   # niets downloaden, alleen metadata van de zoekresultaten
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "socket_timeout": 15,
}


def random_modifier(mode: str) -> str:
    if mode == "raw":
        choice = random.choice(["prefix", "prefix_num", "year"])
        if choice == "year":
            return str(random.randint(2008, 2026))
        prefix = random.choice(RAW_PREFIXES)
        if choice == "prefix_num":
            return f"{prefix}{random.randint(0, 9999):04d}"
        return prefix
    length = random.randint(2, 4)
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def search_random_video(game: str, mode: str, attempts: int = 3):
    for _ in range(attempts):
        modifier = random_modifier(mode)
        query = f"{game} {modifier}"
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch20:{query}", download=False)
        entries = [e for e in (info or {}).get("entries", []) if e and e.get("id")]
        if entries:
            video = random.choice(entries)
            return {
                "id": video["id"],
                "title": video.get("title"),
                "channel": video.get("channel") or video.get("uploader"),
                "views": video.get("view_count"),
                "duration": video.get("duration"),
                "url": f"https://www.youtube.com/watch?v={video['id']}",
                "query": query,
            }
    return None


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/api/random")
def api_random():
    game = (request.args.get("game") or "").strip()
    mode = request.args.get("mode", "normal")
    if not game:
        return jsonify(error="Geef een gamenaam op."), 400
    if mode not in ("normal", "raw"):
        mode = "normal"
    try:
        video = search_random_video(game, mode)
    except Exception as exc:  # yt-dlp kan om vele redenen falen (netwerk, blokkade, ...)
        return jsonify(error=f"Zoeken mislukt: {exc}"), 502
    if not video:
        return jsonify(error="Geen resultaten gevonden, probeer opnieuw."), 404
    return jsonify(video)


@app.get("/health")
def health():
    return jsonify(status="ok", yt_dlp=yt_dlp.version.__version__)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
