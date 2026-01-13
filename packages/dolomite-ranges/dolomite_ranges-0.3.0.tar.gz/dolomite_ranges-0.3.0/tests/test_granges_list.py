import os
from tempfile import mkdtemp

from biocframe import BiocFrame
from dolomite_base import read_object, save_object
from genomicranges import GenomicRanges, CompressedGenomicRangesList
from iranges import IRanges
import numpy as np
import dolomite_ranges


def test_genomic_ranges_list():
    a = GenomicRanges(
        seqnames=["chr1", "chr2", "chr1", "chr3"],
        ranges=IRanges([1, 3, 2, 4], [10, 30, 50, 60]),
        strand=["-", "+", "*", "+"],
        mcols=BiocFrame({"score": [1, 2, 3, 4]}),
    )

    b = GenomicRanges(
        seqnames=["chr2", "chr4", "chr5"],
        ranges=IRanges([3, 6, 4], [30, 50, 60]),
        strand=["-", "+", "*"],
        mcols=BiocFrame({"score": [2, 3, 4]}),
    )

    grl = CompressedGenomicRangesList.from_list(lst=[a, b], names=["a", "b"])

    dir = os.path.join(mkdtemp(), "granges")
    save_object(grl, dir)

    roundtrip = read_object(dir)
    assert roundtrip.get_names() == grl.get_names()
    assert len(roundtrip.get_unlist_data()) == len(grl.get_unlist_data())
    assert np.allclose(roundtrip["a"].start, grl["a"].start)
    assert np.allclose(roundtrip["a"].strand, grl["a"].strand)


def test_genomic_ranges_list_empty():
    grl = CompressedGenomicRangesList.empty(n=100)

    dir = os.path.join(mkdtemp(), "granges_empty")
    save_object(grl, dir)

    roundtrip = read_object(dir)
    assert roundtrip.get_names() == grl.get_names()
    assert len(roundtrip.get_unlist_data()) == len(grl.get_unlist_data())
    assert np.allclose(roundtrip.get_element_lengths(), grl.get_element_lengths())