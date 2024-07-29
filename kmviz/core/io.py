import os
import shutil
from pathlib import Path

from Bio import SeqIO

from kmviz.core import KmVizError
from io import StringIO

class KmVizIOError(KmVizError):
    pass

class KmVizInvalidQuery(KmVizIOError):
    pass

def is_fasta(content: str) -> bool:
    sio = StringIO(content)
    return any(SeqIO.parse(sio, "fasta"))

def is_fastq(content: str) -> bool:
    sio = StringIO(content)
    fq = SeqIO.parse(sio, "fastq")
    try:
        return any(fq)
    except Exception as e:
        return False

def input_type(content: str) -> str:
    if is_fasta(content):
        return "fasta"
    if is_fastq(content):
        return "fastq"

    raise KmVizIOError("Unsupported format, should be fasta/q.")

AMINO_ALPHABET = set("ABCDEFGHIKLMNPQRSTVWXYZabcdefghiklmnpqrstvwxyz")
DNA_ALPHABET = set("ACGTacgt")

def is_amino(content: str) -> bool:
    return all(c in AMINO_ALPHABET for c in content)

def is_dna(content: str) -> bool:
    return all(c in DNA_ALPHABET for c in content)

def validate_alphabet(seq, alpha):
    if alpha == "dna":
        return is_dna(seq)
    elif alpha == "amino":
        return is_amino(seq)
    else:
        return True

def validate_input(idx, seq, seq_size, max_size, nb, limits):
    if nb > limits.max_query:
        raise KmVizIOError(f"The max number of queries is {limits.max_query}")
    if seq_size > limits.max_query_size:
        raise KmVizIOError(f"Query max size is {limits.max_query_size} ({idx}:{seq_size})")
    if max_size > limits.max_size:
        raise KmVizIOError(f"Max cumulative query size is {limits.max_size} ({limits.max_size})")
    if not validate_alphabet(seq, limits.alphabet):
        raise KmVizIOError(f"Alphabet is not '{limits.alphabet}'")


def parse_fastx(content: str, limits: dict):
    sio = StringIO(content)
    max_size = 0
    nb = 0
    for record in SeqIO.parse(sio, input_type(content)):
        if len(record.seq) == 0:
            raise KmVizIOError("Empty sequence found.")

        seq_size = len(record.seq)
        max_size += seq_size
        nb += 1

        if limits is not None:
            validate_input(record.id, record.seq, seq_size, max_size, nb, limits)

        yield record.id, str(record.seq), None

def make_url(url: str, route: str=None, port: int=None) -> str:
    res = url
    if port:
        res += f":{port}"
    if route:
        res += route
    return res

def rm(*paths):
    for path in paths:
        p = Path(path)
        if p.is_file() or p.is_symlink():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)