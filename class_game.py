import threading
import multiprocessing
import socket
import queue
import json
import random
import signal
from class_card import Card
from multiprocessing.managers import BaseManager
import time

class Game():

    def __init__(self, number_of_players):
        self.number_of_players = number_of_players
        self.player_id_counter = 1
        self.players = {}
        self.numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]

        process_shared_memory = multiprocessing.Process(target=self.run_shared_memory)
        process_shared_memory.start()

        self.init_shared_memory()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 8080))
        self.server_socket.listen(5)
        print(f"Le jeu écoute sur 127.0.0.1:8080")
        self.accept_players()

        self.build_shared_memory()
        print(self.shared_memory)
        print(self)
        print(self.players)
        for player in self.players:
            self.send_message("hello", player)
        self.run_game()

    def init_shared_memory(self):
        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory')
        m = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()

        print("initial shared_mem", self.shared_memory)

    def build_shared_memory(self):
        intermediate_data = dict()
        intermediate_data["colors"] = ["blue", "red", "green", "yellow", "white"][:len(self.players)]
        intermediate_data["fuse_token"] = 3
        intermediate_data["info_token"] = len(self.players) + 3
        intermediate_data["suites"] = {f"{color}" : [] for color in intermediate_data["colors"]}

        self.shared_memory.update(intermediate_data)
        self.create_deck()
        self.deal_hands()

    def run_shared_memory(self):
        shared_memory = {"player_number" : {}}
        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory', callable=lambda:shared_memory)
        m_serv = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        s_serv = m_serv.get_server()
        s_serv.serve_forever()
    
    def create_deck(self):
        deck = []
        for color in self.shared_memory.get('colors'):
            for value in self.numbers:
                cardToAppend = Card(color,value)
                deck.append(cardToAppend) 
        random.shuffle(deck)
        self.shared_memory.update({"deck": deck})       

    def accept_players(self):
        temp = {}
        while len(self.players)<self.number_of_players:
            player_socket, addr = self.server_socket.accept()

            player_id = addr[1]
            self.players[player_id] = player_socket
            temp[player_id] = self.player_id_counter
            print(f"Connected to {player_id}, player{self.player_id_counter}")
            self.player_id_counter += 1
            #player_handler = threading.Thread(target=self.handle_player, args=(player_socket, player_id))
            #player_handler.start()
        self.shared_memory.update({"player_number" : temp})
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

    def receive_message(self, exp, _return_=False):
        data = self.players[exp].recv(1024)
        print(f"Reçu du joueur {self.shared_memory.get('player_number').get(exp)} : {data.decode('utf-8')}")
        if _return_:
            return data
        

    def deal_hands(self):
        hands = {}
        for player in self.players:
            hand = [self.draw_card() for _ in range(5)]
            hands.update({player : hand})
        self.shared_memory.update({"hands" : hands})  
  
    def draw_card(self):
        deck = self.shared_memory.get('deck')
        random_index = random.randint(0, len(deck) - 1)
        random_card = deck.pop(random_index)
        self.shared_memory.update({"deck" : deck})
        return random_card

    def run_game(self):
        who_plays = 0
        while True:
            player = list(self.players.keys())[who_plays]
            self.send_message("YOUR TURN\n", player)
            action = self.receive_message(player, True)
            print(f"Player{self.shared_memory.get('player_number').get(player)} does : {action}")
            who_plays = (who_plays+1)%self.number_of_players
        
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
