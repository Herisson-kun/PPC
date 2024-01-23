import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break  # Le serveur a fermé la connexion
            print(data.decode())
        except:
            break

def main():
    # Paramètres du client
    host = '127.0.0.1'
    port = 5555

    # Créer un socket client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Se connecter au serveur
    client_socket.connect((host, port))

    # Créer un thread pour recevoir les messages du serveur
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Envoyer des messages au serveur
    while True:
        message = input("Saisissez votre message (ou 'exit' pour quitter): ")
        client_socket.send(message.encode())

        if message.lower() == 'exit':
            break

    # Fermer le socket client
    client_socket.close()

if __name__ == "__main__":
    main()
