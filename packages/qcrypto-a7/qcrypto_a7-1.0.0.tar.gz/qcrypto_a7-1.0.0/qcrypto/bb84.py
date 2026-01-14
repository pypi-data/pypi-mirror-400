import random
from .qubits import Qubit

def generate_bb84_key(length=64, eve=False):
    alice_bits = [random.choice(["0", "1"]) for _ in range(length)]
    alice_bases = [random.choice(["Z", "X"]) for _ in range(length)]

    qubits = []
    for bit, base in zip(alice_bits, alice_bases):
        if base == "Z":
            qubits.append(Qubit(bit))
        else:
            qubits.append(Qubit("+" if bit == "0" else "-"))

    if eve:
        for q in qubits:
            q.measure(random.choice(["Z", "X"]))

    bob_bases = [random.choice(["Z", "X"]) for _ in range(length)]
    key = []

    for i in range(length):
        result = qubits[i].measure(bob_bases[i])
        if alice_bases[i] == bob_bases[i]:
            key.append(alice_bits[i])

    return "".join(key)
#This is the basic implemenation of BB84
#Contact me : patnamkannabhiram@gmail.com , a7sgarage@gmail.com

