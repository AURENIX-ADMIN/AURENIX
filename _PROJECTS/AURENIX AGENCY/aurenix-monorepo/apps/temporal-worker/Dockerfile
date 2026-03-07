FROM python:3.11

WORKDIR /app

# Install dependencies directly to avoid Poetry overhead/resolution issues in Docker
RUN pip install --no-cache-dir \
    temporalio \
    browser-use \
    langchain-google-vertexai \
    langchain-google-genai \
    asyncpg \
    structlog \
    pydantic \
    python-dotenv

# Copy shared packages
COPY packages/ ./packages/

# Copy app source
COPY apps/temporal-worker/ ./apps/temporal-worker/

WORKDIR /app/apps/temporal-worker

# Ensure the packages are in PYTHONPATH if needed
ENV PYTHONPATH="/app:/app/packages/core-engine:/app/packages/integrations"

CMD ["python", "-m", "src.worker"]
