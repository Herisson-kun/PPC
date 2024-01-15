import multiprocessing
import socket
import queue
import json
import random
import signal

class Game:
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory
        self.players = []
        self.players_deck = [1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5]
        self.deck = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        self.game_process = multiprocessing.Process(target=self.run_game)

    def init_shared_memory(self):
        self.shared_memory["colors"] = self.colors = ["blue", "red", "green", "yellow", "white"][:len(self.players)]
        self.shared_memory["fuse_token"] = 3
        self.shared_memory["info_token"] = len(self.players) + 3
        self.shared_memory["deck"] = random.shuffle(self.deck)
        self.shared_memory["suites"] = {f"{color}" : [] for color in self.shared_memory["colors"]}

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

    def run_game(self):
        # Game logic implementation
        
        pass

    def start_game(self):
        self.init_shared_memory()
        self.deal_hands()
        self.game_process.start()

    def end_game(self):
        # Handle end-of-game events
        pass

class Player:
    def __init__(self, player_id, shared_memory):
        self.player_id = player_id
        self.shared_memory = shared_memory
        self.hand = []
        self.message_queue = multiprocessing.Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.connect(('localhost', 8888))
    
    def display_hands(self):
        for player, hand in self.hands:
            print(f"Player {player.player_id}'s hand: {hand}")

    def run(self):
        # Player interaction logic
        pass

    def send_message(self, message):
        self.socket.send(message.encode())

    def receive_message(self):
        return self.socket.recv(1024).decode()

def signal_handler(signum, frame):
    # Handle signals, e.g., end of game
    pass

if __name__ == "__main__":
    """signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
"""
    shared_memory = multiprocessing.Manager().dict()
    player_list = []

    number_of_players = int(input("How many players ? (2 to 5) : "))
    while number_of_players not in range(2,6):
        print("-----------------------------------")
        print("You must choose a value from 2 to 5")
        number_of_players = int(input("Try again, how many players ? (2 to 5) : "))
        
    game_instance = Game(shared_memory)
    for i in range(number_of_players):
        player = Player(player_id=i+1, shared_memory=shared_memory)
        player_list.append(player)

    game_instance.players.extend(player_list)

    game_instance.start_game()

    for player in game_instance.players:
        multiprocessing.Process(target=player.run).start()

    # Wait for the game to finish
    game_instance.game_process.join()
