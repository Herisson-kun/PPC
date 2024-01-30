class Card():
    def __init__(self, color, number):
        self.color = color
        self.number = number
        self.dico_couleur = {"red": ["\033[1;31m", "\033[0m"], "blue": ["\033[1;34m", "\033[0m"], "green": ["\033[1;32m", "\033[0m"], "yellow": ["\033[1;33m", "\033[0m"], "white": ["\033[1;37m", "\033[0m"]}
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.color == other.color and self.number == other.number
        return False

    def __repr__(self):
        return f"{self.dico_couleur[self.color][0]}{self.number}{self.dico_couleur[self.color][1]}"

        