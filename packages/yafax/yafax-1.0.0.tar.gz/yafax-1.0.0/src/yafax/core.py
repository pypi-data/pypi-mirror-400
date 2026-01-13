"""
core.py

Core functions for Yet Another FASTA Index and Extraction Tool
"""

import sys
from pathlib import Path
from typing import Iterator, Optional
from yafax.logger import logMessage as logger

def revComp(seq: str) -> str:
    """
    Reverse complements a given sequence
    """
    complement = str.maketrans("ACTGNactgn", "TGACNtgacn")
    return seq.translate(complement)[::-1]

def readBed(bed_path: Path) -> Iterator[tuple[str, int, int]]:
    """
    Reads a BED file and generates positions as a tuple
    """
    with open(bed_path, mode = "r", encoding = "utf-8") as bh:
        for line in bh:
            if line.startswith("#") or line.strip() == "":
                continue
            chrom, start, end, *_  = line.rstrip().split("\t")
            yield chrom, int(start), int(end)

def buildIndex(fasta_path: Path) -> dict[str, tuple[int, int | None, int | None, int | None]]:
    """
    Takes a fasta file as input and returns a dictionary
    of index fields.
    """
    index = {}
    with fasta_path.open(mode = "rb") as fh:
        seq_name = None
        seq_len = 0
        seq_offset = None
        bases_per_line = None
        bytes_per_line = None

        while True:
            line_offset = fh.tell()
            line = fh.readline()
            if not line:
                break
            if line.startswith(b">"):
                if seq_name is not None:
                    logger("info", f"Creating index for contig: {seq_name}")
                    index[seq_name] = (seq_len, seq_offset, bases_per_line, bytes_per_line, )
                seq_name = line[1:].strip().split()[0].decode()
                seq_len = 0
                seq_offset = None
                bases_per_line = None
                bytes_per_line = None
                continue
            if seq_offset is None:
                seq_offset = line_offset
            clean = line.rstrip(b"\n")
            line_clean = len(clean)
            if bases_per_line is None:
                bases_per_line = line_clean
                bytes_per_line = len(line)
            seq_len += line_clean
        if seq_name is not None:
            index[seq_name] = (seq_len, seq_offset, bases_per_line, bytes_per_line)
    return index

def writeIndex(index: dict[str, tuple[int, int | None, int | None, int | None]], fasta_path: Path, outdir: Path | None) -> None:
    """
    Takes dictionary of index fields and writes to
    a tab-delimited index file.
    """
    if outdir is not None:
        outdir.mkdir(parents = True, exist_ok = True)
        index_path = outdir / (fasta_path.name + ".fai")
    else:
        index_path = fasta_path.with_suffix(fasta_path.suffix + ".fai")
    if index_path.exists():
        raise FileExistsError(f"Index already exists: {index_path}")
    with index_path.open(mode = "w", encoding = "utf-8") as out:
        for name, (length, offset, bpl, bypl) in index.items():
            out.write(f"{name}\t{length}\t{offset}\t{bpl}\t{bypl}\n")

def readIndex(index_path: Path) -> dict[str, tuple[int, int, int, int]]:
    """
    Reads the FASTA index and returns a tuple of
    chrom and byte fields.
    """
    index = {}
    with index_path.open(mode = "r", encoding = "utf-8") as fh:
        for line in fh:
            chrom, length, offset, bpl, bypl = line.rstrip().split("\t")
            index[chrom] = (int(length), int(offset), int(bpl), int(bypl))
    return index

def fetchSeq(fasta_path: Path, index: dict[str, tuple[int, int, int, int]], chrom: str, start: int, end: int, width: int, revcomp: bool, noheader: bool) -> None:
    """
    Fetches sequence of an interval using the fasta
    index and fasta sequence itself (position is 1-based).
    """
    length, offset, bpl, bypl = index[chrom]
    if end > length:
        raise ValueError(f"Requested end {end} > chromosome length {length}!")
    # Convert to 0-based positions
    start0 = start - 1
    start_line = start0 // bpl
    start_col = start0 % bpl
    bytes_pos = offset + start_line * bypl + start_col
    to_read = end - start0
    lines = (start_col + to_read + bpl - 1) // bpl
    bytes_to_read = lines * bypl
    with fasta_path.open(mode = "rb") as fh:
        fh.seek(bytes_pos)
        seq_bin = fh.read(bytes_to_read)
    seq = seq_bin.replace(b"\n", b"")[:to_read].decode()
    header: str | None = None if noheader else f">{chrom}:{start}-{end}\n"
    writeSeq(seq = seq, header = header, width = width, revcomp = revcomp)

def fetchSeqBed(fasta_path: Path, index: dict[str, tuple[int, int, int, int]], bed_path: Path, width: int = 50, revcomp: bool = False, noheader: bool = False, outfile: Optional[Path] = None) -> None:
    """
    Fetches sequences from intervals of BED entries
    and writes to outfile or STDOUT
    """
    out = sys.stdout if outfile is None else outfile.open(mode = "w", encoding = "utf-8")
    # BED path validity will be provided by the upper level function, assumes correct BED
    try:
        with fasta_path.open(mode = "rb") as fh:
            for chrom, start, end in readBed(bed_path):
                if start < 1 or end < 1 or end < start:
                    logger("warning", f"Invalid BED interval {chrom}:{start}-{end}")
                    continue
                length, offset, bpl, bypl = index[chrom]
                if end > length:
                    logger("warning", f"Requested end {end} > chromosome length {length}!")
                    continue
                logger("info", f"Fetching sequence for {chrom}:{start}-{end}")
                start0 = start - 1
                start_line = start0 // bpl
                start_col = start0 % bpl
                bytes_pos = offset + start_line * bypl + start_col
                to_read = end - start0
                lines = (start_col + to_read + bpl - 1) // bpl
                bytes_to_read = lines * bypl
                fh.seek(bytes_pos)
                seq_bin = fh.read(bytes_to_read)
                seq = seq_bin.replace(b"\n", b"")[:to_read].decode()
                if revcomp:
                    seq = revComp(seq)
                out_lines: list[str] = []
                if not noheader:
                    out_lines.append(f">{chrom}:{start}-{end}\n")
                for pos in range(0, len(seq), width):
                    out_lines.append(seq[pos: pos + width] + "\n")
                out.write("".join(out_lines))
    finally:
        if outfile is not None:
            out.close()

def writeSeq(seq: str, header: None | str, width: int = 50, revcomp: bool = False) -> None:
    """
    Figure out yourself what it does!
    """
    out = sys.stdout
    if revcomp:
        seq = revComp(seq)
    if header is not None:
        out.write(header)
    for pos in range(0, len(seq), width):
        out.write(seq[pos:pos + width] + "\n")
