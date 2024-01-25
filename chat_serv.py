import socket
import threading
import msvcrt

def handle_client(client_socket, client_address):
    print(f"Connexion établie avec {client_address}")

    client_socket.send("Bienvenue sur le serveur de chat!".encode())

    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        message = data.decode()
        print(f"Client {client_address}: {message}")

        broadcast(message, client_socket)

    # Fermer la connexion avec le client
    print(f"Connexion fermée avec {client_address}")
    sock_clients.remove(client_socket)
    client_socket.close()

def broadcast(message, sender_socket):
    for client in sock_clients:
        if client != sender_socket:
            client.send(f"Client {sock_clients.index(sender_socket) + 1}: {message}".encode())

def run_server():
    # Paramètres du serveur
    host = '127.0.0.1'
    port = 5555

    # Créer un socket serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Serveur en écoute sur {host}:{port}")

    # Liste pour stocker les sockets des clients

    running = True
    while running:
        try:
            client_socket, client_address = server_socket.accept()
            sock_clients.append(client_socket)

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        except KeyboardInterrupt:
            # Gérer la sortie proprement lorsque l'utilisateur appuie sur Ctrl+C
            print("Fermeture du serveur...")
            running = False


    server_socket.close()

if __name__ == "__main__":
    sock_clients = []
    run_server()
