import socket
import threading

def handle_client(client_socket, client_address, turn_semaphore):
    print(f"Connexion établie avec {client_address}")

    # Envoyer un message de bienvenue au client
    client_socket.send("Bienvenue sur le serveur de chat!".encode())

    while True:
        # Attendre que ce soit le tour du client pour envoyer un message
        turn_semaphore.acquire()

        # Recevoir le message du client
        data = client_socket.recv(1024)
        if not data:
            break  # Le client a fermé la connexion

        # Afficher le message et le renvoyer à tous les clients connectés
        message = data.decode()
        print(f"Tour du client {clients.index(client_socket) + 1}: {message}")

        # Relâcher le sémaphore pour permettre au prochain client d'envoyer un message
        turn_semaphore.release()

        # Envoyer le message à tous les clients connectés
        broadcast(message, client_socket)

    # Fermer la connexion avec le client
    print(f"Connexion fermée avec {client_address}")
    clients.remove(client_socket)
    client_socket.close()

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(f"Client {clients.index(sender_socket) + 1}: {message}".encode())
            except:
                # En cas d'erreur lors de l'envoi du message, fermer la connexion avec ce client
                clients.remove(client)
                client.close()

# Paramètres du serveur
host = '127.0.0.1'
port = 5555

# Créer un socket serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)

print(f"Serveur en écoute sur {host}:{port}")

# Liste pour stocker les sockets des clients
clients = []

# Sémaphore pour gérer les tours
turn_semaphore = threading.Semaphore(1)

while True:
    # Accepter la connexion d'un client
    client_socket, client_address = server_socket.accept()

    # Ajouter le client à la liste
    clients.append(client_socket)

    # Créer un thread pour gérer le client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, turn_semaphore))
    client_thread.start()
