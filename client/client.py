import grpc
import user_pb2
import user_pb2_grpc

def soglia():
    low_value = input("Inserisci la soglia minima: (fare solo invio se si desidera non specificare il valore)  ")
    high_value = input("Inserisci la soglia massima: (fare solo invio se si desidera non specificare il valore)  ")
    
    # Converti i valori di input in float se non sono vuoti
    low_value = float(low_value) if low_value else 0
    high_value = float(high_value) if high_value else 0
    return low_value, high_value

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        command_stub = user_pb2_grpc.UserCommandServiceStub(channel)
        query_stub = user_pb2_grpc.UserQueryServiceStub(channel)

        while True:
            print("\nMenu:")
            print("1. Registra Utente")
            print("2. Aggiorna ticker utente")
            print("3. Modifica valori di soglia")
            print("4. Elimina Utente")
            print("5. Mostra Tutti i Dati")
            print("6. Mostra Ultimo Valore Azione")
            print("7. Calcola Valore Medio Azione")
            print("8. Elimina Dati per Tempo")
            print("9. Esci")

            choice = input("Inserisci la tua scelta: ")

            match choice:
                case '1':
                    try:
                        email = input("Inserisci l'email: ")
                        ticker = input("Inserisci il ticker: ")
                        low_value, high_value = soglia()
                        if low_value < 0 or high_value < 0:
                            print("ERRORE: specificata una soglia negativa, riprovare ")
                        elif low_value > 0 and high_value > 0 and low_value > high_value:
                            print("ERRORE: la soglia minima è maggiore della massima")
                        else:
                            response = command_stub.RegisterUser(user_pb2.RegisterUserRequest(
                                email=email, 
                                ticker=ticker, 
                                low_value=low_value, 
                                high_value=high_value 
                            ))
                            print("Risposta RegisterUser:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '2':
                    try:
                        email = input("Inserisci l'email: ")
                        ticker = input("Inserisci il nuovo ticker: ")
                        low_value, high_value = soglia()
                        if low_value < 0 or high_value < 0:
                            print("ERRORE: specificata una soglia negativa, riprovare ")
                        elif low_value > 0 and high_value > 0 and low_value > high_value:
                            print("ERRORE: la soglia minima è maggiore della massima")
                        else:
                            response = command_stub.UpdateUser(user_pb2.UpdateUserRequest(
                                email=email, 
                                ticker=ticker, 
                                low_value=low_value, 
                                high_value=high_value
                            ))
                            print("Risposta UpdateUser:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '3':
                    try:
                        email = input("Inserisci l'email: ")
                        print("Istruzioni per inserimento: \n n=0 o invio --> non monitorare quella soglia, \n n<0 --> lasciare il vecchio valore monitorato , \n n>0 --> nuovo valore da inserire")
                        low_value, high_value = soglia()
                        if low_value > 0 and high_value > 0 and low_value > high_value:
                            print("ERRORE: la soglia minima è maggiore della massima")
                        else:
                            response = command_stub.UpdateValue(user_pb2.UpdateValueRequest(
                                email=email, 
                                low_value=low_value, 
                                high_value=high_value
                            ))
                            print("Risposta UpdateValue:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '4':
                    try:
                        email = input("Inserisci l'email: ")
                        response = command_stub.DeleteUser(user_pb2.DeleteUserRequest(email=email))
                        print("Risposta DeleteUser:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '5':
                    try:
                        response = query_stub.GetAllData(user_pb2.Empty())
                        print("Risposta AllData:")
                        for data in response.data:
                            print(data)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '6':
                    try:
                        email = input("Inserisci l'email: ")
                        response = query_stub.GetLastStockValue(user_pb2.EmailRequest(email=email))
                        print("Risposta LastStockValue:", response.message, "Valore:", response.value)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '7':
                    try:
                        email = input("Inserisci l'email: ")
                        count = int(input("Inserisci il numero di valori da calcolare nella media: "))
                        response = query_stub.GetAverageStockValue(user_pb2.AverageStockRequest(email=email, count=count))
                        print("Risposta AverageStockValue:", response.message, "Valore:", response.value)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '8':
                    try:
                        seconds = int(input("Inserisci l'intervallo di tempo in secondi: "))
                        response = command_stub.DeleteDataByTime(user_pb2.DeleteDataByTimeRequest(start_time=seconds))
                        print("Risposta DeleteDataByTime:", response.message)
                    except grpc.RpcError as e:
                        print(f"Errore gRPC: {e.code()} - {e.details()}")

                case '9':
                    print("Uscita in corso...")
                    break

                case _:
                    print("Scelta non valida. Riprova.")

if __name__ == "__main__":
    run()