import threading
import socket
import queue
import json
import random
import signal
from class_card import Card
from multiprocessing.managers import BaseManager

class Game():
    def __init__(self):

        self.player_id_counter = 1
        self.players = {}

        # self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.bind(('127.0.0.1', 8080))
        # self.server_socket.listen(5)
        #print(f"Le jeu écoute sur 127.0.0.1:8080")
        self.player_sockets = {}  # Dictionnaire pour stocker les sockets des joueurs {player:socket}
        #self.accept_players()

        self.shared_memory = dict()
        self.players_deck = []
        self.deck = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        self.init_shared_memory()
        self.create_deck()

    def init_shared_memory(self):
        class QueueManager(BaseManager): pass
        QueueManager.register('get_memory')
        m = QueueManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()
        print(self.shared_memory)
        intermediate_data = dict()
        intermediate_data["colors"] = ["blue", "red", "green", "yellow", "white"][:len(self.players)+2]
        intermediate_data["fuse_token"] = 3
        intermediate_data["info_token"] = len(self.players) + 3
        intermediate_data["deck"] = random.shuffle(self.deck)
        intermediate_data["suites"] = {f"{color}" : [] for color in intermediate_data["colors"]}

        self.shared_memory.update(intermediate_data)
        print(self.shared_memory)
        
    
    def create_deck(self):
        for color in self.shared_memory.get("colors",0):
            for value in self.deck:
                cardToAppend = Card(color,value)
                self.players_deck.append(cardToAppend)
            print(self.players_deck)
        

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
        random_card = self.players_deck.remove(random_index)
        return random_card
    
    def draw_card(self):
        new_card = self.deck.pop()


    def run_game(self):
        # Game logic implementation
        
        pass

    def start_game(self):
        self.init_shared_memory()
        print("shared mem done")
        """self.create_deck()
        for carte in self.players_deck:
            print(f"{carte.color} , {carte.number}")
        self.deal_hands()
        print("hands dealt")"""
        #self.game_process.start()
        #print("process game started")

game = Game()