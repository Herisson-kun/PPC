from class_player import Player
from class_game import Game
from multiprocessing import process, Lock, Manager
"""
if __name__ == "__main__":
    #signal.signal(signal.SIGTERM, signal_handler)
    #signal.signal(signal.SIGINT, signal_handler)

    shared_memory = Manager().dict()
    Lock = Lock()

    game_instance = Game(shared_memory)
    
    print("hey")
    player_1 = Player(shared_memory)
    print(player_1.player_id)
    player_1.receive_messages()

    # Wait for the game to finish
    game_instance.game_process.join()

    """

if __name__ == "__main__":
    shared_memory = Manager().dict()
    Lock = Lock()

    game_instance = Game(shared_memory)
    
    game_instance.start_game()
    #game_instance.game_process.join()