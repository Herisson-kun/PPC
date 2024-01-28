import threading
import multiprocessing
import socket
import random
import signal
from class_card import Card
from multiprocessing.managers import BaseManager
from class_lock import Lock

class Game():

    def __init__(self, number_of_players):
        self.number_of_players = number_of_players
        self.player_id_counter = 1
        self.players = {}
        self.numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]

        lock = threading.Lock()
        thread_shared_memory = threading.Thread(target=self.run_shared_memory, args=(lock,))
        thread_shared_memory.start()
        self.init_shared_memory(lock)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 8080))
        self.server_socket.listen(5)
        print(f"Le jeu écoute sur 127.0.0.1:8080")
        self.accept_players()

        self.build_shared_memory()
        print(self.shared_memory)
        
        for player in self.players:
            self.send_message("hello", player)

        for player in self.players:
            self.receive_message(player)

        self.run_game()
        


    def init_shared_memory(self, lock):
        lock.acquire()
        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory')
        m = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()
        print("initial shared_mem", self.shared_memory)
        lock.release()

    def build_shared_memory(self):
        intermediate_data = dict()
        intermediate_data["lock"] = Lock()
        intermediate_data["colors"] = ["blue", "red", "green", "yellow", "white"][:len(self.players)]
        intermediate_data["fuse_token"] = 3
        intermediate_data["info_token"] = len(self.players) + 3
        intermediate_data["suites"] = {f"{color}" : [] for color in intermediate_data["colors"]}

        self.shared_memory.update(intermediate_data)
        self.create_deck()
        self.deal_hands()

    def run_shared_memory(self, lock):
        lock.acquire()
        shared_memory = {"player_number" : {}}
        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory', callable=lambda:shared_memory)
        m_serv = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        s_serv = m_serv.get_server()
        lock.release()
        s_serv.serve_forever()


    def create_deck(self):
        deck = []
        for color in self.shared_memory.get('colors'):
            for value in self.numbers:
                cardToAppend = Card(color,value)
                deck.append(cardToAppend) 
        random.shuffle(deck)
        self.shared_memory.update({"deck": deck})
    
    def draw_card(self):
        deck = self.shared_memory.get('deck')
        random_index = random.randint(0, len(deck) - 1)
        random_card = deck.pop(random_index)
        self.shared_memory.update({"deck" : deck})
        return random_card
    
    def deal_hands(self):
        hands = {}
        for player in self.players:
            hand = [self.draw_card() for _ in range(5)]
            hands.update({player : hand})
        self.shared_memory.update({"hands" : hands})  


    def accept_players(self):
        temp = {}
        while len(self.players)<self.number_of_players:
            player_socket, addr = self.server_socket.accept()

            player_id = addr[1]
            self.players[player_id] = player_socket
            temp[player_id] = self.player_id_counter
            print(f"Connected to {player_id}, player{self.player_id_counter}")
            self.player_id_counter += 1
            
        self.shared_memory.update({"player_number" : temp})
        print("Everyone is connected, the game may begin")


    def send_message(self, message, dest):
        try:
            #self.players[dest].shutdown(socket.SHUT_WR)
            self.players[dest].send(message.encode('utf-8'))
            
        except socket.error as e:
            print(f"Erreur lors de l'envoi du message : {e}")

    def receive_message(self, exp, _return_=False):
        data = self.players[exp].recv(1024)
        print(f"Reçu du joueur {self.shared_memory.get('player_number').get(exp)} : {data.decode('utf-8')}")
        if _return_:
            return data


    def run_game(self):
        who_plays = 0
        while True:
            player_playing = list(self.players.keys())[who_plays]
            player_turn_number = who_plays + 1
            player_turn_number = str(player_turn_number)
            print("\nCest le tour du joueur : ", player_turn_number)
            for player in self.players:
                self.send_message(player_turn_number, player)
            action = self.receive_message(player_playing, True)
            print(f"Player{self.shared_memory.get('player_number').get(player)} does : {action}")
            who_plays = (who_plays+1)%self.number_of_players
