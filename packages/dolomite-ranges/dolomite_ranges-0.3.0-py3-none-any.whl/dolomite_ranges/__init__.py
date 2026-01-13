import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "dolomite-ranges"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .save_sequence_information import save_sequence_information
from .read_sequence_information import read_sequence_information 
from .save_genomic_ranges  import save_genomic_ranges
from .read_genomic_ranges import read_genomic_ranges 
from .save_genomic_ranges_list import save_compressed_genomic_ranges_list
from .read_genomic_ranges_list import read_genomic_ranges_list