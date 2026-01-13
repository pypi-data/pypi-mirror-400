import os
from typing import Optional

import dolomite_base as dl
import h5py
from genomicranges import GenomicRanges


@dl.save_object.register
@dl.validate_saves
def save_genomic_ranges(
    x: GenomicRanges, path: str, data_frame_args: Optional[dict] = None, **kwargs
):
    """Method for saving :py:class:`~genomicranges.GenomicRanges.GenomicRanges`
    objects to their corresponding file representations, see
    :py:meth:`~dolomite_base.save_object.save_object` for details.

    Args:
        x:
            Object to be staged.

        path:
            Path to a directory in which to save ``x``.

        data_frame_args:
            Further arguments to pass to the ``save_object`` method for
            ``mcols``.

        kwargs:
            Further arguments to be passed to individual methods.

    Returns:
        `x` is saved to `path`.
    """
    os.mkdir(path)

    if data_frame_args is None:
        data_frame_args = {}

    _info = {"genomic_ranges": {"version": "1.0"}}
    dl.save_object_file(path, "genomic_ranges", _info)

    # sequence information
    spath = os.path.join(path, "sequence_information")
    dl.save_object(x.get_seqinfo(), spath)

    with h5py.File(os.path.join(path, "ranges.h5"), "w") as handle:
        ghandle = handle.create_group("genomic_ranges")

        _seqnames = x.get_seqnames(as_type="factor")
        dl.write_integer_vector_to_hdf5(
            ghandle, name="sequence", h5type="u4", x=_seqnames.get_codes()
        )

        _ranges = x.get_ranges()
        dl.write_integer_vector_to_hdf5(
            ghandle, name="start", h5type="i4", x=_ranges.get_start()
        )
        dl.write_integer_vector_to_hdf5(
            ghandle, name="width", h5type="u4", x=_ranges.get_width()
        )

        dl.write_integer_vector_to_hdf5(
            ghandle, name="strand", h5type="i4", x=x.get_strand()
        )

        if x.get_names() is not None:
            dl.write_string_vector_to_hdf5(ghandle, name="name", x=x.get_names())

    _range_annotation = x.get_mcols()
    if _range_annotation is not None and _range_annotation.shape[1] > 0:
        dl.alt_save_object(
            _range_annotation,
            path=os.path.join(path, "range_annotations"),
            **data_frame_args,
        )

    _meta = x.get_metadata()
    if _meta is not None and len(_meta) > 0:
        dl.alt_save_object(
            _meta, path=os.path.join(path, "other_annotations"), **kwargs
        )

    return
