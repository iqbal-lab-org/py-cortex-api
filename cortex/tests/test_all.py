import unittest
from pathlib import Path
import tempfile
import shutil
import random

from Bio.Seq import Seq

import cortex.settings as settings
from cortex.calls import run as cortex_run, MissingVcfFile
from cortex.tests.simulate_seqs import (
    SeqRecord,
    SeqRecords,
    simulate_reads,
    Reads,
    Variant,
    dna_choices,
)

data_dir = Path(__file__).resolve().parent / "data"


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


def setup_fpaths():
    tmp_dir = Path(tempfile.mkdtemp())
    ref_out = tmp_dir / "ref.fa"
    reads_out = tmp_dir / "reads.fq"
    out_vcf = tmp_dir / "out.vcf"
    return ref_out, reads_out, out_vcf


class TestResources(unittest.TestCase):
    def test_FilesExist(self):
        for var_name in ["CORTEX_ROOT", "STAMPY_SCRIPT", "VCFTOOLS_DIRECTORY"]:
            self.assertEqual(True, getattr(settings, var_name).exists())


class TestCortexRunRef1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = setup_ref1()

    def setUp(self) -> None:
        self.ref_out, self.reads_out, self.vcf_out = setup_fpaths()
        self.ref.write(self.ref_out)

    def tearDown(self) -> None:
        shutil.rmtree(str(self.ref_out.parent))
        pass

    def test_reads_below_k31_fails(self):
        nonvars = [Variant("Chr1", (20, 20), self.ref[0].seq[20])]
        reads: Reads = simulate_reads(self.ref, nonvars, read_len=15, fold_cov=1)
        reads.write(self.reads_out)

        with self.assertRaises(MissingVcfFile):
            cortex_run(
                self.ref_out,
                [self.reads_out],
                self.vcf_out,
                mem_height=2,
                tmp_directory=self.reads_out.parent,
            )

    def test_reads_with_no_var_fails(self):
        nonvars = [Variant("Chr1", (50, 50), self.ref[0].seq[50])]
        reads: Reads = simulate_reads(self.ref, nonvars, read_len=40, fold_cov=30)
        reads.write(self.reads_out)

        with self.assertRaises(MissingVcfFile):
            cortex_run(
                self.ref_out,
                [self.reads_out],
                self.vcf_out,
                mem_height=2,
                tmp_directory=self.reads_out.parent,
            )

    def test_reads_with_one_snp_passes(self):
        snp_pos = 50
        ref_base = self.ref[0].seq[snp_pos]
        non_ref_choices = set(dna_choices).difference(set(ref_base))
        assert len(non_ref_choices) == len(dna_choices) - 1
        alt_base = random.choice(list(non_ref_choices))
        vars = [Variant("Chr1", (snp_pos, snp_pos), alt_base)]
        reads: Reads = simulate_reads(self.ref, vars, read_len=40, fold_cov=30)
        reads.write(self.reads_out)

        cortex_run(
            self.ref_out,
            [self.reads_out],
            self.vcf_out,
            mem_height=2,
            tmp_directory=self.reads_out.parent,
            cleanup=False,
        )
        self.assertTrue(self.vcf_out.exists())


if __name__ == "__main__":
    unittest.main()
