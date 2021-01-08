import tempfile
import gzip
from unittest import TestCase
from pathlib import Path

import cortex.settings as settings
from cortex.utils import get_sequence_length


class TestResources(TestCase):
    def test_FilesExist(self):
        for var_name in ["CORTEX_ROOT", "MINIMAP2", "VCFTOOLS_DIRECTORY"]:
            self.assertEqual(True, getattr(settings, var_name).exists())


class TestGetSeqLength(TestCase):
    def test_regular_fasta_supported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / "tmpout.fasta"
            with tmpfile.open("w") as fout:
                fout.write(">ref1\nAAACACAGGGGG\nAG")
            seqlen = get_sequence_length(tmpfile)
            self.assertEqual(seqlen, 14)

    def test_gzipped_fasta_supported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "tmpout.fasta.gz"
            with gzip.open(out, "wt") as fout:
                fout.write(">ref1\nACGCAA")

            seqlen = get_sequence_length(out)
            self.assertEqual(seqlen, 6)
