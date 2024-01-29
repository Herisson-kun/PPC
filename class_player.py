import socket
from multiprocessing.managers import BaseManager
import random
import sys
import sysv_ipc
import os
from class_lock import Lock
import signal


class Player:
    def __init__(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect('127.0.0.1', 8080)
        _, port = self.socket.getsockname()
        self.player_id = port
        self.my_pid = str(os.getpid())
        signal.signal(signal.SIGUSR1, self.victory_handler)
        signal.signal(signal.SIGUSR2, self.defeat_handler)      
        # shared_memory
        self.shared_memory ={}
        self.init_shared_memory()

        self.receive_message()


        self.send_message(self.my_pid)
        
        self.connected_to_neighbor = False
        self.init_network_message_queue()
        self.report_messages = []

        while True:            
            self.play()
            #self.shared


    def victory_handler (self, sig, frame):
        if sig == signal.SIGUSR1:
            self.end_game(True)

    def defeat_handler (self, sig, frame):
        if sig == signal.SIGUSR2:
            self.end_game(False)        
            
    def end_game(self, result):
        if result == True:
            print("WIN")
        else:
            print("LOOSE")
        print("Good bye have a nice day")
        try:
            self.mq.remove()
            print("mq closed")            
        except:
            pass
        self.socket.close()
        print("socket with game closed")
        os.kill(int(self.my_pid), signal.SIGKILL)

            
    def show_info(self):
        print("======== Turn Informations ========")
        
        #Affichage du numero de tour
        print(f"Turn n°{self.shared_memory.get('turn')}\n")

        # Affichage des mains des autres joueurs
        for player in self.shared_memory.get("hands"):
            if player != self.player_id:
                print(f"player{self.shared_memory.get('player_number').get(player)}'s hand : {self.shared_memory.get('hands').get(player)}")

        # Affichage des jetons restants
        print("\nRemaining Tokens:")
        print(f"Info Token: {self.shared_memory.get('info_token')}")
        print(f"Fuse Token: {self.shared_memory.get('fuse_token')}")

        # Affichage de la défausse
        print(f"\nDiscard Pile:", self.shared_memory.get("discard"))

        # Affichage des suites en construction
        print("\nSuites in the Making:")
        for color, suite in self.shared_memory.get("suites").items():
            print(f"{color} suite : {suite}")

        print("\n====================================")

    def report_from_last_turn(self):

            if self.shared_memory.get("turn") !=1:
                os.system('clear')
                print("====== Report From Last Turn ======\n")
                for message in self.report_messages:
                    print(message)
                print("\n===================================")


    def init_shared_memory(self):
        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory'),  
        m = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()

    def init_network_message_queue(self):
        self.key = self.shared_memory.get("player_number").get(self.player_id)
        print("You are Player", self.key)
        try:
            self.mq = sysv_ipc.MessageQueue(self.key, sysv_ipc.IPC_CREX)
        except:
            print("Message queue", self.key, "already exsits.")

        if self.key !=1:
            key_neighbor = self.key - 1
            self.mq_neighbor = sysv_ipc.MessageQueue(key_neighbor)
            #print("success link with player", key_neighbor)
            self.connected_to_neighbor = True
   

    def play(self):

        who_plays = self.socket.recv(1024).decode('utf-8')
        who_plays = int(who_plays)

        self.report_from_last_turn()
        self.report_messages = []
        self.show_info()

        if who_plays != self.key:
            print(f"/IT'S PLAYER{who_plays}'S TURN !/")
            who_plays = int(who_plays)
            if who_plays > self.key:
                
                msg, _  = self.mq.receive()
                msg = msg.decode()
                report_messages = f"Player{who_plays} {msg}"
                
                report_messages = str(report_messages)
                
                self.report_messages.append(report_messages)
                if self.connected_to_neighbor == True:
                    self.mq_neighbor.send(msg)
            else:
                msg, _  = self.mq_neighbor.receive()
                msg = msg.decode()
                report_messages = f"Player{who_plays} {msg}"
                
                
                self.report_messages.append(report_messages)
                #todo - rajouter une condition si on est le joueur le plus élevé pour éviter de remplir une msg q pour rien
                self.mq.send(msg)
        else:
            
            lock = self.shared_memory.get("lock")
            lock.acquire()
            self.shared_memory.update({"lock" : lock})
            
            print("/IT'S YOUR TURN !/")
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
                
                try:
                    msg = (f"has played his card {card_choice} and it was at position {position}")

                    self.mq.send(msg)              
                    if self.connected_to_neighbor:
                        self.mq_neighbor.send(msg)    
                except:
                    print("Error, pas de carte jouée")      

                self.socket.send("DONE".encode())

            if choice == str(2): #rajouter un while pour ne pas pouvoir rentrer autre chose que ce qui est voulu
                kind_of_clue = input("Choose which kind of information you want to give : \n1: Clue about a single color\n2: Clue about a single number\n")
                while kind_of_clue not in ["1","2"]:
                    kind_of_clue = input("Please enter 1 or 2 ")
                if kind_of_clue == str(1):
                    color = input("Enter the color : ")
                    while color not in self.shared_memory.get("colors"):
                        color = input("Enter a valid color : ")
                    positions = []
                    number_of_clues = input("Enter the number of cards you want to give information about ")
                    while number_of_clues not in ["1","2","3","4","5"]:
                        number_of_clues = input("Enter a valid number : ")
                    number_of_clues = int(number_of_clues)
                    for i in range(number_of_clues):
                        
                        position = input("Enter the position of the card ")
                        while position not in ["1","2","3","4","5"] or int(position) in positions:                            
                            position = input("Enter a valid number ")

                        position = int(position)
                        positions.append(position)

                    msg = (f"You have {number_of_clues} {color} cards in your hand. Their positions are {positions}")

                if kind_of_clue == str(2):
                    number = input("Enter the number :")
                    while number not in ["1","2","3","4","5"]:
                        number = input("Enter a valid number : ")
                    positions = []
                    number_of_clues = input("Enter the number of card(s) you want to give information about ")
                    while number_of_clues not in ["1","2","3","4","5"]:
                        number_of_clues = input("Enter a valid number : ")
                    number_of_clues = int(number_of_clues)
                    for i in range(number_of_clues):
                        
                        position = input("Enter the position of the card ")
                        while position not in ["1","2","3","4","5"] or int(position) in positions:             
                            position = input("Enter a valid number ")                                     
                            
                        position = int(position)
                        positions.append(position)

                    msg = (f"You have {number_of_clues} card(s) with the number {number} in your hand. Their positions are {positions}")

                self.mq.send(msg)
                self.lose_info_token()
                self.report_messages.append(f"You said : {msg}")
                if self.connected_to_neighbor:
                    self.mq_neighbor.send(msg)

                self.socket.send("DONE".encode())

            if choice == "3":
                self.mq.remove()
                self.socket.send("DONE".encode())

            lock.release()
            self.shared_memory.update({"lock" : lock})
            

    
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

    def lose_info_token(self):
        info_token = self.shared_memory.get("info_token") -1
        self.shared_memory.update({"info_token": info_token})

    def remove_card_from_hand(self, position, is_discarded):
        new_hand = self.shared_memory.get("hands").get(self.player_id)
        card = new_hand.pop(position-1)
        new_hands = self.shared_memory.get("hands")
        new_hands[self.player_id] = new_hand
        self.shared_memory.update({"hands" : new_hands})
        
        if is_discarded:
            new_discard_cards = self.shared_memory.get("discard")
            new_discard_cards.append(card)
            self.shared_memory.update({"discard": new_discard_cards})

    def add_card_to_hand(self, position):
        random_card = self.draw_card()
        new_hand = self.shared_memory.get("hands").get(self.player_id)
        new_hand.insert(position-1, random_card)
        new_hands = self.shared_memory.get("hands")
        new_hands[self.player_id] = new_hand
        self.shared_memory.update({"hands" : new_hands})

    def add_card_to_suite(self, card):
        color = card.color
        new_suites = self.shared_memory.get("suites")
        new_suites[color].append(card)
        self.shared_memory.update({"suites" : new_suites})
    
    def play_card(self, playable, card, position):
        if playable:
            self.report_messages.append(f"{[card]} has been added to the {card.color} suite !")
            self.add_card_to_suite(card)
            self.remove_card_from_hand(position, False)
        else:
            self.report_messages.append(f"The card {[card]} is not playable... You lose a fuse_token.")
            self.lose_fuse_token()
            self.remove_card_from_hand(position, True)
        
        try:
            self.add_card_to_hand(position)
        except:
            self.report_messages.append("Deck is empty.")


    def connect(self, host, port):
        self.socket.connect((host, port))
        print(f"Connecté au serveur {host}:{port}")

    def send_message(self, message):
        try:
            self.socket.send(message.encode('utf-8'))
        except socket.error as e:
            print(f"Erreur lors de l'envoi du message : {e}")

    def receive_message(self):
        data = self.socket.recv(1024)
        print(f"Received from server : {data.decode('utf-8')}")
        

    def signal_handler(signum, frame):
        # Handle signals, e.g., end of game
        pass