import logging
import smtplib
from email.mime.text import MIMEText
from confluent_kafka import Consumer, KafkaError
import time
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
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def process_message(message):
    alert = message.value().decode('utf-8')
    logging.info(f"Received alert: {alert}")
    # Supponiamo che l'email sia fissa per questo esempio
    #email = 'cristianopistorio@gmail.com'
    #email='giusepperomano2000ct@gmail.com'
    alert_data = json.loads(alert)
    email = alert_data.get('email', 'default@example.com')  # Usa l'email dal messaggio, con un valore di default
    send_email(email, alert, email_conf)
    consumer.commit(asynchronous=False)  # Commit dell'offset dopo aver processato il messaggio

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
            # Commit dell'offset dopo aver processato il messaggio
            consumer.commit(asynchronous=False)
    except Exception as e:
        logging.error(f"Error in AlertNotificationSystem: {e}")
    finally:
        consumer.close()
        logging.info("Consumer closed.")

if __name__ == "__main__": 
    time.sleep(20)
    main()