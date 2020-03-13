def round_by_base(x, base, min):
    return int(base * round(x / base)) + abs(min) % base
