from concurrent import futures
import grpc
import user_pb2
import user_pb2_grpc
import mysql.connector

import logging
from datetime import datetime, timedelta


#funzione per normalizzare le mail, la mail non è case sensitive e non è sensibile ai punti, salviamo le mail tutte minuscole e senza punti nel db per evitare di salvare due vote la stessa email, è una chiave primaria!
def normalize_email(email):
    local, domain = email.split('@')
    # Converte il dominio in minuscolo
    domain = domain.lower()
    # Normalizza la parte locale solo per i domini comuni che ignorano i punti
    if domain in ['gmail.com', 'googlemail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'live.com', 'msn.com']:
        local = local.lower()
        local = local.replace('.', '')
    # Mantiene la parte locale sensibile alle maiuscole per altri domini
    return f"{local}@{domain}"

class UserCommandService(user_pb2_grpc.UserCommandServiceServicer):

    def __init__(self):
        self.conn = mysql.connector.connect(
            host="db",
            user="user",
            password="password",
            database="users"
        )
        self.requestRegister = {}
        self.requestUpdate = {}
        self.requestDelete = {}
        self.create_table()
        logging.basicConfig(level=logging.INFO)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                        (email VARCHAR(255) PRIMARY KEY, ticker VARCHAR(10), low_value FLOAT, high_value FLOAT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS stock_prices
                        (id INT AUTO_INCREMENT PRIMARY KEY, ticker VARCHAR(10), price FLOAT, timestamp TIMESTAMP)''')
        cursor.close()

    def RegisterUser(self, request, context):
        normalized_email = normalize_email(request.email)
        try:
            if normalized_email in self.requestRegister:
                if self.requestRegister[normalized_email] == 0:
                    return user_pb2.RegisterUserResponse(message="Registration in process...")
                elif self.requestRegister[normalized_email] == 1:
                    return user_pb2.RegisterUserResponse(message="User already registered successfully")

            self.requestRegister[normalized_email] = 0
            cursor = self.conn.cursor()
            try:
                logging.info(f"il valore low : {request.low_value}.")
                if request.low_value > 0 and request.high_value > 0 and request.low_value <= request.high_value:
                    cursor.execute("INSERT INTO users (email, ticker, low_value, high_value) VALUES (%s, %s, %s, %s)", 
                                (normalized_email, request.ticker, request.low_value, request.high_value))
                    self.conn.commit()
                    self.requestRegister[normalized_email] = 1
                    if normalized_email in self.requestDelete:
                        self.requestDelete.pop(normalized_email, None)
                    logging.info(f"User {normalized_email} registered successfully.")
                    return user_pb2.RegisterUserResponse(message="User registered successfully")
                elif request.low_value==0 or request.high_value==0 :
                        cursor.execute("INSERT INTO users (email, ticker, low_value, high_value) VALUES (%s, %s, %s, %s)", 
                                    (normalized_email, request.ticker, request.low_value, request.high_value))
                        self.conn.commit()
                        self.requestRegister[normalized_email] = 1
                        if normalized_email in self.requestDelete:
                            self.requestDelete.pop(normalized_email, None)
                        logging.info(f"User {normalized_email} registered successfully.")
                        return user_pb2.RegisterUserResponse(message="User registered successfully")
                else:
                    return user_pb2.RegisterUserResponse(message="Invalid value")
            except mysql.connector.Error as db_err:
                self.conn.rollback()
                self.requestRegister.pop(normalized_email, None)
                logging.error(f"Database error: {db_err}")
                return user_pb2.RegisterUserResponse(message="An error occurred during registration.")
            finally:
                cursor.close()
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return user_pb2.RegisterUserResponse(message="An unexpected error occurred.")

    def UpdateUser(self, request, context):
        normalized_email = normalize_email(request.email)
        key = (normalized_email, request.ticker, request.low_value, request.high_value)
        try:
            if key in self.requestUpdate:
                if self.requestUpdate[key] == 0:
                    return user_pb2.UpdateUserResponse(message="Update in process...")
                elif self.requestUpdate[key] == 1:
                    return user_pb2.UpdateUserResponse(message="User already updated successfully")

            keys_to_delete = [k for k in self.requestUpdate if k[0] == normalized_email]
            for k in keys_to_delete:
                del self.requestUpdate[k]

            self.requestUpdate[key] = 0

            cursor = self.conn.cursor()
            try:
                if request.low_value >= 0 and request.high_value >= 0 and request.low_value <= request.high_value:
                    cursor.execute(
                        "UPDATE users SET ticker = %s, low_value = %s, high_value = %s WHERE email = %s",
                        (request.ticker, request.low_value, request.high_value, normalized_email)
                    )
                    if cursor.rowcount == 0:
                        return user_pb2.UpdateUserResponse(message="No user found with the specified email")
                    self.conn.commit()
                    self.requestUpdate[key] = 1
                    return user_pb2.UpdateUserResponse(message="User updated successfully")
                else:
                    return user_pb2.UpdateUserResponse(message="Invalid value")
            except mysql.connector.Error as db_err:
                self.conn.rollback()
                logging.error(f"Database error: {db_err}")
                return user_pb2.UpdateUserResponse(message="An error occurred during update.")
            finally:
                cursor.close()
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return user_pb2.UpdateUserResponse(message="An unexpected error occurred.")
        
    def UpdateValue(self, request, context):
        normalized_email = normalize_email(request.email)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT low_value, high_value FROM users WHERE email = %s", (normalized_email,))
            result = cursor.fetchone()
            
            if result is None:
                return user_pb2.UpdateValueResponse(message="No user found with the specified email")
            
            current_low_value, current_high_value = result
            
            if request.low_value >= 0 and request.high_value >= 0:
                if request.low_value > request.high_value:
                    return user_pb2.UpdateValueResponse(message="Low value cannot be greater than high value")
                cursor.execute(
                    "UPDATE users SET low_value = %s, high_value = %s WHERE email = %s",
                    (request.low_value, request.high_value, normalized_email)
                )
            elif request.low_value < 0:
                if current_low_value > request.high_value:
                    return user_pb2.UpdateValueResponse(message="Low value cannot be greater than high value")
                cursor.execute(
                    "UPDATE users SET high_value = %s WHERE email = %s",
                    (request.high_value, normalized_email)
                )
            else:
                if request.low_value > current_high_value:
                    return user_pb2.UpdateValueResponse(message="Low value cannot be greater than high value")
                cursor.execute(
                    "UPDATE users SET low_value = %s WHERE email = %s",
                    (request.low_value, normalized_email)
                )
            
            if cursor.rowcount == 0:
                return user_pb2.UpdateValueResponse(message="No user found with the specified email")
            
            self.conn.commit()
            return user_pb2.UpdateValueResponse(message="User updated value successfully")
        except mysql.connector.Error as db_err:
            self.conn.rollback()
            logging.error(f"Database error: {db_err}")
            return user_pb2.UpdateValueResponse(message="An error occurred during value update.")
        finally:
            cursor.close()

    def DeleteUser(self, request, context):
        normalized_email = normalize_email(request.email)
        try:
            if normalized_email in self.requestDelete:
                if self.requestDelete[normalized_email] == 0:
                    return user_pb2.DeleteUserResponse(message="Deletion in process...")
                elif self.requestDelete[normalized_email] == 1:
                    return user_pb2.DeleteUserResponse(message="User already deleted successfully")

            self.requestDelete[normalized_email] = 0

            cursor = self.conn.cursor()
            try:
                cursor.execute("DELETE FROM users WHERE email = %s", (normalized_email,))
                self.conn.commit()
                self.requestDelete[normalized_email] = 1
                if normalized_email in self.requestRegister:
                    self.requestRegister.pop(normalized_email, None)
                return user_pb2.DeleteUserResponse(message="User deleted successfully")
            except mysql.connector.Error as db_err:
                self.conn.rollback()
                self.requestDelete.pop(normalized_email, None)
                logging.error(f"Database error: {db_err}")
                return user_pb2.DeleteUserResponse(message="An error occurred during deletion.")
            finally:
                cursor.close()
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return user_pb2.DeleteUserResponse(message="An unexpected error occurred.")

    def DeleteDataByTime(self, request, context):
        cursor = self.conn.cursor()
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(seconds=request.start_time)
            cutoff_timestamp = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cursor.execute("""
                DELETE FROM stock_prices
                WHERE timestamp < %s
            """, (cutoff_timestamp,))
            self.conn.commit()
            return user_pb2.DeleteDataByTimeResponse(message="Data deleted successfully")
        except mysql.connector.Error as db_err:
            logging.error(f"Database error: {db_err}")
            return user_pb2.DeleteDataByTimeResponse(message="An error occurred while deleting data.")
        finally:
            cursor.close()    
        
class UserQueryService(user_pb2_grpc.UserQueryServiceServicer):

    def __init__(self):
        self.conn = mysql.connector.connect(
            host="db",
            user="user",
            password="password",
            database="users"
        )
        logging.basicConfig(level=logging.INFO)

    def GetAllData(self, request, context):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            data = []
            for table in tables:
                cursor.execute(f"SELECT * FROM {table[0]}")
                rows = cursor.fetchall()
                data.append(f"Table: {table[0]}")
                for row in rows:
                    data.append(str(row))
            return user_pb2.AllDataResponse(data=data)
        except mysql.connector.Error as db_err:
            logging.error(f"Database error: {db_err}")
            return user_pb2.AllDataResponse(data=["An error occurred while retrieving data."])
        finally:
            cursor.close()

    def GetLastStockValue(self, request, context):
        normalized_email = normalize_email(request.email)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cursor.execute("""
                SELECT sp.price 
                FROM stock_prices sp
                JOIN users u ON sp.ticker = u.ticker
                WHERE u.email = %s
                ORDER BY sp.timestamp DESC LIMIT 1
            """, (normalized_email,))
            result = cursor.fetchone()
            if result:
                return user_pb2.StockValueResponse(message="Last stock value retrieved successfully", value=result[0])
            else:
                return user_pb2.StockValueResponse(message="No stock value found for the given email", value=0.0)
        except mysql.connector.Error as db_err:
            logging.error(f"Database error: {db_err}")
            return user_pb2.StockValueResponse(message="An error occurred while retrieving the last stock value.", value=0.0)
        finally:
            cursor.close()

    def GetAverageStockValue(self, request, context):
        normalized_email = normalize_email(request.email)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cursor.execute("SELECT ticker FROM users WHERE email = %s", (normalized_email,))
            user_ticker = cursor.fetchone()
            
            if user_ticker:
                cursor.execute("""
                    SELECT sp.price 
                    FROM stock_prices sp
                    JOIN users u ON sp.ticker = u.ticker
                    WHERE u.email = %s AND u.ticker = %s
                    ORDER BY sp.timestamp DESC LIMIT %s
                """, (normalized_email, user_ticker[0], request.count))
                results = cursor.fetchall()
                if results:
                    average_value = sum([r[0] for r in results]) / len(results)
                    return user_pb2.StockValueResponse(message="Average stock value calculated successfully", value=average_value)
                else:
                    return user_pb2.StockValueResponse(message="No stock values found for the given email and ticker", value=0.0)
            else:
                return user_pb2.StockValueResponse(message="No ticker found for the given email", value=0.0)
        except mysql.connector.Error as db_err:
            logging.error(f"Database error: {db_err}")
            return user_pb2.StockValueResponse(message="An error occurred while calculating the average stock value.", value=0.0)
        finally:
            cursor.close()

    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    user_pb2_grpc.add_UserCommandServiceServicer_to_server(UserCommandService(), server)
    user_pb2_grpc.add_UserQueryServiceServicer_to_server(UserQueryService(), server)
    
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()