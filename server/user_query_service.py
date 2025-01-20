from concurrent import futures
import grpc
import user_pb2
import user_pb2_grpc
import mysql.connector
import logging

def normalize_email(email):
    local, domain = email.split('@')
    domain = domain.lower()
    if domain in ['gmail.com', 'googlemail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'live.com', 'msn.com']:
        local = local.lower()
        local = local.replace('.', '')
    return f"{local}@{domain}"

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
    user_pb2_grpc.add_UserQueryServiceServicer_to_server(UserQueryService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()