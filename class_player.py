import multiprocessing
import socket
from multiprocessing.managers import BaseManager

class Player:
    def __init__(self, player_id=None):
        # player_id and player_socket
        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.connect('127.0.0.1', 8080)
        #_, port = self.socket.getsockname()
        #self.player_id = port
        
        # shared_memory
        #self.shared_memory = shared_memory

        self.hand = []

        self.message_queue = multiprocessing.Queue()

       
        class QueueManager(BaseManager): pass
        QueueManager.register('get_queue')
        self.shared_memory = QueueManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        self.shared_memory.connect()
        
        
    def update_shared_memory(self):
        dico = self.shared_memory.get_queue()
        
        dico.update({"remy": "coucou", "johan": "yo"})
        dico.update({"salut":1})
        print("dans update :",dico)

    def check_shared_memory(self):
        queue = self.shared_memory.get_queue()
        print("dans check : ",queue)


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

if __name__ == "__main__":
    p1 = Player("P1")
    p1.update_shared_memory()
    p1.check_shared_memory()