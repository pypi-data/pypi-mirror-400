import os
from tempfile import mkdtemp

from dolomite_base import read_object, save_object
from genomicranges import GenomicRanges, SeqInfo
from iranges import IRanges
import dolomite_ranges


def test_genomic_ranges():
    gr = GenomicRanges(
        seqnames=["chrA", "chrB", "chrC"],
        ranges=IRanges([10, 30, 2200], [20, 50, 30]),
        strand=["*", "+", "-"],
    )

    dir = os.path.join(mkdtemp(), "granges")
    save_object(gr, dir)

    roundtrip = read_object(dir)
    assert roundtrip.get_seqnames() == gr.get_seqnames()
    assert (roundtrip.get_start() == gr.get_start()).all()
    assert (roundtrip.get_end() == gr.get_end()).all()
    assert (roundtrip.get_strand() == gr.get_strand()).all()
    assert roundtrip.get_seqinfo().get_seqlengths() == gr.get_seqinfo().get_seqlengths()


def test_genomic_ranges_full_load():
    gr = GenomicRanges(
        seqnames=["chrA", "chrB", "chrC"],
        ranges=IRanges([10, 30, 2200], [20, 50, 30]),
        strand=["*", "+", "-"],
    )

    gr.metadata = {"ARG": [5, 3, 2, 1]}
    gr.seq_info = SeqInfo(
        seqnames=["chrA", "chrB", "chrC"],
        seqlengths=[1000, 2000, 3000],
        is_circular=[False] * 3,
        genome=["hg38"] * 3,
    )

    dir = os.path.join(mkdtemp(), "granges2")
    save_object(gr, dir)

    roundtrip = read_object(dir)
    assert roundtrip.seqinfo.seqlengths == gr.seqinfo.seqlengths
    assert list(roundtrip.metadata.keys()) == list(gr.metadata.keys())
