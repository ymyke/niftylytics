import itertools

def ranges(i):
    for a, b in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield b[0][1], b[-1][1]

print(list(ranges(sorted([int(x) for x in meridian_ids]))))
