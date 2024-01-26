import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 8080))
server_socket.listen(5)
print(f"Le jeu écoute sur 127.0.0.1:8080")

player_socket, addr = server_socket.accept()
player_id = addr[1]
print(f"Connexion établie avec {player_id}")

color = player_socket.recv(2000).decode()
number = player_socket.recv(2000).decode()

print(color, number)