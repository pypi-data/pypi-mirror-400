import os
from tempfile import mkdtemp

import dolomite_base as dl
import dolomite_ranges
from genomicranges import SeqInfo

def test_sequence_information():
    si = SeqInfo(
        seqnames=["chrA", "chrB", "chrC"],
        seqlengths=[10, 100, 2200],
        is_circular=[False, True, False],
        genome=["hg19", "hg38", "hg19"],
    )

    dir = os.path.join(mkdtemp(), "seqinfo")
    dl.save_object(si, dir)

    roundtrip = dl.read_object(dir)
    assert roundtrip.get_seqnames() == si.get_seqnames()
    assert roundtrip.get_seqlengths() == si.get_seqlengths()
    assert roundtrip.get_is_circular() == si.get_is_circular()
    assert roundtrip.get_genome() == si.get_genome()


def test_sequence_information_with_none():
    si = SeqInfo(
        seqnames=["chrA", "chrB", "chrC"],
        seqlengths=[10, None, 2200],
        is_circular=[None, True, False],
        genome=["hg19", "hg38", None],
    )

    dir = os.path.join(mkdtemp(), "seqinfo")
    dl.save_object(si, dir)

    roundtrip = dl.read_object(dir)
    assert roundtrip.get_seqnames() == si.get_seqnames()
    assert roundtrip.get_seqlengths() == si.get_seqlengths()
    assert roundtrip.get_is_circular() == si.get_is_circular()
    assert roundtrip.get_genome() == si.get_genome()


def test_sequence_information_all_none():
    si = SeqInfo(
        ["chrA", "chrB", "chrC"],
        [None] * 3,
        [None] * 3,
        [None] * 3
    )

    dir = os.path.join(mkdtemp(), "seqinfo")
    dl.save_object(si, dir)

    roundtrip = dl.read_object(dir)
    assert roundtrip.get_seqnames() == si.get_seqnames()
    assert roundtrip.get_seqlengths() == si.get_seqlengths()
    assert roundtrip.get_is_circular() == si.get_is_circular()
    assert roundtrip.get_genome() == si.get_genome()
