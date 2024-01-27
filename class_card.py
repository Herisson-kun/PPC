class Card():
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.color == other.color and self.number == other.number
        return False

    def __repr__(self):
        return f"{self.color}:{self.number}"
        