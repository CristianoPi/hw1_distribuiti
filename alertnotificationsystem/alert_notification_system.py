import logging
import smtplib
from email.mime.text import MIMEText
from confluent_kafka import Consumer, KafkaError
import json

# Configura il logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configura il consumer Kafka
conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'notification_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['AlertNotificationSystem'])

def send_email(email, alert):
    msg = MIMEText(alert)
    msg['Subject'] = 'Stock Alert'
    msg['From'] = 'your_email@example.com'
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login('your_email@example.com', 'your_password')
            server.sendmail('your_email@example.com', email, msg.as_string())
            logging.info(f"Email sent to {email}: {alert}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def process_message(message):
    alert = json.loads(message.value().decode('utf-8'))
    logging.info(f"Received alert: {alert}")
    send_email(alert['email'], json.dumps(alert))

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
    finally:
        consumer.close()
        logging.info("Consumer closed.")

if __name__ == "__main__":
    main()