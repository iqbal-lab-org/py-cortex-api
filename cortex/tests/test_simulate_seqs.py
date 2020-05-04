from unittest import TestCase

from Bio.SeqRecord import SeqRecord

from .simulate_seqs import (
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
