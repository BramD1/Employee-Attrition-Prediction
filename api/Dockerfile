FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY model_best.pkl .

USER appuser

# Cloud Run (and Heroku, Railway, Fly) inject PORT and expect the app to honour it.
ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://localhost:%s/health' % os.environ.get('PORT','8000'))" || exit 1

# Shell form so ${PORT} expands; exec so uvicorn is PID 1 and gets SIGTERM for graceful shutdown.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
