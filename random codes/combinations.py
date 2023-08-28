# utf-8
from itertools import permutations
from typing import Iterable


def getCombo(seq: Iterable[int], goal: int):
    counter = 0
    # seq.extend(("+", "-", "+", "-", "+"))
    seq = [str(i) for i in seq]
    for item in permutations(seq, len(seq)):
        string = "".join(item)
        print(repr(string))
    return counter


getCombo([1, 1, 1, 1, 1], 3)
