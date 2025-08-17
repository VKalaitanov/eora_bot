FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "bot/bot.py"]
