FROM python:3.11

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    temporalio \
    pydantic \
    python-dotenv \
    asyncpg \
    structlog

# Copy shared packages
COPY packages/ ./packages/

# Copy app source
COPY apps/api-gateway/ ./apps/api-gateway/

WORKDIR /app/apps/api-gateway

ENV PYTHONPATH="/app:/app/packages/core-engine"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
