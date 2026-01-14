def error_rate(key1, key2):
    length = min(len(key1), len(key2))
    errors = sum(1 for i in range(length) if key1[i] != key2[i])
    return errors / length if length else 0
