from typing import Tuple, List, Iterable
from executor import execute, ExternalCommandFailed
from kmviz.core.io import KmVizInvalidQuery

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


def make_cmd(executable: str, subcmd: str, prefix: str="", *args, **kwargs):
    cmd = executable

    if subcmd:
        cmd += f" {subcmd}"

    for k, v in kwargs.items():
        if v is not None:
            cmd += f" {prefix}{k} {v}"
        else:
            cmd += f" {prefix}{k}"

    for e in args:
        cmd += f" {args}"

    return cmd

def exec_cmd(cmd: str, **options):
    try:
        return execute(cmd, **options)
    except ExternalCommandFailed as ec:
        raise KmVizInvalidQuery(str(ec))
