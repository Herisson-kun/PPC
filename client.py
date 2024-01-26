import socket
from class_card import Card

card_color = "blue"
card_number = str(1)
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect(('127.0.0.1', 8080))
print(f"Connecté au serveur")

_, port = socket.getsockname()
player_id = port

socket.send(card_color.encode())
socket.send(card_number.encode())
