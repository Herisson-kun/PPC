from class_game import Game
from multiprocessing import process, Lock, Manager

if __name__ == "__main__":

    shared_memory = Manager().dict()
    game_instance = Game(2)
