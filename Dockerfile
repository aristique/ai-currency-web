FROM python:3.12-slim-bookworm@sha256:6dd8b6dab6b3adc7812bab69eca5dbdc1a5cc690ad28306d234ffb4ef8ac9753 AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
WORKDIR /app
COPY src/ src/
COPY web/ web/

FROM base AS tests
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
COPY tests/ tests/
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]

FROM base AS app
USER 1000:1000
EXPOSE 8080
CMD ["python", "-m", "currency"]
