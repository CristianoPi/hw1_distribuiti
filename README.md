**Requisiti**

Assicurarsi di avere installato docker nel proprio ambiente

Assicurarsi di avere installato kind nel proprio ambiente

Il codice del progetto è visualizzabile nelle cartelle, ogni cartella ha il nome del servizio che racchiude.

**Deploy**
- Portarsi da terminale al percorso .\hw1_distribuiti
- Eseguire il comando *kind start*
- Eseguire il comando *kind create cluster --config kind-config.yaml*
- Fare il build di tutte le immagini (le due del server, datacollector, alertsystem, alertnotificationsystem):
      docker build -t user-command-service:latest -f Dockerfile.command .
      docker build -t user-query-service:latest -f Dockerfile.query .
      e poi 
    Spostarsi nella directory di cui si vuole creare l'immagine ed eseguire: *docker build -t my_example_image:latest .*
- Fare il load di tutte le immagini:
    *kind load docker-image my_datacollector_image:latest user-command-service:latest user-query-service:latest my_alertsystem_image:latest my_alertnotificationsystem_image:latest  --name my-kind-cluster*    
- Fare l'apply in ordine:(*kubectl apply -f .* in ogni cartella)
    -db
    -server
    -kafka-all-in-one
    -datacollector
    -alertsystem
    -alertnotificationsystem
    -prometheus
- Il Client è esguibile portandosi al percorso .\hw1_distribuiti\client ed esegundo il comando *python client.py*

**Relazione**

La relazione dell'hw1, con tutti i dettagli, si trova nella repository al seguente link: https://github.com/CristianoPi/hw1_distribuiti/blob/main/Relazione_HW1.pdf

La relazione dell'hw2, con tutti i dettagli, si trova nella repository al seguente link: https://github.com/CristianoPi/hw1_distribuiti/blob/hw2/Relazione_HW2.pdf

La relazione dell'hw3, con tutti i dettagli, si trova nella repository al seguente link: https://github.com/CristianoPi/hw1_distribuiti/blob/hw2/Relazione_HW3.pdf
