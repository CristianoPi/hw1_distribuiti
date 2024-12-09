import time
import logging
import mysql.connector
from confluent_kafka import Producer
from circuit_breaker import CircuitBreaker

#non cambia quasi nulla notifichiamo solamente ad alert system quando aggiorniamo il tutto

# Configura il logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

# Configura il producer Kafka
conf = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'data_collector'
}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def fetch_stock_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")['Close'].iloc[-1]

def create_table_if_not_exists(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL,
            price FLOAT,
            timestamp TIMESTAMP
        )
    """)

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
                    price = circuit_breaker.call(fetch_stock_price, ticker)
                    results[ticker] = price
                    logging.info(f"Fetched data for {ticker}: {price}")
                except Exception as e:
                    logging.error(f"Error fetching data for {ticker}: {e}")
            
            for ticker, price in results.items():
                try:
                    logging.info(f"Inserting data into database for ticker: {ticker}, price: {price}")
                    cursor.execute("INSERT INTO stock_prices (ticker, price, timestamp) VALUES (%s, %s, NOW())",
                                   (ticker, price))
                    conn.commit()
                    logging.info(f"Inserted data for {ticker}: {price}")
                except Exception as e:
                    logging.error(f"Error inserting data for {ticker}: {e}")
            
            # Invia un messaggio a Kafka per notificare che il database è stato aggiornato
            producer.produce('AlertSystem', key='db_update', value='Database updated', callback=delivery_report)
            producer.flush()
            
            time.sleep(1800)
    except mysql.connector.Error as db_err:
        logging.error(f"Database connection error: {db_err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    main()