FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Wijzigt bij elke build (zie docker-compose.yml) zodat deze laag nooit uit de cache komt
# en yt-dlp bij elke rebuild naar de allernieuwste versie wordt geüpdatet.
ARG CACHEBUST=0
RUN echo "yt-dlp update trigger: ${CACHEBUST}" && pip install -U yt-dlp

COPY app.py index.html ./

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "2", "--threads", "4", "--timeout", "60", "app:app"]
