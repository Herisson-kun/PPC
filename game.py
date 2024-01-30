from class_game import Game

def correct_input():
    while True:
        try:
            number_of_players = int(input("How many players? "))
            if  6 > number_of_players > 0:
                return number_of_players
            else:
                print("Please, enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a positive integer.")

if __name__ == "__main__":
    

    game_instance = Game(correct_input())
