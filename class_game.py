import multiprocessing
import threading
import socket
import queue
import json
import random
import signal
from class_player import Player
from class_card import Card

class Game():
    def __init__(self, shared_memory):

        self.player_id_counter = 1
        """ exemples de joueurs a suppr plus tard """
        player1 = Player("P1")
        player2 = Player("P2")
        self.players = [player1,player2]

        #self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server_socket.bind(('127.0.0.1', 8080))
        #self.server_socket.listen(5)
        #print(f"Le jeu écoute sur 127.0.0.1:8080")
        self.player_sockets = {}  # Dictionnaire pour stocker les sockets des joueurs {player:socket}
        #self.accept_players()

        self.shared_memory = shared_memory

        self.players_deck = []
        self.deck = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]


    def init_shared_memory(self):
        self.shared_memory["colors"] = ["blue", "red", "green", "yellow", "white"][:len(self.players)]
        self.shared_memory["fuse_token"] = 3
        self.shared_memory["info_token"] = len(self.players) + 3
        self.shared_memory["deck"] = random.shuffle(self.deck)
        self.shared_memory["suites"] = {f"{color}" : [] for color in self.shared_memory["colors"]}

    def create_deck(self):
        """Creation de la pioche avec 10 cartes par couleurs"""
        for color in self.shared_memory["colors"]:           
            for value in self.deck:
                cardToAppend = Card(color,value)
                self.players_deck.append(cardToAppend)
        
        

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
        """ Creation de la main de 5 cartes pour un joueur sous la forme d'une liste de Card"""
        hands = []
        for i in range (5):
            drawn_card = self.draw_card()
            hands.append(drawn_card)
            
        return hands
    
    def draw_card(self):
        """Choisis une carte au hasard dans la liste players_deck la supprime de cette
        derniere et return la carte"""
        random_index = random.randint(0, len(self.players_deck)-1)
        random_card = self.players_deck[random_index]
        del self.players_deck[random_index]
        return random_card
    
   


    def run_game(self):
        # Game logic implementation
        
        pass

    def start_game(self):
        self.init_shared_memory()
        print("shared mem done")
        self.create_deck()
        for player in self.players:
            player.hand = self.deal_hands()
            print(player.player_id)
            for card in player.hand:
                print(f"{card.color} , {card.number}")

        print("hands dealt")
        print("cartes restantes")
        for card in self.players_deck:
            print(f"{card.color} , {card.number}")
        #self.game_process.start()
        #print("process game started")

    def end_game(self):
        # Handle end-of-game events
        pass

