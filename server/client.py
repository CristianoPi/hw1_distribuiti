import grpc
import user_pb2
import user_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)

        while True:
            print("\nMenu:")
            print("1. Registra Utente")
            print("2. Aggiorna Utente")
            print("3. Elimina Utente")
            print("4. Mostra Tutti i Dati")
            print("5. Mostra Ultimo Valore Azione")
            print("6. Calcola Valore Medio Azione")
            print("7. Elimina Dati per Tempo")
            print("8. Esci")

            choice = input("Inserisci la tua scelta: ")

            match choice:
                case '1':
                    try:
                        email = input("Inserisci l'email: ")
                        ticker = input("Inserisci il ticker: ")
                        response = stub.RegisterUser(user_pb2.RegisterUserRequest(email=email, ticker=ticker))
                        print("Risposta RegisterUser:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '2':
                    try:
                        email = input("Inserisci l'email: ")
                        ticker = input("Inserisci il nuovo ticker: ")
                        response = stub.UpdateUser(user_pb2.UpdateUserRequest(email=email, ticker=ticker))
                        print("Risposta UpdateUser:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '3':
                    try:
                        email = input("Inserisci l'email: ")
                        response = stub.DeleteUser(user_pb2.DeleteUserRequest(email=email))
                        print("Risposta DeleteUser:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '4':
                    try:
                        response = stub.GetAllData(user_pb2.Empty())
                        print("Risposta AllData:")
                        for data in response.data:
                            print(data)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '5':
                    try:
                        email = input("Inserisci l'email: ")
                        response = stub.GetLastStockValue(user_pb2.EmailRequest(email=email))
                        print("Risposta LastStockValue:", response.message, "Valore:", response.value)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '6':
                    try:
                        email = input("Inserisci l'email: ")
                        count = int(input("Inserisci il numero di valori da calcolare nella media: "))
                        response = stub.GetAverageStockValue(user_pb2.AverageStockRequest(email=email, count=count))
                        print("Risposta AverageStockValue:", response.message, "Valore:", response.value)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")
                case '7':
                    try:
                        seconds = int(input("Inserisci l'intervallo di tempo in secondi: "))
                        response = stub.DeleteDataByTime(user_pb2.DeleteDataByTimeRequest(start_time=seconds))
                        print("Risposta DeleteDataByTime:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")
                case '8':
                    print("Uscita in corso...")
                    break

                case _:
                    print("Scelta non valida. Riprova.")

if __name__ == "__main__":
    run()
