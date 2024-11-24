import time
import mysql.connector
import yfinance as yf
from circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

def fetch_stock_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")['Close'].iloc[-1]

def create_table_if_not_exists(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            ticker VARCHAR(10) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)

def main():
    conn = mysql.connector.connect(
        host="db",
        user="user",
        password="password",
        database="users"
    )
    cursor = conn.cursor()
    
    # Ensure the table exists
    create_table_if_not_exists(cursor)
    
    while True:
        cursor.execute("SELECT email, ticker FROM users")
        users = cursor.fetchall()
        for email, ticker in users:
            try:
                price = circuit_breaker.call(fetch_stock_price, ticker)
                cursor.execute("INSERT INTO stock_prices (email, ticker, price, timestamp) VALUES (%s, %s, %s, NOW())",
                               (email, ticker, price))
                conn.commit()
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
        time.sleep(3600)  # Wait for 1 hour before fetching data again

if __name__ == "__main__":
    main()