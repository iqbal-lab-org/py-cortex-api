import os
import shutil
import tempfile
import sys
from pathlib import Path
from typing import List

from cortex.file_manip import (
    StrPath,
    PathLike,
    _find_final_vcf_file_path,
    _make_empty_vcf,
)
from . import settings
from . import utils


class _CortexIndex:
    def __init__(self, directory: Path):
        self.base = directory.resolve()
        self.base.mkdir(exist_ok=True)

        self.ref_names_file = self.base / "fofn"
        self.dump_binary_ctx = self.base / "k31.ctx"

    def make(self, reference_fasta: Path, mem_height: int):
        with self.ref_names_file.open("w") as f:
            print(str(reference_fasta), file=f)

        cortex_var = os.path.join(settings.CORTEX_ROOT, "bin", "cortex_var_31_c1")
        utils.syscall(
            [
                cortex_var,
                "--kmer_size",
                31,
                "--mem_height",
                mem_height,
                "--mem_width",
                100,
                "--se_list",
                self.ref_names_file,
                "--max_read_len",
                10000,
                "--dump_binary",
                self.dump_binary_ctx,
                "--sample_id",
                "REF",
            ]
        )

        self.ref_names_file.unlink()


class _CortexCall:
    """
    fofn: file of file names
    """

    def __init__(
        self, directory: Path, reference_fasta: Path, ploidy: int, mem_height: int
    ):
        self.base: Path = directory.resolve()
        self.base.mkdir(parents=True, exist_ok=True)

        self.ploidy = ploidy
        self.mem_height = mem_height

        self.cortex_log = self.base / "cortex.log"
        self.output_directory = self.base / "cortex_output"
        self.reads_fofn = self.base / "cortex_reads_in.fofn"
        self.reads_index = self.base / "cortex_reads_in.index"
        self.reference_fofn = self.base / "cortex_in_index_ref.fofn"

        self.index = _CortexIndex(self.base / "indexes")
        self.index.make(reference_fasta, self.mem_height)

    def make_input_files(
        self, reference_fasta: Path, reads_files: List[Path], sample_name: str
    ):
        self.base.mkdir(parents=True, exist_ok=True)

        # List sample's read files
        with self.reads_fofn.open("w") as f:
            for reads_file in reads_files:
                print(reads_file, file=f)

        # Sample name + file listing read files
        with self.reads_index.open("w") as f:
            print(sample_name, self.reads_fofn, ".", ".", sep="\t", file=f)

        with self.reference_fofn.open("w") as f:
            print(reference_fasta, file=f)

    def execute_calls(self, reference_fasta: Path):
        number_of_bases_in_reference = utils.get_sequence_length(reference_fasta)
        cortex_calls_script = os.path.join(
            settings.CORTEX_ROOT, "scripts", "calling", "run_calls.pl"
        )

        # See https://github.com/iqbal-lab/cortex/tree/master/doc for
        # guidance on command arguments
        command = [
            cortex_calls_script,
            "--first_kmer",
            31,
            "--fastaq_index",
            self.reads_index,
            "--auto_cleaning",
            "yes",
            "--bc",
            "yes",
            "--pd",
            "no",
            "--outdir",
            self.output_directory,
            "--outvcf",
            "cortex",
            "--ploidy",
            self.ploidy,
            "--minimap2_bin",
            settings.MINIMAP2,
            "--list_ref_fasta",
            self.reference_fofn,
            "--refbindir",
            self.index.base,
            "--genome_size",
            number_of_bases_in_reference,
            "--qthresh",
            5,
            "--mem_height",
            self.mem_height,
            "--mem_width",
            100,
            "--vcftools_dir",
            settings.VCFTOOLS_DIRECTORY,
            "--do_union",
            "yes",
            "--ref",
            "CoordinatesAndInCalling",
            "--workflow",
            "independent",
            "--logfile",
            self.cortex_log,
        ]

        try:
            utils.syscall(command)
        except RuntimeError as e:
            # In cortex, stderr and stdout gets written log files so that raised errors
            # in this API do not necessarily get what Actually caused the error.
            print(
                "----------------------------\n"
                "Please refer to cortex log file at {} for more information.".format(
                    self.cortex_log
                ),
                file=sys.stderr,
            )
            raise e from None


def run(
    reference_fasta: StrPath,
    reads_files: List[StrPath],
    output_vcf_file_path: StrPath,
    sample_name: str = "sample",
    ploidy: int = 1,
    tmp_directory: PathLike = None,
    mem_height: int = 22,
    cleanup: bool = True,
) -> None:
    reference_fasta = Path(reference_fasta).resolve()
    if type(reads_files) is not list:
        raise ValueError("read files must be passed as list, even if single file")

    reads_files = [Path(reads_file).resolve() for reads_file in reads_files]

    if tmp_directory is None:
        tmp_directory = tempfile.mkdtemp()
    tmp_directory = Path(tmp_directory).resolve()

    if ploidy not in {1, 2}:
        raise ValueError("ploidy must be in {1, 2}")

    caller = _CortexCall(tmp_directory, reference_fasta, ploidy, mem_height)
    caller.make_input_files(reference_fasta, reads_files, sample_name)
    caller.execute_calls(reference_fasta)

    final_vcf_path = _find_final_vcf_file_path(tmp_directory)
    if final_vcf_path is not None:
        shutil.copyfile(final_vcf_path, output_vcf_file_path)
    else:
        _make_empty_vcf(output_vcf_file_path, sample_name)

    if cleanup:
        shutil.rmtree(tmp_directory)
    else:
        print(
            f"Not cleaning tmp directory. "
            f"Cortex output and log files in {tmp_directory}"
        )
