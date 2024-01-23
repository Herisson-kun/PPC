import socket

# Créez une socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Liez la socket à une adresse IP et un numéro de port
server_socket.bind(('127.0.0.1', 0))  # Utilisez le numéro de port 0 pour une attribution automatique

# Obtenez les informations sur le numéro de port attribué
_, port = server_socket.getsockname()

print(f"La socket est liée à l'adresse '127.0.0.1' et au port {port}")
