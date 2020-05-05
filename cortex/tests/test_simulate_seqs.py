from unittest import TestCase, mock

from Bio.SeqRecord import SeqRecord

from cortex.tests.simulate_seqs import (
    simulate_refs,
    simulate_reads,
    dna_choices,
    SeqRecords,
    Variant,
)


class TestSimulateRefs(TestCase):
    def test_make_two_refs(self):
        ids = ["ID1", "ID2"]
        lengths = [4, 5]
        result = simulate_refs(ids, lengths)

        result_ids = [rec.id for rec in result]
        self.assertEqual(result_ids, ids)

        result_lengths = [len(rec) for rec in result]
        self.assertEqual(result_lengths, lengths)

        for rec in result:
            all_dna = sum([base in dna_choices for base in str(rec.seq)])
            self.assertEqual(all_dna, len(rec))


class TestSimulateReadsNearRefBoundaries(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.refs = SeqRecords([SeqRecord("ATCGC", id="r1")])

    def test_read_len_beyond_ref_start_fails(self):
        variants = [Variant("r1", (1, 1), "T")]
        with self.assertRaises(ValueError):
            simulate_reads(self.refs, variants, 3)

    def test_read_len_beyond_ref_end_fails(self):
        variants = [Variant("r1", (3, 3), "T")]
        with self.assertRaises(ValueError):
            simulate_reads(self.refs, variants, 2)

    def test_read_on_ref_end_passes(self):
        variants = [
            Variant("r1", (3, 3), "T"),
            Variant("r1", (1, 1), "T"),
        ]
        simulate_reads(self.refs, variants, 1)


class TestSimulateReadsSeqAndCoverage(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.refs = SeqRecords([SeqRecord("CCCCCAACCGCGGATACGCT", id="r1")])

    def test_simulate_reads_no_variant(self):
        nonvars = [Variant("r1", (9, 9), self.refs[0].seq[9])]

        with mock.patch("random.randint") as randint:
            randint.return_value = 8

            reads = simulate_reads(self.refs, nonvars, 7, fold_cov=3)
            expected_seq = str(self.refs[0].seq[8 : 8 + 7])
            self.assertTrue(all([read.seq == expected_seq for read in reads]))

    def test_simulate_reads_with_variant(self):
        variants = [Variant("r1", (9, 10), "AAT")]
        with mock.patch("random.randint") as randint:
            randint.return_value = 8

            reads = simulate_reads(self.refs, variants, 7, fold_cov=3)
            self.assertTrue(all([read.seq == "CAATGGA" for read in reads]))
