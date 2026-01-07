import datetime

class Intake:
    def __init__(self, food_name, quantity, kcal, timestamp, feeling=None, bathroom=None):
        self.food_name = food_name
        self.quantity = quantity
        self.kcal = kcal
        self.timestamp = timestamp
        self.feeling = feeling  # Después de comer
        self.bathroom = bathroom  # Info de baño