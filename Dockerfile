FROM python:3.13-slim

WORKDIR /code
COPY . .

RUN pip install uv
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
