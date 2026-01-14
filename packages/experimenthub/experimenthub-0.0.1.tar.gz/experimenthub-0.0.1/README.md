[![PyPI-Server](https://img.shields.io/pypi/v/experimenthub.svg)](https://pypi.org/project/experimenthub/)
![Unit tests](https://github.com/biocpy/experimenthub/actions/workflows/run-tests.yml/badge.svg)

# experimenthub

**ExperimentHub** provides an interface to access and manage data from the Bioconductor [ExperimentHub](https://bioconductor.org/packages/ExperimentHub/) service directly in Python.

It is designed to work within the **BiocPy** ecosystem, converting R data objects (like `SingleCellExperiment` or `SummarizedExperiment`) into their Python equivalents (e.g., `SummarizedExperiment`) using [rds2py](https://github.com/biocpy/rds2py).

> [!NOTE]
>
> This is an ***experimental*** package. It may not work with all RDS files from ExperimentHub.
> Currently, this package filters ExperimentHub resources to provide access to:
> - **File Formats:** `.rds`
> - **R Classes:** `SingleCellExperiment`, `SummarizedExperiment`, `RangedSummarizedExperiment`, `GRanges` etc
>
> Files are converted to their respective BiocPy representations or common Python formats.

## Install

To get started, install the package from [PyPI](https://pypi.org/project/experimenthub/)

```bash
pip install experimenthub
```

## Usage

### Initialize the Registry

The registry manages the local cache of `ExperimentHub` metadata and resources. On the first run, it downloads the metadata database.

```py
from experimenthub import ExperimentHubRegistry

# Initialize the registry (downloads metadata if needed)
eh = ExperimentHubRegistry()
```

### Searching for Resources

ExperimentHub contains thousands of datasets. Use the `search()` method to find resources by title, description, or species.

```py
# Search for mouse-related datasets
results = eh.search("mus musculus")

# Print the first few matches
for record in results[:5]:
    print(f"{record.ehub_id}: {record.title}")
# Output:
# EH1041: Brain scRNA-seq data, sample ...,
# EH1042: Brain scRNA-seq data, gene ...,
# ...
```

### Inspecting Metadata

You can retrieve detailed metadata for a specific ID.

```py
record = eh.get_record("EH4663")

print(f"Title: {record.title}")
print(f"Species: {record.species}")
print(f"Genome: {record.genome}")
print(f"Description: {record.description}")
print(f"R Class: {record.preparer_dataclass}")

## Output:
# Title: Lohoff biorXiv spatial coordinates (sample 2)
# Species: Mus musculus
# Genome: mm10
# Description: Cell spatial coordinates for sample 2 for the E8.5 seqFISH dataset from biorXiv
# R Class: character
```

### Loading Data

The `load()` method handles the download, caching, and loading of the dataset.

If the resource is an R data file (.rds) containing a supported Bioconductor object (e.g., `SingleCellExperiment`), it is automatically read and converted to an equivalent python object using rds2py.

```py
# Load a data.frame as an BiocFrame object
data = eh.load("EH4663")

print(data)
# BiocFrame with 8425 rows and 3 columns
#                                           x                   y             z
#                                 <FloatList>         <FloatList> <IntegerList>
#  embryo1_Pos0_cell10_z5  0.7084368794499625 -2.7071263060540645             5
# embryo1_Pos0_cell100_z5  0.9763043488304248  -2.517971233335359             5
# embryo1_Pos0_cell101_z5  0.9749347757408557 -2.6739635081030855             5
#                                         ...                 ...           ...
# embryo1_Pos28_cell97_z5 -1.3992279805347039  3.1761928631722824             5
# embryo1_Pos28_cell98_z5  -1.389353519722718  3.1349508225406666             5
# embryo1_Pos28_cell99_z5  -1.394992277928857  2.5812717935734355             5
```

<!-- biocsetup-notes -->

## Note

This project has been set up using [BiocSetup](https://github.com/biocpy/biocsetup)
and [PyScaffold](https://pyscaffold.org/).
