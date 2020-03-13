

def round_by_base(x, base, mini=0):
    return int(base * round(x/base)) + mini