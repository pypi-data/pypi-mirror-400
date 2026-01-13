"""
test_getseq.py

Test script to run test for YAFAX getseq
"""

import sys
from pathlib import Path
import pytest
import subprocess

def test_getseq() -> bool:
    """
    Uses chrm.fa as the genome and chrm.fa.fai
    as the index. Both are stored in tests/data

    Runs yafax getseq and checks whether it matches
    with tests/data/chrm_10000_11000.fa
    """
    position = "chrM:10000-11000"
    genome = Path("tests/data/chrm.fa")
    expected_result = Path("tests/data/chrm_10000_11000.fa")

    cli_cmd = ["yafax", "getseq", position, str(genome)] 
    out = subprocess.run(cli_cmd, capture_output = True, text = True, check = True)
    assert out.stdout == expected_result.read_text()

if __name__ == "__main__":
    pytest.main()
