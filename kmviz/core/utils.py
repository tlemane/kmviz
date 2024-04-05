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

    if cov[-1]:
        n += (k-1)

    begin = [covyb[x-1] / x for x in range(1, k)]
    mid = [x / k for x in covyb[k-1:size-k+1]]
    end = [covyb[x] / (k-(i)) for i, x in enumerate(range(size-k, size-1))]
    covyb = begin + mid + end

    nk = size - k + 1
    return (m / nk), (n / size), sum(covyb) / size, covyb


