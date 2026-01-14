
Package for Multi-Criteria Decision Analysis named `mcda`.


# Table of contents

[TOC]


# Package description

This package is used as a basis to represent Multi-Criteria Decision Aiding (MCDA) problems as well as solve them.
It also contains relatively low-level plotting functions to visualize a MCDA problem and its solution.

It is released on PyPI as [mcda](https://pypi.org/project/mcda/).

Its documentation is available [here](https://py-mcda.readthedocs.io/).


# Requirements

To be able to plot relations and outranking graphs, this package requires that `graphviz` be installed.
On Debian/Ubuntu this is done with:

```bash
sudo apt-get install graphviz
```


# Installation

If you want to simply use this package, simply install it from [PyPI](https://pypi.org/project/mcda/):

```bash
pip install mcda
```

**Note:**

This package can be installed with different optional dependencies to unlock full features:

* plot: unlock plotting utilities
* all: include all the above optional dependencies

If you want all optional dependencies for instance, do:

```bash
pip install "mcda[all]"
```

Once you installed our package, you can have a look at our [notebooks](examples/) section which contains examples on how to use our package.

If you want to contribute to this package development, we recommend you to read [this](#contributors).


# Documentation

Documentation on this package can be found [here](https://py-mcda.readthedocs.io/).

It also can be built locally by executing the following command in the package root folder:

```bash
make doc
```

and then visiting `doc/html/index.html` (this can be useful if you're not using a released version of this package).


# Notebooks

We added [jupyter notebooks](https://jupyter.org/) that can be run as examples in [examples/](examples/).


# Contributors

This package is growing continuously and contributions are welcomed.
Contributions can come in the form of new features, bug fixes, documentation improvements
or any combination thereof.
It can also simply come in the form of issues describing the idea for a new feature, a bug encountered, etc.

If you want to contribute to this package, please read the [guidelines](https://py-mcda.readthedocs.io/en/latest/contributing.html).
If you have any new ideas or have found bugs, feel free to [create an issue](https://gitlab.com/decide.imt-atlantique/pymcda/-/issues/new>).
Finally, any contribution must be proposed for integration as a [Merge Request](https://gitlab.com/decide.imt-atlantique/pymcda/-/merge_requests/new).


# License

This software is licensed under the [European Union Public Licence (EUPL) v1.2](https://joinup.ec.europa.eu/page/eupl-text-11-12).
For more information see [LICENSE](LICENSE).


# Citations

@todo write section
