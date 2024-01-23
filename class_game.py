import multiprocessing
import threading
import socket
import queue
import json
import random
import signal
from class_player import Player

class Game():
    def __init__(self, shared_memory):

        self.player_id_counter = 1
        self.players = {}

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 8080))
        self.server_socket.listen(5)
        print(f"Le jeu écoute sur 127.0.0.1:8080")
        self.player_sockets = {}  # Dictionnaire pour stocker les sockets des joueurs {player:socket}
        self.accept_players()

        self.shared_memory = shared_memory

        self.players_deck = [1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5]
        self.deck = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]


    def init_shared_memory(self):
        self.shared_memory["colors"] = ["blue", "red", "green", "yellow", "white"][:len(self.players)]
        self.shared_memory["fuse_token"] = 3
        self.shared_memory["info_token"] = len(self.players) + 3
        self.shared_memory["deck"] = random.shuffle(self.deck)
        self.shared_memory["suites"] = {f"{color}" : [] for color in self.shared_memory["colors"]}

    def accept_players(self):
        while True:
            player_socket, addr = self.server_socket.accept()
            player_id = addr[1]
            self.players[player_id] = player_socket
            print(f"Connexion établie avec {addr}")
            # player_handler = threading.Thread(target=self.handle_player, args=(player_socket, player_id))
            # player_handler.start()

    def handle_player(self, player_id, address):
        print(f"Joueur {player_id} connecté depuis {address}")

        while True:
            # Handle communication with the player here
            data = self.player_sockets[player_id].socket.recv(1024)
            if not data:
                break  # Player disconnected
            print(f"Received from Joueur {player_id}: {data.decode()}")

        # Clean up when player disconnects
        print(f"Joueur {player_id} déconnecté")
        socket.close()


    def send_message(self, message):
        try:
            self.socket.send(message.encode('utf-8'))
        except socket.error as e:
            print(f"Erreur lors de l'envoi du message : {e}")

    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                print(f"Reçu du serveur : {data.decode('utf-8')}")
            except:
                break

    def deal_hands(self):
        hands = {}
        for player in self.players:
            hand = [self.draw_hand_card() for _ in range(5)]
            hands["player".format] = hand
        print(hands)
        json_hands = json.dumps(hands)
        print(json_hands)
        return hands
    
    def draw_hand_card(self):
        random_index = random.randint(0, len(self.players_deck)-1)
        random_card = self.players_deck.pop(random_index)
        return random_card
    
    def draw_card(self):
        new_card = self.deck.pop()


    def run_game(self):
        # Game logic implementation
        
        pass

    def start_game(self):
        self.init_shared_memory()
        print("shared mem done")
        self.deal_hands()
        print("hands dealt")
        self.game_process.start()
        print("process game started")

    def end_game(self):
        # Handle end-of-game events
        pass

