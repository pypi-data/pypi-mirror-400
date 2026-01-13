"""
index.py

Indexing module for Yet Another FASTA Index and Extraction Tool
"""

import sys
import argparse
from pathlib import Path
from yafax.core import buildIndex, writeIndex

def runIndex(args: argparse.Namespace) -> None:
    """
    Runs the index module
    """
    fasta = args.fasta_path
    outdir = args.out_dir
    if not outdir:
        outdir = None
    if not fasta.exists():
        print(f"FASTA file {fasta} does not exist!", file = sys.stderr)
        sys.exit(2)
    index = buildIndex(fasta)
    writeIndex(index, fasta, outdir)

if __name__ == "__main__":
    runIndex()
