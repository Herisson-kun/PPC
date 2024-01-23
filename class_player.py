import multiprocessing
import socket

class Player:
    def __init__(self, player_id=None, shared_memory=None):
        # player_id and player_socket
        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.connect('127.0.0.1', 8080)
        #_, port = self.socket.getsockname()
        self.player_id = player_id
        
        # shared_memory
        self.shared_memory = shared_memory

        self.hand = []

        #self.message_queue = multiprocessing.Queue()
        
    
    def display_hands(self):
        for player, hand in self.hands:
            print(f"Player {player.player_id}'s hand: {hand}")

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