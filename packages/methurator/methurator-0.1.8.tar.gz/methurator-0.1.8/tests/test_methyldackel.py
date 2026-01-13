import os
import subprocess
import pandas as pd
import pathlib


def test_run_methyldackel(tmp_path, monkeypatch):

    # Init the data and set min coverage to 1
    fasta = pathlib.Path(__file__).parent / "data" / "genome.fa"
    bam_path = pathlib.Path(__file__).parent / "data" / "Ecoli.csorted.bam"
    min_cov = 1

    # Use the BAM filename (without directories) as prefix
    bam_name = os.path.basename(bam_path)
    cov_dir = os.path.join(tmp_path, "covs")
    os.makedirs(cov_dir, exist_ok=True)
    prefix = os.path.join(cov_dir, os.path.splitext(bam_name)[0])
    cmd = ["MethylDackel", "extract", "-o", str(prefix), fasta, bam_path]

    # Run command
    subprocess.run(cmd)

    # Read the file (assuming tab-separated)
    file = prefix + "_CpG.bedGraph"
    df = pd.read_csv(file, sep="\t", header=None, skiprows=1)
    # Count rows where column 5 + column 6 >= 3 (0-based indexing in pandas)
    num_cpgs = int(((df[4] + df[5]) >= min_cov).sum())

    # Check correct stats returned
    assert num_cpgs == 41  # 41 CpGs pass filter
