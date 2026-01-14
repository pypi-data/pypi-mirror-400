def encrypt(msg, key):
    return "".join(
        chr(ord(c) ^ ord(key[i % len(key)]))
        for i, c in enumerate(msg)
    )

def decrypt(cipher, key):
    return encrypt(cipher, key)
