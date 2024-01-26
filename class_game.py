import threading
import socket
import queue
import json
import random
import signal
from class_card import Card
from multiprocessing.managers import BaseManager

class Game():

    def __init__(self, number_of_players):
        self.number_of_players = number_of_players
        self.player_id_counter = 1
        self.players = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 8080))
        self.server_socket.listen(5)
        print(f"Le jeu écoute sur 127.0.0.1:8080")
        self.accept_players()

        self.shared_memory = dict()
        self.numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        self.init_shared_memory()
        print(self.shared_memory)
        print(self)
        self.send_message("salut", list(self.players.keys())[0])

    def init_shared_memory(self):
        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory')
        m = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()

        print("initial shared_mem", self.shared_memory)

        intermediate_data = dict()
        intermediate_data["colors"] = ["blue", "red", "green", "yellow", "white"][:len(self.players)]
        intermediate_data["fuse_token"] = 3
        intermediate_data["info_token"] = len(self.players) + 3
        intermediate_data["suites"] = {f"{color}" : [] for color in intermediate_data["colors"]}

        self.shared_memory.update(intermediate_data)
        self.create_deck()
        self.deal_hands()
    
    def create_deck(self):
        deck = []
        for color in self.shared_memory.get("colors",0):
            for value in self.numbers:
                cardToAppend = Card(color,value)
                deck.append(cardToAppend) 
        random.shuffle(deck)
        print(len(deck))
        self.shared_memory.update({"deck": deck})       

    def accept_players(self):
        while len(self.players)<self.number_of_players:
            player_socket, addr = self.server_socket.accept()
            player_id = addr[1]
            self.players[player_id] = player_socket
            print(f"Connexion établie avec {player_id}")
            #player_handler = threading.Thread(target=self.handle_player, args=(player_socket, player_id))
            #player_handler.start()
        print("Everyone is connected, the game may begin")

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


    def send_message(self, message, dest):
        try:
            self.players[dest].send(message.encode('utf-8'))
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
            hand = [self.draw_card() for _ in range(5)]
            hands.update({player : hand})
        self.shared_memory.update({"hands" : hands})  
  
    def draw_card(self):
        deck = self.shared_memory.get("deck")
        random_index = random.randint(0, len(deck) - 1)
        random_card = deck.pop(random_index)
        self.shared_memory.update({"deck" : deck})
        return random_card

    def run_game(self):
        # Game logic implementation
        
        pass

    def start_game(self):
        print("shared mem done")
        """self.create_deck()
        self.create_deck()
        for carte in self.players_deck:
            print(f"{carte.color} , {carte.number}")
        self.deal_hands()
        print("hands dealt")
        print("hands dealt")"""
        #self.game_process.start()
        #print("process game started")

game = Game(2)