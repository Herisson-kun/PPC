import socket
import threading
from class_player import Player

# Utilisation
if __name__ == "__main__":
    
    player_1 = Player()
    print(player_1.player_id)
    player_1.receive_messages()
    