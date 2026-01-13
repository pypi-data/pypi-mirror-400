import os
from typing import Optional

import dolomite_base as dl
import h5py
from dolomite_base.read_object import read_object_registry
from genomicranges import SeqInfo

read_object_registry[
    "sequence_information"
] = "dolomite_ranges.read_sequence_information"


def read_sequence_information(path: str, metadata: Optional[dict], **kwargs) -> SeqInfo:
    """Load sequence information into a
    :py:class:`~genomicranges.SeqInfo.SeqInfo` object.

    This method should generally not be called directly but instead be
    invoked by :py:meth:`~dolomite_base.read_object.read_object`.

    Args:
        path:
            Path to the directory containing the object.

        metadata:
            Metadata for the object.

        kwargs:
            Further arguments, ignored.

    Returns:
        A :py:class:`~genomicranges.SeqInfo.SeqInfo` object.
    """

    with h5py.File(os.path.join(path, "info.h5"), "r") as handle:
        ghandle = handle["sequence_information"]

        seqnames = dl.load_vector_from_hdf5(
            ghandle["name"], expected_type=str, report_1darray=True
        )

        seqlengths = dl.load_vector_from_hdf5(
            ghandle["length"], expected_type=int, report_1darray=True
        )

        is_circular = dl.load_vector_from_hdf5(
            ghandle["circular"], expected_type=bool, report_1darray=True
        )

        genome = dl.load_vector_from_hdf5(
            ghandle["genome"], expected_type=str, report_1darray=True
        )

    return SeqInfo(seqnames, seqlengths, is_circular, genome)
