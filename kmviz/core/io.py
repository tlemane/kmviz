
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

def parse_fastx(content: str):
    sio = StringIO(content)
    for record in SeqIO.parse(sio, input_type(content)):
        if len(record.seq) == 0:
            raise KmVizIOError(f"Empty sequence found.")
        yield record.id, str(record.seq), None


def readfq(fp): # this is a generator function
    last = None # this is a buffer keeping the last unprocessed line
    while True: # mimic closure; is it a bad idea?
        if not last: # the first record or a record following a fastq
            for l in fp: # search for the start of the next record
                if l[0] in '>@': # fasta/q header line
                    last = l[:-1] # save this line
                    break
        if not last: break
        name, seqs, last = last[1:].partition(" ")[0], [], None
        for l in fp: # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+': # this is a fasta record
            yield name, ''.join(seqs), None # yield a fasta record
            if not last: break
        else: # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp: # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq): # have read enough quality
                    last = None
                    yield name, seq, ''.join(seqs); # yield a fastq record
                    break
            if last: # reach EOF before reading enough quality
                yield name, seq, None # yield a fasta record instead
                break
