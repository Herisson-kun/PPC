import socket
from multiprocessing.managers import BaseManager
import random
import sys
import sysv_ipc
import os
from class_lock import Lock



class Player:
    def __init__(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect('127.0.0.1', 8080)
        _, port = self.socket.getsockname()
        self.player_id = port
                
        # shared_memory
        self.shared_memory ={}
        self.init_shared_memory()

        self.receive_message()
        self.send_message( "hello")
        
        self.connected_to_neighbor = False
        self.init_network_message_queue()

        while True:
            self.report_from_last_turn()
            self.show_info()
            self.report_messages = []
            self.play()
            
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
        print(f"\nThe Discard Pile:", self.shared_memory.get("discard"))

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


    def init_shared_memory(self):
        class MemoryManager(BaseManager): pass
        MemoryManager.register('get_memory'),  
        m = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
        m.connect()
        self.shared_memory = m.get_memory()

    def init_network_message_queue(self):
        self.key = self.shared_memory.get("player_number").get(self.player_id)
        print("my key : ", self.key)
        try:
            self.mq = sysv_ipc.MessageQueue(self.key, sysv_ipc.IPC_CREX)
        except:
            print("Message queue", self.key, "already exsits.")

        if self.key !=1:
            key_neighbor = self.key - 1
            self.mq_neighbor = sysv_ipc.MessageQueue(key_neighbor)
            print("success link with player", key_neighbor)
            self.connected_to_neighbor = True
   

        

        #for player in self.shared_memory.get('player_number'):


    def play(self):

        lock = self.shared_memory.get("lock")
        print(lock.value)
        
        who_plays = self.socket.recv(1024).decode('utf-8')
        who_plays = int(who_plays)

        if who_plays != self.key:
            print(f"/IT'S PLAYER{who_plays}'S TURN !/")
            who_plays = int(who_plays)
            if who_plays > self.key:
                
                msg, _  = self.mq.receive()
                msg = msg.decode()
                self.report_messages.append("clue from ", self.key + 1, " : ", msg)
                if self.connected_to_neighbor == True:
                    self.mq_neighbor.send(msg)
            else:
                msg, _  = self.mq_neighbor.receive()
                msg = msg.decode()
                self.report_messages.append("clue from ", self.key + 1, " : ", msg)
                #todo - rajouter une condition si on est le joueur le plus élevé pour éviter de remplir une msg q pour rien
                self.mq.send(msg)
        else:
            
            lock = self.shared_memory.get("lock")
            print(lock.value)
            lock.acquire()
            self.shared_memory.update({"lock" : lock})
            print("lock acquired", self.shared_memory.get("lock").value)

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
                
                print("Turn is done")
                self.socket.send("DONE".encode())

            if choice == str(2):
                msg = input("Give your information here : ")
                self.mq.send(msg)
                self.lose_info_token()

                if self.connected_to_neighbor:
                    self.mq_neighbor.send(msg)

                print("Turn is done")
                self.socket.send("DONE".encode())

            if choice == "3":
                self.mq.remove()
                print("Turn is done")
                self.socket.send("DONE".encode())

            lock.release()
            self.shared_memory.update({"lock" : lock})
            print("lock released", self.shared_memory.get("lock").value)


            
    
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

    def remove_card_from_hand(self, position):
        new_hand = self.shared_memory.get("hands").get(self.player_id)
        card = new_hand.pop(position-1)
        new_hands = self.shared_memory.get("hands")
        new_hands[self.player_id] = new_hand
        
        new_discard_cards = self.shared_memory.get("discard")
        new_discard_cards.append(card)

        self.shared_memory.update({"hands" : new_hands, "discard": new_discard_cards})


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

player = Player()
