from typing import Tuple, List, Iterable

def covxb_from_covxk(cov: Iterable[int], k: int, size: int) -> Tuple[float, List[int]]:
    covxb = [0 for _ in range(size)]
    n = 0
    for i, value in enumerate(cov):
        if value:
            covxb[i:i+k] = [value] * k
            n += 1

    return (n / size), covxb

