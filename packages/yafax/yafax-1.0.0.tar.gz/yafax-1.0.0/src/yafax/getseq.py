"""
getseq.py

getseq module for Yet Another FASTA Index and Extraction Tool
"""

import sys
import argparse
from pathlib import Path
from yafax.core import revComp, readBed, readIndex, writeSeq, fetchSeq, fetchSeqBed

def runGetseq(args: argparse.Namespace) -> None:
    """
    Runs the getseq module
    """
    width = args.width
    isrevcomp = args.revcomp
    isheader = args.no_header
    fasta = args.fasta_path

    # Check FASTA path
    if not fasta.exists():
        print(f"FASTA file {fasta} does not exist!", file = sys.stderr)
        sys.exit(2)

    # Check index path
    index = args.index_path
    if not index:
        index = fasta.with_suffix(fasta.suffix + ".fai")
    if not index.exists():
        print(f"Index {index} does not exist!, try indexing first", file = sys.stderr)
        sys.exit(2)

    bedfile = args.bedfile
    position = args.position
    outfile = args.outfile

    # Check if --bedfile and <position> supplied together
    if bedfile and position:
        print("Cannot use <position> when --bedfile is provided", file = sys.stderr)
        sys.exit(1)
    elif not bedfile and not position:
        print("Must provide either <position> or --bedfile", file = sys.stderr)
        sys.exit(1)

    # if --bedfile is provided run fetchSeqBed else if <position> is valid run fetchSeq
    if bedfile:
        if not bedfile.exists():
            print(f"BED file {bedfile} does not exist!", file = sys.stderr)
            sys.exit(2)
        if not outfile:
            print("Outfile not provided, writing to STDOUT", file = sys.stderr)
            outfile = None
        index_dict = readIndex(index)
        fetchSeqBed(fasta, index_dict, bedfile, width, isrevcomp, isheader, outfile)
    else:
        try:
            chrom, ival = position.strip().split(":")
            start_str, end_str = ival.split("-")
            start = int(start_str)
            end = int(end_str)
        except ValueError:
            print("Position must be in the format chrom:start-end", file = sys.stderr)
            sys.exit(1)
        if start < 0 or end < 0 or start >= end:
            print("Start and end must be positive and start < end", file = sys.stderr)
            sys.exit(1)
        index_dict = readIndex(index)
        fetchSeq(fasta, index_dict, chrom, int(start), int(end), width, isrevcomp, isheader)

if __name__ == "__main__":
    runGetseq()
