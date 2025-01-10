FROM python:3.12.7

WORKDIR /app

COPY . .

# Installa le dipendenze necessarie
RUN pip install mysql-connector-python yfinance circuitbreaker confluent_kafka prometheus_client

CMD ["python", "datacollector.py"]