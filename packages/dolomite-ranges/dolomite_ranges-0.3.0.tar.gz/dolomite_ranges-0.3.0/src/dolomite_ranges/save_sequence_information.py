import os

import dolomite_base as dl
import h5py
from genomicranges import SeqInfo


@dl.save_object.register
@dl.validate_saves
def save_sequence_information(x: SeqInfo, path: str, **kwargs):
    """Save Sequence information to disk.

    Args:
        x:
            Object to be saved.

        path:
            Path to a directory in which to save ``x``.

        kwargs:
            Further arguments to be passed to individual methods.

    Returns:
        `x` is saved to `path`.
    """
    os.mkdir(path)

    _info = {"sequence_information": {"version": "1.0"}}
    dl.save_object_file(path, "sequence_information", _info)

    with h5py.File(os.path.join(path, "info.h5"), "w") as handle:
        ghandle = handle.create_group("sequence_information")

        dl.write_string_vector_to_hdf5(ghandle, name="name", x=x.get_seqnames())
        dl.write_integer_vector_to_hdf5(
            ghandle, name="length", x=x.get_seqlengths(), h5type="u4"
        )

        dl.write_boolean_vector_to_hdf5(ghandle, name="circular", x=x.get_is_circular())
        dl.write_string_vector_to_hdf5(ghandle, name="genome", x=x.get_genome())

    return
