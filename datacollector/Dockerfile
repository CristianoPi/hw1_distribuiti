FROM python:3.12.7

WORKDIR /app

COPY . .

RUN pip install mysql-connector-python yfinance circuitbreaker

CMD ["python", "datacollector.py"]