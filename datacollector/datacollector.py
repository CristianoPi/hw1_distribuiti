# #se chiamo due volte il valore di apple perchè ddevo fare due richiesta ad yfinance?
# import time
# import mysql.connector
# import yfinance as yf
# from circuit_breaker import CircuitBreaker

# circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

# def fetch_stock_price(ticker):
#     stock = yf.Ticker(ticker)
#     return stock.history(period="1d")['Close'].iloc[-1]

# def create_table_if_not_exists(cursor):
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS stock_prices (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             email VARCHAR(255) NOT NULL,
#             ticker VARCHAR(10) NOT NULL,
#             price DECIMAL(10, 2) NOT NULL,
#             timestamp DATETIME NOT NULL
#         )
#     """)

# def main():
#     conn = mysql.connector.connect(
#         host="db",
#         user="user",
#         password="password",
#         database="users"
#     )
#     cursor = conn.cursor()
    
#     #Mi assicuro che esistano le tabelle
#     create_table_if_not_exists(cursor)
    
#     while True:
#         cursor.execute("SELECT email, ticker FROM users")
#         users = cursor.fetchall()
#         print("Users fetched from database:", users)  # Stampa i risultati sulla console
#         for email, ticker in users:
#             try:
#                 price = circuit_breaker.call(fetch_stock_price, ticker)
#                 cursor.execute("INSERT INTO stock_prices (email, ticker, price, timestamp) VALUES (%s, %s, %s, NOW())",
#                             (email, ticker, price))
#                 conn.commit()
#                 print(f"Inserted data for {email}, {ticker}: {price}")  # Stampa i dettagli dell'inserimento
                
#             except Exception as e:
#                 print(f"Error fetching data for {ticker}: {e}")
#         time.sleep(60)

# if __name__ == "__main__":
#     main()

import time
import logging
import mysql.connector
import yfinance as yf
from circuit_breaker import CircuitBreaker

# Configura il logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

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
        
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED") #senza questo comando ogni operazione di lettura verrebbe fatta attraverso un snapshot del db ciò provocherebbe dei problemi nell'aggiornamento
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
            
            time.sleep(60)
    except mysql.connector.Error as db_err:
        logging.error(f"Database connection error: {db_err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    main()