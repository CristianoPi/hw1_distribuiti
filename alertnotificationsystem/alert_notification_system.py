import logging
import smtplib
from email.mime.text import MIMEText
from confluent_kafka import Consumer, KafkaError
import time
import json
from prometheus_client import start_http_server, Counter, Gauge

# Configura il logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

email_counter = Counter('emails_sent', 'Total number of emails sent', ['service', 'node'])
error_counter = Counter('total_errors', 'Total number of errors', ['service', 'node'])
message_counter = Counter('messages_received', 'Total number of messages received', ['service', 'node'])
processing_time_gauge = Gauge('message_processing_time_seconds', 'Time taken to process a message', ['service', 'node'])
# Configura il consumer Kafka
conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'notification_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['AlertNotificationSystem'])

# Configura le impostazioni email
email_conf = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_user': 'cristiano.pistorio@gmail.com',
    'smtp_password': 'iiujymduizmhgmvf',
    'from_email': 'cristiano.pistorio@gmail.com'
}

def send_email(email, alert, email_conf):
    msg = MIMEText(alert)
    msg['Subject'] = 'Stock Alert'
    msg['From'] = email_conf['from_email']
    msg['To'] = email

    try:
        logging.info("Connessione al server SMTP...")
        with smtplib.SMTP(email_conf['smtp_server'], email_conf['smtp_port'], timeout=50) as server:
            logging.info("Starting process...")
            server.starttls()
            server.login(email_conf['smtp_user'], email_conf['smtp_password'])
            logging.info("Connessione SMTP...")
            server.sendmail(email_conf['from_email'], email, msg.as_string())
            logging.info(f"Email sent to {email}: {alert}")
            email_counter.labels(service='alertnotificationsystem', node='worker').inc()
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        error_counter.labels(service='alertnotificationsystem', node='worker').inc()

def process_message(message):
    start_time = time.time()
    alert = message.value().decode('utf-8')
    logging.info(f"Received alert: {alert}")
    alert_data = json.loads(alert)
    email = alert_data.get('email')  # Usa l'email dal messaggio, con un valore di default
    send_email(email, alert, email_conf)
    try:
        consumer.commit(asynchronous=False)
        logging.info("Offset committed")
    except KafkaError as e:
        logging.error(f"Commit failed: {e}")
        error_counter.labels(service='alertnotificationsystem', node='worker').inc()

        
    processing_time = time.time() - start_time
    processing_time_gauge.labels(service='alertnotificationsystem', node='worker').set(processing_time)
    message_counter.labels(service='alertnotificationsystem', node='worker').inc()

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
        logging.error(f"Error in AlertNotificationSystem: {e}")
        error_counter.labels(service='alertnotificationsystem', node='worker').inc()
    finally:
        consumer.close()
        logging.info("Consumer closed.")

if __name__ == "__main__": 
    start_http_server(8002)
    time.sleep(20)
    main()