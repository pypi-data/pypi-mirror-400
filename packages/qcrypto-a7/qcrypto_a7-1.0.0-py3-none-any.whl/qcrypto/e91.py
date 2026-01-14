import random

def generate_e91_key(length=64, eve=False):
    alice_measurements = []
    bob_measurements = []

    for _ in range(length):
        entangled_bit = random.choice(["0", "1"])

        alice_basis = random.choice(["Z", "X"])
        bob_basis = random.choice(["Z", "X"])

        alice_bit = entangled_bit
        bob_bit = entangled_bit

        if eve:
            # Eve disturbs entanglement
            bob_bit = random.choice(["0", "1"])

        if alice_basis == bob_basis:
            alice_measurements.append(alice_bit)
            bob_measurements.append(bob_bit)

    key = [
        a for a, b in zip(alice_measurements, bob_measurements) if a == b
    ]
    return "".join(key)

#This is the basic implemenation of E91 - ENTANGLEMENT PROTOCOL
#Contact me : patnamkannabhiram@gmail.com , a7sgarage@gmail.com
