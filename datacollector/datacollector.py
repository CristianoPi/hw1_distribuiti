import time
import logging
import mysql.connector
import yfinance as yf
from confluent_kafka import Producer, KafkaError
from circuit_breaker import CircuitBreaker
from prometheus_client import start_http_server, Gauge, Counter

# Configura il logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

response_time_gauge = Gauge('response_time_seconds', 'Response time of fetching stock price', ['service', 'node'])
request_counter = Counter('total_requests', 'Total number of requests', ['service', 'node'])
error_counter = Counter('total_errors', 'Total number of errors', ['service', 'node'])

# Configura il producer Kafka
conf = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'datacollector'
}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
        error_counter.labels(service='datacollector', node='worker').inc()
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def fetch_stock_price(ticker):
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        response_time = time.time() - start_time
        response_time_gauge.labels(service='datacollector', node='worker').set(response_time)
        return price
    except Exception as e:
        logging.error(f"Error fetching stock price for {ticker}: {e}")
        error_counter.labels(service='datacollector', node='worker').inc()
        raise

def create_table_if_not_exists(cursor):
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                price FLOAT,
                timestamp TIMESTAMP
            )
        """)
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        error_counter.labels(service='datacollector', node='worker').inc()
        raise

def main():
    try:
        logging.info("Connecting to the database...")
        conn = mysql.connector.connect(
            host="db",
            user="user",
            password="password",
            database="users"
        )
        cursor = conn.cursor()
        logging.info("Connected to the database.")
        
        # Mi assicuro che esistano le tabelle
        logging.info("Creating table if not exists...")
        create_table_if_not_exists(cursor)
        logging.info("Table check/creation done.")
        
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        while True:
            logging.info("Fetching tickers from database...")
            cursor.execute("SELECT DISTINCT ticker FROM users")
            tickers = cursor.fetchall()
            logging.info(f"Tickers fetched from database: {tickers}")
            
            results = {}
            for (ticker,) in tickers:
                try:
                    logging.info(f"Fetching data for ticker: {ticker}")
                    request_counter.labels(service='datacollector', node='worker').inc()
                    price = circuit_breaker.call(fetch_stock_price, ticker)
                    results[ticker] = price
                    logging.info(f"Fetched data for {ticker}: {price}")
                except Exception as e:
                    logging.error(f"Error fetching data for {ticker}: {e}")
                    error_counter.labels(service='datacollector', node='worker').inc()
            inserted = False
            for ticker, price in results.items():
                try:
                    logging.info(f"Inserting data into database for ticker: {ticker}, price: {price}")
                    cursor.execute("INSERT INTO stock_prices (ticker, price, timestamp) VALUES (%s, %s, NOW())",
                                   (ticker, price))
                    conn.commit()
                    logging.info(f"Inserted data for {ticker}: {price}")
                    inserted=True
                except Exception as e:
                    logging.error(f"Error inserting data for {ticker}: {e}")
                    error_counter.labels(service='datacollector', node='worker').inc()
            if inserted:
                # Invia un messaggio a Kafka per notificare che il database è stato aggiornato
                max_retries = 3
                retries = 0
                while retries < max_retries:
                    try:
                        producer.produce('AlertSystem', key='db_update', value='Database updated', callback=delivery_report)
                        producer.flush()
                        break  # Esce dal ciclo se produce è successo
                    except KafkaError as e:
                        retries += 1
                        logging.error(f"Produce failed: {e}. Retrying ({retries}/{max_retries})...")
                        time.sleep(2)  # Attende prima di riprovare

            time.sleep(60)
    
    except mysql.connector.Error as db_err:
        logging.error(f"Database connection error: {db_err}")
        error_counter.labels(service='datacollector', node='worker').inc()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        error_counter.labels(service='datacollector', node='worker').inc()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    # Avvia il server HTTP di Prometheus sulla porta 8000
    start_http_server(8000)
    main()