import random

def add_noise(key, probability=0.05):
    noisy = ""
    for bit in key:
        if random.random() < probability:
            noisy += "1" if bit == "0" else "0"
        else:
            noisy += bit
    return noisy
