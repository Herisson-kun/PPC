import multiprocessing
import socket
import os
from multiprocessing.managers import BaseManager
import random

class Player:
    def __init__(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect('127.0.0.1', 8080)
        _, port = self.socket.getsockname()
        self.player_id = port

        self.report_messages = []
                
        # shared_memory
        self.shared_memory ={}

        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory'),  
        m = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()

        self.receive_message()
        
        while True:
            message = self.socket.recv(1024).decode().strip()
            os.system('cls')
            self.report_from_last_turn()
            self.show_info()

            if message == "YOUR TURN":
                print("\n/IT'S YOUR TURN !/")
                self.play()

            if message.startswith("TURN OF PLAYER"):
                player = message.split()[-1]
                print(f"\n/IT'S {player}'S TURN !/")
            
    def show_info(self):
        print("======== Turn Informations ========\n")
        
        # Affichage des mains des autres joueurs
        for player in self.shared_memory.get("hands"):
            if player != self.player_id:
                print(f"player{self.shared_memory.get('player_number').get(player)}'s hand : {self.shared_memory.get('hands').get(player)}")

        # Affichage des jetons restants
        print("\nRemaining Tokens:")
        print(f"Info Token: {self.shared_memory.get('info_token')}")
        print(f"Fuse Token: {self.shared_memory.get('fuse_token')}")

        # Affichage des suites en construction
        print("\nSuites in the Making:")
        for color, suite in self.shared_memory.get("suites").items():
            print(f"Suite {color}: {suite}")

        print("\n====================================")

    def report_from_last_turn(self):
        print("====== Report From Last Turn ======\n")
        for message in self.report_messages:
            print(message)
        print("\n===================================")

    def play(self):

        # game.self_lock.acquire()
        choice = self.input_choice()

        if choice == str(1):
            while True:
                try:
                    position, card_choice = self.input_position()
                except:
                    break
                if self.is_playable(card_choice):
                    playable = True
                    self.play_card(playable, card_choice, position)
                    break
                else:
                    playable = False
                    self.play_card(playable, card_choice, position)
                    break
            
            print("Turn is done")
            self.socket.send("DONE".encode())

                
        """elif choice == 2:
            self.socket.send("GIVE INFORMATION".encode())
            other_players =[p for p in self.shared_memory["players"] if p != self.id]
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
        self.message_queue = multiprocessing.Queue()"""
        # game.self_lock.release()
    
    def draw_card(self):
        deck = self.shared_memory.get("deck")
        random_index = random.randint(0, len(deck) - 1)
        random_card = deck.pop(random_index)
        self.shared_memory.update({"deck" : deck})
        return random_card

    def input_choice(self):
        while True:
            choice = input("What will you do ? : 1 to play card, 2 to give information\n")
            if choice == str(1) or  choice == str(2):
                return choice
            else:
                print("Enter a valid action!")
        
    def input_number(self):
        while True:
            number = input("Enter the number of the card you want to play (1-5): ")
            if number.isdigit():
                number = int(number)
                if 1 <= number <= 5:
                    return number
                else:
                    print("Please enter a number between 1 and 5.")
            else:
                print("This is not a valid number.")

    def input_color(self):
        while True:
            color = input("Enter the color of the card you want to play : ")
            if color in self.shared_memory.get("colors"):
                return color
            print("Enter a valid color.")
        
    def input_position(self):
        while True:
            position = input("Enter the position of the card you want to play (1-5): ")
            if position.isdigit():
                position = int(position)
                if 1 <= position <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            else:
                print("This is not a valid number.")
        card = self.shared_memory.get("hands").get(self.player_id)[position-1]
        return position, card
    
    def is_playable(self, card):

        if self.shared_memory.get("suites").get(card.color) == []:
            return True if card.number == 1 else False
        else:
            return True if card.number == self.shared_memory.get("suites").get(card.color).pop().number + 1 else False

    def lose_fuse_token(self):
        fuse_token = self.shared_memory.get("fuse_token") - 1
        self.shared_memory.update({"fuse_token": fuse_token})

    def remove_card_from_hand(self, position):
        new_hand = self.shared_memory.get("hands").get(self.player_id)
        new_hand.pop(position-1)
        new_hands = self.shared_memory.get("hands")
        new_hands[self.player_id] = new_hand
        self.shared_memory.update({"hands" : new_hands})

    def add_card_to_hand(self, position):
        random_card = self.draw_card()
        new_hand = self.shared_memory.get("hands").get(self.player_id)
        new_hand.insert(position-1, random_card)
        new_hands = self.shared_memory.get("hands")
        new_hands[self.player_id] = new_hand
        self.shared_memory.update({"hands" : new_hands})
        self.report_messages.append(f"The card {[random_card]} has been added to your hand at position {position}.")

    def add_card_to_suite(self, card):
        color = card.color
        new_suites = self.shared_memory.get("suites")
        new_suites[color].append(card)
        self.shared_memory.update({"suites" : new_suites})
    
    def play_card(self, playable, card, position):
        if playable:
            self.report_messages.append(f"{[card]} has been added to the {card.color} suite !")
            self.add_card_to_suite(card)
        else:
            self.report_messages.append(f"The card {[card]} is not playable... You lose a fuse_token.")
            self.lose_fuse_token()
            
        self.remove_card_from_hand(position)
        self.add_card_to_hand(position)


    def connect(self, host, port):
        self.socket.connect((host, port))
        print(f"Connecté au serveur {host}:{port}")

    def send_message(self, message, dest):
        try:
            self.players[dest].send(message.encode('utf-8'))
        except socket.error as e:
            print(f"Erreur lors de l'envoi du message : {e}")

    def receive_message(self):
        data = self.socket.recv(1024)
        print(f"Received from server : {data.decode('utf-8')}")
        
    def signal_handler(signum, frame):
        # Handle signals, e.g., end of game
        pass

player = Player()
