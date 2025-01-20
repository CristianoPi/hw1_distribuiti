from concurrent import futures
import grpc
import user_pb2
import user_pb2_grpc
import mysql.connector
import logging
from datetime import datetime, timedelta

def normalize_email(email):
    local, domain = email.split('@')
    domain = domain.lower()
    if domain in ['gmail.com', 'googlemail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'live.com', 'msn.com']:
        local = local.lower()
        local = local.replace('.', '')
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
                
                if request.low_value < 0 or request.high_value < 0:
                    self.requestRegister.pop(normalized_email, None)
                    return user_pb2.RegisterUserResponse(message="Invalid input: values cannot be negative")
                
                if request.low_value > 0 and request.high_value > 0:
                    if request.low_value < request.high_value:
                        cursor.execute("INSERT INTO users (email, ticker, low_value, high_value) VALUES (%s, %s, %s, %s)", 
                                    (normalized_email, request.ticker, request.low_value, request.high_value))
                        self.conn.commit()
                        self.requestRegister[normalized_email] = 1
                        if normalized_email in self.requestDelete:
                            self.requestDelete.pop(normalized_email, None)
                        logging.info(f"User {normalized_email} registered successfully.")
                        return user_pb2.RegisterUserResponse(message="User registered successfully")
                    else:
                        self.requestRegister.pop(normalized_email, None)
                        return user_pb2.RegisterUserResponse(message="Invalid input: low_value must be less than high_value")
                
                elif request.low_value == 0 or request.high_value == 0:
                    cursor.execute("INSERT INTO users (email, ticker, low_value, high_value) VALUES (%s, %s, %s, %s)", 
                                (normalized_email, request.ticker, request.low_value, request.high_value))
                    self.conn.commit()
                    self.requestRegister[normalized_email] = 1
                    if normalized_email in self.requestDelete:
                        self.requestDelete.pop(normalized_email, None)
                    logging.info(f"User {normalized_email} registered successfully.")
                    return user_pb2.RegisterUserResponse(message="User registered successfully")
                
                else:
                    self.requestRegister.pop(normalized_email, None)
                    return user_pb2.RegisterUserResponse(message="Invalid input")
            
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
        logging.info(f"Current state of requestUpdate ad inizio funzione {self.requestUpdate}")
        try:
            if key in self.requestUpdate:
                if self.requestUpdate[key] == 0:
                    return user_pb2.UpdateUserResponse(message="Update in process...")
                elif self.requestUpdate[key] == 1:
                    return user_pb2.UpdateUserResponse(message="User already updated successfully")
                elif self.requestUpdate[key] == 2:
                    return user_pb2.UpdateUserResponse(message="invalid input") 

            keys_to_delete = [k for k in self.requestUpdate if k[0] == normalized_email]
            for k in keys_to_delete:
                del self.requestUpdate[k]

            self.requestUpdate[key] = 0
            logging.info(f"Current state of requestUpdate after setting key to 0: {self.requestUpdate}")
            cursor = self.conn.cursor()
            try:
                if request.low_value < 0 or request.high_value < 0:
                    self.requestUpdate[key] = 2
                    logging.info(f"Current state of requestUpdate after invalid input: {self.requestUpdate}")
                    return user_pb2.UpdateUserResponse(message="Invalid input: values cannot be negative")
                
                if request.low_value > 0 and request.high_value > 0:
                    if request.low_value < request.high_value:
                        cursor.execute(
                            "UPDATE users SET ticker = %s, low_value = %s, high_value = %s WHERE email = %s",
                            (request.ticker, request.low_value, request.high_value, normalized_email)
                        )
                        if cursor.rowcount == 0:
                            return user_pb2.UpdateUserResponse(message="No user found with the specified email")
                        self.conn.commit()
                        self.requestUpdate[key] = 1
                        logging.info(f"Current state of requestUpdate after successful update: {self.requestUpdate}")
                        return user_pb2.UpdateUserResponse(message="User updated successfully")
                    else:
                        return user_pb2.UpdateUserResponse(message="Invalid input: low_value must be less than high_value")
                
                elif request.low_value == 0 or request.high_value == 0:
                    cursor.execute( "UPDATE users SET ticker = %s, low_value = %s, high_value = %s WHERE email = %s",
                                (request.ticker, request.low_value, request.high_value, normalized_email))
                    self.conn.commit()
                    self.requestUpdate[key] = 1
                    return user_pb2.UpdateUserResponse(message="User updated successfully")
                
                else:
                    self.requestUpdate[key] = 2
                    return user_pb2.UpdateUserResponse(message="Invalid input")
            except Exception as e:
                return user_pb2.UpdateUserResponse(message=f"An error occurred: {str(e)}")

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

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserCommandServiceServicer_to_server(UserCommandService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()