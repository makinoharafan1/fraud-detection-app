FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src /app/src

ENV PYTHONPATH=/app/src
