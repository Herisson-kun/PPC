import socket
from multiprocessing.managers import BaseManager
import random
import sys
import sysv_ipc
import os
from class_lock import Lock
import signal
import time


class Player:
    def __init__(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect('127.0.0.1', 8080)
        _, port = self.socket.getsockname()
        self.player_id = port
        self.my_pid = str(os.getpid())
        signal.signal(signal.SIGUSR1, self.victory_handler)
        signal.signal(signal.SIGUSR2, self.defeat_handler)  
        self.dico_couleur = {"red": ["\033[1;31m", "\033[0m"], "blue": ["\033[1;34m", "\033[0m"], "green": ["\033[1;32m", "\033[0m"], "yellow": ["\033[1;33m", "\033[0m"], "white": ["\033[1;37m", "\033[0m"]}
 

        # shared_memory
        self.shared_memory ={}
        self.init_shared_memory()

        print("===== Welcome to Hanabis ! =====\n")
        self.receive_message()
        print("\n=================================")


        self.send_message(self.my_pid)
        
        self.connected_to_neighbor = False
        self.init_network_message_queue()
        self.report_messages = []

        while True:            
            self.play()
            #self.shared

    def get_score(self):
        for color in self.shared_memory.get("colors"):
            try:
                score += self.shared_memory.get("suites").get(color).pop().number
            except:
                print("empty suite")

    def victory_handler (self, sig, frame):
        if sig == signal.SIGUSR1:
            self.end_game(True)

    def defeat_handler (self, sig, frame):
        if sig == signal.SIGUSR2:
            self.end_game(False)        
            
    def end_game(self, result):
        os.system('clear')
        score = self.receive_message(True).decode('utf-8')
        if result:
            print("====== End of the Game ======\n")
            print("YOU WIN !")
            print("Turns :", self.shared_memory.get("turn"))
            print("Score :", score)
            print("\n=============================")
        else:
            print("====== End of the Game ======\n")
            print("YOU LOST !")
            print("Score :", score)
            print("\n=============================")
        try:
            self.mq.remove()
        except:
            pass
        self.socket.close()
        print("Game is closing...")
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
            print(f"{self.dico_couleur[color][0]} {color} suite :{self.dico_couleur[color][1]}{suite}") 

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
            while not self.connected_to_neighbor:
                try:
                    self.mq_neighbor = sysv_ipc.MessageQueue(key_neighbor)
                    self.connected_to_neighbor = True
                except:
                    pass
   

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
                report_messages = f"Player{who_plays} : {msg}"
                
                report_messages = str(report_messages)
                
                self.report_messages.append(report_messages)
                if self.connected_to_neighbor == True:
                    self.mq_neighbor.send(msg)
            else:
                msg, _  = self.mq_neighbor.receive()
                msg = msg.decode()
                report_messages = f"Player{who_plays} : {msg}"
                
                
                self.report_messages.append(report_messages)
                #todo - rajouter une condition si on est le joueur le plus élevé pour éviter de remplir une msg q pour rien
                self.mq.send(msg)
        else:
            
            lock = self.shared_memory.get("lock")
            lock.acquire()
            self.shared_memory.update({"lock" : lock})
            
            print("/IT'S YOUR TURN !/")
            choice = self.input_choice()

            if choice == "play":
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
                    msg = (f"has played his card {[card_choice]} and it was at position {position}")

                    self.mq.send(msg)              
                    if self.connected_to_neighbor:
                        self.mq_neighbor.send(msg)    
                except:
                    print("Error, pas de carte jouée")      

                self.socket.send("DONE".encode())

            if choice == "info":

                if len(self.shared_memory.get("player_number")) > 2:
                    player_list = [1,2,3,4,5][:len(self.shared_memory.get("player_number"))]
                    player_list.remove(self.key)
                    to_who = int(input("\nChoose the player you want to give information to : "))
                    while to_who not in player_list:
                        to_who = int(input(f"Enter a valid player in {player_list} : "))
                else:
                    for player_number in self.shared_memory.get("player_number").values():
                        if player_number != self.key:
                            to_who = player_number
                            break

                kind_of_clue = input("\n'color': Clue about a single color;\n'number': Clue about a single number;\nChoose which kind of information you want to give : ")
                while kind_of_clue not in ["color","number"]:
                    kind_of_clue = input("Please enter 'color' or 'number' :")

                if kind_of_clue == "color":
                    color = input("Enter the color : ")
                    while color not in self.shared_memory.get("colors"):
                        color = input("Enter a valid color : ")
                    positions = []
                    number_of_clues = input("Enter the number of cards you want to give information about ")
                    while number_of_clues not in ["1","2","3","4","5"]:
                        number_of_clues = input("Enter a valid number : ")
                    number_of_clues = int(number_of_clues)
                    for i in range(number_of_clues):
                        
                        position = input("Enter the position of the card : ")
                        while position not in ["1","2","3","4","5"] or int(position) in positions:                            
                            position = input("Enter a valid number : ")

                        position = int(position)
                        positions.append(position)

                    msg = (f"Player{to_who} has {number_of_clues} {color} cards in his hand. Their positions are {positions}")

                if kind_of_clue == "number":
                    number = input("Enter the number : ")
                    while number not in ["1","2","3","4","5"]:
                        number = input("Enter a valid number : ")
                    positions = []
                    number_of_clues = input("Enter the number of card(s) you want to give information about ")
                    while number_of_clues not in ["1","2","3","4","5"]:
                        number_of_clues = input("Enter a valid number : ")
                    number_of_clues = int(number_of_clues)
                    for i in range(number_of_clues):
                        
                        position = input("Enter the position of the card : ")
                        while position not in ["1","2","3","4","5"] or int(position) in positions:             
                            position = input("Enter a valid number : ")                                     
                            
                        position = int(position)
                        positions.append(position)

                    msg = (f"Player{to_who} has {number_of_clues} card(s) with the number {number} in his hand. Their positions are {positions}")

                self.mq.send(msg)
                self.lose_info_token()
                self.report_messages.append(f"You said : {msg}")
                if self.connected_to_neighbor:
                    self.mq_neighbor.send(msg)
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
            choice = input("\n'play' : Play a card;\n'info' : Give an information;\n What will you do : ")
            if choice == "play" or  (choice == "info" and self.shared_memory.get("info_token") > 0):
                return choice
            else:
                print("Enter a valid action! : [play, info] ")

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
    
    def add_info_token(self, card):
        if card.number == 5:
            info_token = self.shared_memory.get("info_token") + 1
            self.shared_memory.update({"info_token": info_token})
            self.report_messages.append("You completed a suite ! You gain an info_token.")

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
            self.add_info_token(card)
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

    def receive_message(self, _result_=False):
        data = self.socket.recv(1024)
        if _result_:
            return data
        else:
            print(f"Received from server : {data.decode('utf-8')}")