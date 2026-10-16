FROM python:3.12-alpine

# Links this image to the Git repository so GITHUB_TOKEN can create the GHCR package.
ARG IMAGE_SOURCE="https://github.com/ramneek3/taskboard"
LABEL org.opencontainers.image.source="${IMAGE_SOURCE}" \
      org.opencontainers.image.description="TaskBoard API"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOME=/tmp

WORKDIR /app

RUN apk upgrade --no-cache \
    && adduser -D -u 10001 -h /home/appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini alembic.ini
COPY alembic alembic
COPY app app
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 755 /usr/local/bin/docker-entrypoint.sh \
    && chown -R appuser:appuser /app

USER 10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
