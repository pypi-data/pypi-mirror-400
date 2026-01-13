import os
from typing import Optional

import dolomite_base as dl
import h5py
from compressed_lists import Partitioning
from dolomite_base.read_object import read_object_registry
from genomicranges import CompressedGenomicRangesList

read_object_registry["genomic_ranges_list"] = "dolomite_ranges.read_genomic_ranges_list"


def read_genomic_ranges_list(path: str, metadata: Optional[dict], **kwargs) -> CompressedGenomicRangesList:
    """Load genomic ranges into a
    :py:class:`~genomicranges.grangeslist.CompressedGenomicRangesList` object.

    This method
    should generally not be called directly but instead be invoked by
    :py:meth:`~dolomite_base.read_object.read_object`.

    Args:
        path:
            Path to the directory containing the object.

        metadata:
            Metadata for the object.

        kwargs:
            Further arguments, ignored.

    Returns:
        A :py:class:`~genomicranges.grangeslist.CompressedGenomicRangesList` object.
    """

    with h5py.File(os.path.join(path, "partitions.h5"), "r") as handle:
        ghandle = handle["genomic_ranges_list"]

        lengths = dl.load_vector_from_hdf5(ghandle["lengths"], expected_type=int, report_1darray=True)

        names = None
        if "names" in ghandle:
            names = dl.load_vector_from_hdf5(ghandle["names"], expected_type=str, report_1darray=True)

    _all_granges = dl.alt_read_object(path=os.path.join(path, "concatenated"), **kwargs)

    counter = 0
    _split_granges = []
    if lengths.sum() == 0:
        _split_granges = _all_granges
    else:
        for ilen in lengths:
            _frag = _all_granges[counter : (counter + ilen)]
            _split_granges.append(_frag)
            counter += ilen

    grl = CompressedGenomicRangesList(
        unlist_data=_all_granges, partitioning=Partitioning.from_lengths(lengths=lengths, names=names)
    )

    _elem_annotation_path = os.path.join(path, "element_annotations")
    if os.path.exists(_elem_annotation_path):
        _mcols = dl.alt_read_object(_elem_annotation_path, **kwargs)
        grl = grl.set_element_metadata(_mcols)

    _meta_path = os.path.join(path, "other_annotations")
    if os.path.exists(_meta_path):
        _meta = dl.alt_read_object(_meta_path, **kwargs)
        grl = grl.set_metadata(_meta.as_dict())

    return grl
