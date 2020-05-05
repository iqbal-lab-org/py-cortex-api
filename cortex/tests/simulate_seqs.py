import random
from typing import List, NamedTuple, Tuple, Sequence
from enum import Enum
from pathlib import Path

from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio import SeqIO


class DNA(Enum):
    A = "A"
    C = "C"
    G = "G"
    T = "T"


dna_choices = [base.value for base in DNA]

DNAString = Sequence[DNA]


class SeqRecords:
    def __init__(self, records: List[SeqRecord]):
        self.records = records

    def __getitem__(self, item):
        return self.records[item]

    def get_by_id(self, target_id: str):
        for record in self.records:
            if record.id == target_id:
                return record
        raise ValueError(f"No record with ID {target_id} found.")

    def __iter__(self):
        return iter(self.records)

    def write(self, path: Path):
        SeqIO.write(self.records, str(path), "fasta")


class Variant(NamedTuple):
    ref_ID: str
    pos: Tuple[int, int]
    alt: DNAString


Variants = List[Variant]


class Read(NamedTuple):
    id: str
    seq: DNAString
    qual: str


class Reads:
    def __init__(self):
        self.reads: List[Read] = list()

    def __iter__(self):
        return iter(self.reads)

    def add(self, reads: List[Read]):
        self.reads.extend(reads)

    def write(self, path: Path):
        with path.open("w") as fout:
            for read in self.reads:
                print(read.id, read.seq, "+", read.qual, sep="\n", file=fout)


def simulate_refs(seq_ids: List[str], seq_lengths: List[int]) -> SeqRecords:
    records: List[SeqRecord] = list()
    for seq_id, seq_len in zip(seq_ids, seq_lengths):
        new_rec = SeqRecord(
            Seq("".join(random.choices(dna_choices, k=seq_len))), seq_id
        )
        records.append(new_rec)
    return SeqRecords(records)


def simulate_reads(
    refs: SeqRecords, variants: Variants, read_len: int, fold_cov: int = 10
) -> Reads:
    result = Reads()
    for variant in variants:
        sampled_reads: List[Read] = list()

        ref_record = refs.get_by_id(variant.ref_ID)
        variant_start_pos = variant.pos[0]
        variant_end_pos = variant.pos[0] + len(variant.alt) - 1

        applied_seq = str(ref_record.seq)
        applied_seq = (
            applied_seq[: variant.pos[0]]
            + variant.alt
            + applied_seq[variant.pos[1] + 1 :]
        )

        start_pos = max(variant_start_pos - read_len + 1, 0)
        end_pos = min(variant_end_pos + read_len - 1, len(applied_seq) - 1)
        if start_pos == 0 or end_pos == len(ref_record) - 1:
            raise ValueError(
                f"Cannot fit read of length {read_len} "
                f"around positions ({start_pos}, {end_pos}) in ref {variant.ref_ID}"
            )

        while len(sampled_reads) < fold_cov:
            read_start_pos = random.randint(start_pos, variant_end_pos)
            sampled_reads.append(
                Read(
                    variant.ref_ID,
                    applied_seq[read_start_pos : read_start_pos + read_len],
                    "." * read_len,
                )
            )

        result.add(sampled_reads)
    return result
