from typing import Tuple, List, Iterable

def covxb_from_covxk(cov: Iterable[int], k: int, size: int) -> Tuple[float, List[int]]:
    covxb = [0 for _ in range(size)]
    for i, value in enumerate(cov):
        if value:
            covxb[i:i+k] = [value] * k
    return sum(covxb) / size, covxb

def covyb_from_covyk(cov: Iterable[int], k: int, size: int) -> Tuple[float, List[int]]:
    covyb = [0 for _ in range(size)]
    n = 0
    m = 0
    for i, value in enumerate(cov):
        if value:
            for j in range(i, i+k):
                covyb[j] += value
            n += 1
            m += value

    covyb = [x / k for x in covyb]

    nk = size - k + 1
    return (m / nk), (n / size), sum(covyb) / size, covyb


