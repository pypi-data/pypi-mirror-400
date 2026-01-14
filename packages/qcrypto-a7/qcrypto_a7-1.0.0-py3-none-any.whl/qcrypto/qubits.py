import random

class Qubit:
    def __init__(self, state):
        self.state = state

    def measure(self, basis):
        if basis == "Z":
            if self.state in ["0", "1"]:
                return self.state
            return random.choice(["0", "1"])

        if basis == "X":
            if self.state in ["+", "-"]:
                return self.state
            return random.choice(["+", "-"])
