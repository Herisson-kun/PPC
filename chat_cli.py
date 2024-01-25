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

    host = '127.0.0.1'
    port = 5555

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input("Saisissez votre message (ou 'exit' pour quitter): ")
        client_socket.send(message.encode())

        if message.lower() == 'exit':
            break

    # Fermer le socket client
    client_socket.close()

if __name__ == "__main__":
    main()
