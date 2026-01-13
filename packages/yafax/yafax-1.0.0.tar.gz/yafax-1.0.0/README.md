# YAFAX (<ins>Y</ins>et <ins>A</ins>nother <ins>FA</ins>STA Index and E<ins>x</ins>traction Tool)

## Introduction

Pure-Python implementation of `samtools faidx` with no external dependencies. The tool provides two modes: `index`, which creates a genome index, and `getseq`, which retrieves sequences from an indexed genome. As with `samtools faidx`, the genome must be indexed before sequence retrieval. By default, the genome index is expected to be located in the same directory as the genome FASTA file. Since this is an **exact subset** of `samtools faidx`, it is fully interoperable with it. An index created using `yafax index` can be used by `samtools faidx` for sequence retrieval, and vice versa. It offers reasonable performance: fetching 2 million queries, each with a width of 1 kbp, takes less than 2 minutes for the GRCh38 build of human genome. It is faster than the existing `pyFaidx` package due to lower overhead, but it offers fewer options.

## Dependencies

YAFAX does not have any external dependencies. However, since the source code utilizes type hints, **Python 3.11 or higher is recommended**. Additionally, the `argparse` module in Python 3.13 includes enhanced formatting features that are used in the help message, so **Python 3.13 or higher is recommended** for full compatibility.

YAFAX has been tested on **Ubuntu 20.04, 22.04, 24.04**, and **Alpine Linux v3.22** with Python versions **3.10–3.13**. It should also work on Windows, although **Windows Subsystem for Linux (WSL)** is recommended for best results.

## Installation

### Installation from PyPI

```bash
pip install yafax
```

### Installation from source

```bash
git clone https://github.com/dasprosad/yafax.git
cd yafax
pip install .
```

## Usage and options

For help and usage

```bash
yafax -h/--help
yafax <mode> -h/--help
```

### General options

```
usage: yafax <mode> --help
       yafax <mode> [mode optional arguments] <fasta file>

YAFAX (Yet Another FASTA Index and Extraction Tool)

positional arguments:
  FASTA FILE      path to FASTA file

options:
  -h, --help      show this help message and exit
  -v, --version   show program's version number and exit

yafax mode:
  {index,getseq}
    index         generate a FASTA index
    getseq        fetch sequence of an interval using position
```

### YAFAX `index` options

```
usage: yafax index [optional arguments] <fasta file>

options:
  -h, --help      show this help message and exit
  -d, --out-dir   directory of the output FASTA index
```

### YAFAX `getseq` options

```
usage: yafax getseq [optional arguments] <position> <fasta file>

positional arguments:
  position           position interval in format chr:start-end

options:
  -h, --help         show this help message and exit
  -i, --index-path   path of FASTA index (Default: file.fa.fai)
  -r, --revcomp      reverse complement the sequence (Default: False)
  -w, --width        wrapping width of FASTA lines (Default: 50)
  -n, --no-header    do not include FASTA header (Default: False)
  -b, --bedfile      BED file with regions
  -o, --outfile      output file, only used when BED is provided (Default: STDOUT)
```

## Examples

### YAFAX `index` examples

- To index a genome use

```bash
yafax index genome.fa
```

- Index a genome and store it into some other location

```bash
yafax index --out-dir /some/other/path genome.fa
```

### YAFAX `getseq` examples

- To get sequence of an interval `chrK:start-end`

```bash
yafax getseq chrK:start-end genome.fa
```

- To get sequence using index path

```bash
yafax getseq chrK:start-end --index-path /path/to/index/genome.fa.fai
```

- To get a reverse-complemented sequence of an interval

```bash
yafax getseq --revcomp chrK:start-end genome.fa
```

- By default the FASTA sequence are wrapped to 50 characters. To set a custom width use

```
yafax getseq --width INT chrK:start-end genome.fa
```

- If you do not want the FASTA headers on the sequences, use

```bash
yafax getseq --no-header chrK:start-end genome.fa
```

- By default the output is sent to STDOUT. They can be saved to a file by using

```bash
yafax getseq chrK:start-end --outfile FILENAME.fa genome.fa
```

- If multiple entries to be used it is convenient use a BED file

```bash
yafax getseq --bedfile POSITIONS.bed genome.fa
```

- To fetch reverse-complemented sequence of the interval chrM:10000-11000 with no FASTA header

```bash
yafax getseq --revcomp --no-header chrM:10000-11000 genome.fa
```

## Benchmarking with `faidx` cli and `samtools faidx`

When benchmarked with both `faidx` cli from `pyFaidx` and the original `samtools faidx`, `yafax getseq` was almost **43x faster** than `faidx` and only **2.26x slower** than `samtools faidx`. Given that `samtools` is written in C, pure Python `yafax` is very much performant. All of the tests were done on Ubuntu 22.04 LTS x86-64 using Intel Xeon 2.30GHz, single core, and a solid state drive. The results are the following.

### Pure `samtools faidx` (SAMtools v1.22.1 with htslib 1.22.1)

BED file was transformed to chr:start-end to meet samtools faidx requirement.

```bash
time samtools faidx hg38.fa --region-file seed100_interval1000.txt --output samtoolsfaidxout.fa

real    0m43.708s
user    0m4.674s
sys     0m21.075s
```

### `faidx` cli from `pyFaidx` with CPython v3.11 (pyFaidex v0.9.0.3)

```bash
time faidx --bed seed100_interval1000.bed --out faidxout.fa hg38.fa

real    42m47.490s
user    3m32.369s
sys     0m53.095s
```

### `getseq` from `yafax` with CPython v3.13 (faidex v1.0.0)

```bash
time yafax getseq --bedfile seed100_interval1000.bed --outfile yafaxgetseqout.fa hg38.fa

real    1m39.025s
user    1m24.853s
sys     0m13.172s
```

## License

YAFAX is distributed under the GNU General Public License v3. You should have received a copy the license with the program.

## Release history

- 1.0.0 First stable release

## Typing

YAFAX ships with inline type hints and includes a `py.typed` marker. It is compatible with `mypy` and `pyright`.

## Development

For testing tests are located in the `tests/` directory and be tested by cloning the repository and running

```bash
pip install -e .
pip install pytest
pytest
```

## Reporting issues

If you find any bugs or would like a new feature, please report the same in the GitHub [YAFAX](https://github.com/dasprosad/yafax) issue tracker.

## Contributing

1. **Fork** the repository on GitHub (<https://github.com/dasprosad/yafax>)
2. **Clone** your fork (`git clone https://github.com/yourname/yourproject`)
2. **Create** your feature branch (`git checkout -b feature/my-new-feature`)
3. **Commit** your changes (`git commit -am 'Describe your changes here'`)
4. **Push** to the branch (`git push origin feature/my-new-feature`)
5. Create a new **Pull Request**

## Reference

- Li, H., Handsaker, R. E., Wysoker, A., Fennell, T., Ruan, J., Homer, N., Marth, G., Abecasis, G., & Durbin, R.; 1000 Genome Project Data Processing Subgroup (2009). *The Sequence Alignment/Map format and SAMtools.* **Bioinformatics**, 25(16), 2078–2079. [DOI:10.1093/bioinformatics/btp352](https://doi.org/10.1093/bioinformatics/btp352).

- Shirley, M. D., Ma, Z., Pedersen, B. S., & Wheelan, S. J. (2015). *Efficient “pythonic” access to FASTA files using pyfaidx*. **PeerJ PrePrints**, 3, e1196. [DOI:10.7287/peerj.preprints.970v1](https://doi.org/10.7287/peerj.preprints.970v1).
