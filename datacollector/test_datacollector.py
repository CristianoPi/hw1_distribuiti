import mysql.connector
import time
from circuit_breaker import CircuitBreaker
from datacollector import fetch_stock_price, create_table_if_not_exists

def setup_test_db():
    conn = mysql.connector.connect(
        host="db",
        user="user",
        password="password",
        database="users"
    )
    cursor = conn.cursor()
    create_table_if_not_exists(cursor)
    cursor.execute("DELETE FROM users")  # Pulisce la tabella degli utenti
    cursor.execute("DELETE FROM stock_prices")  # Pulisce la tabella dei prezzi delle azioni
    cursor.execute("INSERT INTO users (email, ticker) VALUES (%s, %s)", ("test1@example.com", "AAPL"))
    cursor.execute("INSERT INTO users (email, ticker) VALUES (%s, %s)", ("test2@example.com", "GOOGL"))
    conn.commit()
    cursor.close()
    conn.close()

def test_fetch_stock_price():
    try:
        price = fetch_stock_price("AAPL")
        print(f"Prezzo azione AAPL: {price}")
    except Exception as e:
        print(f"Errore durante il recupero del prezzo dell'azione: {e}")

def test_circuit_breaker():
    circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10)
    
    def failing_function():
        raise Exception("Errore simulato")

    # Simula fallimenti per attivare il circuit breaker
    for _ in range(3):
        try:
            circuit_breaker.call(failing_function)
        except Exception as e:
            print(f"Errore catturato: {e}")

    # Verifica che il circuit breaker sia aperto
    try:
        circuit_breaker.call(failing_function)
    except Exception as e:
        print(f"Errore atteso con circuit breaker aperto: {e}")

    # Attendi il timeout di recupero
    print("Attesa per il timeout di recupero...")
    time.sleep(10)

    # Verifica che il circuit breaker si sia ripristinato
    try:
        circuit_breaker.call(failing_function)
    except Exception as e:
        print(f"Errore dopo il recupero: {e}")

if __name__ == "__main__":
    #setup_test_db()
    test_fetch_stock_price()
    #test_circuit_breaker()