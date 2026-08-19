# Build recipe for the attrition API image.
# See DEPLOY.md for how to build, run, and ship this to Cloud Run.

# "slim" keeps the image small by omitting build tools and docs. Python is
# pinned to 3.11 so the container never silently jumps to a new release that
# your dependencies haven't been tested against.
FROM python:3.11-slim

# Everything below lands in /app, and this is the working directory the app
# starts from. Chosen to match the "app.main:app" import path used by uvicorn.
WORKDIR /app

# Create an unprivileged account to run the server. Containers run as root by
# default, which means a bug in the app would have root inside the container -
# an unnecessary risk for a process that only needs to read a model file.
# -r makes it a system account (no home directory, no login shell).
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Dependencies are copied and installed BEFORE the application code, on purpose.
# Docker caches each step and only reruns those whose inputs changed, so editing
# a .py file reuses the cached install instead of re-downloading every package.
# Copying the code first would invalidate that cache on every single edit.
COPY requirements.txt .

# --no-cache-dir skips pip's download cache, which would otherwise be baked into
# the image as tens of MB that are never used again at runtime.
RUN pip install --no-cache-dir -r requirements.txt

# Now the parts that change often: the code, then the trained model.
COPY app ./app
COPY model_best.pkl .

# Drop privileges. Everything after this line runs as appuser, including the
# server itself. Placed after the COPY/RUN steps because those need root.
USER appuser

# Cloud Run (and Heroku, Railway, Fly) inject PORT and expect the app to honour it.
# The default keeps `docker run -p 8000:8000` working locally with no extra flags.
ENV PORT=8000

# Documentation only - EXPOSE advertises the port but does not publish it.
# Reaching the server still requires -p on `docker run`.
EXPOSE 8000

# Lets Docker distinguish "process is running" from "process is actually serving".
# Reads $PORT so it stays correct when the host overrides the port.
# Note: Cloud Run ignores HEALTHCHECK and runs its own probes instead.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://localhost:%s/health' % os.environ.get('PORT','8000'))" || exit 1

# --host 0.0.0.0 binds every interface. The default (127.0.0.1) would only accept
# connections from inside the container, making the service unreachable from the
# host even with -p correctly set.
# Shell form so ${PORT} expands; exec so uvicorn is PID 1 and gets SIGTERM for graceful shutdown.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
