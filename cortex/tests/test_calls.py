from unittest import TestCase, mock
from pathlib import Path
import tempfile
import shutil
import random

from Bio.Seq import Seq

import cortex.settings as settings
from cortex.calls import run as cortex_run
from cortex.tests.simulate_seqs import (
    SeqRecord,
    SeqRecords,
    simulate_reads,
    simulate_refs,
    Reads,
    Variant,
    dna_choices,
)


class tmpInputFiles:
    def __init__(self):
        self._tmp_dir = Path(tempfile.mkdtemp())
        self.ref_out = self._tmp_dir / "ref.fa"
        self.reads_out = self._tmp_dir / "reads.fq"
        self.out_vcf = self._tmp_dir / "out.vcf"

    def __enter__(self):
        return self

    def cleanup(self):
        if self._tmp_dir.exists():
            shutil.rmtree(self._tmp_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class TestCortexRunErrors(TestCase):
    def test_not_enough_memory_fails(self):
        refs = simulate_refs(["id1"], [10000])
        reads = simulate_reads(refs, variants=list(), read_len=10)

        with tmpInputFiles() as paths:
            refs.write(paths.ref_out)
            reads.write(paths.reads_out)

            with self.assertRaises(RuntimeError):
                cortex_run(
                    paths.ref_out,
                    [paths.reads_out],
                    paths.out_vcf,
                    tmp_directory=paths._tmp_dir,
                    mem_height=1,
                )


def setup_ref1() -> SeqRecords:
    chr1 = SeqRecord(
        Seq(
            "ACGTGCGGAGATTTATACTACGGCCCTATACTATTACGCGAGGACGACT"
            "CGGGAATTATCTATCAGTTACGATTACGTTTGGTACATAAACAAAATTT"
            "TTTCATCATTTTGGTCATATTACGATTAGCTATATATCGATCGATGTGA"
        ),
        id="Chr1",
    )
    chr2 = SeqRecord(
        Seq(
            "TAAAGCCCCGGGCCCTCCCCCCCCCCCCCCCCCGGCTAAGCACTACGGGCCCCCCCCCCC"
            "CCCCCCCCCAAGGCATACATGACAGGAAAAAAAAAACAGGCAGGAGCAGATTACGTTACG"
            "GATATCAGTACTATCGATCAGCTAGCTCGGCTAGCATCTACTATCGATTTAGCAGATTAC"
            "GTTACGGATATCAGTACTATCGATCAGCTAGCTCGGCTAGCATCTACTATCGATTTAGCA"
            "GATTACGTTACGGATATCAGTACTATCGATCAGCTAGCTCGGCTAGCATCTACTATCGAT"
            "TTAGCAGATTACGTTACGGATATCAGTACTATCGATCAGCTAGCTCGGCTAGCATCTACT"
            "ATCGATTT"
        ),
        id="Chr2",
    )
    return SeqRecords([chr1, chr2])


class TestCortexRunRef1(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = setup_ref1()

    def setUp(self) -> None:
        self.paths = tmpInputFiles()
        self.ref.write(self.paths.ref_out)

    def tearDown(self) -> None:
        self.paths.cleanup()

    def test_reads_below_k31_makes_empty_vcf(self):
        nonvars = [Variant("Chr1", (20, 20), self.ref[0].seq[20])]
        reads: Reads = simulate_reads(self.ref, nonvars, read_len=15, fold_cov=1)
        reads.write(self.paths.reads_out)

        with mock.patch("cortex.calls._make_empty_vcf") as mock_empty_vcf:
            cortex_run(
                self.paths.ref_out,
                [self.paths.reads_out],
                self.paths.out_vcf,
                mem_height=2,
                tmp_directory=self.paths._tmp_dir,
                sample_name="mysample",
            )
            mock_empty_vcf.assert_called_once_with(self.paths.out_vcf, "mysample")

        # Check the vcf gets actually made
        self.setUp()
        reads.write(self.paths.reads_out)
        cortex_run(
            self.paths.ref_out,
            [self.paths.reads_out],
            self.paths.out_vcf,
            mem_height=2,
            tmp_directory=self.paths._tmp_dir,
            cleanup=False,
        )
        self.assertTrue(self.paths.out_vcf.exists())

    def test_reads_with_no_var_makes_empty_vcf(self):
        nonvars = [Variant("Chr1", (50, 50), self.ref[0].seq[50])]
        reads: Reads = simulate_reads(self.ref, nonvars, read_len=40, fold_cov=30)
        reads.write(self.paths.reads_out)

        with mock.patch("cortex.calls._make_empty_vcf") as mock_empty_vcf:
            cortex_run(
                self.paths.ref_out,
                [self.paths.reads_out],
                self.paths.out_vcf,
                mem_height=2,
                tmp_directory=self.paths._tmp_dir,
            )
            mock_empty_vcf.assert_called_once()

    def test_reads_with_one_snp_non_empty_vcf(self):
        snp_pos = 50
        ref_base = self.ref[0].seq[snp_pos]
        non_ref_choices = set(dna_choices).difference(set(ref_base))
        assert len(non_ref_choices) == len(dna_choices) - 1
        alt_base = random.choice(list(non_ref_choices))
        vars = [Variant("Chr1", (snp_pos, snp_pos), alt_base)]
        reads: Reads = simulate_reads(self.ref, vars, read_len=40, fold_cov=30)
        reads.write(self.paths.reads_out)

        cortex_run(
            self.paths.ref_out,
            [self.paths.reads_out],
            self.paths.out_vcf,
            mem_height=2,
            tmp_directory=self.paths.reads_out.parent,
            cleanup=False,
        )
        with self.paths.out_vcf.open() as vcf_out:
            all_lines = vcf_out.readlines()
            all_lines = [line for line in all_lines if line[0] != "#"]
        self.assertTrue(len(all_lines) > 0)


class TestResources(TestCase):
    def test_FilesExist(self):
        for var_name in ["CORTEX_ROOT", "STAMPY_SCRIPT", "VCFTOOLS_DIRECTORY"]:
            self.assertEqual(True, getattr(settings, var_name).exists())
