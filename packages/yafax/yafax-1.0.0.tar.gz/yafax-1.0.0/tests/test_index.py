"""
test_index.py

Script to test yafax index module
"""

import sys
import subprocess
import pytest
from pathlib import Path

def test_index(tmp_path: Path) -> bool:
    """
    Uses tests/data/chrm.fa as input for
    indexing. If the indexing happens it
    will check whether it matches the expected
    result
    """
    genome = Path("tests/data/chrm.fa")
    expected_index = Path("tests/data/chrm.fa.fai")
    faidir = tmp_path / "results"
    faidir.mkdir()

    cli_cmd = ["yafax", "index", "--out-dir", str(faidir), str(genome)]
    subprocess.run(cli_cmd, capture_output = True, check = True, text = True)
    
    produced_index = faidir / "chrm.fa.fai"
    
    assert produced_index.exists()
    assert produced_index.read_text() == expected_index.read_text()

if __name__ == "__main__":
    pytest.main()
