import multiprocessing
import socket
from multiprocessing.managers import BaseManager


class Player:
    def __init__(self):
        # player_id and player_socket
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.connect('127.0.0.1', 8080)
        # _, port = self.socket.getsockname()
        # self.player_id = port
        
        # shared_memory
        self.shared_memory ={}

        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory'),  
        m = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()
        print(self.shared_memory)
        self.shared_memory.update({"remy": "coucou", "johan": "yo"})
        self.shared_memory.update({"salut":1})
        print(self.shared_memory)

        # self.message_queue = multiprocessing.Queue()
        
    def play(self, game, shared_memory, msg_queue):
        
        message = self.socket.recv(1024).decode()
        while message != "Your turn\n":
            print(message)

        game.self_lock.acquire()
        while True:
            choice = input("Enter the number of your choice: 1 to play card, 2 to give information\n")
            if choice == 1 or  choice == 2:
                break
            else:
                print("Enter a valid number")
            
        if choice == 1:
            card_choice = input("Enter the number of the card you want to play\n")
            while True:
                if card_choice:
                    break
                else:
                    print("Enter a valid number for card that you want to play")
            card_played = self.hand[card_choice]
            card_played.played = True
            self.hand.pop(card_choice)  # remove the card from hand
            self.socket.send(f"PLAY CARD".encode())
            self.socket.send(f"PLAY CARD {card_choice}".encode())
                
        elif choice == 2:
            self.socket.send("GIVE INFORMATION".encode())
            other_players =[p for p in shared_memory["players"] if p != self.id]
            player_choice = input(f"Enter the number of the player among {other_players} you want to give information to \n")
            while True:
                try:
                    player_choice = int(player_choice)
                    break
                except:
                    print("Enter a valid number for player that you want to give information to")            
            
            #print(cards_info)
            info_choice = input(f"Enter the type of the information you want to give, 1 for color, 2 for number\n")
            while True:
                try:
                    info_choice = int(info_choice)
                    break
                except:
                    print("Enter a valid number for type of information")

    def run(self):
        # Player interaction logic
        pass

    def connect(self, host, port):
        self.socket.connect((host, port))
        print(f"Connecté au serveur {host}:{port}")
        self.send_message(f"Hello")

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

    def signal_handler(signum, frame):
        # Handle signals, e.g., end of game
        pass

player = Player()