FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

ENV DJANGO_SETTINGS_MODULE=webapp.settings.prod
RUN POSTGRES_DB=collectstatic POSTGRES_USER=collectstatic POSTGRES_PASSWORD=collectstatic \
    REDIS_URL=redis://localhost:6379/0 \
    python manage.py collectstatic --noinput

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "webapp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]