FROM python:3.12.7

WORKDIR /app

COPY . .

RUN pip install mysql-connector-python confluent_kafka prometheus_client

CMD ["python", "alert_system.py"]