# Completely Random YT Video Searcher

Find a truly random YouTube video about any game, without the recommendation algorithm getting in the way.

Type in a game name, pick a mode, and the app digs up a random video for it. You can watch it in an embedded player on the page or open it in a new tab. Everything runs in a single Docker container on one port, with no YouTube API key required.

## Features

- **Random video for any game**: enter a game name and get one random result out of 20 search hits.
- **Algorithm bypass**: your game name is combined with a random search modifier behind the scenes, so you don't get the usual popular results.
- **Two modes**:
  - **Normal**: appends a random 2 to 4 character combination of letters and digits (for example `Minecraft k3x`).
  - **Raw / 0-views**: appends default file names of recording software, such as `IMG_`, `OBS`, `VID_`, `replay` (also `MOV_`, `Desktop`, `Screen Recording`), optionally followed by a number, or a year between 2008 and 2026. This tends to surface obscure, barely watched videos.
- **Watch right away**: play the video in an embedded player or open it in a new browser tab.
- **Fast**: uses `yt-dlp` with `extract_flat=True`, so nothing is downloaded and only search metadata is fetched.
- **No API keys**: no YouTube Data API needed.
- **One container, one port**: the Flask backend also serves the frontend.
- **Self-healing builds**: the Docker image always installs the latest `yt-dlp` on rebuild, so YouTube blocks are fixed by simply rebuilding.

## Quick start

### Requirements

- [Docker](https://docs.docker.com/get-docker/) with the Compose plugin (`docker compose`)

### Run it

```bash
git clone https://github.com/VulcanoSoftware/completely-random-yt-video-searcher.git
cd completely-random-yt-video-searcher
CACHEBUST=$(date +%s) docker compose up --build -d
```

Then open <http://localhost:8000> in your browser.

> `CACHEBUST` makes sure the `yt-dlp` update step is never taken from Docker's build cache, so you always get the newest version.

### Stop it

```bash
docker compose down
```

## How to use

1. Open <http://localhost:8000>.
2. Enter a **game name**, for example `Euro Truck Simulator 2`.
3. Choose a **mode**:
   - **Normal** for a random video that is still fairly findable.
   - **Raw / 0-views** for obscure, unedited footage.
4. Click **Zoek willekeurige video** ("Search random video", or press Enter).
5. When a video is found, you can:
   - click **Speel hier af** ("Play here") to watch it in the embedded player,
   - click **Open in nieuw tabblad** ("Open in new tab") to open it on YouTube,
   - click **Nog een** ("Another one") to roll again with a new random modifier.

> The interface is currently in Dutch; the English meaning of each button is given above.

The page also shows the title, channel, view count, duration and the exact search query that was used.

## Updating `yt-dlp`

YouTube changes often, and `yt-dlp` has to keep up. If searches start failing, rebuild the image to pull the latest version:

```bash
CACHEBUST=$(date +%s) docker compose up --build -d
```

## Configuration

| Setting | Default | Description |
| --- | --- | --- |
| Host port | `8000` | Change the left side of `"8000:8000"` in `docker-compose.yml`, for example `"3000:8000"`. |
| `PORT` | `8000` | Port the app listens on when started directly with `python app.py`. |

## API

The frontend talks to a small JSON API that you can also call yourself.

### `GET /api/random`

| Query parameter | Required | Description |
| --- | --- | --- |
| `game` | yes | Name of the game to search for. |
| `mode` | no | `normal` (default) or `raw`. |

Example:

```bash
curl "http://localhost:8000/api/random?game=Minecraft&mode=raw"
```

Response:

```json
{
  "id": "VIDEO_ID",
  "title": "Video title",
  "channel": "Channel name",
  "views": 12,
  "duration": 184,
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "query": "Minecraft OBS0421"
}
```

Errors return JSON with an `error` field: `400` for a missing game name, `404` when nothing was found, and `502` when `yt-dlp` fails.

### `GET /health`

Returns the service status and the installed `yt-dlp` version.

## Running without Docker

You need Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app is then available on <http://localhost:8000>.

## Project structure

```
.
├── app.py               # Flask backend: search logic, API and static frontend serving
├── index.html           # Frontend (HTML, CSS and JavaScript in one file)
├── requirements.txt     # Python dependencies (Flask, gunicorn, yt-dlp)
├── Dockerfile           # Image build, always updates yt-dlp
└── docker-compose.yml   # One-command startup
```

## How it works

1. The frontend sends the game name and mode to `/api/random`.
2. The backend builds a query: `<game name> <random modifier>`.
3. `yt-dlp` runs `ytsearch20:<query>` in flat mode and returns 20 results without downloading anything.
4. One result is picked at random and returned to the frontend.
5. If a query returns no results, the backend retries with a new modifier (up to 3 attempts).

## Troubleshooting

- **"Search failed" errors**: `yt-dlp` is probably outdated or YouTube is blocking requests. Rebuild with `CACHEBUST=$(date +%s) docker compose up --build -d`.
- **The embedded player shows an error**: some uploaders disable embedding. Use **Open in new tab** instead.
- **Port 8000 is already in use**: change the host port in `docker-compose.yml`.
- **Raw mode doesn't always return 0-view videos**: the modifiers only imitate default file names, so a low view count is likely but not guaranteed.

## Disclaimer

This project is not affiliated with YouTube or Google. Videos are random and unfiltered, so the content is not moderated.
