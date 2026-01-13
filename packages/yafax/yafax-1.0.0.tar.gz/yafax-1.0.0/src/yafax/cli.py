"""
cli.py

CLI interface for Yet Another FASTA Index and Extraction Tool

Parses args and exposes the CLI interface
"""

import argparse
from pathlib import Path
from yafax import __version__
from yafax.index import runIndex
from yafax.getseq import runGetseq

def buildParser() -> argparse.ArgumentParser:
    """
    Function to setup argparse and fetch args.
    """
    parser = argparse.ArgumentParser(
            prog = "yafax",
            description = "YAFAX (Yet Another FASTA Indexing and Extraction Tool)",
            usage = "\tyafax <mode> --help\n\tyafax <mode> [mode optional arguments] <fasta file>",
            allow_abbrev = False
    )

    parser.add_argument(
            "-v",
            "--version",
            action = "version",
            version = f"%(prog)s {__version__}"
    )

    # Create subparsers for modules
    mode_parser = parser.add_subparsers(
            title = "yafax mode",
            dest = "mode",
            required = True
    )

    INDEX_parser = mode_parser.add_parser(
            "index",
            help = "generate a FASTA index",
            usage = "yafax index [optional arguments] <fasta file>"
    )

    # Attach function
    INDEX_parser.set_defaults(func = runIndex)

    GETSEQ_parser = mode_parser.add_parser(
            "getseq",
            help = "fetch sequence of an interval using position",
            usage = "yafax getseq [optional arguments] <position> <fasta file>"
    )

    # Attach function
    GETSEQ_parser.set_defaults(func = runGetseq)

    parser.add_argument(
            "fasta_path",
            type = Path,
            metavar = "FASTA FILE",
            help = "path to FASTA file"
    )

    INDEX_parser.add_argument(
            "-d",
            "--out-dir",
            type = Path,
            required = False,
            metavar = "",
            help = "directory of the output FASTA index"
    )

    GETSEQ_parser.add_argument(
            "-i",
            "--index-path",
            type = Path,
            required = False,
            metavar = "",
            help = "path of FASTA index (Default: file.fa.fai)"
    )

    GETSEQ_parser.add_argument(
            "-r",
            "--revcomp",
            default = False,
            action = "store_true",
            help= "reverse complement the sequence (Default: False)"
    )

    GETSEQ_parser.add_argument(
            "-w",
            "--width",
            type = int,
            default = 50,
            metavar = "",
            help = "wrapping width of FASTA lines (Default: 50)"
    )

    GETSEQ_parser.add_argument(
            "-n",
            "--no-header",
            default = False,
            action = "store_true",
            help = "do not include FASTA header (Default: False)"
    )

    GETSEQ_parser.add_argument(
            "-b",
            "--bedfile",
            type = Path,
            metavar = "",
            required = False,
            help = "BED file with regions"
    )

    GETSEQ_parser.add_argument(
            "-o",
            "--outfile",
            type = Path,
            metavar = "",
            required = False,
            help = "output file, only used when BED is provided (Default: STDOUT)"
    )

    GETSEQ_parser.add_argument(
            "position",
            type = str,
            nargs = "?",
            help = "position interval in format chr:start-end"
    )

    return parser

def cli() -> None:
    """
    CLI entrypoint
    """
    parser = buildParser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    cli()
