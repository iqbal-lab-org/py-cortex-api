import unittest
from pathlib import Path
import cortex.settings as settings
import cortex.calls as calls

data_dir = Path(__file__).resolve().parent / "data"


class TestResources(unittest.TestCase):
    def test_FilesExist(self):
        for var_name in ["CORTEX_ROOT", "STAMPY_SCRIPT", "VCFTOOLS_DIRECTORY"]:
            self.assertEqual(True, getattr(settings, var_name).exists())


class TestCortexRun(unittest.TestCase):
    def test_oneRef_oneFq_ReadsTooShort(self):
        """
        The reads are all < 31bp so no vcf of calls produced.
        """
        ref = data_dir / "ref1.fa"
        reads = data_dir / "reads1_ref1.fastq"
        out_vcf = data_dir / "tmp_out.vcf"
        with self.assertRaises(FileNotFoundError):
            calls.run(ref, [reads], out_vcf, mem_height=2)


if __name__ == "__main__":
    unittest.main()
