import unittest
from pathlib import Path
import tempfile
import shutil

from Bio.Seq import Seq

import cortex.settings as settings
import cortex.calls as calls
from .simulate_seqs import (
    SeqRecord,
    SeqRecords,
    simulate_reads,
    Reads,
    Variant,
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

    def test_reads_below_cortex_k31_fails(self):
        nonvars = [Variant("Chr1", (20, 20), self.ref[0].seq[20])]
        reads: Reads = simulate_reads(self.ref, nonvars, read_len=15, fold_cov=1)
        reads.write(self.reads_out)

        with self.assertRaises(FileNotFoundError):
            calls.run(self.ref_out, [self.reads_out], self.vcf_out, mem_height=2)


if __name__ == "__main__":
    unittest.main()
