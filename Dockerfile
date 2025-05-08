FROM python:3.13.1-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv 
COPY requirements.txt requirements.txt
COPY . .

RUN uv pip install --system --no-cache-dir -r requirements.txt
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]