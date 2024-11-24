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
            print("7. Esci")

            choice = input("Inserisci la tua scelta: ")

            match choice:
                case '1':
                    email = input("Inserisci l'email: ")
                    ticker = input("Inserisci il ticker: ")
                    response = stub.RegisterUser(user_pb2.RegisterUserRequest(email=email, ticker=ticker))
                    print("Risposta RegisterUser:", response.message)

                case '2':
                    email = input("Inserisci l'email: ")
                    ticker = input("Inserisci il nuovo ticker: ")
                    response = stub.UpdateUser(user_pb2.UpdateUserRequest(email=email, ticker=ticker))
                    print("Risposta UpdateUser:", response.message)

                case '3':
                    email = input("Inserisci l'email: ")
                    response = stub.DeleteUser(user_pb2.DeleteUserRequest(email=email))
                    print("Risposta DeleteUser:", response.message)

                case '4':
                    response = stub.GetAllData(user_pb2.Empty())
                    print("Risposta AllData:")
                    for data in response.data:
                        print(data)

                case '5':
                    email = input("Inserisci l'email: ")
                    response = stub.GetLastStockValue(user_pb2.EmailRequest(email=email))
                    print("Risposta LastStockValue:", response.message, "Valore:", response.value)

                case '6':
                    email = input("Inserisci l'email: ")
                    count = int(input("Inserisci il numero di valori da calcolare nella media: "))
                    response = stub.GetAverageStockValue(user_pb2.AverageStockRequest(email=email, count=count))
                    print("Risposta AverageStockValue:", response.message, "Valore:", response.value)

                case '7':
                    print("Uscita in corso...")
                    break

                case _:
                    print("Scelta non valida. Riprova.")

if __name__ == "__main__":
    run()
