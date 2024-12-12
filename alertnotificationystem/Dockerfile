FROM python:3.12.7

WORKDIR /app

COPY . .

RUN pip install confluent_kafka

RUN apt-get update && apt-get install -y \
    ssmtp \
    && rm -rf /var/lib/apt/lists/*

CMD ["python", "alert_notification_system.py"]