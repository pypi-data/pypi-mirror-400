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
## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/
