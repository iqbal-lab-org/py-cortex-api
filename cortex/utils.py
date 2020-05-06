import sys
import subprocess
import gzip
from pathlib import Path

from Bio import SeqIO


def get_sequence_length(fasta_file_path: Path) -> int:
    if fasta_file_path.suffix == ".gz":
        with gzip.open(fasta_file_path, "rt") as fhandle:
            record = next(SeqIO.parse(fhandle, "fasta"))
    else:
        record = next(SeqIO.parse(fasta_file_path, "fasta"))
    return len(record.seq)


def syscall(command):
    command = list(map(str, command))
    completed_process = subprocess.run(
        command,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    if completed_process.returncode == 0:
        return completed_process

    print("Error running this command:", command, file=sys.stderr)
    print("Return code:", completed_process.returncode, file=sys.stderr)
    print(
        "Output from stdout and stderr:",
        completed_process.stdout,
        sep="\n",
        file=sys.stderr,
    )
    raise RuntimeError("Error in system call. Cannot continue")
