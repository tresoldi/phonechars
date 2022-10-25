# phonechars

`phonechars` is a Python library and command-line tool
for extracting phonological phylogenetic characters from aligned lexical data,
both for purposes of investigation into correspondence sets and phylogenetic
analyses.


## Installation

In any standard Python environment, `phonechars` can be installed with:

```bash
pip install phonechars
```

## How to use

The library can be conveniently used by means of the `phonechars` command-line
tool. While different options are available, a simple call to the program
when provided the path to a wordlist of aligned data
will generate three files with related information:

  - A `.chars.tsv` file, extending the alignment information with correspondences
    inferred by means of different methods (currently, only a method modified from
    List (2019) and available via the `lingrex` library is offered)
  - A `.corrs.tsv` file, informing the detected correspondences
  - A `.nex` (NEXUS) file, suitable for analysis with standard phylogenetic tools
    including SplitsTree and BEAST2

A demo file, with information from Ryukyuian dialects as presented in
Huisman (2022), is distributed with the standard installation and can be
used for testing the command-line tool:

```bash
$ phonechars demo/ryukyu.tsv
```

## Community guidelines

While the author can be contacted directly for support, it is recommended that
third parties use GitHub standard features, such as issues and pull requests, to
contribute, report problems, or seek support.

Contributing guidelines, including a code of conduct, can be found in the
`CONTRIBUTING.md` file.


## Author and citation

The library is developed by Tiago Tresoldi (tiago.tresoldi@lingfil.uu.se). The library is developed in the context of
the [Cultural Evolution of Texts](https://github.com/evotext/) project, with funding from the
[Riksbankens Jubileumsfond](https://www.rj.se/) (grant agreement ID:
[MXM19-1087:1](https://www.rj.se/en/anslag/2019/cultural-evolution-of-texts/)).

If you use `phonechars`, please cite it as:

> Tresoldi, Tiago, (2022). Phonechars: a Python library for extracting phonological phylogenetic characters. Version 0.1. Uppsala, University of Uppsala. https://github.com/tresoldi/phonechars

In BibTeX:

```
@misc{Tresoldi2022phonechars,
  url = {https://doi.org/10.21105/joss.03173},
  year = {2022},
  author = {Tiago Tresoldi},
  title = {Phonechars: a Python library for extracting phonological phylogenetic characters. Version 0.1},
  address = {Uppsala},
  publisher = {University of Uppsala}
}
```