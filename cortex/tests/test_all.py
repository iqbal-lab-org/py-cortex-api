import unittest
import os
import cortex.settings as settings
import cortex.calls as calls

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"data"))

class TestResources(unittest.TestCase):
    def test_FilesExist(self):
        for var_name in ["CORTEX_ROOT","STAMPY_SCRIPT","VCFTOOLS_DIRECTORY"]:
            self.assertEqual(True, os.path.exists(getattr(settings,var_name)))

class TestCortexRun(unittest.TestCase):
    def test_oneRef_oneFq_tooSmallSequence(self):
        """
        The reference provided has only 18 bases, so the sequence graph at k=31 will be empty
        So no vcf of calls will be produced.
        """
        ref = os.path.join(data_dir, "ref1.fa")
        reads = os.path.join(data_dir, "reads_ref1.fastq")
        out_vcf = os.path.join(data_dir, "tmp_out.vcf")
        with self.assertRaises(FileNotFoundError):
            calls(ref, [reads], out_vcf)

if __name__=="__main__":
    unittest.main()
