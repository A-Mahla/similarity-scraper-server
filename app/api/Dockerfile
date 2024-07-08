FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5678