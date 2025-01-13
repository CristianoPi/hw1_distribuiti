import time
import logging
import mysql.connector
import json
from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from prometheus_client import start_http_server, Gauge, Counter

# Configura il logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

request_counter = Counter('total_requests', 'Total number of requests', ['service', 'node'])
error_counter = Counter('total_errors', 'Total number of errors', ['service', 'node'])
gauge_metric = Gauge('custom_gauge_metric', 'A custom gauge metric', ['service', 'node'])

def create_topic(topic_name, bootstrap_servers='kafka:9092'):
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    topic_list = [NewTopic(topic_name, num_partitions=1, replication_factor=1)]
    fs = admin_client.create_topics(topic_list)

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logging.info(f"Topic {topic} created successfully.")
        except Exception as e:
            logging.error(f"Failed to create topic {topic}: {e}")


# Configura il consumer Kafka
consumer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'alert_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False  # Disabilita il commit automatico
}
consumer = Consumer(consumer_conf)
consumer.subscribe(['AlertSystem'])

# Configura il producer Kafka per inviare notifiche
producer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'alert_system',
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
        error_counter.labels(service='alertsystem', node='worker').inc()
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def check_thresholds_and_alert(cursor, conn):
    cursor.execute("""
        SELECT users.email, stock_prices.ticker, stock_prices.price, users.low_value, users.high_value, stock_prices.timestamp
        FROM stock_prices
        JOIN users ON stock_prices.ticker = users.ticker
        WHERE stock_prices.timestamp = (
            SELECT MAX(sp.timestamp)
            FROM stock_prices sp
            WHERE sp.ticker = users.ticker
        )
    """)
    rows = cursor.fetchall()
    logging.info(f"SONO QUI, lunghezza rows: {len(rows)}")
    for row in rows:
        email, ticker, price, low_value, high_value, timestamp = row 
        if low_value !=0 and price < low_value :
            alert_message = {
                'email': email,
                'ticker': ticker,
                'stock_value': price,
                'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Converti datetime in stringa
                'alert': 'Stock value out of lower limit, the new threshold value will be this value'
            } 
            producer.produce('AlertNotificationSystem', key=ticker, value=json.dumps(alert_message), callback=delivery_report)
            #producer.produce('AlertNotificationSystem', key=ticker, value="prova", callback=delivery_report)
            producer.flush()
            # Aggiorna i valori di soglia nel database
            if low_value is not None and price < low_value:
                cursor.execute("UPDATE users SET low_value = %s WHERE ticker = %s", (price, ticker))
            if high_value is not None and price > high_value:
                cursor.execute("UPDATE users SET high_value = %s WHERE ticker = %s", (price, ticker))
            conn.commit()

        if high_value!=0 and price > high_value :
            alert_message = {
                'email': email,
                'ticker': ticker,
                'stock_value': price,
                'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Converti datetime in stringa
                'alert': 'Stock value out of upper limit, the new threshold value will be this value'
            } 
            producer.produce('AlertNotificationSystem', key=ticker, value=json.dumps(alert_message), callback=delivery_report)
            #producer.produce('AlertNotificationSystem', key=ticker, value="prova", callback=delivery_report)
            producer.flush()
            # Aggiorna i valori di soglia nel database
            if low_value is not None and price < low_value:
                cursor.execute("UPDATE users SET low_value = %s WHERE ticker = %s", (price, ticker))
            if high_value is not None and price > high_value:
                cursor.execute("UPDATE users SET high_value = %s WHERE ticker = %s", (price, ticker))
            conn.commit()

def process_message(message):
    alert = message.value().decode('utf-8')
    logging.info(f"Received alert: {alert}")
    request_counter.labels(service='alertsystem', node='worker').inc()
    gauge_metric.labels(service='alertsystem', node='worker').set(1)  # Imposta la metrica gauge a 1 quando viene ricevuto un messaggio
    if alert == 'Database updated':
        try:
            conn = mysql.connector.connect(
                host="db",
                user="user",
                password="password",
                database="users"
            )
            cursor = conn.cursor()
            check_thresholds_and_alert(cursor, conn)
        except mysql.connector.Error as db_err:
            logging.error(f"Database connection error: {db_err}")
            error_counter.labels(service='alertsystem', node='worker').inc()
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                logging.info("Database connection closed.")
    consumer.commit(asynchronous=False)
    logging.info("Offset committed")            

def main():
    create_topic('AlertSystem')
    create_topic('AlertNotificationSystem')
    # Quando provi a creare un topic che già esiste utilizzando la libreria confluent_kafka, 
    # otterrai un'eccezione TopicAlreadyExistsError. Tuttavia, questa eccezione non interromperà l'esecuzione del programma, 
    # a meno che tu non la gestisca esplicitamente.
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
                    error_counter.labels(service='alertsystem', node='worker').inc()
            else:
                process_message(msg)
    
    except Exception as e:
        logging.error(f"Error in AlertSystem: {e}")
    finally:
        consumer.close()
        logging.info("Consumer closed.")

if __name__ == "__main__":
    start_http_server(8001)  # Avvia il server HTTP di Prometheus sulla porta 8001
    main()