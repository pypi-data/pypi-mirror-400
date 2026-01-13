<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/dolomite-ranges.svg?branch=main)](https://cirrus-ci.com/github/<USER>/dolomite-ranges)
[![ReadTheDocs](https://readthedocs.org/projects/dolomite-ranges/badge/?version=latest)](https://dolomite-ranges.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/dolomite-ranges/main.svg)](https://coveralls.io/r/<USER>/dolomite-ranges)
[![PyPI-Server](https://img.shields.io/pypi/v/dolomite-ranges.svg)](https://pypi.org/project/dolomite-ranges/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/dolomite-ranges.svg)](https://anaconda.org/conda-forge/dolomite-ranges)
[![Monthly Downloads](https://pepy.tech/badge/dolomite-ranges/month)](https://pepy.tech/project/dolomite-ranges)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/dolomite-ranges)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/dolomite-ranges.svg)](https://pypi.org/project/dolomite-ranges/)
![Unit tests](https://github.com/ArtifactDB/dolomite-ranges/actions/workflows/pypi-test.yml/badge.svg)

# Save and load genomic ranges objects to file

This package implements methods for saving and loading `GenomicRanges` and `GenomicRangesList` objects. It provides a language-agnostic method for serializing genomic coordinates in these objects, as well as data in related objects like sequence information. To get started, install the package from PyPI:

```bash
pip install dolomite-ranges
```

We can then save a `GenomicRanges` to a file, preserving its **metadata** and **mcols**:

```python
import os
from tempfile import mkdtemp

from dolomite_base import read_object, save_object
from genomicranges import GenomicRanges
from iranges import IRanges
import dolomite_ranges

gr = GenomicRanges(
     seqnames=["chrA", "chrB", "chrC"],
     ranges=IRanges([10, 30, 2200], [20, 50, 30]),
     strand=["*", "+", "-"],
)

dir = os.path.join(mkdtemp(), "granges")
save_object(gr, dir)

roundtrip = read_object(dir)
```

Similarly save and load a `GenomicRangesList` to a file,

```python
import os
from tempfile import mkdtemp

from dolomite_base import read_object, save_object
from genomicranges import GenomicRanges, SeqInfo
from iranges import IRanges
import dolomite_ranges

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

grl = GenomicRangesList(ranges=[a, b], names=["a", "b"])

dir = os.path.join(mkdtemp(), "granges_list")
save_object(gr, dir)

roundtrip = read_object(dir)
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.
