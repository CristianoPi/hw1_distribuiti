import logging
import mysql.connector
import json
from confluent_kafka import Consumer, KafkaError, Producer

# Configura il logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configura il consumer Kafka
consumer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'alert_group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(consumer_conf)
consumer.subscribe(['AlertSystem'])

# Configura il producer Kafka per inviare notifiche
producer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'alert_system'
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def check_thresholds_and_alert(cursor):
    cursor.execute("""
        SELECT users.email, stock_prices.ticker, stock_prices.price, users.low_value, users.high_value
        FROM stock_prices
        JOIN users ON stock_prices.ticker = users.ticker
    """)
    rows = cursor.fetchall()
    for row in rows:
        email, ticker, price, low_value, high_value = row
        if price < low_value or price > high_value:
            alert_message = {
                'email': email,
                'ticker': ticker,
                'stock_value': price,
                'alert': 'Stock value out of bounds'
            }
            producer.produce('AlertNotificationSystem', key=ticker, value=json.dumps(alert_message), callback=delivery_report)
            producer.flush()

def process_message(message):
    alert = message.value().decode('utf-8')
    logging.info(f"Received alert: {alert}")
    if alert == 'Database updated':
        try:
            conn = mysql.connector.connect(
                host="db",
                user="user",
                password="password",
                database="users"
            )
            cursor = conn.cursor()
            check_thresholds_and_alert(cursor)
        except mysql.connector.Error as db_err:
            logging.error(f"Database connection error: {db_err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                logging.info("Database connection closed.")

def main():
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logging.error(msg.error())
                    break
            process_message(msg)
    except Exception as e:
        logging.error(f"Error in AlertSystem: {e}")
    finally:
        consumer.close()
        logging.info("Consumer closed.")

if __name__ == "__main__":
    main()